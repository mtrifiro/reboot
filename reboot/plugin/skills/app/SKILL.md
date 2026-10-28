---
name: app
description: Build a Reboot application from a user description. Every backend is designed ready for both front doors, an MCP UI (ChatGPT, Claude, VSCode, Goose) and a standalone web app, with one `User` per identity via `oauth=...`. Builds the front door the prompt names (MCP/Claude/ChatGPT → `mcp-ui`; a URL/SPA/"website" → `web-app`; both named → both; an API or backend for the user's own frontend, mobile app or service → a backend only, with a generated client); otherwise builds the web app first without asking, and offers the other front door at handoff. Load it as the very first step of any request to build an app, before a task list, a plan or any other tool call: it says what to show first.
argument-hint: [<app-description>]
allowed-tools: Bash, Read, Write, Glob, Grep, Edit
---

# app — Build a Reboot Application

Decide which front door to build first and defer to the matching
skill. The backend is always ready for both.

**A new app asks one thing before its design: how to build it,**
then follows [`references/design-first.md`](references/design-first.md),
which overrides the front door's round of scope questions.

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

**1. Say what will be built, ask how, then say what to expect.** The
first text of the build, before any tool call and before the front
door's skill, in the user's nouns.
It replaces the decision flow's one sentence. No heading.

- **What will be built,** a paragraph of three sentences, one for
  each, from the prompt alone: (1) what the app is, its name, and who
  uses it; (2) what it will keep track of, as the user's nouns, three
  to five of them; (3) the first feature it will build and the rule
  that makes it worth building first, and which front door (a web app,
  an MCP UI, or both). A name the build picked, because the prompt
  gave none, says so the first time it appears: "Chore Chart (working
  name)". Not one sentence that runs the three together, and not a
  description of the method: that is the next paragraph's job.
- **A first feature seen from both sides.** When the app has a staff
  side and a customer side (a hotel and its guests, an airline and its
  passengers, a theater and its patrons, a restaurant and its diners,
  a clinic and its patients), the first feature is the business's core
  transaction, the thing it sells, from both sides: the customer acts
  on a page of their own and the staff see it land on theirs, live,
  under the same rules. A hotel's guest books a room and the front desk
  sees the reservation on the room board (never an amenity first); an
  airline's passenger books a seat; a theater's patron buys a ticket; a
  diner reserves a table; a patient books an appointment. One domain
  model, two pages. An app with one side (an internal tool, a chore
  chart, a CRM) keeps a one-page first feature. Its handoff starts with
  the two pages side by side (`references/conversation.md`).
- **How it will be built, the user's choice,** a second paragraph of its own, the same for
  every app and either path, these words exactly, as plain text like
  the first paragraph (never merged into it, never paraphrased, never
  a quote block, never broken across lines): "I'll build it with Reboot,
  starting from its domain model: the objects it keeps and the rules
  they follow, each rule proved by a scenario. You choose how: a
  feature at a time, trying each one before the next, or the whole app
  at once, without stopping."

