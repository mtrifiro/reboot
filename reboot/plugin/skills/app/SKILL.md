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

**1. The opening.** The build's first response is this, filled in from
the prompt alone, in the user's nouns:

```text
<App> (working name) is <what it is>, used by <who>. It keeps track of
<three to five of the user's nouns>. The first feature is <feature>,
<its rule>; built as <a web app | an MCP UI | both>, with the backend
ready for the other front door too.

I'll build it with Reboot, starting from its rules: what must always hold, each proved by a scenario, and the domain model that keeps them. You choose how: the first feature with you, then the rest without stopping; a feature at a time; or the whole app at once.
```

Then the dialog **How should it be built?** (`AskUserQuestion`; where
there is none, the same as one plain line), its options word for word:

- "Mixed (Recommended)": "You approve the design and try the first
  feature, about 15 minutes; then the rest is built and tested
  without stopping, an hour or more."
- "Step by step": "A feature at a time, about 15 minutes each. You
  check each part."
- "Hands-off": "No stops at all, not even for the design: every
  feature a real product needs, built and tested, an hour or more. You
  see it at the end."

Rules for that response:

- Both paragraphs are its visible text, never only in thinking; then
  the dialog, its only tool call. Never the dialog alone.
- The second paragraph word for word, as plain text, never merged with
  the first.
- Nothing about how it will be built before the answer: that is the
  user's choice. Mixed is first and the only option marked
  recommended.
- "(working name)" only when the build picked the name.
- **One feature first:** the feature at the centre of the named side's
  day, on one page: the main page's central object and a rule the user
  can see it keep. "Manage a hotel" names its staff, and their day is
  the rooms: the room status floor plan, each room moving occupied →
  dirty → cleaned → inspected, with no guest put in a room that isn't
  inspected. A sale comes first only when the prompt is about selling
  (a booking site, a shop, a ticket office). An app with a customer side (a hotel and its
  guests, an airline and its passengers) builds that side later, as
  its own feature: the customer's page, with what they do landing
  live on the staff's page, the first part recommended after the
  first feature. The prompt's framing decides whether there is one: a
  prompt that names the staff's tool ("an operations app", "a back
  office", "a dispatch tool") has none, its customer side someone
  else's system. The first sentence says which ("used by its front
  desk and housekeeping; guests get their own page later", or "used by its dispatchers
  and pilots; passengers book through the airline's own system").
- **No roles first:** the first feature has sign-in (the development
  accounts) and an authorizer on every method, "anyone signed in",
  never `allow()`; no roles, roster or role rules. Who may do what is
  its own feature, **Who may do what**, in the build order before
  any deploy.

Example: "Maison Desk (working name) is an app for a 56-room boutique
hotel, used by its front desk and housekeeping; guests get their own
page later. It keeps track of the rooms and their status, the guests
and their stays, and the amenities they book. The first feature is the
room status floor plan: every room moving from occupied to dirty to
cleaned to inspected, and no guest put in a room that isn't inspected;
built as a web app with the backend ready for an MCP UI too."

**What to expect,** right after the answer, before any other tool
call: the chosen path's items, each its own line of a list under
"What to expect:", filled in for this app:

- **Mixed:** the proposed design in a few minutes, nothing to answer
  until then · after the go-ahead, <first feature> built and tested
  without stopping, its backend against its rules, then its frontend
  (<its page>) in a browser, about 15 minutes · then your turn to try
  it · once you say so, the rest of the design, built and tested
  without stopping, an hour or more, then the whole app to try.
- **Step by step:** the proposed design in a few minutes, nothing to
  answer until then · each feature in two parts, its backend tested
  against its rules, then its frontend tested in a browser · after the
  go-ahead, <first feature>'s backend, with the dashboard's link to
  check its domain model, then its actions tested against every rule ·
  once you say so, its frontend (<its page>), about 15 minutes in
  all · then each next feature as you choose it, 15 to 20 minutes.
- **Hands-off:** no questions from here on, not even about the design
  · the design, with every feature a real <domain> app needs, in
  design/design.md · then the whole backend and the whole frontend,
  tested, without stopping, an hour or more. Then hand the build to
  the [`one-shot` skill](../one-shot/SKILL.md) from its step 1.

**2. Then read [`references/conversation.md`](references/conversation.md)**
once: what the build says, links, opens and asks at every stage from
here on. Each path's next steps are read when they start: the design
([`references/design-first.md`](references/design-first.md)), the task
list (`references/task-list.md`), and for the rest of a Mixed build
and for Hands-off, the [`one-shot` skill](../one-shot/SKILL.md).

**3. Throughout the build:**

- **Task list:** none beside the opening's dialog. Made before the
  answer, it has one item, "Propose the design for <app>"; a list
  that exists when this skill loads is replaced with that item first,
  in a response of its own.
- **Times,** always "about", only in the opening: the design, a few
  minutes; the first feature, 15; each next feature, 15 to 20; the
  whole app, or the rest of it, an hour or more.
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
