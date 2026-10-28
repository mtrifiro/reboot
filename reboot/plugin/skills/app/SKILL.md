---
name: app
description: "Build a Reboot application from a description, asking first how: Guided (a high-level design to approve, then each part built), Learn Reboot as it builds (the guide skill), Shape the architecture (the build skill) or Hands off (the vibe skill), and whether to ask questions before the design (up to 20, only when the user says yes); a prompt that already says how goes straight to that skill. Holds the front-door routing every build uses: an MCP App (ChatGPT, Claude, VSCode, Goose) or a standalone web app by the prompt's own words, otherwise the web app, the other offered at handoff. Use for any prompt that asks to build an app and names no skill."
argument-hint: '[<app-description>, or <Name>: <app-description>]'
allowed-tools: Bash, Read, Write, Glob, Grep, Edit, AskUserQuestion
---

# app — Choose How to Build, Then Build

This skill chooses how the app is built, then hands the prompt to the
skill that builds it. The user sees only message text and dialogs;
nothing here is said in thinking.

## First: how to build it

When the prompt already says how, load that skill at once with the
Skill tool, its argument the prompt as typed, never by reading its
file, and ask nothing:

- **[`/reboot:app-whole`](../app-whole/SKILL.md)** (`/reboot:vibe`):
  the whole app at once ("the whole app", "one shot", "in one go", "no
  questions", "hands off").
- **[`/reboot:app-basic`](../app-basic/SKILL.md)**: one feature hands
  off ("just one feature", "something small, no questions").
- **[`/reboot:app-just`](../app-just/SKILL.md)**: no design ("just
  build it", "exactly what I typed").
- **[`/reboot:brainstorm`](../brainstorm/SKILL.md)**: talk through or
  brainstorm the architecture first.
- **[`/reboot:build`](../build/SKILL.md)**: control the architecture
  of the app it builds.
- **[`/reboot:guide`](../guide/SKILL.md)**: be taught Reboot as it
  builds ("explain as you build", "verbose", "teach me").

Otherwise the response's first act (loading this skill was the first)
is one dialog (AskUserQuestion), before any text, read or plan, header
"How to build", question **How do you want to build <the app, in the
prompt's nouns>?**, these options word for word:

- **Guided (Recommended):** "A high-level design of what the app does
  and the rules it keeps, for you to approve; then each part built,
  and you can change any feature."
- **Learn Reboot as it builds:** "The same, with each step explained:
  the domain objects, the kinds of method, the rules and the scenarios
  that prove them."
- **Shape the architecture:** "Talk through the objects and the calls
  between them first, then approve the API before any code is
  written."
- **Hands off:** "The whole app a real product needs, designed, built
  and reviewed with no questions, handed over at the end."

In the same dialog, a second question, header "Questions", **Should I
ask you questions before the design?**, these options word for word:

- **No, assume and show me (Recommended):** "The design comes in a few
  minutes, with what it assumed listed; any of it is a word away."
- **Yes, ask me first:** "Up to 20 questions, four at a time, until
  there is enough to design it well; the design follows your
  answers."

On **Yes** (or a prompt that asks for questions first: "ask me
questions", "interview me"), the questions of
[`references/interview.md`](references/interview.md) come next, their
answers in `design/interview.md`, and only then the skill below.

The dialog carries the explanation, since text at the start of a
build is not reliably shown (hotel-300 to hotel-338 wrote the opening
only in thinking; every dialog was shown). Then load, its argument the
prompt followed by ", chosen": Guided, the
[`app-guided` skill](../app-guided/SKILL.md); Learn, the
[`guide` skill](../guide/SKILL.md); Shape, the
[`build` skill](../build/SKILL.md); Hands off, the
[`vibe` skill](../vibe/SKILL.md). A free answer is matched to the
nearest (one feature only: `app-basic`; no design: `app-just`).

Nothing is read, no folder is listed and no plan is made before the
dialog (the interview reference is read after it, and only on Yes). A skill named in the prompt (`/reboot:app-whole …`) never
comes here.

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
