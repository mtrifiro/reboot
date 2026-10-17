---
name: app
description: "Build a Reboot application from a user description, design first: the design skill's one round of questions about what to build and how (all at once, guided, prompt by prompt, where the user says what to build at each step and nothing is asked, or unguided, which hands over to the build skill) and its proposed design, then the go-ahead and the build; a design already proposed in design/design.md is built on without asking again. Every backend is ready for both front doors, an MCP UI (ChatGPT, Claude, VSCode, Goose) and a standalone web app; builds the front door the prompt names, otherwise the web app, and offers the other at handoff."
argument-hint: [<app-description>]
allowed-tools: Bash, Read, Write, Glob, Grep, Edit
---

# app — Build a Reboot Application, Design First

> **The user sees only message text. Say every status the way these
> skills give it, as the response's own visible text.**
>
> Thinking is never shown as a message. The Claude app shows at most a
> summary of it, which drops and rewords what you wrote: builds that
> drafted the opening in thinking showed the user a paraphrase that
> promised "feature by feature" before they had chosen, and lost
> "(working name)". So everything this plugin tells you to say (the
> opening, What to expect, what the research found, "Writing the
> design", each part's line, each result, each handoff) goes out as
> text in the response, **in the skills' words, before that response's
> tool calls**. Drafting it in thinking is not saying it. Before every
> tool call, ask: is there something the user should read first? Then
> write it, word for word, before the call.

## First, Before Reading Anything

**1. The design, by the [`design` skill](../design/SKILL.md).** The
response's first act, before any text or other tool call, is to load
it with the Skill tool (`/reboot:design <the prompt>`), never by
reading its file. It says the opening, asks the one round of questions
(the first build's features, who signs in, the accent, and how to
build: all at once, guided, prompt by prompt, or unguided),
reads what the design needs and shows the whole proposed design, once,
in the chat. On "Unguided" the design skill hands the prompt and the
answers to the [`build` skill](../build/SKILL.md) and this skill's part
is over: no design, no go-ahead, no **What to expect**.
The front door is never asked (Routing, below). Then, in the same
response as the design, the go-ahead, **Build on this design?**
([`../app/references/design-first.md`](../app/references/design-first.md),
section 3), which takes a change to the design as its free answer; on
the prompt-by-prompt path there is no go-ahead dialog: the design's closing
line says what to do, and the user's next prompt is the build.

**A design already proposed:** when `design/design.md` is in the
project with the status "proposed" and the prompt asks to build it
("build it", "build the gig calendar", or the `design` skill handing
over), it is the design and the words are the go-ahead: no round, no
proposal, no dialog. **Assumed** holds the round's answers, the path
among them ("How should it be built?"); a path named in the prompt
wins. Start at **What to expect**. A prompt that changes it first is
a design change, made by the `design` skill's rules, then the same.

**What to expect,** right after the go-ahead (after the design; on the
prompt-by-prompt path, right after the design's closing line), before any
other tool call: the chosen path's items, each its own line of a list
under "What to expect:", filled in from the design:

- **Guided:** each feature in two parts, its backend tested
  against its rules, then its frontend tested in a browser ·
  <first feature>'s backend, with the dashboard's link to check its
  domain model, then its actions tested against every rule · once you
  say so, its frontend (<its page>), about 15 minutes in all · then
  each next feature as you choose it, 15 to 20 minutes.
- **All at once:** every feature in the design, the pages built in
  parallel with the backend, then everything tested together, without
  stopping, about <time> · then the whole app to try. · "build the
  rest guided" at any handoff switches.
- **Prompt by prompt:** each thing you ask for at the prompt, built and
  tested against its rules, then handed off with its links · the build
  asks nothing and waits for your next prompt · the design is in
  `design/design.md`, yours to change at any prompt.

**2. Before the design, nothing** beyond what the `design` skill
reads. **After the go-ahead (on the prompt-by-prompt path, after the
design), read
[`../app/references/conversation.md`](../app/references/conversation.md)**
once: what the build says, links, opens and asks at every stage from
there on. Each path's next steps are read when they start: the build's
dialogs
([`../app/references/design-first.md`](../app/references/design-first.md),
sections 3 to 5), the task list (`../app/references/task-list.md`),
and for the whole app, the [`one-shot` skill](../one-shot/SKILL.md)'s
steps 4 and 5.

**3. Throughout the build:**

- **Task list:** until the go-ahead it has the `design` skill's one
  item, "Propose the design for <app>". The chosen path's list follows
  the go-ahead (on the prompt-by-prompt path, the design).
- **Times,** always "about", only in the opening's dialog and in
  **What to expect**: the design, a few minutes; the first feature,
  15; each next feature, 15 to 20; the whole app, about 10 a feature, more for a hard domain.
- **Never a minute without a line,** at every stage: in the design,
  one when the research ends (what it found), then the design itself,
  one message (the `design` skill); in the build, one as each part starts (the API, the servicers, the
  tests, the page), saying what Reboot does for this app at that step
  (`../app/references/conversation.md`, "Say what Reboot does here").
  Reading the plugin's references gets no line of its own. Before a
  slow step, one fact about Reboot said for this app
  ([`../app/references/while-you-wait.md`](../app/references/while-you-wait.md)).
- **Files a part at a time** with the Write tool, never every file in
  one shell command.
- **Read this plugin with the Read tool,** one call per file, several
  in one response, and Glob to find one; never `cat`, `awk`, `sed` or
  a loop in a shell: a shell result over about 30 KB comes back as a
  2 KB preview and a saved file, and the references in it go unread
  (the `python` skill has the rule in full).

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

Each route starts with the `design` skill above, then, after the
go-ahead, loads that skill with the Skill tool (`/reboot:web-app`,
`/reboot:mcp-ui`), never by reading its `SKILL.md` (the tool loads it
whole and marks the route taken), or reads `backend-only.md`, and
follows it from the top.

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
