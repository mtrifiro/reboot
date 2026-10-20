---
title: Specify Behavior in Feature Files
impact: MEDIUM
impactDescription: Feature files are the application's specification and its test suite at once; a suite written any other way is neither reviewable by the developer nor shown by the dashboard
tags: testing, bdd, gherkin, feature, scenario, rule, pytest-bdd, reboot.bdd, wip, blocked, custom-steps, world
---

## Specify Behavior in Feature Files

> **Critical:** a Reboot application's tests are Gherkin `.feature`
> files run by `reboot.bdd`, which ships built-in steps for every
> call an application takes. Write scenarios in the built-in steps'
> spelling below; write a custom step only for what they cannot
> say, and write it as plain Reboot code. Every step that calls
> names who calls: there is no current user and no anonymous call.

A feature file is the specification the developer reviews, the
suite `pytest` runs through the `Reboot()` harness, and what the
dashboard's Features page shows; it serves all three only in the
built-in steps' spelling.

The [`reboot-bank-pydantic`](https://github.com/reboot-dev/reboot-bank-pydantic)
example's `tests/*.feature` files are the reference for
every pattern here.

## What Goes Where

`testing-project-setup.md` has the `tests/` layout, `pytest.ini`,
`pyproject.toml`, and the `.gitignore`.

- **One `.feature` file per capability**, named for the activity:
  `transfers.feature`, `opening_accounts.feature`. Not
  `bank.feature` or `account.feature`: those name state types, which
  the dashboard already indexes as such.
- **One test module per application configuration**: the
  `application` fixture returning the `Application(...)` the
  scenarios run against, and a `scenarios(...)` call naming the
  feature files that run against it: the bank's `full_bank_test.py`
  (authorizers and interest off), `interest_test.py` (interest on),
  and `web_test.py` (the scenarios that open the web app).

The minimal module:

```python
"""The bank's tests: the Gherkin scenarios in the `.feature` files
beside this module."""

import pytest
from account_servicer import AccountServicer
from bank_servicer import BankServicer
from reboot.aio.applications import Application
from reboot.bdd import scenarios


@pytest.fixture
def application() -> Application:
    return Application(servicers=[AccountServicer, BankServicer])


scenarios('deposits.feature', 'withdrawals.feature')
```

Nothing imports the built-in steps: the `reboot` package registers
them as a pytest plugin, active whenever `reboot[dev]` is installed.
A module runs a second application by naming it: `Given the "proxy"
application is up` runs what a `proxy_application` fixture returns.

`uv run pytest` from the project root runs the suite; one file,
`uv run pytest tests/full_bank_test.py`; one scenario,
`-k "transfer between two"`; by tag, `-m wip` or `-m "not wip"`.

## The Shape of a Feature

```gherkin
Feature: Customers can transfer money between accounts
  A customer moves money from one of their accounts to another
  account of the bank in one step, which is how they pay someone
  without a withdrawal and a deposit that could come apart.

  Background:
    Given the application is up

  Rule: A transfer moves exactly the amount from one account to the other
    Neither account sees any other change.

    Scenario: A transfer between two customers' accounts
      Given "anonymous" is an unauthenticated user
      And "anonymous" creates a `Bank` via `create`
      And the resulting state id is saved as <bank id>
      When "anonymous" does a `sign_up` with `customer_id="test@reboot.dev"` on `Bank` of <bank id>
      And "anonymous" does an `open_account` with `initial_deposit=1000.0` on `Customer` of "test@reboot.dev"
      And the resulting `account_id` is saved as <first account id>
      And "anonymous" does a `sign_up` with `customer_id="test2@reboot.dev"` on `Bank` of <bank id>
      And "anonymous" does an `open_account` with `initial_deposit=0.0` on `Customer` of "test2@reboot.dev"
      And the resulting `account_id` is saved as <second account id>
      And "anonymous" does a `transfer` with `from_account_id=<first account id>` and `to_account_id=<second account id>` and `amount=250.0` on `Bank` of <bank id>
      Then as "anonymous", `balance` on the `Account` for <first account id> has `amount=750.0`
      And as "anonymous", `balance` on the `Account` for <second account id> has `amount=250.0`

  Rule: A transfer that would overdraw the source leaves both accounts unchanged
    A transfer is one transaction: when the withdrawal from the source
    account aborts, the deposit into the destination is rolled back
    too, so money is never created by a failed transfer.

    Scenario: A transfer for more than the source account holds
      ...
```

**A feature is a capability, a rule is an invariant, a scenario is
an example.**

- The **feature** is one thing a user can do, named as a sentence
  about the activity, with a description saying what it is for; it
  is the right size when its rules all serve one user goal and read
  like a specification someone could implement from.
- A **rule** is a business invariant someone would verify formally
  (money is conserved by a transfer), stated once, in its name and
  description. A scenario that only shows what an operation or a
  page does sits at the feature's top level, with no rule.
- A **scenario** is one concrete illustration, named for the
  situation, never a restatement of the rule; a `Scenario Outline`
  with an `Examples` table illustrates one rule at several values.
- The **background** carries what every scenario starts from
  (`Given the application is up`, the users everyone needs); a user
  only some scenarios use stays out of it.
- Tests of Reboot's own mechanisms (a spawned task runs, a schedule
  fires) belong in Reboot's suite, not in the application's
  specification.

