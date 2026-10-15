---
name: app
description: Build a Reboot application from a user description. Every backend is designed ready for both front doors, an MCP UI (ChatGPT, Claude, VSCode, Goose) and a standalone web app, with one `User` per identity via `oauth=...`. Builds the front door the prompt names (MCP/Claude/ChatGPT → `mcp-ui`; a URL/SPA/"website" → `web-app`; both named → both; an API or backend for the user's own frontend, mobile app or service → a backend only, with a generated client); otherwise builds the web app first without asking, and offers the other front door at handoff.
argument-hint: [<app-description>]
allowed-tools: Bash, Read, Write, Glob, Grep, Edit
---

# app — Build a Reboot Application

Decide which front door to build first and defer to the matching
skill. The backend is always ready for both.

**A new app asks nothing until its design document is written.** It
is built one feature at a time, without asking how: say what will be
built in one paragraph, take the recommended answer to every scope
question, write the whole proposed design to `design/design.md`, then
ask one thing, build the first feature or change something first, as
[`references/design-first.md`](references/design-first.md) says. It
overrides the front door's round of scope questions. For the whole app
at once, with every feature, the user asks for the
[`one-shot` skill](../one-shot/SKILL.md) by name.

## First, Before Reading Anything

**1. Say what will be built.** The first text of the build, before
any tool call and before the front door's skill: one paragraph of at
most four sentences, from the prompt alone, in the user's nouns and in
the build's voice, never "I": what the app is and who uses it, what it
will keep track of, the first feature it will build, and which front
door, ending word for word "The proposed design comes next, in
`design/design.md`; nothing to answer yet." It replaces the decision
flow's one sentence. No heading, no list, no question. For the hotel:

> Maison Desk will run a 56-room boutique hotel for its staff: the
> rooms and their status, the guests' stays, and who on the staff may
> do what. The first feature is a floor plan of every room, where a
> room can't be checked into until it's clean. It's a web app, with
> the backend ready for an MCP UI too. The proposed design comes next, in
> `design/design.md`; nothing to answer yet.

**2. Make the task list,** where the agent keeps one, with every item
now, filled in from the paragraph (`references/task-list.md` has the
rules, where the plugin has it). For one feature at a time:

1. Propose the design for <app>
2. Wait for your go-ahead on the design
3. Set up the project
4. <feature>: write its rules as scenarios
5. <feature>: build the domain model
6. Start the developer dashboard to display the domain model
7. <feature>: build the actions, their rules and who may do each
8. <feature>: add demo data
9. <feature>: run the scenarios
10. <feature>: check the types
11. Set up the frontend
12. <feature>: build its page
13. <feature>: add a browser scenario for its page
14. Check the <page> page in a browser
15. Show <feature> for your review

`<feature>` is the first feature's full name ("Room status floor
plan"), lowercase inside an item.

**3. Read with the file tools.** This plugin's skills and references
are read with the Read, Grep and Glob tools, never `cat`, `grep`,
`ls` or `cd` in a shell: a host's auto mode can block a shell command
in the plugin's install folder, and after a few blocks it asks the
user about every action.

Then route (below), and follow
[`references/design-first.md`](references/design-first.md).

## Routing

Every app gets a backend **ready for both front doors**: a `User`
type, `oauth=...`, and for each method its role for an AI caller and a
`description=` written for one (the front-door skill's Design Phase).
A wrong first front door costs no rebuild, only the other one added
later, so routing never has to ask. What varies is which front door is
built first.

### The destinations

- **`mcp-ui`** — an MCP UI: the app is exposed through an
  MCP host (ChatGPT, Claude, VSCode, Goose, etc.) via MCP tools, and
  any visual UI is embedded into the host through MCP UI artifacts.
- **`web-app`** — a standalone web app: the app is served at a URL
  and used in a normal browser, with the Reboot backend behind a
  React (or similar) frontend.
- **A backend only** — the API without a frontend of ours: the
  user's own frontend, mobile app or service calls it through a
  generated client. Follow
  [`references/backend-only.md`](references/backend-only.md).

### Triggers (verbatim in the prompt)

A trigger is one of the phrases below, in the user's prompt. No
inference, no synonyms:

**Commit to `mcp-ui` if the prompt contains any of:**

- `MCP`, `MCP host`, `MCP server`, `MCP app`, `MCP tool`, `mcp=Tool`,
  `UI()` (as a Reboot method type).
- `ChatGPT`, `Claude`, `VSCode`, `Goose`, `Cursor`, or
  "Anthropic / OpenAI" **named as the runtime** — e.g. "I want to
  use this from Claude", "expose it as a tool to ChatGPT". Just
  mentioning the company (e.g. "like ChatGPT") doesn't count.
- "MCP UI", "AI tool", "tool for an LLM/agent", "expose to an
  LLM/agent".

**Commit to `web-app` if the prompt contains any of:**

- A URL or scheme: `https://…`, `localhost:`, `example.com`.
- An explicit route/page literal: `/login`, `/dashboard`, `/home`,
  `/admin`, etc.
- "website", "web app", "web site", "SPA", "single-page app", "in
  the browser", "served at <url>".
- A standard browser-auth phrase: "log in via email", "OAuth login",
  "cookie session", "sign up form".

**Commit to a backend only if the prompt contains any of:**

- "an API", "a backend", "back end", "API only", "backend only",
  "headless".
- "for my mobile app", "React Native", "for my existing app",
  "for my frontend", or a Node.js service named as the caller.

**Commit to BOTH (load mcp-ui + web-app together) only if the
prompt contains an explicit conjunction:** e.g. "and also a
website", "MCP server **plus** a dashboard", "expose it to Claude
**and** host it on the web". Dual-frontend apps share one backend,
one `oauth=...`, and one `User` actor per upstream identity;
cross-frontend SSO is automatic.

### Not triggers

The word "app" alone, domain words (CRM, blog, store, dashboard, todo,
journal, kanban, tracker, chat room, …), "users", "login" or
"permissions", and "frontend" or "UI" without "browser", "website" or
"URL" are not triggers: they say what the app does, not where it is
used. A prompt with no trigger takes the default, step 3 below.

### Decision flow

1. **Both front doors named** (an explicit conjunction: "and also a
   website", "MCP server **plus** a dashboard", "expose it to Claude
   **and** host it on the web") → say what will be built
   ("First, Before Reading Anything" above), naming this front door, then load the
   [`mcp-ui` skill](../mcp-ui/SKILL.md) _and_ the
   [`web-app` skill](../web-app/SKILL.md), and follow them together.
   The backend `Application(oauth=...)` is configured once and serves
   both frontends; a single `User` actor per upstream identity is
   shared.
2. **Only an MCP UI trigger** → say what will be built
   ("First, Before Reading Anything" above), naming this front door, then
   load the [`mcp-ui` skill](../mcp-ui/SKILL.md) and follow it from
   the top, with the user's description as input.
3. **Only a web-app trigger, or no trigger (the default)** → say what will be built
   ("First, Before Reading Anything" above), naming this front door, then load the
   [`web-app` skill](../web-app/SKILL.md) and follow it from the top,
   with the user's description as input. Don't ask which kind of app:
   the web app is the default first front door.
4. **Only a backend trigger** → say what will be built
   ("First, Before Reading Anything" above), naming this front door, then follow
   [`references/backend-only.md`](references/backend-only.md).
5. **"Just", "only" or "no …"** ("just a website", "only an MCP
   tool", "no web UI") → build that one front door, and skip the
   offer at handoff.

**At handoff**, unless step 5 applied, offer the other front door in
one line: "Want this in Claude and ChatGPT too? The backend is ready;
it adds an MCP UI beside the web app." (or the reverse). On a yes, load
that front door's skill and follow its Update Flow.

### Worked examples

| Prompt fragment                                                          | Decision                | Why                              |
| ------------------------------------------------------------------------ | ----------------------- | -------------------------------- |
| "a CRM for my personal relationships, with notes and a timeline"         | `web-app`, offer MCP UI | No trigger: the default.         |
| "a todo list app"                                                        | `web-app`, offer MCP UI | "app" alone is not a trigger.    |
| "a dashboard for our team's metrics, served at metrics.example.com"      | `web-app`, offer MCP UI | Explicit URL.                    |
| "a tool I can use from Claude to track my reading list"                  | `mcp-ui`, offer web app | "from Claude" names the runtime. |
| "just a simple website for event signups"                                | `web-app`, no offer     | "just" scopes it to one.         |
| "a backend API for my React Native workout app"                          | Backend only            | "backend API", "React Native".   |
| "expose a CRM as an MCP server, and also a dashboard at crm.example.com" | Both, load both skills  | Explicit conjunction.            |

## Note

Whichever route, each capability of the app is agreed on in plain
English and written down as a `@wip` feature file before its API
exists, per the [`feature` skill](../feature/SKILL.md); the build
flows of both routes start there.

Both `mcp-ui` and `web-app` layer on top of the [`python`
skill](../python/SKILL.md) for Reboot backend mechanics. You don't need
to load `python` here — those skills load it themselves. A
dual-frontend app loads both, but they share a single `python`
layer underneath, so reference files aren't double-loaded.
