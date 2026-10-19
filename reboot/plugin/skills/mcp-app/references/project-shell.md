---
title: Project Shell — MCP App Deltas
impact: CRITICAL
impactDescription: The shell files (`.rbtrc`, `pyproject.toml`, `.python-version`, `main.py`, `example_prompts.py`) wire the build, the dev server, the HMR routing and the entry point. They are copied from this skill's `assets/shell/`; a wrong shape breaks codegen or live reload before the app boots.
tags: project, shell, rbtrc, pyproject, python-version, main, application-entry, hmr, portless, ports, dist
---

## Project Shell — MCP App Deltas

The `python` skill covers the canonical project shape
(`lifecycle-project-setup.md`, with the project-root `.mypy.ini` and
`.gitignore` to create as well; the base `.gitignore` already covers
`frontend/api/`, `frontend/dist/` and `node_modules/`) and the `.rbtrc`
format (`lifecycle-rbtrc.md`). What an MCP App adds on top is copied,
never retyped and never read:

```sh
cp -R <this skill>/assets/shell/. .
```

Then replace `<project-name>` in `.rbtrc` and `pyproject.toml`, and
fill in `backend/src/main.py` and `backend/src/example_prompts.py` as
below. What the copy holds:

- `.python-version`: `3.12`.
- `.rbtrc`: the python skill's shape plus three `dev run` configs.
  `portless`, the default, serves the app at
  `https://<project-name>.localhost` with `--frontend-url` naming Vite
  at `https://frontend.<project-name>.localhost`
  (`cd frontend && npm run dev:portless`); `ports` is the same on plain
  ports, the app at `http://localhost:9991` and Vite at
  `http://localhost:5173` (`--config=ports`, `npm run dev:ports`);
  both carry `--mcp-app`, so Envoy proxies each MCP App from the dev
  server with HMR. `dist` serves the built MCP Apps
  (`--mcp-app-dist-path=frontend/dist/mcp`, after `npm run build`).
  Which of `portless` and `ports` to start, without asking: the
  [`run` skill](../../run/SKILL.md). The `--web-app` /
  `--web-app-dist-path` lines are commented out until the app gets a
  web app. Also the `dashboard:portless` / `dashboard:ports` configs;
  the `generate --react=frontend/api` line; and the `serve run` block
  production uses (Reboot Cloud's containers run `rbt serve run`,
  `python/references/lifecycle-dockerfile.md`): the `dev run` block
  minus the dev-only knobs. `dev run --application-name=<project-name>`
  is what makes state survive restarts;
  `uv run rbt dev expunge --application-name=<project-name>` resets it.
- `pyproject.toml`: the base shape plus `httpx` and `anyio`.
  `reboot[dev]` (the same version as `reboot`) is what the tests and
  the dashboard run on; a development environment always installs it.
- `backend/src/example_prompts.py`: the `ExamplePrompt`s, the
  ready-to-send chat scenarios the root-page wizard offers so a user
  can try the app the moment it runs, kept out of `main.py`. Each has
  a `title` (its identity: re-registering the same title replaces the
  entry) and `prompts`, the messages the user sends one per turn: a
  **sequence** that walks one flow end to end (create something, act
  on it, view it), never an isolated message. Write three or so that
  together exercise the main user stories, phrased as a person talks
  to a chat client, most ending on a "show me / open / view …" turn
  that renders a `UI()` ("Example Prompts" in `SKILL.md`). The copy's
  counter set is the shape to replace.
- `backend/src/main.py`: registers every servicer (`User` and the
  application types) and passes `example_prompts` through. `title` and
  `description` are shown by the wizard, so both read as a person
  would say them (`title` defaults to the application name). A
  typical MCP App has no `initialize` hook: the auto-constructed `User`
  covers per-user setup, and application-type instances are created on
  demand by `User`'s Transaction methods.