## Who Calls

Every scenario declares its people, and every step that calls says
who:

```gherkin
Given "alice" is an authenticated user
And "admin" has the bearer token "secret-admin-token"
And "bob" is an unauthenticated user
```

- `is an authenticated user` mints a test token for that user id
  through the same path a real sign-in takes, so the application's
  `User` for them is auto-constructed. A scenario that needs an
  authorizer to let someone in, or keep someone out, says who it is
  this way; it never subclasses a servicer to weaken the authorizer.
- `has the bearer token "..."` names a user by a raw token, for an
  application whose own `TokenVerifier` accepts it.
- `is an unauthenticated user` declares someone whose calls carry
  no token. Their refusal is the rule's: `Unauthenticated` from a
  built-in sign-in check, `PermissionDenied` from a role check of
  your own (hotel-302 assumed the first).

A call starts with the user; a read starts with `as "alice",`:

```gherkin
When "alice" does a `deposit` with `amount=50` on `Account` of "alice"
Then as "alice", `balance` on the `Account` for "alice" has `balance=50`
```

A step that names nobody is refused with a hint. There is no
current user and no anonymous call: a scenario with a single
unauthenticated caller names them `"anonymous"`, and invents names
only when it has two people to tell apart.

`Given as "alice", a shared context` makes every call from then on
share one context, the way one client session does; every later
call must then name the same user.

## Calls, Results, and Saved Values

```gherkin
Given "alice" creates an `Account` via `open` with `initial_balance=100`
And the resulting state id is saved as <account id>
When "alice" does a `deposit` with `amount=50` on `Account` of <account id>
Then the result has `updated_balance=150`
And the resulting `account_id` is saved as <alice account id>
```

- **`creates`** calls a factory. Leave the id out and the factory
  makes one up (saved as below). Give an id, `creates an `Account`of "alice" via`open``, only when the id means something to the application: a user id, a singleton the code itself refers to (`"coupon-book"`), a natural key.
- **`does`** calls a writer, transaction, or workflow; the article
  follows English (`does an `open_account`` ). The properties of the request come right after the method: `with `a=1` and `b="x" ``.
- **A call does one thing; its result is saved on the next line.**
  `the resulting `account_id` is saved as <...>` saves a response
  property; `the resulting state id` and `the resulting task id`
  save what `creates` and `spawns` produced. `the result has ...`
  asserts on the last response.
- **A value is saved as a variable**, `saved as <first account id>`
  (spaces allowed), and said back bare, `of <account id>` or
  `amount=<balance>`. It becomes its JSON text, a string with its
  quotes, so `of "<account id>"` fails as not JSON, and a string can't
  be built into another (`url="/a/<account id>"`; assert `containing`).
  An Outline's columns work the same (a string column quoted in its
  table), so a save may not use a column's name.
- **Values are JSON** with JSON5's leniencies: `owner={name: "Frank", tags: ["vip"]}`. A dotted path nests when calling,
  `owner.name="Frank"`, and reaches into the response when
  asserting, `balances[0].account_id=<ann account id>` or
  `owners["main"].name="Heidi"`.

