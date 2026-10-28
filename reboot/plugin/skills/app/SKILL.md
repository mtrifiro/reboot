---
name: app
description: "Build a Reboot application from a description: up to 20 questions first, in rounds of four, on what the prompt leaves open (the part to start with, who signs in, the rules, connections; never the data, the name or the look), then the guided build on the answers (the app-guided skill: the design to approve, then each part built); a prompt that names another way (hands off, the architecture first, no design) goes straight to that skill. Holds the front-door routing every build uses: an MCP App (ChatGPT, Claude, VSCode, Goose) or a standalone web app by the prompt's own words, otherwise the web app, the other offered at handoff. Use for any prompt that asks to build an app and names no skill."
argument-hint: '[<app-description>, or <Name>: <app-description>]'
allowed-tools: Bash, Read, Write, Glob, Grep, Edit, AskUserQuestion
---

# app — Questions, Then the Guided Build

This skill asks what the prompt leaves open, then hands the prompt and
the answers to the guided build, or to the skill the prompt names. The user sees only message text and dialogs;
nothing here is said in thinking.

## First: a path the prompt names

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

Otherwise the build is the guided one, and it starts with questions.

## Then: questions, before the design

The response's first act (loading this skill was the first) is the
first round of questions, one dialog (`AskUserQuestion`; where there
is none, the same as plain lines), before any text, read or plan,
from the prompt alone. The dialogs carry the build's start, since
text at the start of a build is not reliably shown (hotel-300 to
hotel-338 wrote the opening only in thinking; every dialog was shown).

- **Rounds of up to four questions, 20 in all,** each two to four
  options, the recommended one first and marked "(Recommended)", so
  accepting every recommendation is one answer; the free answer is
  always there. Stop the moment nothing left would change the design:
  20 is a ceiling, never a target.
- **The first round, always,** unless the prompt leaves nothing open.
- **Every question is about the app,** never about how the build
  reports: learning mode is `/reboot:guide`, or "explain as you build"
  at any point, and the design's opening names it (hotel-346 was asked
  "Explain the code as it builds?" beside its features).
- **Only what the prompt leaves open,** never what it says, and never
  a question whose recommended answer any builder would pick. Each
  round is written from the answers before it. The most
  consequential first:
  1. **Which part should it start with?**, single-select, up to four
     parts in the user's nouns, the recommended one first: one feature
     is built and handed off first, about 15 minutes, never several
     (hotel-350's multi-select recommended three). The parts not
     picked are the design's next features, in order, offered at the
     handoff's **What should I build next?**; "build it all", typed,
     is the whole app at once. A later question never adds a part to
     the first build: when the part picked needs another's data
     (arriving guests for the front desk), the build seeds that data,
     as it seeds the demo rooms, and the other part stays next
     (hotel-350's second round asked "Without the Reservations
     feature, where do arriving guests come from?", and both were
     built before the first handoff).
  2. Who uses it: who signs in, and the roles if any.
  3. The rules the domain turns on, where the prompt is ambiguous ("Can
     a room be booked while it is being cleaned?").
  4. What it connects to: payments, email, a calendar, another system.

  Never asked: the demo data. The build always seeds believable rows
  sized from the prompt (56 rooms for a 56-room hotel), disposable in
  development; real data comes in later, when the user asks (hotel-346
  asked how to seed the hotel). Never asked either: the name and the
  look. The design names the app when the prompt doesn't, and the look
  is the house palette unless the prompt names a brand; both are
  listed under Assumed, and either changes when the user asks
  (hotel-351 asked "The Larkspur (Recommended)", and offered two
  palettes that don't exist).
- **Every question explains itself:** it says what its answer changes
  when that isn't obvious ("Roles add rules on who may do what.").
- **"That's enough", Skip, or "just build it"** ends the questions at
  once: every question not asked takes its recommended answer ("just
  build it" with no design is the `app-just` skill).

After the last round, `design/interview.md` with the Write tool
(`mkdir -p design` first): every question and its answer, one line
each, in the order asked, under `# Questions before the design`. Then load the
[`app-guided` skill](../app-guided/SKILL.md) with the Skill tool, its
argument the prompt followed by ", interviewed" (and ", verbose" when
the prompt asks to learn as it builds). The `app-design` skill takes the file's answers
as given.

Nothing is read, no folder is listed and no plan is made before the
first round. A skill named in the prompt (`/reboot:app-whole …`) never
comes here, and asks none of these questions.

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
the design, `app-whole` after its design, `app-just` at once.

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
