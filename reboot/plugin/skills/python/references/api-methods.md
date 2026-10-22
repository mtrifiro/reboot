---
title: Pick a Method Factory — `Reader`, `Writer`, `Transaction`, or `Workflow`
impact: CRITICAL
impactDescription: The factory drives the context type, isolation, and access semantics
tags: method, reader, writer, transaction, workflow, factory, constructor
---

## Pick a Method Factory — `Reader`, `Writer`, `Transaction`, or `Workflow`

> **Critical:** the factory you choose for a method fixes the
> Servicer method's context type: `Reader(...)` → `ReaderContext`;
> `Writer(...)` → `WriterContext`; `Transaction(...)` →
> `TransactionContext`; `Workflow(...)` → `WorkflowContext` (and the
> implementation must be a `@classmethod`, with no `self.state`).
> Wrong context type = runtime error.

Every method in a `Methods(...)` block uses one of four factories from
`reboot.api`. The factory chooses the context type passed to the
Servicer method and the isolation level applied:

- **`Reader(...)`** — read-only access to `self.state`. Multiple readers
  may run concurrently. Servicer signature: `context: ReaderContext`.
- **`Writer(...)`** — mutates `self.state` for one actor. Serialized with
  other writes/transactions on that actor. Signature: `context: WriterContext`.
- **`Transaction(...)`** — atomic across multiple actors and external
  effects. Signature: `context: TransactionContext`. Must say how it
  holds the lock on its own state with `mode=Exclusive()` (writes its
  own state, or in doubt) or `mode=Shared()` (mostly reads its own
  state while writing others); see `api-pydantic.md`.
- **`Workflow(...)`** — durable, long-running, restartable. Implemented as
  a `@classmethod` (no `self.state`). Signature: `context: WorkflowContext`.
  See `servicer-workflow.md` — the single, comprehensive workflow
  reference — to pick the right primitive for each call (Reboot
  scopes vs. `at_least_once` vs. `at_most_once`), plus
  `context.loop`, state mutation via
  `ref().<scope>.write(context, fn)`, and the rest.

**Incorrect (missing factory):**

```python
# DON'T — every entry must be a Reader/Writer/Transaction/Workflow.
AccountMethods = Methods(
    balance=BalanceResponse,   # WRONG — not a factory call
)
```

