---
title: Set Up a Reboot Python Project
impact: CRITICAL
impactDescription: Project won't build or run without the right files in place; the shell and the starter app are rendered from the python skill's assets by `render.py`
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
  frontend/              # see the `web-app` and `mcp-app` skills
    api/                 # rbt generate --react output
    web/                 # the browser SPA, if the app has one
    mcp/<ui-name>/       # the MCP Apps, if the app has any
```

An MCP App copies its own shell (`mcp-app/references/project-shell.md`).
A web app or a backend renders the shell and the starter app from the
`python` skill's assets, named for the design, never retyped and never
read:

```sh
python3 '<the python skill>/assets/render.py' --app '<App Name>' \
    --pkg <pkg> --hub <Hub> --thing <Thing> [--things <Things>] [--web] .
```

Single quotes, as written. `<Hub>` is the design's one hub object (the
hotel, the band), `<Thing>` the first feature's central object (a room,
a gig); `--web` adds the web app and its browser scenarios (the
`web-app` skill's step 1). Besides the files below it writes a working
app in that shape, green as it stands (`uv sync && uv run rbt generate
&& uv run pytest`): a `User`, the hub and the thing in
`api/<pkg>/v1/<pkg>.py`, their servicers with real authorizers,
`main.py`, the tests in the built-in steps, the test record and
scripts. **A path with a space:** do what `render.py` prints (the venv
outside the project; `rbt generate` fails under it). The build edits it into the design with the Edit tool: the
design's fields and methods beside the starter's, in the same shape; a
name that doesn't fit is renamed, no file rewritten whole; a file that
exists is kept. What the shell holds, and the rule behind each file:

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
  `reboot` (`reboot[anthropic]==1.7.1` in `dependencies`), so it
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
  with spurious "module not found" errors. **The project-root `api/`
  entry is required:** without it `from <pkg>.v1.<name> import <X>State`
  quietly resolves to `Any`, mypy still reports "Success", and every
  annotation on a state or request model checks nothing. To confirm
  the config is live, `reveal_type` a typed local (below): it names
  your class. Never test it on `self.state`, which is `Any` either
  way.
- `.rbtrc`: the `generate`, `dev run`, `dev expunge` and `serve run`
  lines, and the dashboard's `portless` (default) and `ports` configs;
  `--web` appends the web app's `portless` / `ports` / `dist` configs
  (`lifecycle-rbtrc.md`). `pytest.ini`:
  `testing-project-setup.md`. `backend/src/main.py`:
  `lifecycle-application-entry.md`.

## Always Type-Check What You Write

After writing or changing any Python in `backend/`, run
`uv run mypy backend/ tests/` from the project root and fix every
error before the work is done, the same way the tests run. mypy
checks the calls you write against the generated `*_rbt.py`: a
method called with the wrong context type, a missing or misspelled
keyword argument, a servicer method returning the wrong type. It does
**not** check `self.state` or a method's `request` inside a servicer:
`_rbt.py` declares `<Type>.State` and each `<Method>Request` as
`typing.cast(type, ...)`, which mypy reads as `Any`
(`reveal_type(self.state)` → `Revealed type is "Any"`, verified at
1.6.1), so a misspelled or missing field passes. Bind both to the
hand-written models as typed locals, first thing in every method
that touches them:

```python
from <app>.v1.<app> import CounterState, IncrementRequest

    async def increment(self, context, request: Counter.IncrementRequest) -> None:
        state: CounterState = self.state
        req: IncrementRequest = request
        state.value += req.amount   # now `state.valeu` is an error
```

A green mypy run plus a passing `uv run pytest`
(`testing-project-setup.md`) is the bar for "done".

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
