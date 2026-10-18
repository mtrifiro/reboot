---
name: app
description: "Build a Reboot application from a description. First one question, how it should be built, with one skill per answer: guided (a design to approve, the user's choices, each part built and explained: the guided skill), the whole app with no questions (the one-shot skill), or just what was typed (the build skill), none recommended; then that skill, with the prompt. Holds the front-door routing every build uses: an MCP UI (ChatGPT, Claude, VSCode, Goose) or a standalone web app by the prompt's own words, otherwise the web app, the other offered at handoff. Use for any prompt that asks to build an app and names no skill."
argument-hint: [<app-description>]
allowed-tools: Bash, Read, Write, Glob, Grep, Edit
---

# app — How Should It Be Built? Then That Skill

This skill says nothing of its own: it asks one question and hands
the prompt to the skill for the answer. The user sees only message
text; nothing here is said in thinking.

## First: the one question

The response's first act, before any text and before any other tool
call (loading this skill was the first), is one dialog
(`AskUserQuestion`; where there is none, the same as plain lines),
word for word:

- Title: **How should it be built?**, none of its options marked
  recommended, in this order:
- "Guided": "A design to approve, your choices, each part built and
  explained, step by step (great for learning). `/reboot:guided`"
- "The whole app, no questions": "Designed, built, reviewed and
  handed over once, about an hour or two (great for fast progress).
  `/reboot:one-shot`"
- "Just what I typed": "Exactly that and nothing more: no design, no
  questions, then the links (great for power users). `/reboot:build`"

Then load the chosen skill with the Skill tool
([`/reboot:guided`](../guided/SKILL.md),
[`/reboot:one-shot`](../one-shot/SKILL.md),
[`/reboot:build`](../build/SKILL.md)), its argument the prompt as
typed, never by reading its file; that skill takes it from there.

- **No answer** (the dialog skipped, or a host that can't ask):
  Guided, with no line about the choice; the guided skill's first
  words are the next thing said.
- **A free answer** is read for one of the three ("the whole thing,
  no questions" is one-shot; "just build it" is build); otherwise
  Guided.
- **A skill named in the prompt** (`/reboot:build …`,
  `/reboot:one-shot …`, `/reboot:design …`) never comes here.
- Nothing is read, no folder is listed and no plan is made before the
  question. A host that asks for a plan first gets one item, "Decide
  how to build <app>", which the chosen skill's list replaces.

## Routing

Every backend is ready for both front doors: a `User` type,
`oauth=...`, and for each method its role for an AI caller and a
`description=` written for one. A wrong first front door costs no
rebuild, so routing never asks. A trigger is one of these phrases in
the prompt, verbatim, never inferred:

| Front door | Triggers |
| --- | --- |
| [`mcp-ui`](../mcp-ui/SKILL.md) | MCP, MCP host/server/app/tool, `mcp=Tool`, `UI()`; ChatGPT, Claude, VSCode, Goose, Cursor **named as where it runs** ("use this from Claude"); "AI tool", "tool for an LLM/agent", "expose to an LLM/agent" |
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
(`/reboot:web-app`, `/reboot:mcp-ui`), never by reading its
`SKILL.md` (the tool loads it whole and marks the route taken), or
reads `backend-only.md`, and follows it from the top: `guided` after
the go-ahead, `one-shot` after its design, `build` at once.

**At handoff,** unless "just/only/no" applied, offer the other front
door in one line: "Want this in Claude and ChatGPT too? The backend is
ready; it adds an MCP UI beside the web app." (or the reverse). On a
yes, follow that front door's Update Flow.

| Prompt | Builds |
| --- | --- |
| "a CRM for my personal relationships" | `web-app`, offer MCP UI |
| "a dashboard served at metrics.example.com" | `web-app`, offer MCP UI |
| "a tool I can use from Claude to track my reading" | `mcp-ui`, offer web app |
| "just a simple website for event signups" | `web-app`, no offer |
| "a backend API for my React Native app" | backend only |
| "an MCP server, and also a dashboard at crm.example.com" | both |

## Note

Each capability is agreed in plain English as a `@wip` feature file
before its API exists ([`feature` skill](../feature/SKILL.md)). Both
front doors load the [`python` skill](../python/SKILL.md) themselves.
