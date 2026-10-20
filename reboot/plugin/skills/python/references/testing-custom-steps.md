---
title: Custom Steps Are Plain Reboot Code
impact: HIGH
impactDescription: A custom step that calls through `World.call`, steps outside the scenario's identity, or shares a stand-in across modules passes for the wrong reason, and a recovery test written as a scenario tests Reboot instead of the application
tags: testing, bdd, custom-steps, world, parsers, mock, autouse, fixtures, stand-ins, harness
---

## Custom Steps Are Plain Reboot Code

When a scenario needs a step the built-in steps
([`testing-features.md`](testing-features.md)) don't have, write it
as the code below.

Write a custom step only for what the built-in steps cannot say: a
loop, an assertion on a mock, a stand-in's side channel. Its body
is the same code any Reboot caller writes:

```python
from bank.v1.account_rbt import Account
from reboot.bdd import parsers, then, when
from reboot.bdd.fixtures import World


@when(
    parsers.parse(
        '"{user}" does {count:d} deposits of {amount:d} on `Account` of '
        '<{name}>'
    )
)
async def _makes_deposits(
    world: World,
    user: str,
    name: str,
    count: int,
    amount: int,
) -> None:
    # The account is named by a saved value, the id the factory made
    # up, which the step reads from what the scenario has saved.
    context = world.context(user)
    for _ in range(count):
        await Account.ref(str(world.saved[name])).deposit(
            context,
            amount=amount,
        )
```

- Take the `world` fixture and get the context from
  `world.context(user)`, naming the user the step calls as, spelled
  in the step text the way the built-in steps spell it: a call
  starts with the user, a read with `as "alice",`. That context
  carries the token of a user the scenario declared; reach for
  `rbt.create_external_context()` only to step outside the
  scenario's identity on purpose.
- Call the generated clients directly. Never call through
  `World.call` or `World.request`; they are the built-in steps'
  internals.
- A saved value is read from `world.saved[name]`; the built-in
  substitution of `<name>` does not run on custom steps.
- A step may be `async def`; `reboot.bdd`'s `given` / `when` /
  `then` / `step` run it on the harness's event loop.
- **A fixture may save values** with `world.save('name', value)`,
  so that scenarios say `<name>`: a scripted model that learns a
  page id when a tool returns saves it for the scenario to assert
  on. Order the scenario so a step that recalls the name runs after
  the save is certain (a recall resolves when its step starts).

**Mocked externals assert through one-line custom steps.** A mock
replaces the external call in an autouse fixture, and a `Then` step
asserts on it:

```python
@pytest.fixture(autouse=True)
def send_email() -> Iterator[mock.AsyncMock]:
    with mock.patch('account_servicer.send_email') as mocked:
        yield mocked


@then('the welcome email was sent')
def _the_welcome_email_was_sent(send_email: mock.AsyncMock) -> None:
    # Reboot re-runs methods twice in development mode to validate
    # that they are idempotent, so the email sends twice.
    assert send_email.call_count == 2
```

**Model and dependency stand-ins are autouse fixtures**, and a
module's scenarios share its fixtures, so each stand-in gets a test
module of its own: an application with a scripted LLM has one
module per script, each running the feature files that script
serves.

## What Stays Outside a Feature File

A test that crashes the application in the middle of a method and
brings it back (`testing-failure-recovery.md`) is about Reboot's
recovery, not the application's behavior, and stays an
`IsolatedAsyncioTestCase` on the `Reboot()` harness
(`testing-harness.md`). Everything a user of the application can
observe belongs in a feature file.
