---
title: "Call Actor Methods with Kwargs and a Context, and Get Their References with `Service.ref(id)`"
impact: HIGH
impactDescription: Calling with Request wrappers fails at type-check or runtime; calling a constructor through `.ref(...).method(...)` skips creation semantics; wrong ref-construction calls hit nonexistent actors or crash at startup
tags: rpc, call, kwargs, context, await, constructor, create, factory, ref, actor, identity
---

## Call Actor Methods with Kwargs and a Context

> **Critical:** pass arguments as **kwargs**, not as a Request wrapper.
> `await ref.deposit(context, amount=10)` — not
> `await ref.deposit(context, DepositRequest(amount=10))`. Constructor
> calls return a `(ref, response)` tuple — reuse the returned ref
> instead of re-constructing one.

Actor methods are called as `await ref.method(context, **kwargs)`. The
context is always positional; the request fields are passed as **keyword
arguments** matching the request `Model`. Do not construct and pass
a `Request` wrapper.

**Incorrect (passing a Request wrapper):**

```python
# DON'T — pass kwargs, not the Request type.
await account.deposit(context, DepositRequest(amount=100))
```

**Correct (matches the [`reboot-bank`](https://github.com/reboot-dev/reboot-bank) example):**

```python
await account.deposit(context, amount=100)
```

## The Context Type Must Match the Method

| Calling from         | Readers | Writers, transactions, workflows |
| -------------------- | ------- | -------------------------------- |
| `ReaderContext`      | yes     | no                               |
| `WriterContext`      | yes     | no, not even its own actor's     |
| `TransactionContext` | yes     | yes                              |
| `WorkflowContext`    | yes     | yes                              |
| `ExternalContext`    | yes     | yes                              |

A writer can't call another writer, including one on its own actor
through `self.ref()`. The call fails as it is made, with
`TypeError: reboot.aio.contexts.WriterContext is not an instance or
subclass of one of the expected type(s): ['reboot.aio.contexts.TransactionContext', ...]`.
To change two actors together, make the caller a `Transaction`; to
change this actor in two steps, do both in one writer.

When in doubt, call from a `transaction` context — it can call any method
on any actor.

## Returns the Response Message

`await ref.method(...)` returns the response `Model`. Read its
fields directly:

```python
response = await chat_room.messages(context)
print(response.messages)
```

## Constructor Calls Use `Service.create` / `Service.<ctor>`

Rule: never invoke a constructor through `Service.ref(id).method(...)`
— that skips creation semantics. Use `await Service.create(context, id)`
for the default constructor (idempotent from `initialize`, so safe on
every start) and `await Service.<CtorMethod>(context, id, **kwargs)`
for a `factory=True` method. Both return a `(ref, response)` tuple;
reuse that ref instead of constructing another with `Service.ref(...)`.

```python
# Wrong — a regular call; the actor does not exist yet.
await Account.ref(account_id).open(context)

# Right — creates the actor and runs the factory method.
account, _ = await Account.open(context, account_id)
await account.deposit(context, amount=request.initial_deposit)

# Default constructor, from `initialize`:
await Bank.create(context, SINGLETON_BANK_ID)
```

## Concurrent Calls with `asyncio.gather`

Within a transaction, parallelize independent calls with
`asyncio.gather`:

```python
import asyncio

await asyncio.gather(
    from_account.withdraw(context, amount=request.amount),
    to_account.deposit(context, amount=request.amount),
)
```

## Get Actor References with `Service.ref(id)`

> **Critical:** `self.state_id` does **not** exist on a Servicer
> instance. Use `self.ref().state_id` inside writer/reader/transaction
> methods, and `context.state_id` inside `@classmethod` workflows. Plain
> `self.state_id` raises `AttributeError`.

`Service.ref(id)` returns a typed handle to the actor with the given
string ID. The ref is cheap to construct, doesn't hit storage, and can be
made anywhere a context is in scope.

**Incorrect (instantiating the Servicer directly):**

```python
# DON'T — Servicer instances are managed by Reboot, not callers.
servicer = ChatRoomServicer()
await servicer.send(...)
```

**Correct (use `.ref(id)`):**

```python
from chat_room.v1.chat_room_rbt import ChatRoom

chat_room = ChatRoom.ref("reboot-chat-room")
await chat_room.send(context, message="Hello!")
```

## IDs Are Caller-Supplied Strings

The actor ID is whatever string the caller chooses. Common patterns:

- A semantic key (account ID, room name).
- A UUID generated at creation time.

```python
from uuid import uuid4

self.state.account_ids_map_id = str(uuid4())
# OrderedMap is constructed implicitly on the first `insert`.
```

## `self.ref()` Inside a Servicer Refers to the Current Actor

A Servicer can get a ref to itself with `self.ref()`. Useful for
self-scheduling:

```python
async def open(
    self, context: WriterContext, request: OpenRequest,
) -> OpenResponse:
    await self.ref().schedule(when=timedelta(seconds=1)).interest(context)
    return OpenResponse()
```

## Use `self.ref().state_id` (Not `self.state_id`) Inside Servicers

A Servicer instance does **not** carry the actor's ID as `self.state_id`
— that attribute doesn't exist and accessing it raises `AttributeError`.
The right form depends on the context type:

| Context                                                  | Get the actor's state ID via |
| -------------------------------------------------------- | ---------------------------- |
| `ReaderContext` / `WriterContext` / `TransactionContext` | `self.ref().state_id`        |
| `WorkflowContext`                                        | `context.state_id`           |

**Incorrect (raises `AttributeError: 'XServicer' object has no attribute 'state_id'`):**

```python
async def tick(self, context: WriterContext, request) -> None:
    rng = random.Random(hash((self.state_id, ...)))  # self.state_id doesn't exist
```

**Correct (writer/reader/transaction):**

```python
async def tick(self, context: WriterContext, request) -> None:
    rng = random.Random(hash((self.ref().state_id, ...)))
```

**Correct (workflow):**

```python
@classmethod
async def control_loop(cls, context: WorkflowContext, request):
    queue = Queue.ref(f"{context.state_id}-messages-queue")
    ...
```

This is also why composite-key patterns (e.g. naming an `OrderedMap`
after the parent actor) reach for `self.ref().state_id` from a writer/
transaction and `context.state_id` from a workflow.

## Refs Don't Materialize Actors

Calling `Service.ref(id)` does **not** create the actor. The actor exists
when its constructor (explicit or implicit) has been called. A reader call
on a non-existent actor returns the zero-valued state; a writer
call against a state without an explicit constructor implicitly creates
the actor and proceeds.
