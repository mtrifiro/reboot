---
name: run
description: Run an existing Reboot application locally. Detects whether the project is an MCP App or a standalone Web App, makes sure dependencies and secrets are in place, then starts every process the app needs — for an MCP App a Cloudflare quick tunnel (so external MCP clients can reach the dev server) via the bundled `cloudflared` shim, the backend (`rbt dev run`), and the frontend dev server (for MCP Apps it also opens the setup wizard, from which the user can launch MCPJam on demand). Use this to bring an app back up, e.g. at the start of a new session.
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
[`mcp-app` skill](../mcp-app/SKILL.md) and the
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

**MCP App** — any of:

- An API file under `api/` uses `mcp=Tool(` or `UI(` (the `UI()`
  method type). `mcp=None` says nothing: every method of every app
  requires the `mcp=` argument, so a Web App has `mcp=None` on all
  of them.
- There is a `frontend/mcp/<name>/index.html`.
- `.rbtrc` has a `dev run:portless --frontend-url=...` line (or a
  `dev run:ports --frontend-url=...` one, for an app kept on plain
  ports) with `--mcp-app`: Envoy proxying the MCP Apps from the dev
  server.

**Web App** — all of: no `mcp=Tool(` / `UI(` anywhere under `api/`;
the SPA entry `frontend/web/index.html`, and no `frontend/mcp/`.

If the signals conflict, or none match, ask the user
("Is this an MCP App or a standalone Web App?"). Do not guess: the
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

1. **Find the required variables.** Search the backend (`grep -rn` through Bash) for
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
root. An MCP App has two more steps around these, the Cloudflare
quick tunnel before the backend and the setup wizard after it:
[`references/mcp-app-processes.md`](references/mcp-app-processes.md).
Skip the tunnel for a **Web App**: it has no MCP clients, and a
tunnel would publish a dev server where the `Development()` picker
lets anyone sign in as anyone.

### Portless when it is ready, plain ports otherwise

