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

**1. Say what will be built, and what to expect.** The first text of
the build, before any tool call and before the front door's skill, in
the user's nouns and in the build's voice, never "I". It replaces the
decision flow's one sentence. No heading and no question.

- **One paragraph** of at most three sentences, from the prompt alone:
  what the app is and who uses it, what it will keep track of, the
  first feature it will build, and which front door. A name the build
  picked, because the prompt gave none, says so the first time it
  appears: "Partner Loop (working name)".
- **What to expect,** a list of four lines, word for word but for the
  angle brackets, with the time estimates below:

For the hotel:

> Maison Desk (working name) will run a 56-room boutique hotel for its staff: the
> rooms and their status, the guests' stays, and who on the staff may
> do what. The first feature is a floor plan of every room, where a
> room can't be checked into until it's clean, in a web app with the
> backend ready for an MCP UI too.
>
> What to expect:
> - The proposed design, in a few minutes. Nothing to answer until
>   then.
> - After your go-ahead, once the domain model is written, the Reboot
>   dashboard opens with its link: the app's domain model and rules,
>   updated as they're built.
> - The floor plan, working, in about 15 minutes, with its rules
>   proven by scenarios, for you to try.
> - Then each next feature, about 15 to 20 minutes, as you choose it.

**2. Make the task list,** where the agent keeps one, with every item
now, filled in from the paragraph (`references/task-list.md` has the
rules, where the plugin has it). For one feature at a time:

1. Propose the design for <app>
2. Wait for your go-ahead on the design
3. Scaffold the project
4. Write the <feature>'s rules as scenarios
5. Build the <feature>'s domain model
6. Start the Reboot dashboard to show the domain model
7. Build the <feature>'s actions, who may do each, and demo data
8. Prove the <feature>'s rules (scenarios pass, types check)
9. Build the <feature>'s page, with a browser scenario
10. Start the app for you to see, and check it in a browser
11. Your turn: review the <feature>

Every item starts with a verb; `<feature>` is the first feature's full
name ("the room status floor plan"), lowercase inside an item.

**3. Time estimates,** from measured builds, always "about", only in
the opening's list, never a guess of the build's own: the proposed
design, a few minutes; the first feature after the go-ahead, about 15
minutes; each next feature, about 15 to 20 minutes; the whole app at
once (`one-shot`), an hour or more.

**4. Links at every major turn.** Once the app has started, every
major turn ends with one line linking both, on the ports they started
on, so the user never scrolls back for them:

> App: http://localhost:5173/ · Dashboard: http://127.0.0.1:9871/

The major turns: the app's first start (the `run` skill), each
handoff (in its **In short**), each feature finished, each change
made, and the build's last message. Before the app runs, the line has
the dashboard alone, once it is up.

**5. Read with the file tools.** This plugin's skills and references
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
