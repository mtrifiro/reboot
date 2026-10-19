---
title: Build a Backend Only
impact: MEDIUM
impactDescription: When the user's frontend already exists or isn't ours to build, the app is its API and behaviors; building pages for it wastes the build and hides what matters
tags: backend, api, headless, client, react, react native, mobile, nodejs, generate
---

## Build a Backend Only

The app is its API: the objects, the actions and the rules, proven by
scenarios. Someone else's frontend calls it through a client that
`rbt generate` writes for their platform.

Load the [`web-app` skill](../../web-app/SKILL.md) and follow its
Design Phase and its build flow, one feature at a time, with these
differences:

- **Scope questions:** when the prompt doesn't say, one question is
  which frontend will call the API: a React web app (recommended), a
  React Native app, a Node.js service, or another. If their frontend
  is an existing project, ask for its folder.
- **The client:** in `.rbtrc`, generate the client for that platform
  instead of `frontend/api`: `generate --react=<dir>` for React,
  `--mobile=<dir>` for React Native, `--nodejs=<dir>` for Node.js, or
  `--web=<dir>` for a plain web page. `<dir>` is in their project
  when they gave one.
- **The task list:** as [`task-list.md`](task-list.md) says for a
  backend only.
- **No pages:** skip the frontend steps and the web app scenario. The
  scenarios in the built-in steps prove every action and rule.
- **Auth:** keep `User` and `oauth=` as the front doors do; their
  frontend signs users in through the app's OAuth server (for React,
  as `web-app/references/react-client.md` shows).
- **Checking it running:** start the app with the
  [`run` skill](../../run/SKILL.md) and check the demo data with
  `rbt inspect` instead of a browser.
- **Showing it:** as the `web-app` skill says, but "How to check it"
  is the dashboard's Models and Features pages and `rbt inspect`; and
  add how their frontend calls one action with the generated client,
  in a few lines (for React, the hooks in
  `python/references/react-generated-client.md`).
- **At handoff:** offer a web app or an MCP App in one line; the
  backend is ready for both. To deploy, the [`deploy`
  skill](../../deploy/SKILL.md)'s backend step is all there is.
