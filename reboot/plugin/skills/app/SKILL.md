---
name: app
description: "Build a Reboot application from a description: the interactive build (the app-guided skill: a design to approve, each part built and explained), learning mode asked in its first round; a prompt that asks for the whole app at once loads the app-whole skill, one feature hands off the app-basic skill. Holds the front-door routing every build uses: an MCP App (ChatGPT, Claude, VSCode, Goose) or a standalone web app by the prompt's own words, otherwise the web app, the other offered at handoff. Use for any prompt that asks to build an app and names no skill."
argument-hint: [<app-description>]
allowed-tools: Bash, Read, Write, Glob, Grep, Edit
---

# app — The Interactive Build, Unless the Prompt Asks Otherwise

This skill says nothing of its own and asks nothing: it hands the
prompt to the skill that builds it. The user sees only message text;
nothing here is said in thinking.

## First: the skill for the prompt

The response's first act (loading this skill was the first) is to
load one skill with the Skill tool, its argument the prompt as typed,
never by reading its file:

- **[`/reboot:app-whole`](../app-whole/SKILL.md)** when the prompt
  asks for the whole app at once, in so many words ("the whole app",
  "one shot", "in one go", "no questions", "hands off").
- **[`/reboot:app-basic`](../app-basic/SKILL.md)** when it asks for
  one feature hands off ("just one feature", "something small, no
  questions").
- **[`/reboot:app-just`](../app-just/SKILL.md)** when it asks for no
  design ("just build it", "exactly what I typed").
- **[`/reboot:app-guided`](../app-guided/SKILL.md)** otherwise: the
  interactive build, whose first round asks whether to explain as it
  builds (learning mode, [`references/exegesis.md`](references/exegesis.md)).
  A prompt that already says so ("explain as you build", "verbose",
  "teach me") is followed by ", verbose" in the argument, and the
  round doesn't ask.

Nothing is read, no folder is listed and no plan is made first. The
hands-off paths are asked for, never offered by a dialog: the
interactive build's opening names them in one line (the `app-design`
skill, section 1), and `/reboot:help` lists them. A skill named in the
prompt (`/reboot:app-whole …`) never comes here.

## Routing

Every backend is ready for both front doors: a `User` type,
`oauth=...`, and for each method its role for an AI caller and a
`description=` written for one. A wrong first front door costs no
rebuild, so routing never asks. A trigger is one of these phrases in
the prompt, verbatim, never inferred:

| Front door | Triggers |
| --- | --- |
| [`mcp-app`](../mcp-app/SKILL.md) | MCP, MCP host/server/app/tool, `mcp=Tool`, `UI()`; ChatGPT, Claude, VSCode, Goose, Cursor **named as where it runs** ("use this from Claude"); "AI tool", "tool for an LLM/agent", "expose to an LLM/agent" |
| [`web-app`](../web-app/SKILL.md) | a URL (`https://…`, `localhost:`); a route (`/login`, `/dashboard`); "website", "web app", "SPA", "in the browser", "served at"; "log in via email", "OAuth login", "sign up form" |
| A backend only ([`../app/references/backend-only.md`](../app/references/backend-only.md)) | "an API", "a backend", "API only", "headless"; "for my mobile app", "React Native", "for my existing app", "for my frontend" |

- **Not triggers:** "app", domain words (CRM, store, dashboard,
  tracker), "users", "login", "frontend" or "UI" alone.
- **No trigger:** the web app, without asking.
- **Both named with an explicit conjunction** ("and also a website",
  "MCP server plus a dashboard"): load both skills; one backend, one
  `oauth=...`, one `User` per identity.
- **"Just", "only", "no …"** ("just a website"): that front door only,
  and no offer at handoff.

The skill chosen above loads the front door with the Skill tool
(`/reboot:web-app`, `/reboot:mcp-app`), never by reading its
`SKILL.md` (the tool loads it whole and marks the route taken), or
reads `backend-only.md`, and follows it from the top: `app-guided` after
the go-ahead, `app-whole` after its design, `app-just` at once.

**At handoff,** unless "just/only/no" applied, offer the other front
door in one line: "The backend can also serve an MCP App for Claude and
ChatGPT; ask to add it." (or the reverse). On a
yes, follow that front door's Update Flow.

| Prompt | Builds |
| --- | --- |
| "a CRM for my personal relationships" | `web-app`, offer MCP App |
| "a dashboard served at metrics.example.com" | `web-app`, offer MCP App |
| "a tool I can use from Claude to track my reading" | `mcp-app`, offer web app |
| "just a simple website for event signups" | `web-app`, no offer |
| "a backend API for my React Native app" | backend only |
| "an MCP server, and also a dashboard at crm.example.com" | both |

## Note

Each capability is agreed in plain English as a `@wip` feature file
before its API exists ([`feature` skill](../feature/SKILL.md)). Both
front doors load the [`python` skill](../python/SKILL.md) themselves.