**Correct (matches the [`reboot-bank-pydantic`](https://github.com/reboot-dev/reboot-bank-pydantic) example):**

```python
from reboot.api import (
    API, Exclusive, Field, Methods, Model, Reader, Shared, Transaction, Type,
    Writer,
)

AccountMethods = Methods(
    balance=Reader(
        request=None, response=BalanceResponse,
        description="Returns how much money the account holds right "
        "now, which is the most that can be withdrawn or transferred "
        "out of it.",
        mcp=None,
    ),
    deposit=Writer(
        request=DepositRequest, response=None,
        description="Adds the amount given to the account's balance. "
        "Any positive amount is accepted, and the new balance is "
        "visible to every reader as soon as the deposit returns.",
        mcp=None,
    ),
)

BankMethods = Methods(
    transfer=Transaction(
        # The bank only coordinates the two accounts and never writes
        # its own state, so transfers proceed through it concurrently.
        mode=Shared(),
        request=TransferRequest, response=TransferResponse,
        description="Moves an amount from one account to another. "
        "The withdrawal and the deposit happen together or not at "
        "all, so money is never taken from one account without "
        "reaching the other.",
        mcp=None,
    ),
)
```

## The Servicer Signature Each Declaration Obliges

`rbt generate` turns every `Methods(...)` entry into one method
declaration on `<Type>.Servicer`, and the servicer you write must
match it. The whole contract is these six lines — there is nothing
further to learn by opening the generated `*_rbt.py`, which is tens
of thousands of lines:

```python
class AnyNameServicer(<Type>.Servicer):    # subclass this alias

    # `@classmethod`, for a `Workflow(...)` method only.
    async def <entry_name>(                # snake_case, as declared
        self,                              # `cls` for a `Workflow`
        context: <Kind>Context,            # per the factory, above
        request: <Type>.<Entry>Request,   # omitted if `request=None`
    ) -> <Type>.<Entry>Response:          # `None` if `response=None`
```

`<Entry>` is the PascalCase form of the entry name: `add_task`
declared on `Type("TaskList", ...)` gives `TaskList.AddTaskRequest` /
`TaskList.AddTaskResponse`, while the method you write stays
snake_case. So

```python
add_task=Transaction(
    mode=Exclusive(),
    request=AddTaskRequest, response=AddTaskResponse,
    description="Append one task, returning the id it was given.",
    mcp=None,
),
lists=Reader(
    request=None, response=ListsResponse,
    description="Every list this user owns.",
    mcp=None,
),
ensure=Transaction(
    mode=Exclusive(),
    request=None, response=None,
    description="Create the user's default list if they have none.",
    mcp=None,
),
```

obliges exactly:

```python
async def add_task(
    self,
    context: TransactionContext,
    request: TaskList.AddTaskRequest,
) -> TaskList.AddTaskResponse: ...

async def lists(self, context: ReaderContext) -> User.ListsResponse: ...

async def ensure(self, context: TransactionContext) -> None: ...
```

**Two shapes in the generated file look like contradictions of this.
Both are real, and neither is what you write:**

- A **PascalCase twin** of every method (`AddTask` next to
  `add_task`) that delegates to the snake_case one. It keeps
  servicers written before the snake_case rename working. Implement
  the snake_case method.
- A **`state:` parameter**, in signatures like
  `(self, context, state, request)`. Those belong to
  `<Type>.singleton.Servicer`, a variant the framework uses for its
  own singletons. Applications subclass `<Type>.Servicer` and reach
  state through `self.state`.

## `factory=True` Marks the Creation Method

A `Writer` or `Transaction` with `factory=True` is the explicit
creation path for the actor. The Servicer can branch on
`context.constructor` to set initial state:

```python
open=Writer(
    request=OpenRequest,
    response=None,
    factory=True,
    description="Bring the account into existence with a zero balance.",
    mcp=None,
),
```

`Reader` and `Workflow` reject `factory=True` at codegen time — see
`api-pydantic.md` ("`factory=True` Only Works on `Writer` and
`Transaction`"). To kick off a workflow on actor creation, make the
factory a `Writer(factory=True)` / `Transaction(factory=True)` and
schedule the workflow from its body.

A `Type` without an explicit factory method is created implicitly on
first write (see `lifecycle-seeding.md`).

## Pick the Right Factory

- Reading `self.state` only? → `Reader`
- Mutating `self.state` for **one** actor, no calls to other actors? → `Writer`
- Mutating across multiple actors in a single one-shot transaction? → `Transaction`
- Long-running, durable, restartable work (control loops, agents,
  multi-step orchestration), or external calls? → `Workflow`

Wrong-factory symptoms include "context type mismatch" runtime errors and
deadlocks when a `Writer` tries to call into another actor.

## `errors=[...]` Declares Typed Errors

Error `Model`s declared elsewhere in the API file can be attached to a
method, making them part of the typed contract:

```python
class OverdraftError(Model):
    amount: float = Field(tag=1, default=0.0)

withdraw=Writer(
    request=WithdrawRequest,
    response=None,
    errors=[OverdraftError],
    description="Take funds out, or raise `OverdraftError` if the "
    "balance would go negative.",
    mcp=None,
),
```

See `api-errors.md` for raising and catching them.

## `description=` Says What the Method Does

All four method kinds take an optional `description=`:

```python
balance=Reader(
    request=None,
    response=BalanceResponse,
    description="Returns how much money the account holds right "
    "now, which is the most that can be withdrawn.",
    mcp=None,
),
withdraw=Writer(
    request=WithdrawRequest,
    response=None,
    errors=[OverdraftError],
    description="Takes the amount given out of the account. If the "
    "account holds less than that, nothing is taken and the call is "
    "refused with `OverdraftError`, which says how much is available.",
    mcp=Tool(),
),
```

The dev dashboard shows it, and `mcp=Tool()` methods use it as the
tool's description. Write what a caller cannot derive from the
signature: the precondition, the side effect, the unit, which error it
raises and when.

### How a description reads

The descriptions are the app's own documentation: a teammate reads
them on the dashboard's Models page, and an AI caller reads them to
decide what to call. Write them to explain, for someone who knows the
domain but not this app:

- **Whole sentences, in the domain's words.** A method's opens with
  what it does as a verb ("Checks a walk-in guest into the room…"),
  an object's with what one instance is ("One of the hotel's
  rooms…"), a field's with what the value means. Never a fragment,
  a list of nouns, or a colon doing a sentence's work.
- **The why beside the what.** Say what the rule protects: not "the
  consistency boundary for every step", but "every change to a room
  goes through it one at a time, so two people can't check two guests
  into it at once".
- **The conditions in full.** What must be true first, what changes,
  who sees it, and each error by name with what it tells the caller.
- **Two to four sentences** for an object or a method, one or two for
  a field. Calm and plain: no jokes, no clipped shorthand, no "just".

```python
# DON'T — terse, and it leaves the reader to work out the why.
description="One room, keyed by its number: its status in the cycle "
"occupied, dirty, cleaned, inspected, and the guest in it. The "
"consistency boundary for every step taken on it."

# DO — what it is, what it holds, and what that guarantees.
description="One of the hotel's rooms, found by its room number. It "
"holds where the room is in the housekeeping cycle (occupied, then "
"dirty, cleaned and inspected, ready again) and who is staying in it. "
"Every change to a room goes through it one at a time, so two people "
"can never check two guests into the same room."
```

A state type takes one too, via `Type(description=...)`; see
`api-pydantic.md`.

## Every Factory Takes `mcp=`

All four factories require an explicit `mcp=` keyword. Use
`mcp=None` when the method should not be exposed as an MCP tool;
use `mcp=Tool(...)` in MCP Apps projects. See `api-pydantic.md` for
the full rule.

## Seven Method Names Are Off Limits

Don't name a method `read`, `write`, `delete`, `state`, `schedule` or
`spawn`. Reboot uses those names on every state type, and
`rbt generate` refuses the API with
`has illegal name: <Name> is reserved`. Pick the name before the API
is written: `schedule_cleaning`, `delete_booking`.

Nor the API package's own name: a method `rooms` in
`api/rooms/v1/rooms.py` becomes an attribute `rooms` on the generated
class, and from there every annotation `rooms.v1.rooms_pb2.…` in
`rooms_rbt.py` resolves to the method, not the module. `rbt generate`
and the tests pass; `mypy` then fails with
`Name "rooms.v1.rooms_pb2.FloorPlanAddRoomRequest" is not defined` on
every method declared after it (hotel-330: 1 min 20 s to find). Name
it for what it returns: `list_rooms`.

## See Also

`api-pydantic.md` for field rules; `servicer-reader.md`,
`servicer-writer.md`, `servicer-transaction.md`,
`servicer-workflow.md` and `servicer-constructor.md` per factory;
`rpc-calls.md` for calling.