Every app these skills scaffold can run under
[portless](https://github.com/vercel-labs/portless), which gives each
local server a name instead of a port: the app is
`https://<app>.localhost` (`<app>` the `.rbtrc`'s
`--application-name`), serving the API, the web app at `/` and the
MCP Apps, all from one origin; the dashboard is
`https://dashboard.<app>.localhost`; several apps run at once with no
port to collide on. Its `.rbtrc` defaults to it
(`dev run --default-config=portless`).

Never ask about it. Before the backend, run `portless doctor` (the
plugin's `portless` shim installs the CLI on first use) and read two
things: the proxy running on port 443, and the local CA trusted.

- **Both:** use portless, saying nothing about it: `rbt dev run` and
  `rbt dashboard` with their default configs, the frontend with
  `npm run dev:portless`. First check that the names are this
  project's: Reboot registers them with `--force`, so a second project
  with the same `--application-name` would take the first one's
  addresses without an error. `portless list`, then for each of
  `https://<app>.localhost` and `https://dashboard.<app>.localhost`
  that is routed to a port something listens on, the folder that
  process runs from:

  ```sh
  pid=$(lsof -nP -iTCP:<port> -sTCP:LISTEN -t | head -1)
  lsof -a -p "$pid" -d cwd -Fn | sed -n 's/^n//p'
  ```

  Another project's folder: run this one on plain ports instead, and
  say so in one line ("Another project already has
  https://<app>.localhost, so this one runs on plain ports"). A route
  to a port nothing listens on is a stale one (reboot#268) and free.
  The name is the project folder's (`render.py`), so this happens only
  for a project named by hand.
- **Either missing:** plain ports, with no question: `rbt dev run
  --config=ports`, `rbt dashboard --config=ports`, the frontend with
  `npm run dev:ports`. The app is `http://localhost:9991`, the
  dashboard `http://127.0.0.1:9871`, read wherever this skill says
  `https://<app>.localhost`.

Never run `sudo`, `portless proxy start` or `portless trust`
yourself: binding port 443 and trusting a CA are the user's. On plain
ports, the first handoff says once how to switch: "For named URLs
(`https://<app>.localhost`) that never collide with another app's
ports, run `portless proxy start` and `portless trust` once in your
own terminal; the next start uses them."

### Backend — both app types

On plain ports, check first that its port is free (`lsof -i :9991`,
or the port `.rbtrc` sets): a process there is a copy left running, by
this session or an earlier one, so stop it instead of starting a
second. (Under portless the backend binds any free port behind its
name, so there is nothing to collide with.) Then, in its own background shell:

```sh
uv run rbt dev run --no-chaos
```

For an MCP App, add `--tunnel-url=<URL>`, the tunnel's URL from
above. `--env-file=.env` in `.rbtrc` loads the secrets into the process;
`--no-chaos` disables the Chaos Monkey, a useful bug-finder that is
confusing to a developer who cannot see the backend terminal. Under
portless (above), the `.rbtrc`'s default config passes `--portless`
and the backend logs its named URLs once it is serving; on plain
ports, add `--config=ports`.

`Backwards incompatibility encountered` in the backend's log means
the backend is waiting, not crashed: the API changed in a way the
saved state can't take. Make the change additive
(`python/references/api-schema-evolution.md`) and it reloads. When
the development data is disposable, stop the backend and run
`rbt dev expunge --application-name=<name> --yes` instead; a
background shell can't press `x`.

### Frontend — both app types

The Vite dev server, from `frontend/`, with the script that matches
the backend's config (its `package.json` mirrors the `.rbtrc`). Under
portless:

```sh
cd frontend && npm run dev:portless
```

On plain ports:

```sh
cd frontend && npm run dev:ports
```

## Stopping the App

Stop `rbt dev run` with Ctrl-C, or `kill -INT <pid>` from another
shell. Stop only this project's: other Reboot apps may be running on
the same machine, and `pkill -f "rbt dev run"` or the first match of
`pgrep` stops theirs. Find its pid by this project's own path, which
also skips the `uv` wrapper that a signal would otherwise reach first:

```shell
P=$(pgrep -f "${UV_PROJECT_ENVIRONMENT:-$PWD/.venv}/bin/rbt dev run"); kill -INT $P
for i in $(seq 10); do kill -0 $P 2>/dev/null || break; sleep 1; done
if kill -0 $P 2>/dev/null; then pkill -TERM -P $P; kill -TERM $P; sleep 5
  kill -0 $P 2>/dev/null && kill -KILL $P; fi
```

**Every stop the build makes to start again** (an `api/` change, a
new dependency, a hang) is followed at once by
`python3 '<this skill>/assets/standby.py' start`: a "Restarting" page
at the app's address, in place of the proxy's 404 or 502, that reloads
itself until the app is back. `standby.py stop` ends it: under portless
once the app answers, on plain ports just before the start (it holds
9991). One line first: "The app is restarting; its page comes back by
itself in a minute or so." (crm-30 showed the proxy's list of every app
on the machine.)

The loop waits, at most 10 seconds, until it has exited: its Envoy and
ports go with it, and a suite started while they are still up has
failed scenarios that pass alone (hotel-211: two failed in a full run
started three seconds after the signal, and passed in the next). One
caught mid-restart, after an `api/` change, can ignore the interrupt
and stay up, unresponsive (seen on a rendered starter, 2026-10-19): the last
line stops that one process, and its own children, by its pid, never
another app's.

**Test runs and the running app.** The suite (and `mypy`) run with
the app still up, unless a file under `api/` changed since the app
last started. A change to `api/` stops the app before its first edit
there, and starts it again as soon as `uv run rbt generate` has run,
before the servicers are written: it restarts itself as they change,
and the scenarios then run with it up, since `api/` hasn't changed
since it started. When the change also changes the demo data, clear
the old data (`uv run rbt dev expunge --yes`) before that start, not
after the servicers. The suite runs its own Reboot
on its own ports; what collides is a running `rbt dev run`
regenerating the code when `api/` changes, under the tests, which
fails scenarios and can hang the app mid-restart. Measured on a
rendered starter (2026-10-19): with the app up and no `api/` change,
4 of 4 full runs passed and the app stayed up; started right after an
`api/` edit, 1 of 2 failed and the app hung.

**A restart that hangs** (a workaround for
[reboot-dev/reboot#278](https://github.com/reboot-dev/reboot/issues/278)):
when the app hasn't answered 45 seconds after `rbt dev run` began a
restart and its log's last line hasn't changed for 30 seconds, it is
waiting on a cancelled task and won't recover. Stop it by its pid as
"Stopping the App" says and start it fresh, at once, never another
wait (crm-30 waited five minutes in two loops before doing so). Once
a Reboot release fixes #278, the restart ends or says why, and this
paragraph goes.

**A stop you made reports as a failure.** `rbt dev run` ends with exit
code 130 when it is interrupted, and the background task that started
it then reports that it failed. After a stop the build made itself,
that notice is expected: never a failure to look into or report
(hotel-255 spent a turn investigating its own stop).

**The design's and the mockup's servers** from the design step
(`design/.design.pid`, the `app-design` skill, section 3;
`design/.comp.pid`, `web-app/references/comp.md`) keep running beside
the app, through the suite and the restarts, so what the user was
shown stays open next to the real page. They are stopped only when the
user asks to stop the app: `kill $(cat design/.design.pid
design/.comp.pid) && rm -f design/.design.pid design/.comp.pid`.

## Step 6 — Hand off

As soon as every process is up, during a build too and before any
check of the page, say one line with both links. Under portless:

> App: https://<app>.localhost/ · Dashboard: https://dashboard.<app>.localhost/

On plain ports:

> App: http://localhost:9991/ · Dashboard: http://127.0.0.1:9871/

The web app is opened at the backend's URL, which serves it (Envoy
sends `/` to the Vite dev server, `--web-app`), never at Vite's own
port, where the page would call the wrong origin. For an MCP App the
app link is the setup wizard at that same URL. Then confirm every
process is up from its logs, and give the user the application's own
inspect-page URL (and that `rbt inspect` inspects the same state from
the CLI, the [inspect skill](../inspect/SKILL.md)); for a Web App, a
first page to open; for an MCP App, what
[`references/mcp-app-processes.md`](references/mcp-app-processes.md)
says at the hand-off (the wizard, a first prompt, never an MCPJam
URL).

> **Always start every process the app needs.** An MCP App needs
> backend and frontend; a Web App needs the same. (MCPJam is not in
> this set — it is launched on demand from the wizard, only if the
> user picks it.) The app is not usable until both are up, so do
> not stop after one.