- **Then one dialog,** only once the two paragraphs are out as text of
  their own: the user reads the intent and how it's built first, then answers. Never the
  paragraph inside the dialog, and never the dialog alone. The response
  that asks is, in this order: the first paragraph, the second, then
  the dialog's tool call. Both paragraphs are that response's own
  text: written only in thinking, the user never gets them (the
  Claude app may show a thought's summary, but it is not the message),
  and the dialog then arrives alone. Never a word about how it will be
  built (feature by feature, all at once) before the answer: the
  second paragraph names both ways and the dialog asks. The dialog
  (`AskUserQuestion` where available; otherwise the same as one plain
  line), word for word but for the angle brackets:
  - Title: **How should it be built?**
  - "Interactively", first, with no "(Recommended)": "A feature at a
    time, about 15 minutes each (25 to 30 for the first, seen from both
    sides). You check each part." (For a one-sided app: "A feature at a
    time, about 15 minutes each. You check each part.")
  - "Automatically": "You approve the design; then the whole app is
    built and tested without stopping: an hour or more."
  - "Hands-off": "No stops at all, not even for the design: every
    feature a real product needs, built and tested, an hour or more.
    You see it at the end."

  On "Hands-off", hand the build to the [`one-shot`
  skill](../one-shot/SKILL.md) from its step 1 (its ambitious scope,
  no questions, one handoff), after its "What to expect"; the opening
  already said what will be built, so its step 0 is skipped.

  No option is marked recommended: they are equal choices, each giving
  up more of the user's involvement for speed, and their times say
  what each trades. Interactively is listed first only so it is the
  one preselected.
- **What to expect,** right after the answer and before any other
  tool call (research, reading references, writing files), the list
  for that path, word
  for word but for the angle brackets: a list, never folded into a
  paragraph.

For the hotel (the `>` marks the example here; the build writes plain
text):

> Maison Desk (working name) is an app for a 56-room boutique hotel,
> used by its staff (the front desk, housekeeping and the manager) and
> by its guests. It keeps track of the rooms and their status, the
> guests and their stays, the amenities they book, and who on the
> staff may do what. The first feature is booking a room, from both
> sides: guests book a stay on their own page, and the front desk sees
> each reservation land on the room board, which refuses a room
> already taken for any of those nights; built as a web app with the
> backend ready for an MCP UI too.
>
> I'll build it with Reboot, starting from its domain model: the
> objects it keeps and the rules they follow, each rule proved by a
> scenario. You choose how: a feature at a time, trying each one
> before the next, or the whole app at once, without stopping.

Then the dialog. On **Interactively**:

> What to expect:
> - The proposed design, in a few minutes. Nothing to answer until
>   then.
> - Each feature in two parts: first its backend, tested against its
>   rules, then its frontend, tested in a browser.
> - After your go-ahead, room booking's backend: its rules written as
>   scenarios and its domain model built, with the Reboot dashboard's
>   link to check the model; then its actions, tested against every
>   rule, for you to check.
> - Once you say so, its frontend: the guests' booking page and the
>   front desk's room board, tested side by side in a browser. About
>   25 to 30 minutes in all, for you to try.
> - Then each next feature, as you choose it, about 15 to 20 minutes.

On **Automatically**:

> What to expect:
> - The proposed design, in a few minutes. Nothing to answer until
>   then.
> - After your go-ahead, in two parts without stopping: the whole
>   backend, every feature tested against its rules, then the whole
>   frontend, every page tested in a browser. An hour or more; nothing
>   to answer until it's done, then the whole app to try.

On **Hands-off**:

> What to expect:
> - No questions from here on, not even about the design.
> - The design, with every feature a real hotel app needs, written to
>   design/design.md for you to read whenever you like.
> - Then, in two parts without stopping: the whole backend, every
>   feature tested against its rules, then the whole frontend, every
>   page tested in a browser. An hour or more; the whole app to try at
>   the end.

**2. Then read [`references/conversation.md`](references/conversation.md)**
once, right after saying what to expect: what the build says, links,
opens and asks at every stage from here on (links at every turn, the
Browser pane, a line after every answer, research, backend and
frontend named apart, the questions inside the build, narration, the
first feature's rules in plain words). Each path's further steps are
read when they start: the design ([`references/design-first.md`](references/design-first.md)),
the task list (`references/task-list.md`, where the plugin has it),
and, for Automatically and Hands-off, the [`one-shot` skill](../one-shot/SKILL.md).

**3. The task list** is made after the answer, never beside the
question: the question is the only tool call in its response. A list
made before the answer at all has one item, "Propose the design for
<app>". A list that already exists when this skill loads (the host
may have planned before loading it) is replaced first, in a response
of its own, with that one item, so the opening and its dialog still
come alone. The lists, one per part (the backend, then the frontend), are
in `references/task-list.md`, where the plugin has it.

**4. Time estimates,** from measured builds, always "about", only in
the opening's dialog and list: the design, a few minutes; the first
feature, about 15 minutes, or 25 to 30 seen from both sides (an
estimate until a build measures it); each next feature, 15 to 20
minutes; the whole app, an hour or more.

**While a slow step runs,** a short true fact about Reboot that fits
it goes out first, once per build each:
[`references/while-you-wait.md`](references/while-you-wait.md).
And the user never waits more than about a minute without a line, at
every stage, the design included: in the design, one when the research
ends, saying what it found, and one before each of the design's three
parts (`references/design-first.md`); in
the build, one before the references a stage reads, and one as each
part starts (the API, the servicers, the tests, the page). Files are written one
part at a time with the Write tool, never every file in one shell
command: a single call that runs for minutes shows nothing.

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
