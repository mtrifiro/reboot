---
name: app
description: Build a Reboot application from a user description. Every backend is designed ready for both front doors, an MCP UI (ChatGPT, Claude, VSCode, Goose) and a standalone web app, with one `User` per identity via `oauth=...`. Builds the front door the prompt names (MCP/Claude/ChatGPT → `mcp-ui`; a URL/SPA/"website" → `web-app`; both named → both; an API or backend for the user's own frontend, mobile app or service → a backend only, with a generated client); otherwise builds the web app first without asking, and offers the other front door at handoff. Load it as the very first step of any request to build an app, before a task list, a plan or any other tool call: it says what to show first.
argument-hint: [<app-description>]
allowed-tools: Bash, Read, Write, Glob, Grep, Edit
---

# app — Build a Reboot Application

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
3. "I'll design it now, starting from its rules; you'll see it in a
   few minutes, then choose how to build it." word for word.

**No question follows it:** the build goes straight on to the design,
which picks the features itself:

- **Four or five features**, in build order: the one sentence 2 names
  first, then the staff's other features, and last, only when the
  prompt implies customers who use the app themselves ("a hotel where
  guests book online"), a feature for them, built right after the
  first and saying who it is for. "Manage a hotel" gets no guest page.
- **Everything else** a real app in the domain needs (and Who may do
  what) goes in a separate list, **Not in this build**, never built
  unless the user asks.
- **The design is the review:** a change ("drop billing", "add an
  owner page") is typed at **How should it be built?**, the one
  question, asked once after the design is shown
  ([`references/design-first.md`](references/design-first.md),
  section 3); the design is updated and the question asked again. The
  name, the front door, sign-in and the rest are assumed and listed
  under **Assumed**.

Rules for that response:

- Written as the response's text, before any tool call, and the same
  three sentences wherever it is drafted: never a longer or different
  version in thinking, since that is what the user may see instead.
- Nothing more in it: what the app keeps track of, the front door and
  the rest are in the design, minutes later.
- Nothing about how it will be built: that is asked after the design.
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
- **No roles first:** the first feature has sign-in (the development
  accounts) and an authorizer on every method, "anyone signed in",
  never `allow()`; no roles, roster or role rules. Who may do what is
  its own feature, **Who may do what**, in the build order before
  any deploy.

Example: "An app for a 56-room boutique hotel, used by its front desk
and housekeeping. I'd start with the room status floor plan: every
room from occupied to dirty to cleaned to inspected, and no guest put
in a room that isn't inspected. I'll design it now, starting from its rules;
you'll see it in a few minutes, then choose how to build it."

**What to expect,** right after the answer to **How should it be
built?** (after the design), before any other tool call: the chosen
path's items, each its own line of a list under "What to expect:",
filled in from the design:

- **Step by step:** each feature in two parts, its backend tested
  against its rules, then its frontend tested in a browser ·
  <first feature>'s backend, with the dashboard's link to check its
  domain model, then its actions tested against every rule · once you
  say so, its frontend (<its page>), about 15 minutes in all · then
  each next feature as you choose it, 15 to 20 minutes.
- **The whole app:** every feature in the design, the whole backend
  and then the whole frontend, tested, without stopping, about <time>
  · then the whole app to try.

**2. Then read [`references/conversation.md`](references/conversation.md)**
once: what the build says, links, opens and asks at every stage from
here on. Each path's next steps are read when they start: the design
([`references/design-first.md`](references/design-first.md)), the task
list (`references/task-list.md`), and for the whole app, the
[`one-shot` skill](../one-shot/SKILL.md)'s steps 4 and 5.

**3. Throughout the build:**

- **Task list:** until the answer to **How should it be built?** it
  has one item, "Propose the design for <app>", made right after the
  opening; a list that exists when this skill loads is replaced with
  that item first, in a response of its own. The chosen path's list
  follows the answer.
- **Times,** always "about", only in the opening and in **How should
  it be built?**: the design, a few minutes; the first feature, 15; each next feature, 15 to 20; the
  whole app, about 7 a feature.
- **Never a minute without a line,** at every stage: in the design,
  one when the research ends (what it found) and one before each of
  the design's three parts (`references/design-first.md`); in the build, one before the references a stage reads
  and one as each part starts (the API, the servicers, the tests, the
  page). Before a slow step, one fact about Reboot that fits it
  ([`references/while-you-wait.md`](references/while-you-wait.md)).
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
| A backend only ([`references/backend-only.md`](references/backend-only.md)) | "an API", "a backend", "API only", "headless"; "for my mobile app", "React Native", "for my existing app", "for my frontend" |

- **Not triggers:** "app", domain words (CRM, store, dashboard,
  tracker), "users", "login", "frontend" or "UI" alone.
- **No trigger:** the web app, without asking.
- **Both named with an explicit conjunction** ("and also a website",
  "MCP server plus a dashboard"): load both skills; one backend, one
  `oauth=...`, one `User` per identity.
- **"Just", "only", "no …"** ("just a website"): that front door only,
  and no offer at handoff.

Each route starts with the opening above, naming its front door, then
loads that skill (or `backend-only.md`) and follows it from the top.

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
