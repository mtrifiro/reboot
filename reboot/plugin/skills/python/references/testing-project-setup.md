---
title: Lay Out a Reboot Backend Test Suite
impact: MEDIUM
impactDescription: Without `reboot[dev]`, the pytest paths, and the git-ignore, the built-in steps are missing, generated `_rbt` modules can't be imported, and recordings get committed
tags: testing, pytest, layout, pyproject, conftest, uv, reboot-dev, gitignore, recordings
---

## Lay Out a Reboot Backend Test Suite

> **Critical:** a Reboot application's tests are Gherkin `.feature`
> files in `tests/` at the project root, run by `reboot.bdd` through
> `pytest`.
> The built-in steps come with the `reboot[dev]` extra, which a
> development environment always installs; without it the scenarios
> have no steps and `rbt dashboard` refuses to start. No
> `pytest-asyncio`: `reboot.bdd` and `IsolatedAsyncioTestCase` run
> `async def` code on their own.

This reference covers the project-level scaffolding every Reboot
backend test suite shares. Writing the scenarios is
[testing-features.md](testing-features.md); driving the web app from
them is [testing-web-app.md](testing-web-app.md); the harness and
context patterns a custom step or a harness test uses are
[testing-harness.md](testing-harness.md) and
[testing-external-context.md](testing-external-context.md).

## Where Tests Live

**One `.feature` file per capability, one test module per
application configuration**, in `tests/` at the project root, next
to `api/` and `backend/`. The tests are the application's, not the
backend's: a scenario that opens the web app drives the frontend too.

```
<app>/
├── api/                      # `*.py` pydantic API definitions.
├── backend/
│   ├── api/                  # Generated `_rbt` modules.
│   └── src/servicers/chat_room.py
├── tests/
│   ├── posting.feature           # One feature per capability.
│   ├── moderation.feature
│   ├── chat_room_test.py         # `application` fixture + `scenarios(...)`.
│   ├── web_test.py               # The scenarios that open the web app.
│   ├── posting.recordings/       # Made by running; git-ignored.
│   ├── last_run.py               # The test record, copied (below).
│   └── conftest.py
├── .gitignore                # `*.recordings/` and the test record.
├── pytest.ini                # Copied with the project shell.
└── pyproject.toml
```

- A feature file is named for the activity (`transfers.feature`),
  not for a state type.
- A test module ends in `_test.py` so `pytest` picks it up, defines
  the `application` fixture returning the `Application(...)` its
  scenarios run against, and calls `scenarios('a.feature', 'b.feature')`
  from `reboot.bdd`. One module per way of configuring the
  application: with authorizers, with a scheduled job turned off,
  with a scripted LLM, with the web app served. The minimal module is
  in [testing-features.md](testing-features.md).
- A crash-and-recover test
  ([testing-failure-recovery.md](testing-failure-recovery.md)) is an
  `IsolatedAsyncioTestCase` in its own `_test.py` module.

## `pytest.ini`, Copied With the Project Shell

The copied `pytest.ini` (`lifecycle-project-setup.md`) names `tests`
as `testpaths`, so a bare `pytest` runs the suite, and puts
`backend/src`, `backend/api`, `api` and `scripts` on the `pythonpath`,
so nothing needs a `pip install -e .`. **Three source entries, not
two:** `backend/src` and `backend/api` cover the servicers and the
generated `_rbt` modules, but tests also import the hand-written API
definition itself (the typed errors and models) as
`from <pkg>.v1.<name> import QuotaExceededError`, which lives in the
project-root `api/`; without it the suite fails at import with
`ModuleNotFoundError: No module named '<pkg>.v1.<name>'`, which looks
like a codegen failure but is a path problem. `scripts` lets the test
of `scripts/model_diff.py` import it (below).

**`timeout = 180`** (from `pytest-timeout`, a dev dependency) fails
any one test that runs past three minutes, with its name and where it
was waiting. Without it, a scenario that hangs (a call that never
answers, a page that never loads) holds the whole run silent until the
command's own limit, which names nothing. Three minutes covers the
slowest browser scenario, which starts the web app's dev server first.

## `conftest.py` — The Test Record, Then Only What's Needed

Every app built with the Reboot Flywheel
(`app/references/flywheel.md`) records each test run as evidence:
`render.py` (`lifecycle-project-setup.md`) writes `tests/last_run.py`,
`scripts/model_diff.py`, `scripts/test.sh`, `scripts/release_record.py`
and `scripts/design_links.py` from the `app` skill's `assets/`, and a
`tests/conftest.py` that imports the record's four pytest hooks from
`last_run` and nothing else.

Add anything else only when a module imported by tests **eagerly**
instantiates something that needs an environment variable, typically
an LLM provider that constructs a client at import time: set a
placeholder (`os.environ.setdefault("ANTHROPIC_API_KEY", "test-placeholder")`)
so the import succeeds; tests must still mock the real call before any
RPC fires. Put a fixture here only when several test modules share
it; a stand-in for a model or a dependency is an autouse fixture in
the one test module whose scenarios use it, since a module's scenarios
share its fixtures ([testing-features.md](testing-features.md)).

## Dev Dependencies

The copied `pyproject.toml` has `reboot[dev]` at the same pin as
`reboot`, `pytest` and `pytest-timeout`; `reboot[dev]` carries what
`reboot.bdd` and the dashboard's Features page run on and registers
the built-in steps as a pytest plugin, so no test module imports
them. An application whose scenarios open its web app also needs the
two commented lines, `playwright` and `pytest-playwright` (and
`uv run playwright install chromium` once). Do **not** add
`pytest-asyncio`: `reboot.bdd` runs its steps on the harness's event
loop, `IsolatedAsyncioTestCase` handles its own, and `pytest-asyncio`
conflicts with both. `uv sync` installs the `dev` group by default,
so `uv run pytest`, `uv run mypy backend/ tests/` and
`uv run rbt dashboard` just work; an application packaged for
`rbt serve` installs plain `reboot`.

Running a scenario that opens the web app records a video and
screenshots into `<feature>.recordings/` beside the feature file
([testing-web-app.md](testing-web-app.md)); the copied `.gitignore`
keeps `*.recordings/` and the test record out of git.

## Running Tests

From the application root:

```bash
uv run pytest                           # Whole suite.
uv run pytest tests/chat_room_test.py   # One module (the feature files it runs).
uv run pytest -k "posts a message"      # One scenario, by (part of) its name.
uv run pytest -m wip                    # What is being worked on; -m "not wip" for the rest.
uv run pytest -v -s                     # Verbose, print() output to the terminal.
```

A `@blocked` scenario is skipped, with its description as the reason,
so it shows in the summary without failing the suite.

## Don't Construct Servicer Instances Directly

The #1 trap for new Reboot test authors is calling
`ChatRoomServicer().send(...)` directly, in a custom step or a harness
test. That bypasses identity, context, persistence, and authorization:
it tests nothing the framework does. The built-in steps call through
the application; a custom step does the same with
`world.context(user)` and `Service.ref(id).method(context, ...)`
([testing-features.md](testing-features.md)), and a harness test with
`rbt.create_external_context(...)`
([testing-harness.md](testing-harness.md)).
