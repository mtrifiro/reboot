---
title: Startup: `initialize`, Then Seed in Batches
impact: HIGH
impactDescription: A singleton created in the wrong place never exists; a seed of one transaction per record, or of batches run concurrently, stalls or takes minutes; a full production seed in every test dominates the suite
tags: initialize, InitializeContext, singleton, idempotent, idempotently, alias, seeding, seed, demo data, batch, fixture, OrderedMap
---

## Startup: `initialize`, Then Seed in Batches

Everything that runs at application start. When a seed stalls, hangs
or errors, read
[`lifecycle-seeding-troubleshooting.md`](lifecycle-seeding-troubleshooting.md).

### The `initialize` Hook

`initialize` is an optional `async` callback passed to
`Application(...)` ([`lifecycle-application-entry.md`](lifecycle-application-entry.md)).
It runs against an `InitializeContext` and is where singletons and
seed data are created: not a Servicer's `__init__`, which runs lazily
when an actor is first referenced, not at app start, and has no
context.

```python
async def initialize(context: InitializeContext):
    await Bank.create(context, SINGLETON_BANK_ID)
```

> **Critical:** `initialize` runs on **every** application start, so
> everything it does must be safe to run twice. Its calls get an
> **auto-generated idempotency key** (one per `actor` + `method`) and
> run once; `Service.create(context, id)` and factory methods are a
> no-op on existing actors. The catch: to call the **same method on
> the same actor more than once** you **must** distinguish the calls
> with `.idempotently("alias")` (or an explicit `key=`), or the second
> one raises `ValueError: To call '...' more than once using the same
> context an idempotency alias or key must be specified`. Reusing one
> alias for two different calls is also an error: one distinct alias
> per distinct call.

Reboot may also retry a transaction internally, so nothing in one
depends on running exactly once: the same input produces the same
state change once committed. A constructor that may run again on an
existing actor gates its set-once fields on `context.constructor`
([`servicer-constructor.md`](servicer-constructor.md)).

A `Type` with no `factory=True` method is constructed implicitly by
its first writer call, so `await ChatRoom.ref(ROOM_ID).send(context,
message="Hello")` needs no `create`. When the API declares a factory,
call it: `Service.create(context, id)` or
`Service.<CtorMethod>(context, id, ...)`.

### Seed Data in Batches, Sequentially, with Aliases

For more than a few records (a catalog, demo data, a development
dataset), three rules make a seed fast and restartable:

- **One function, with the size as parameters.** `initialize` passes
  the production size; tests pass a small one.
- **One transaction per batch.** It creates the batch's actors
  (distinct actors need no alias) and adds them to the shared index
  with one bulk `insert(entries=...)`, not one insert per record
  ([`stdlib-ordered-map.md`](stdlib-ordered-map.md)). It calls only
  constructors and that insert: put each record's starting state (a
  member's plan, a room's status) in its create request, instead of
  calling the record's methods one after another.
- **One batch at a time**, each call with an **alias built from the
  batch's contents**, so a seed that restarts skips the batches that
  already landed.

`backend/src/seed.py`:

```python
from reboot.aio.external import ExternalContext
from chain.v1.chain_rbt import Chain

CHAIN_ID = "chain"


async def seed_chain(
    context: ExternalContext,
    *,
    theaters: int,
    seats_per_row: int,
    batch_size: int = 20,
) -> None:
    await Chain.create(context, CHAIN_ID)
    chain = Chain.ref(CHAIN_ID)
    ids = [f"theater-{n:03d}" for n in range(theaters)]
    for start in range(0, len(ids), batch_size):
        batch = ids[start:start + batch_size]
        # The same method on the same actor every iteration, so each
        # call needs its own alias. Built from the ids, not a clock or
        # a random value, it is the same when the seed runs again.
        await chain.idempotently(f"add-theaters-{batch[0]}").add_theaters(
            context, theater_ids=batch, seats_per_row=seats_per_row,
        )
```

An index keyed by time gets many keys per millisecond from a seed.
Mint them with Reboot's `reboot.uuidv7.uuid7`, not the
`uuid7-standard` package that `reboot` also installs: its `create()`
is not monotonic, so two keys minted in the same millisecond may
iterate out of order.

`initialize` calls the seed at full size. A test calls it small,
through an app-internal context, since seeding methods are usually
internal-only and a user's context gets `PermissionDenied`:

```python
await seed_chain(
    self.rbt.create_external_context(name="seed", app_internal=True),
    theaters=2, seats_per_row=5,
)
```

Tests assert against the seed's constants, not literal counts, so a
change to the seed doesn't break them. Only the few tests about the
production size need the production seed.

### Demo Data in Development Only

A believable dataset makes every view show something the first time it
opens. Seed it only under `rbt dev run`:

```python
from reboot.run_environments import running_rbt_dev


async def initialize(context: InitializeContext):
    if running_rbt_dev():
        await seed_demo(context, rooms=12, guests=8)
```

`running_rbt_dev()` is true only when `rbt dev run` set the
environment, so it is false under `rbt serve`, on Reboot Cloud, and in
the test harness. Scenarios seed what each one needs.

### Seeding `User` Actors

There is no public API for it. The generated servicer has a static
`_authenticated(context, state_id, claims=None)`; call it on the
servicer class (`UserServicer._authenticated(context, state_id=user_id)`,
not `User._authenticated`). It constructs the `User` if it doesn't
exist and does nothing otherwise, so it is safe from `initialize`. A
seed can't act as a user, though: `initialize` has no user identity.

### See Also

- [`testing-harness.md`](testing-harness.md): fixtures and `app_internal=True`
