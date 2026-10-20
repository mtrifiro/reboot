---
title: Define APIs in Pydantic
impact: CRITICAL
impactDescription: The pydantic API file is the source of truth; everything else is generated from it
tags: pydantic, api, Model, Methods, Reader, Writer, Transaction, factory
---

## Define APIs in Pydantic

> **Critical:**
>
> 1. Every `Field(tag=N)` needs an explicit default. Missing defaults
>    → `AttributeError` at first access (codegen uses
>    `model_construct()` which skips undeclared defaults).
> 2. `default=` **must be the type's zero value** (`""`, `0`, `0.0`,
>    `False`; `default_factory=list` or `dict` for a list or dict,
>    since `default=[]` is refused; for a `Literal`, its first value).
>    Non-zero defaults raise
>    `UserPydanticError` at import. Set domain defaults inside the
>    constructor or a `start`-style writer, not on the Field.
> 3. Every `Field(tag=N)` gets a `description=` saying what the value
>    means. The dashboard shows it beside the property; a property
>    without one shows a request to add it.

Reboot APIs are pydantic `.py` files. `rbt generate` consumes them
and produces a `<name>_rbt.py` module with the typed `<Type>` class
(request/response messages nested as attributes), the
`<Type>.Servicer` base class, and the `<Type>.ref(id)` factory. The
[`reboot-bank-pydantic`](https://github.com/reboot-dev/reboot-bank-pydantic)
repository is the canonical example.

**Incorrect (free-floating decls that aren't wired up via `API(...)`):**

```python
# DON'T — Methods is the binding from name to method type; declarations
# outside of an API(...) block never reach the generator.
from reboot.api import API, Field, Methods, Model, Writer

class AccountState(Model):
    balance: float = Field(tag=1, default=0.0)

class DepositRequest(Model):
    amount: float = Field(tag=1, default=0.0)

# Free-floating, never wired up:
deposit_request = DepositRequest
```

**Correct (from [`reboot-bank-pydantic`](https://github.com/reboot-dev/reboot-bank-pydantic), `api/bank/v1/account.py`, two methods shown):**

```python
from reboot.api import API, Field, Methods, Model, Reader, Type, Writer


class AccountState(Model):
    balance: float = Field(
        tag=1,
        default=0.0,
        description="What the account holds, in dollars: every deposit "
        "added and every withdrawal and transfer out taken away, and "
        "never below zero.",
    )


class BalanceResponse(Model):
    amount: float = Field(
        tag=1,
        default=0.0,
        description="The balance at the moment of the read, in dollars.",
    )


class DepositRequest(Model):
    amount: float = Field(
        tag=1,
        default=0.0,
        description="How much to add, in dollars; any amount is accepted.",
    )


AccountMethods = Methods(
    balance=Reader(
        request=None,
        response=BalanceResponse,
        description="The funds currently available to withdraw.",
        mcp=None,
    ),
    deposit=Writer(
        request=DepositRequest,
        response=None,
        description="Add funds. Any amount is accepted.",
        mcp=None,
    ),
)


api = API(
    Account=Type(
        state=AccountState,
        methods=AccountMethods,
        description="One customer's money, and the consistency "
        "boundary for every change to it.",
    ),
)
```

## Every Property Has a Description

Each `Field(...)` takes `description=`, a sentence or two saying
what the value means to the application, as a method's
`description=` says what the method does. Write one for every
property of every Model: state, request, response, and error. The
dashboard's Models page shows it beside the property, and for a
property without one shows "No description provided, please ask
your friendly coding agent to add one for you."

Describe the meaning, the units and any invariant the value obeys,
not the type, which the annotation already says, in whole sentences
as `api-methods.md`'s "How a description reads" says:

```python
# DON'T — restates the annotation.
balance: float = Field(tag=1, default=0.0, description="The balance.")

# DO — says what the number is and what is true of it.
balance: float = Field(
    tag=1,
    default=0.0,
    description="What the account holds, in dollars: every deposit "
    "added and every withdrawal and transfer out taken away, and "
    "never below zero.",
)
```

When adding a property to an existing Model, add its description in
the same change.

## Method Factories

`Reader`, `Writer`, `Transaction` and `Workflow` are the four
factories; `api-methods.md` picks between them and gives the
servicer signature each obliges. Attach typed errors via
`errors=[ErrorModel, ...]`. Mark a method as a constructor with
`factory=True` (only valid on `Writer` and `Transaction`, see
below). Say what the method does with `description="..."`.

Every `Transaction(...)` must also say how it holds the lock on its
own state while it runs, with `mode=Exclusive()` or `mode=Shared()`
(both imported from `reboot.api`); `rbt generate` refuses a
transaction without one. `Exclusive()` takes the lock exclusive from
the start, so concurrent callers of the same state queue behind it:
the choice for a transaction that writes its own state, which is most
of them, and the safe choice when in doubt. `Shared()` takes the lock
shared and upgrades it only if the body writes its own state, so
callers proceed concurrently while none of them writes it: the choice
for a transaction that mostly reads its own state while writing
others, such as the root of a tree of states.

### `factory=True` Only Works on `Writer` and `Transaction`

`Reader` and `Workflow` reject `factory=True` at codegen:

```text
Error while parsing option value for "method": Message type
"rbt.v1alpha1.WorkflowMethodOptions" has no field named "constructor".
```

```python
# OK
open=Writer(... factory=True ...),       # Account.Open(ctx, id, ...)
place=Transaction(... factory=True ...), # Order.Place(ctx, id, ...)

# REJECTED by `rbt generate`
hello=Workflow(... factory=True ...),    # codegen error
get=Reader(... factory=True ...),        # codegen error
```

To kick off a workflow on actor creation, make the factory a
`Writer(factory=True)` or `Transaction(factory=True)` and have
its body call `self.ref().schedule().<workflow_name>(context, ...)`;
see `servicer-workflow.md`.

Calling `<Type>.<MethodPascalCase>(ctx, <state-id>, **kwargs)` both
creates the actor and runs the factory method. Never call a factory
through `<Type>.ref(<id>).<method>(...)`: the actor doesn't exist
yet. See `rpc-calls.md`.

### Every Method Factory Takes a Required `mcp=` Argument

`Reader`, `Writer`, `Transaction`, **and `Workflow`** all require an
explicit `mcp=` kwarg. The MCP Apps integration uses it to control
tool exposure; in non-MCP projects (or for methods not exposed as
tools) the value is `mcp=None`. Omitting it raises at codegen:

```text
1 validation error for Workflow
mcp
  Field required [type=missing, input_value=...]
```

Workflows get caught by this most, being rarely tool-callable:

```python
autoplay=Workflow(
    request=None, response=None,
    description="Play the game out to a result without a human taking "
    "turns.",
    mcp=None,
),
```

## Field Tags Are Required

`Field(tag=N)` is the wire-level field number. Tags are required on
every field and must be unique within a `Model`.

## Every Field Needs an Explicit Default

The codegen builds the **initial** state with
`<Type>.State.model_construct()`, which in pydantic v2 skips fields
without a default. The model then raises `AttributeError` the first
time that field is read or written, typically inside the constructor.

**Incorrect (no defaults: the first access raises `AttributeError`):**

```python
class GameState(Model):
    board: str = Field(tag=1)            # AttributeError on access
    turn: str = Field(tag=2)
    history: list[str] = Field(tag=3)
```

```text
AttributeError: 'GameState' object has no attribute 'history'
```

**Correct (every Field carries a default):**

```python
class GameState(Model):
    board: str = Field(tag=1, default="")
    turn: str = Field(tag=2, default="")
    history: list[str] = Field(tag=3, default_factory=list)
    score: int = Field(tag=4, default=0)
    paused: bool = Field(tag=5, default=False)
```

Use `default=<zero>` for scalar fields (`""`, `0`, `False`) and
`default_factory=list` / `default_factory=dict` for collections. This
applies to **state**, **request/response** and **error** Models,
anywhere `model_construct` may run.

### `default=` Must Be the Type's Zero Value

The only legal `default=` is the field type's **zero value**. The
wire format has nowhere to store a per-field default, so a non-zero
one could never take effect; the codegen rejects it at import
instead.

**Incorrect (non-zero defaults are rejected at import time):**

```python
class CheckersState(Model):
    turn: str = Field(tag=1, default="r")          # rejected
    move_delay_seconds: float = Field(tag=2, default=1.0)  # rejected
    max_players: int = Field(tag=3, default=2)     # rejected
```

```text
reboot.api.UserPydanticError: Field `turn` in model `CheckersState` uses
`default` with an unsupported value. Supported default value for `str`
is ``.
```

**Correct (zero default in the API, real value set in the constructor):**

```python
class CheckersState(Model):
    turn: str = Field(tag=1, default="")
    move_delay_seconds: float = Field(tag=2, default=0.0)
    max_players: int = Field(tag=3, default=0)
```

Apply the domain defaults inside the constructor method, gated on
`context.constructor` (`servicer-constructor.md`), or unconditionally
inside a `start`-style reset writer:

```python
DEFAULT_MOVE_DELAY = 1.0


async def open(
    self, context: WriterContext, request: OpenRequest,
) -> None:
    if context.constructor:
        self.state.turn = "r"
        self.state.move_delay_seconds = DEFAULT_MOVE_DELAY
```

## Collections of Nested Models Are Supported

`list[<Model>]` and `dict[str, <Model>]` are first-class field types,
with the same defaulting rule: `default_factory=list` /
`default_factory=dict`.

```python
class Move(Model):
    from_row: int = Field(tag=1, default=0)
    to_row: int = Field(tag=2, default=0)


class GameState(Model):
    history: list[Move] = Field(tag=1, default_factory=list)
    moves_by_id: dict[str, Move] = Field(tag=2, default_factory=dict)
```

`list[str]`, `list[int]`, `list[float]`, `list[bool]`,
`dict[str, str]`, `list[<Model>]`, and `dict[str, <Model>]` all work.

## State Class Is a Separate `Model`

State is a plain `Model` class. Bind it to its method set and a public
type name via `Type(state=<NameState>, methods=<NameMethods>)` inside an
`API(...)` block. The generated module exports `<Name>` (e.g. `Account`)
with `<Name>.Servicer`, `<Name>.ref(id)`, and request/response messages
nested as attributes (`Account.BalanceResponse`, `Account.DepositRequest`).

### `Type(description=...)` Says What the State Type Is For

`Type` takes an optional `description=`, shown by the dev dashboard
beside the state type's name and file (see `api = API(...)` above).
A state type's name alone rarely says what it is _for_. Write the
part a reader cannot derive from the fields and methods listed
beside it: what it is the consistency boundary for, what one
instance corresponds to, how its ID is chosen. Per-method
descriptions are separate; see `api-methods.md`, whose "How a
description reads" applies to every description: whole sentences,
the why beside the what, the conditions in full.

### Generated Request/Response Names Come From the **Method Name**

The nested attributes are `<Type>.<MethodPascalCase>Request` and
`<Type>.<MethodPascalCase>Response`, named after the method, not
after the source class bound to `request=` / `response=`; see gotcha
15 in `patterns-common-gotchas.md`. The servicer signature each
declaration obliges, including `request=None` / `response=None`, is
in `api-methods.md` ("The Servicer Signature Each Declaration
Obliges").

## `.rbtrc`

`generate api/` picks up pydantic `.py` API definition files from `api/`.
See `lifecycle-rbtrc.md` for the rest.
