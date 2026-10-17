---
title: Implement Transaction Methods
impact: HIGH
impactDescription: Cross-actor atomic work requires a transaction
tags: servicer, transaction, TransactionContext, atomic, multi-actor
---

## Implement Transaction Methods

> **Critical:** transactions are **all-or-nothing across actors** —
> any `<Method>Aborted` rolls back **all** mutations in the
> transaction. Reboot may also retry transactions internally, so the
> body must be safe to re-run with the same input — and must **never**
> call outside the system (see below).

A method declared with `Transaction(...)` in the API file receives a
`TransactionContext` and is the only place where you can atomically
mutate multiple actors. The runtime serializes transactions that touch
overlapping actors. The declaration's `mode=` says how the transaction
holds the lock on its own state: `Exclusive()` takes it exclusive as
the transaction starts, so concurrent callers of the actor queue, and
is the choice for a body that writes `state`; `Shared()` takes it
shared and upgrades only if the body writes `state`, so callers that
only read proceed concurrently.

**Incorrect (multi-actor work in a writer):**

```python
async def transfer(
    self, context: WriterContext, request: Bank.TransferRequest,
) -> None:
    # WRONG — writers can only mutate one actor.
    await Account.ref(request.from_id).withdraw(context, ...)
    await Account.ref(request.to_id).deposit(context, ...)
```

**Correct (matches the [`reboot-bank-pydantic`](https://github.com/reboot-dev/reboot-bank-pydantic) example's `BankServicer`):**

`api/bank/v1/bank.py`:

```python
transfer=Transaction(
    # The bank only coordinates: it reads nothing of its own state and
    # writes the accounts, so transfers proceed through it concurrently.
    mode=Shared(),
    request=TransferRequest,
    response=None,
    description="Move funds between two accounts, both sides landing "
    "together or neither.",
    mcp=None,
),
```

`main.py`:

```python
import asyncio
from bank.v1.account_rbt import Account
from bank.v1.bank_rbt import Bank
from reboot.aio.contexts import TransactionContext


class BankServicer(Bank.Servicer):

    async def transfer(
        self,
        context: TransactionContext,
        request: Bank.TransferRequest,
    ) -> None:
        from_account = Account.ref(request.from_account_id)
        to_account = Account.ref(request.to_account_id)

        await asyncio.gather(
            from_account.withdraw(context, amount=request.amount),
            to_account.deposit(context, amount=request.amount),
        )
```

## Transactions Are Atomic Across Actors

If any call inside a transaction fails (raises a `<Method>Aborted`), the
runtime rolls back **all** the mutations made within that transaction —
across every actor it touched.

## External Calls Belong in a Workflow, Not a Transaction

A transaction is **all-or-nothing**: if it aborts, no effect has
taken place. A call that leaves the system — email, a third-party
API, an **LLM / model API call**, a payment, an SMS login code —
**cannot be rolled back**, and Reboot may retry a transaction or, in
development, re-run its body for **effect validation**, firing the
call more than once. Values that differ between runs, such as a
`uuid4()` id, are fine: only one run's mutations are kept.

So a transaction **never** makes an external call itself. It may
call any **in-system actor**; the external call lives in a
`Workflow`, which picks its primitive per `servicer-workflow.md`, and
a `Transaction` (or `Writer`) reaches it only by **scheduling** it:
`await self.ref().schedule().<workflow_method>(context)`. Gotcha 8
in `patterns-common-gotchas.md` has the reasoning.

Rule of thumb: **if a call leaves the system, it belongs in a
workflow, not a transaction.**

## Use `asyncio.gather` for Concurrent Sub-Calls

Independent calls inside a transaction can run concurrently with
`asyncio.gather`. Reboot serializes them as needed at the storage layer; the
gather only parallelizes the network/RPC roundtrips.

## Don't Hold State Outside the Context

Don't stash data on `self` inside a transaction — every call may run on a
fresh Servicer instance, and instance attributes don't persist. State lives
in `self.state` (per-actor) or external systems.

## Transactions May Have No Response

`Transaction(... response=None ...)` is a valid shape for transactions
that have no payload to return. The method's return type is then
`-> None` and the body has no `return` statement — common for
orchestration calls where the caller only needs success/failure
(raised errors). See `api-methods.md` for the obliged signature.

## See Also

`api-methods.md` for the obliged signature; `rpc-forall.md` for
fan-out across many actors; `servicer-workflow.md` for durable
orchestration.
