---
name: app
description: "Build a Reboot application from a user description, design first: one round of questions about what to build and how (all at once, step by step, or power user, where the user directs every step at the prompt and nothing is asked), then the whole proposed design shown in the chat and the go-ahead. Every backend is ready for both front doors, an MCP UI (ChatGPT, Claude, VSCode, Goose) and a standalone web app; builds the front door the prompt names, otherwise the web app, and offers the other at handoff."
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

**1. The opening.** The build's first words: one short paragraph of
three sentences, in the user's nouns. It is what the user sees first,
sent as text or shown from the build's thinking, so it carries
everything that matters on its own, the most important first. No name
yet: the app is named in the design, as a working name.

1. "An app for <what it is>, used by <who>." (the rules below)
2. "I'd start with <feature>: <its rule, in plain words>."
3. "First, a few questions about what to build and how; then I'll
   design it, starting from its rules." word for word.

**Then one round of questions, what to build and how,** as the front
door's scope round asks it: one dialog (`AskUserQuestion`; where there
is none, the same as plain lines), from the prompt alone, before
reading any reference. Two to four questions, each two to four
options, the simplest first and marked "(Recommended)" where one is
recommended, so accepting every recommendation is one answer:

- **"Which features should the first build include?"** (multi-select):
  four features worked out from the prompt, each its name in the
  user's nouns as the label and its rule in a few words as the
  description, in this order: the one sentence 2 names, first, marked
  "(Recommended)" (a multi-select starts with nothing ticked, so it
  leads); then the staff's other features; last, only when the prompt
  implies customers who use the app themselves ("a hotel where guests
  book online"), a feature for them, its description starting with who
  it is for. The features ticked are the build, in that order.
- **"Who signs in?"**, when the prompt leaves it open: "Anyone signed
  in can do everything; roles later (Recommended)" or "Staff roles from
  the start", naming the roles in the user's nouns ("front desk, vets
  and techs"). Roles chosen are in the first build; otherwise they are
  **Who may do what**, before any deploy.
- **"Which accent?"**, only when the prompt names no brand: two or
  three accents that suit the domain, from the list
  `web-app/references/ui-design.md` gives and no other, the first
  recommended, plus "Use my brand" (a site or tokens to read).
- **"How should it be built?"**, always, last, none of its options
  recommended: "All at once": "Every feature in the design without
  stopping, about 7 minutes a feature; you see it at the end." ·
  "Step by step": "A feature at a time, about 15 minutes each; you
  check each part as it's built: great for learning Reboot." · "Power
  user": "You direct every step at the prompt. Nothing is asked: each
  thing you ask for is built, tested and handed off, then the build
  waits for your next prompt."

The front door is never asked (Routing, below): the one
the prompt names, otherwise the web app, with the backend ready for an
MCP UI, offered at handoff. The answers are the design's scope: the features chosen, in build
order, and nothing else; what else a real app in the domain needs goes
under **Not in this build**, never built unless the user asks. A free
answer is taken as written. Nothing else is asked before the design.
After the design comes the go-ahead, **Build on this design?**
([`../app/references/design-first.md`](../app/references/design-first.md),
section 3), which takes a change to the design as its free answer; on
the power-user path there is no go-ahead dialog: the design's closing
line says what to do, and the user's next prompt is the build. The
name and the rest are assumed and listed under **Assumed**.

Rules for that response:

- Written as the response's text, before any tool call, and the same
  three sentences wherever it is drafted: never a longer or different
  version in thinking, since that is what the user may see instead.
- Nothing more in it: what the app keeps track of, the front door and
  the rest are in the design, minutes later. Then the dialog, the
  response's only tool call.
- Nothing about how it will be built beyond the dialog's own options:
  **What to expect** comes after the design.
- **No name before the design.** The design proposes one, marked
  "(working name)" the first time it appears, with the accent, under
  what the build assumed.
- **The first feature:** the feature at the centre of the named
  side's day, on one page: the main page's central object and a rule
  the user can see it keep. "Manage a hotel" names its staff, and
  their day is the rooms: the room status floor plan, each room moving
  occupied → dirty → cleaned → inspected, with no guest put in a room
  that isn't inspected.
- **A sale first only when the prompt is about selling:** a booking
  site, a shop, a ticket office.
- **Customer features last**, and never first unless the prompt is
  about selling: they need both the staff's side and the customer's to
  be worth trying.
- **A staff tool has no customer side:** a prompt that names the
  staff's tool ("an operations app", "a back office", "a dispatch
  tool") offers no customer feature; its customers use someone else's
  system.
- **No roles first,** unless "Who signs in?" chose them: the first
  feature has sign-in (the development accounts) and an authorizer on
  every method, "anyone signed in", never `allow()`; no roles, roster
  or role rules. Who may do what is
  its own feature, **Who may do what**, in the build order before
  any deploy.

Example: "An app for a 56-room boutique hotel, used by its front desk
and housekeeping. I'd start with the room status floor plan: every
room from occupied to dirty to cleaned to inspected, and no guest put
in a room that isn't inspected. First, a few questions about what to
build and how; then I'll design it, starting from its rules."

**What to expect,** right after the go-ahead (after the design; on the
power-user path, right after the design's closing line), before any
other tool call: the chosen path's items, each its own line of a list
under "What to expect:", filled in from the design:

- **Step by step:** each feature in two parts, its backend tested
  against its rules, then its frontend tested in a browser ·
  <first feature>'s backend, with the dashboard's link to check its
  domain model, then its actions tested against every rule · once you
  say so, its frontend (<its page>), about 15 minutes in all · then
  each next feature as you choose it, 15 to 20 minutes.
- **All at once:** every feature in the design, the pages built in
  parallel with the backend, then everything tested together, without
  stopping, about <time> · then the whole app to try.
- **Power user:** each thing you ask for at the prompt, built and
  tested against its rules, then handed off with its links · the build
  asks nothing and waits for your next prompt · the design is in
  `design/design.md`, yours to change at any prompt.

**2. Before the design, read only what it needs** (`../app/references/design-first.md`,
section 2). **After the go-ahead (on the power-user path, after the
design), read
[`../app/references/conversation.md`](../app/references/conversation.md)**
once: what the build says, links, opens and asks at every stage from
there on. Each path's next steps are read when they start: the design
([`../app/references/design-first.md`](../app/references/design-first.md)), the task
list (`../app/references/task-list.md`), and for the whole app, the
[`one-shot` skill](../one-shot/SKILL.md)'s steps 4 and 5.

**3. Throughout the build:**

- **Task list:** until the go-ahead it has one item, "Propose the
  design for <app>", made right after the answers to the opening's
  questions; a list that exists when this skill loads is replaced with
  that item first, in a response of its own. The chosen path's list
  follows the go-ahead (on the power-user path, the design).
- **Times,** always "about", only in the opening's dialog and in
  **What to expect**: the design, a few minutes; the first feature,
  15; each next feature, 15 to 20; the whole app, about 7 a feature.
- **Never a minute without a line,** at every stage: in the design,
  one when the research ends (what it found), then the design itself,
  one message (`../app/references/design-first.md`, section 2); in
  the build, one as each part starts (the API, the servicers, the
  tests, the page), saying what Reboot does for this app at that step
  (`../app/references/conversation.md`, "Say what Reboot does here").
  Reading the plugin's references gets no line of its own. Before a
  slow step, one fact about Reboot said for this app
  ([`../app/references/while-you-wait.md`](../app/references/while-you-wait.md)).
- **Files a part at a time** with the Write tool, never every file in
  one shell command.
- **Read this plugin with Read, Grep and Glob,** never `cat`, `ls` or
  `cd` in a shell: auto mode may block shell commands in the plugin's
  folder.

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

Each route starts with the opening above, naming its front door, then
loads that skill with the Skill tool (`/reboot:web-app`,
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
