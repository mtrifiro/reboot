---
title: Set Up a Reboot Python Project
impact: CRITICAL
impactDescription: Project won't build or run without the right files in place; the shell is copied from the python skill's `assets/project/`
tags: project-setup, pyproject, python-version, dependencies, layout
---

## Set Up a Reboot Python Project

> **Critical:** the `api/` directory holds pydantic API definition
> files (`.py`); generated `*_rbt.py` lives under `backend/api/`.
> Never hand-edit a generated file. No `__init__.py` anywhere — not
> in `api/`, not under `backend/`.

A Reboot Python project has a fixed top-level layout. The CLI (`rbt`)
reads `.rbtrc` from the project root, `rbt generate` writes generated
code into `backend/<output>/`, and the application entry point lives
in `backend/src/main.py`:

```
my-app/
  .rbtrc                 # required: per-project rbt CLI config
  .gitignore             # required
  .mypy.ini              # required: type-check config
  pyproject.toml         # required: Python deps
  pytest.ini             # required: see `testing-project-setup.md`
  api/                   # API definition root (referenced from .rbtrc)
    <pkg>/v1/<name>.py
  backend/
    api/                 # rbt generate --python output
    src/
      main.py            # application entry
      servicers/
        <name>.py        # one Servicer per state machine
  tests/                 # see `testing-project-setup.md`
    <capability>.feature
    <name>_test.py
  frontend/              # see the `web-app` and `mcp-ui` skills
    api/                 # rbt generate --react output
    web/                 # the browser SPA, if the app has one
    mcp/<ui-name>/       # the MCP UIs, if the app has any
```

The shell files are copied from the `python` skill's assets, never
retyped and never read:

```sh
cp -R <the python skill>/assets/project/. .
```

Then replace `<project-name>` in `.rbtrc` and `pyproject.toml`. What
the copy holds, and the rule behind each file:

- `pyproject.toml`: Reboot supports Python 3.10+. The only runtime
  dependency is `reboot`; `reboot[dev]`, at the same pin, adds what
  the tests (`reboot.bdd`) and the dashboard run on (`rbt dashboard`
  refuses to start without it, `rbt dev run` warns), and a
  development environment always installs it: `uv sync` installs the
  `dev` group by default, then `uv run mypy backend/ tests/` and
  `uv run pytest` use that environment. An application packaged for
  `rbt serve` installs plain `reboot`. `name` and `version` are
  required (`uv` refuses to sync without them); there is **no
  `[build-system]` table**, which tells `uv` this is a virtual
  project: the dependencies go into `.venv`, the app itself is never
  built. An LLM provider SDK for `reboot.agents` is an extra of
  `reboot` (`reboot[anthropic]==1.6.0` in `dependencies`), so it
  resolves at the version that works with the Pydantic AI release
  `reboot` pins (`agent-pydantic-ai.md`). An older project's
  `[tool.rye]` table migrates to this shape: its dev dependencies into
  `[dependency-groups].dev`, `name`/`version` added,
  `requirements*.lock` replaced by `uv lock`.
- `.gitignore`: `.rbt/` (dev-server state), `backend/api/` and
  `frontend/api/` (generated, recreated by `rbt generate`: a fresh
  clone and CI run `rbt generate` before anything imports or
  type-checks, `rbt dev run` regenerates on its own), `.env` (secrets,
  `lifecycle-secrets.md`), `*.recordings/` (browser scenarios,
  `testing-web-app.md`), the test record (`tests/.last-run.json`,
  `.suite-running`, `.progress.jsonl`), the virtualenv and caches,
  `node_modules/` and `frontend/dist/`.
- `.mypy.ini`: generated modules and servicer code have **no
  `__init__.py`** (`protoc` doesn't emit them), so `mypy_path` names
  the source roots (`tests:backend/src:backend/api:api`) with
  `explicit_package_bases`; without it `mypy backend/ tests/` fails
  with bogus "module not found" errors. **The project-root `api/`
  entry is required:** without it `from <pkg>.v1.<name> import <X>State`
  quietly resolves to `Any`, mypy still reports "Success", and every
  annotation on a state or request model checks nothing. To confirm
  the config is live, add a bogus attribute access on a state model
  and check that mypy reports `has no attribute`.
- `.rbtrc`: `lifecycle-rbtrc.md`. `pytest.ini`:
  `testing-project-setup.md`. `backend/src/main.py`:
  `lifecycle-application-entry.md`.

## Always Type-Check What You Write

After writing or changing any Python in `backend/`, run
`uv run mypy backend/ tests/` from the project root and fix every
error before the work is done, the same way the tests run. The
generated `*_rbt.py` stubs are fully typed, so mypy catches what a
glance misses: a field of the wrong type, a missing or misspelled
keyword argument, a method called with the wrong context type, a
response field that doesn't exist. A green mypy run plus a passing
`uv run pytest` (`testing-project-setup.md`) is the bar for "done".

## Do Not Create `__init__.py` — Anywhere

An `__init__.py` inside `api/` confuses `rbt generate`'s package
detection, and `backend/` and `tests/` don't need one: `.mypy.ini`
resolves imports via `explicit_package_bases`, and at runtime the
`PYTHONPATH` that `rbt` sets up does. A Reboot project contains no
hand-written `__init__.py` at all.

## Generated Code Lives Under `backend/`

`rbt generate` (configured in `.rbtrc`) writes
`backend/api/<pkg>/<v>/<name>_rbt.py`; the file is read-only, every
regen overwrites it.
