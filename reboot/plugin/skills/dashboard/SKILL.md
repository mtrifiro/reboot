---
name: dashboard
description: Start the Reboot developer dashboard (`rbt dashboard`) for a project and open it in the browser. Puts the minimum files in place (a `pyproject.toml` depending on `reboot[dev]`, a `.rbtrc`, the API directory), starts the dashboard in a background shell if one is not already serving (it opens itself in the browser), and hands the user its URL. Use this while BUILDING an app — the dashboard watches the API directory from before anything is running, so the developer watches the API take shape as it is written. Not for running an app (see the run skill).
argument-hint: [<project-directory>]
allowed-tools: Bash, Read, Write, Glob, Grep, Edit
---

# dashboard — Start the Reboot Developer Dashboard

> **Version notices** from `rbt` (a mismatch, a newer Reboot): the [upgrade skill](../upgrade/SKILL.md).

The developer dashboard, served by `rbt dashboard`, shows an
application's API and call graph (Models), its `.feature` files with
their rules, scenarios and browser recordings (Features), and a
changelog of the API. It reads files, not a running app, so start it
early and the developer watches the API take shape. Use this skill
when a build flow directs you here (the `mcp-app` and `web-app`
skills do, right before the API is written) or when the user asks
for the dashboard while an app is being built.

> This skill **starts the dashboard**, nothing else. It does not run
> the application — that is the [run skill](../run/SKILL.md).
> The dashboard is optional: if any step below fails, tell the user
> the dashboard is not available and continue the build. Do not stop the build to debug it.

## Step 1 — Locate the project

Work in the directory the user named, or the current directory. The
project root is the directory holding (or about to hold) `.rbtrc`.
Every command below runs from the project root. The API files live
in `api/` at the project root in every scaffold this plugin produces;
deviate only if the project visibly keeps its API elsewhere (the
`generate <dir>` line of an existing `.rbtrc`).

## Step 2 — The minimum files

`rbt dashboard` needs three things on disk. In a build flow the
scaffolding step has created them all; check, and create only what
is missing:

1. **`pyproject.toml` depending on `reboot` and, in its dev group,
   `reboot[dev]`** (plus `.python-version`), so `uv run rbt`
   resolves: `rbt dashboard` refuses to start without the extra,
   which carries what its Features page runs on, and a project that
   pins only `reboot` gets `reboot[dev]` added at the same version.
   If missing, both come from the python skill's project template
   (`../python/references/lifecycle-project-setup.md`).
2. **`.rbtrc`.** Everything the dashboard reads of the project comes
   from here: the API directory from the `generate <dir>` line, and,
   for its code checks, the application from `dev run --application=`
   and the generated Python from `generate --python=`; its location
   anchors the working directory and the `.rbt/` state. Without a
   `generate <dir>` line it refuses to start. With no `.rbtrc` yet,
   a stub the later scaffolding extends:

   ```
   generate api/
   generate --python=backend/api/
   dev run --application=backend/src/main.py
   ```

3. **The API directory** from Step 1 (`mkdir -p api`). It may be
   empty: the dashboard watches it and picks up files as they appear.

`uv` is always on PATH under this plugin, whose `uv` shim installs it
on demand (elsewhere, `curl -LsSf https://astral.sh/uv/install.sh | sh`).

## Step 3 — Is a dashboard already serving?

Where the dashboard serves follows the app's mode (the run skill's
"Portless when it is ready, plain ports otherwise": `portless doctor`,
never a question). Under portless it is
`https://dashboard-<app>.localhost/`, `<app>` being the `.rbtrc`'s
`dev run --application-name`; on plain ports it is
`http://127.0.0.1:9871/`. Call that URL `<dashboard>` below. Probe it:

```sh
curl -sf -o /dev/null --max-time 2 <dashboard>
```

- **Under portless,** an answer is this project's dashboard (the name
  is this app's): do not start a second one. Surface the URL and stop.
- **On plain ports,** an answer may be another project's: a project
  built earlier on the same machine keeps its dashboard on 9871, and
  its links show that project's model. Check which folder it runs
  from, from the project root:

  ```sh
  pid=$(lsof -nP -iTCP:9871 -sTCP:LISTEN -t | head -1)
  ps -o command= -p "$(ps -o ppid= -p "$pid")" | grep -F "$PWD/" \
    && echo "this project's" || echo "another project's"
  ```

  This project's: surface the URL and stop. Another project's (or
  nothing named in the command): leave it running, since it isn't
  this build's to stop, and start this project's own on the first
  free port from 9872 up (`lsof -nP -iTCP:<port> -sTCP:LISTEN` prints
  nothing for a free one), with `--port=<port>` in Step 4. Every
  dashboard link from then on uses that port, and the hand-over says
  why it isn't 9871.

