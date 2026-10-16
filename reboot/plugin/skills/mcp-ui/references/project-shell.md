---
title: Project Shell — MCP UI Deltas
impact: CRITICAL
impactDescription: The shell files (`.rbtrc`, `pyproject.toml`, `.python-version`, `main.py`, `example_prompts.py`) wire the build, the dev server, the HMR routing and the entry point. They are copied from this skill's `assets/shell/`; a wrong shape breaks codegen or live reload before the app boots.
tags: project, shell, rbtrc, pyproject, python-version, main, application-entry, hmr, dist
---

## Project Shell — MCP UI Deltas

The `python` skill covers the canonical project shape
(`lifecycle-project-setup.md`, with the project-root `.mypy.ini` and
`.gitignore` to create as well; the base `.gitignore` already covers
`frontend/api/`, `frontend/dist/` and `node_modules/`) and the `.rbtrc`
format (`lifecycle-rbtrc.md`). What an MCP UI adds on top is copied,
never retyped and never read:

```sh
cp -R <this skill>/assets/shell/. .
```

Then replace `<project-name>` in `.rbtrc` and `pyproject.toml`, and
fill in `backend/src/main.py` and `backend/src/example_prompts.py` as
below. What the copy holds:

- `.python-version`: `3.12`.
- `.rbtrc`: the python skill's shape plus `--default-config=hmr` and
  the `:hmr` and `:dist` configs, which route Envoy to the Vite dev
  server (`cd frontend && npm run dev`, on 4444) or to a built
  `frontend/dist/` (`--config=dist`, after `npm run build`); the
  `generate --react=frontend/api` line; and the `serve run` block
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
  typical MCP UI has no `initialize` hook: the auto-constructed `User`
  covers per-user setup, and application-type instances are created on
  demand by `User`'s Transaction methods.