## Reads and Assertions

```gherkin
Then as "alice", `balance` on the `Account` for <account id> has `amount=100.0`
And as "alice", `balances` on the `Customer` for "ann" has `balances` of length `1` and `balances[0].balance=25.0`
And as "anonymous", `all_customer_ids` on the `Bank` for <bank id> has `customer_ids` containing `"alice"`
And as "alice", `has_at_least` with `amount=50` on the `Account` for <account id> has `enough=true`
```

- A `Then ... has` asserts; clauses are `path=value`, `path`
  containing `value` (a substring, a list element, or a map key),
  and `path` of length `n`, joined by `and` or commas.
- A reader that takes properties is given them right after the
  method, the way a call is: `has_at_least` with `amount=50` on the
  `Account` for ...`.
- Readers are only read this way: `does` and `attempts` refuse a
  reader, and `has` refuses a writer.
- A `Given` or `When ... has` saves instead of asserting: `has `owner.name` saved as <owner name>`.

**Waiting** for a task, a schedule, or a workflow to land is a
reactive read with a bound, never a sleep:

```gherkin
Then as "anonymous", `balance` on the `Account` for <account id> eventually has `amount=1.0` within 10 seconds
```

`eventually has` is only a `Then`. A `Given` or `When ... has` saves
what it reads *now*, so `eventually has` there is refused ("Almost: a
Given or When 'has' saves what it reads now; 'eventually has' asserts,
under a Then"). To wait for something before acting on it (a brief a
workflow writes, then edited), write the wait as a `Then` and go on
with `When` steps after it:

```gherkin
When as "alice", does a `research` on the `Account` for <account id>
Then as "alice", `brief` on the `Account` for <account id> eventually has `ready=true` within 30 seconds
When as "alice", does an `edit_brief` on the `Account` for <account id> with `summary="Expanding to EMEA"`
```

## Attempts, Aborts, and Tasks

```gherkin
When "alice" attempts a `withdraw` with `amount=50` on `Account` of <account id>
Then the attempt aborts with `OverdraftError` with `amount=20`
And as "alice", `balance` on the `Account` for <account id> has `balance=30`

Then as "anonymous", `balance` on the `Account` for "ghost" aborts with `StateNotConstructed`
```

- `attempts` makes a call that may abort; `the attempt aborts with`
  names the declared error type and, optionally, its properties. A
  reader's abort is asserted on the read itself.
- **An uncaught non-Reboot error aborts with `Unknown`**: a
  validation `ValueError` in a servicer, an index out of range.
  Declare an error and assert on that instead.

```gherkin
When "anonymous" spawns a `deposit` with `amount=15` on `Account` of <account id>
And the resulting task id is saved as <first>
Then "anonymous" awaits the `deposit` task <first> on `Account` within 30 seconds
And the result has `updated_balance=15`
```

`spawns` runs the call as a task; a task id a response carries is
saved and awaited the same way.

## Tags: `@wip` and `@blocked`

```gherkin
@wip
Feature: Users can sign in
  ...

  Rule: A user signs up once

    @blocked
    Scenario: Signing up twice under the same id
      The bank does not refuse a second sign-up yet: the customer's
      factory aborts with `StateAlreadyConstructed`, which the bank
      lets surface as `Unknown`. This waits for a declared error.

      Given ...
```

- **`@wip`** marks the feature, rule, or scenario being worked on.
  It runs as usual; the dashboard marks it in green and filters by
  it. Where it goes and when it comes off: the
  [`feature` skill](../../feature/SKILL.md).
- **`@blocked`** marks a scenario the application cannot pass yet,
  or one that needs a person to do something first (a credential, a
  decision, an external system). Its description, the paragraph
  right under the `Scenario:` line, says why; the scenario is
  skipped with that reason, and the dashboard marks it in red and
  filters by it.

The `feature` skill (`../../feature/SKILL.md`) is the workflow that
puts these tags on and takes them off.

## Custom Steps

A step the built-in steps don't have is a custom step:
[`testing-custom-steps.md`](testing-custom-steps.md).