## Step 4 — Start the dashboard

From the project root, in its own background shell:

```sh
uv run rbt dashboard
```

**In the Claude app** (or any host with a Browser pane, such as the
app's `preview_start` tool), start it so it opens nothing outside the
app, and show it in the pane instead (`app` skill, "Open the dashboard
in the app's Browser pane"): `rbt dashboard` opens its page through
Python's `webbrowser`, which runs `$BROWSER` when it is set, and
`true` does nothing and succeeds:

```sh
BROWSER=true uv run rbt dashboard                  # under portless
BROWSER=true uv run rbt dashboard --config=ports   # on plain ports
```

It takes the API directory from the `generate <dir>` line in
`.rbtrc`, spelled relative to the project root, which is how file
names are shown. It prints `Your dashboard is at http://127.0.0.1:9871/`
(or the port given) immediately and keeps running, even when it can't
take the port: wait until the probe from Step 3 succeeds and the check
there names this project before calling it up. It stays running for
the life of the session and never needs a restart when code changes.
If it fails to come up (for example the local Envoy check fails
because neither Docker nor an `envoy` executable is available, or
the user declined portless and the proxy is not running: then
`uv run rbt dashboard --config=ports`, on the plain port), warn
the user in one sentence and continue the build without it.

## Step 5 — Hand over the URL

In the Claude app, the pane is where it opens (Step 4); never also in
the external browser. Elsewhere, do not open the page yourself:
`rbt dashboard` opens it once it is serving, unless a tab is already
showing it or the developer chose "Don't reopen automatically", and
opening it as well gives the developer two tabs.

Tell the user the dashboard is up, in one line that always starts
with its URL (`<dashboard>`, as it started, even when the browser opened
it: a terminal session may have no window, and the line is where the
user finds it again later), then what it is for, a link to each object
the API declares so far and to each feature file written so far, then
continue the build:

> The developer dashboard is at https://dashboard-hotel.localhost/ (it
> opens in your browser): it shows the domain model as it's written,
> starting with [Room](https://dashboard-hotel.localhost/#/models?type=hotel.v1.Room)
> and [Hotel](https://dashboard-hotel.localhost/#/models?type=hotel.v1.Hotel),
> and the [Room status floor plan](https://dashboard-hotel.localhost/#/features/tests/room_status.feature)
> feature with its rules.

(On plain ports the same line with `http://127.0.0.1:9871/`.)

**In a build that checks the model next** (the `app-guided` skill's "Build
on this domain model?", `app/references/design-first.md`, section 4),
this line is not written on its own: the model check's lead line is
the hand-over, the dashboard named once, a plain-ports dashboard on a
port other than 9871 said there in a few words. Never a second line listing the same objects,
and never the URL line, the objects line and the Models · Features ·
Changelog line one after another.

### Links to an Object or a Rule

The dashboard opens on the exact thing a link names, so link each
object and rule wherever you name it, from `<dashboard>` as it
started:

- An object: `<dashboard>#/models?type=<package>.<Type>`,
  such as `#/models?type=hotel.v1.Room`; a method appends
  `.<method>` (`hotel.v1.Room.check_in`).
- A feature: `#/features/<path from the project root>`, such as
  `#/features/tests/room_status.feature`; its rules add `/rules/<n>`,
  counted from 1 in file order.
- The dashboard's three pages: `#/models` (the domain model),
  `#/features` (each feature with its rules and scenarios) and
  `#/changelog` (every change to the model and the rules, newest
  first). Once a feature file exists, every line that links the
  dashboard links all three, as "Dashboard: Models · Features ·
  Changelog", each word a link to its page on the port the dashboard
  started on.
- **When the call graph appears.** The models page draws lines
  between methods for the Reboot calls it finds in the servicers'
  code (one object's method calling another's). Those lines appear
  only once servicer code exists, so the first time a servicer calling
  another object is written, link the models page again in one line:
  the call graph now shows which actions reach which objects.
