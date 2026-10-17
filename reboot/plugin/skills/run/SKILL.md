---
name: run
description: Run an existing Reboot application locally. Detects whether the project is an MCP UI or a standalone Web App, makes sure dependencies and secrets are in place, then starts every process the app needs — for an MCP UI a Cloudflare quick tunnel (so external MCP clients can reach the dev server) via the bundled `cloudflared` shim, the backend (`rbt dev run`), and the frontend dev server (for MCP UIs it also opens the setup wizard, from which the user can launch MCPJam on demand). Use this to bring an app back up, e.g. at the start of a new session.
argument-hint: [<project-directory>]
allowed-tools: Bash, Read, Write, Glob, Grep, Edit, AskUserQuestion
---

# run — Run a Reboot Application

> **Version notices** from `rbt` (a mismatch, a newer Reboot): the [upgrade skill](../upgrade/SKILL.md).
>
> **Errors:** grep a fragment of the string in `python/references/errors.md` (never read whole); known defects and workarounds: [`KNOWN-ISSUES.md`](../../KNOWN-ISSUES.md).

Bring an existing Reboot application up locally: the one "start the
app" procedure, for a run, a restart, or a fresh session where no
process and no exported environment survive from last time. It
**runs** an app; it does not build or modify one. To build, the
[`mcp-ui` skill](../mcp-ui/SKILL.md) and the
[web-app skill](../web-app/SKILL.md), which defer here for their
"run the app" step.

## Step 1 — Locate the project

Work in the directory the user named, or the current directory. The
project root is the directory that contains `.rbtrc`; if none is
obvious, ask the user where the app is. Every command below runs
from the project root. If the project has no `AGENTS.md`, or its
`CLAUDE.md` is not just `@AGENTS.md`, give it both with the
[`agents-md` skill](../agents-md/SKILL.md) before starting anything,
so the next session in this project starts with its map.

## Step 2 — Detect the app type

A Reboot project is one of two kinds. Decide by these signals,
strongest first.

**MCP UI** — any of:

- An API file under `api/` uses `mcp=Tool(` or `UI(` (the `UI()`
  method type). `mcp=None` says nothing: every method of every app
  requires the `mcp=` argument, so a Web App has `mcp=None` on all
  of them.
- There is a `frontend/mcp/<name>/index.html`.
- `.rbtrc` has a `dev run --default-config=hmr` line together with
  a `dev run:hmr --frontend-host=...` line: Envoy proxying the
  frontend, which only MCP UIs need.

**Web App** — all of: no `mcp=Tool(` / `UI(` anywhere under `api/`;
the SPA entry `frontend/web/index.html`, and no `frontend/mcp/`.

If the signals genuinely conflict, or none match, ask the user
("Is this an MCP UI or a standalone Web App?"). Do not guess: the
app type decides whether the tunnel runs and the setup wizard opens.

## Step 3 — Dependencies

From the project root: if `.venv/` is missing, run `uv sync`. If
`rbt dev run` later warns that `reboot[dev]` is not installed, add
`reboot[dev]` at the same pin as `reboot` to the dev group of
`pyproject.toml` (`../python/references/lifecycle-project-setup.md`)
and `uv sync` again; the extra is what the tests and the dashboard's
Features page run on. If `frontend/node_modules/` is missing, run
`npm install` in `frontend/`.

## Step 4 — Secrets: the git-ignored env file

Reboot apps read secrets from `os.environ`; `rbt dev run` loads them
from the env file `.rbtrc` names. Set this up **before** starting
the backend:

1. **Find the required variables.** Grep the backend for
   `os.environ[...]`, `os.environ.get(...)` and `os.getenv(...)`,
   and check `main.py` for `Application(oauth=...)` provider
   credentials. Every name found is a variable the app needs.
2. **`.rbtrc` has the line `dev run --env-file=.env`.** If it does
   not, add it.
3. **`.env` is git-ignored**, before any secret is written into it:
   if no line of the project-root `.gitignore` ignores `.env`, add
   one (creating the file if it does not exist).
4. **Fill `.env`** with standard `KEY=VALUE` lines (e.g.
   `ANTHROPIC_API_KEY=sk-ant-...`). For every required variable not
   already a line in `.env` (and not already exported in the
   environment), ask the user for the value and write it in. Never
   start the backend with a required variable missing: the app fails
   at boot or on first use, and the failure is hard to read.

The full secrets story, dev and Reboot Cloud, is
`python/references/lifecycle-secrets.md`.

## Step 5 — Start the processes

Run each process in its own background shell, from the project
root. An MCP UI has two more steps around these, the Cloudflare
quick tunnel before the backend and the setup wizard after it:
[`references/mcp-ui-processes.md`](references/mcp-ui-processes.md).
Skip the tunnel for a **Web App**: it has no MCP clients, and a
tunnel would publish a dev server where the `Development()` picker
lets anyone sign in as anyone.

### Backend — both app types

Before starting it, check that its port is free (`lsof -i :9991`, or
the port `.rbtrc` sets): a process there is a copy left running, by
this session or an earlier one, so stop it instead of starting a
second. Then, in its own background shell:

```sh
uv run rbt dev run --no-chaos
```

`--env-file=.env` in `.rbtrc` loads the secrets into the process;
`--no-chaos` disables the Chaos Monkey, a useful bug-finder that is
confusing to a developer who cannot see the backend terminal.

`Backwards incompatibility encountered` in the backend's log means
the backend is waiting, not crashed: the API changed in a way the
saved state can't take. Make the change additive
(`python/references/api-schema-evolution.md`) and it reloads. When
the development data is disposable, stop the backend and run
`rbt dev expunge --application-name=<name> --yes` instead; a
background shell can't press `x`.

### Frontend — both app types

The Vite dev server, from `frontend/`:

```sh
cd frontend && npm run dev
```

## Stopping the App

Stop `rbt dev run` with Ctrl-C, or `kill -INT <pid>` from another
shell. Stop only this project's: other Reboot apps may be running on
the same machine, and `pkill -f "rbt dev run"` or the first match of
`pgrep` stops theirs. Find its pid by this project's own path, which
also skips the `uv` wrapper that a signal would otherwise reach first:

```shell
kill -INT $(pgrep -f "$PWD/.venv/bin/rbt dev run")
```

**Stop it before running the test suite**, and start it again once
the suite passes. The suite runs its own Reboot over the same
generated code; a running `rbt dev run` regenerates that code when
`api/` changes, under the tests, and the run hangs.

## Step 6 — Hand off

As soon as every process is up, during a build too and before any
check of the page, say one line with both links, on the ports they
started on:

> App: http://localhost:5173/ · Dashboard: http://127.0.0.1:9871/

(For an MCP UI, the app link is the setup wizard,
`http://localhost:9991`.) Then confirm every process is up from its
logs, and give the user the application's own inspect-page URL (and
that `rbt inspect` inspects the same state from the CLI, the
[inspect skill](../inspect/SKILL.md)); for a Web App, the URL the
Vite dev server printed (`http://localhost:5173/` by default) and a
first page to open; for an MCP UI, what
[`references/mcp-ui-processes.md`](references/mcp-ui-processes.md)
says at the hand-off (the wizard, a first prompt, never an MCPJam
URL).

> **Always start every process the app needs.** An MCP UI needs
> backend and frontend; a Web App needs the same. (MCPJam is not in
> this set — it is launched on demand from the wizard, only if the
> user picks it.) The app is not usable until both are up, so do
> not stop after one.
