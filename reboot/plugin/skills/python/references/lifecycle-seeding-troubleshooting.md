---
title: When a Seed Stalls, Hangs or Errors
impact: MEDIUM
impactDescription: Concurrent or oversized seed transactions stall with nothing logged; an uncertain mutation makes the next bare call from the same context fail
tags: seeding, troubleshooting, deadlock, lock wait, effect validation, expunge, PermissionDenied, IdempotencyUncertainError
---

## When a Seed Stalls, Hangs or Errors

Read when a seed stalls, hangs or errors. The seed itself is
[`lifecycle-seeding.md`](lifecycle-seeding.md).

### What Goes Wrong

- **Concurrent seeding transactions** (`asyncio.gather` over batches,
  a semaphore of 12). Transactions that share actors (the index, a
  parent) queue on each other's locks. Twelve concurrent bulk imports
  were observed to stall indefinitely with nothing logged, where run
  one at a time each took five to seven seconds (1.5.0).
- **One transaction per record.** About 3,600 calls at about 1.5 s
  each in development were unfinished after five minutes (1.5.0).
- **Too much in one transaction.** There is no documented size limit,
  but one is reachable: 138 creates plus inserts into one shared
  `OrderedMap` worked, while 360 hung the app at startup with the log
  filling with lock waits and no error (1.4.1). Keep batches to tens of
  creates. A lock wait gives up after 30 s and the transaction retries
  (`LOCK_ACQUIRE_DEADLINE_DEFAULT`), so an oversized seed loops on lock
  waits instead of failing.
- **Methods called per record inside the seed transaction.** A batch
  that joins each member, then sells a plan, then checks them in makes
  three calls per record while holding the parent's lock. Under
  `rbt dev run`, effect validation runs the transaction a second
  time; at 1.6.0 that second run was observed to wait on the first
  one's lock until Reboot aborted it as `PRESUMED_DEADLOCK` and the
  app stopped serving.
- **A large `list[...]` inline on an actor the seed keeps writing.**
  Every write re-serializes the whole list. Collections that grow go in
  an `OrderedMap` ([`state-collections.md`](state-collections.md)).
- **Development state that lived through incompatible designs.**
  Expunge and reseed. `rbt dev expunge` asks for confirmation and waits
  for an answer, so pass `--yes` when running it without a terminal.

### Effect Validation and Seed Speed

`rbt dev run` runs each mutation twice to check it has no side effects
outside Reboot, which was observed to roughly double mutation latency.
For a large seed, turn it off: `rbt dev run --effect-validation=disabled`
(choices `enabled`, `quiet`, `disabled`; the default is `quiet`), or in
the harness `rbt.up(..., effect_validation=EffectValidation.DISABLED)`.

With validation on, a `Re-running method <name> to validate effects`
line per seeded method is normal. Under `quiet`, it prints once per
method and is then silenced for five minutes, so a long seed goes
quiet. Measure its progress from state (`rbt inspect`), not the log.

Observed sizes, for scale: a sequential seed with validation disabled
admitted 193 records at about one per second, then about 6 s per bulk
import, about 15 minutes in all on an M-series laptop, and a restart
part way resumed through the aliases (1.5.0). A full production seed
added about 30 s to each harness test; a small seed cut one suite from
7m50s to 3m52s (1.4.1).

### Errors

| Error text                                                                        | Meaning                                                                                 | Fix                                                                                                                             |
| --------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `PermissionDenied` on a seed call in a test                                       | An internal-only method called with a user's context                                    | Seed through `create_external_context(name=..., app_internal=True)`                                                             |
| `database.cc Check failed`                                                        | Development state from an incompatible earlier design                                   | Stop the app, `rbt dev expunge --application-name=<name> --yes`, reseed                                                         |
| `is presumed deadlocked with it; aborting so that the older transaction proceeds` | Transactions contending for the same actors; the younger one is rolled back and retried | Seed one batch at a time; observed at 1.6.0 also on sequential `initialize` transactions, about 2.5 s each, and then succeeding |

### Uncertain Mutations — `IdempotencyUncertainError`

When a mutation call raises, the client has to decide whether the
mutation actually happened on the server. It can only be sure when
the exception is **definitively from the backend**: an `Aborted`
carrying an error the method _declared_. Those are recoverable — a
caller can catch one and the transaction still commits.

Anything else (a transport failure, a cancellation, an undeclared
error) leaves the client genuinely unable to tell, so it marks the
context as having an **uncertain mutation**. The next mutation you
make from that same context _without_ an idempotency key then
fails with `IdempotencyUncertainError`:

> Because we don't know if the mutation from calling `X` of state
> `'…'` failed or succeeded AND you've made some NON-IDEMPOTENT
> mutations we can't reliably determine whether or not the call to
> `Y` … is due to a retry which may cause an undesired mutation

The refusal is caused by an _earlier_ call that left the context
uncertain.

Two consequences:

- **Asserting a declared error is safe.** A test that does
  `with self.assertRaises(TaskList.AddTaskAborted)` on a method
  that declares `QuotaExceededError` creates no uncertainty, and
  the context stays usable for the assertions that follow.
- **Retrying a mutation yourself requires an idempotency key.**
  Any hand-written retry loop, and any mutation issued after a
  cancelled or transport-failed one, must carry
  `.idempotently("alias")` or an explicit `key=`:

  ```python
  await TaskList.ref(list_id).idempotently("Add the first task").add_task(
      context, title="Milk",
  )
  ```

  The alias must be unique within the lifetime of the context —
  reusing one is how you tell Reboot "this is the same logical
  mutation", which is exactly right for a retry and exactly wrong
  for two different additions.

### See Also

- [`lifecycle-seeding.md`](lifecycle-seeding.md): the seed's three rules, `seed.py`, demo data
- [`testing-harness.md`](testing-harness.md): a fresh context per expected failure
- [`errors.md`](errors.md): every error text, with its reference
