---
name: app
description: Build a Reboot application from a user description. Every backend is designed ready for both front doors, an MCP UI (ChatGPT, Claude, VSCode, Goose) and a standalone web app, with one `User` per identity via `oauth=...`. Builds the front door the prompt names (MCP/Claude/ChatGPT → `mcp-ui`; a URL/SPA/"website" → `web-app`; both named → both; an API or backend for the user's own frontend, mobile app or service → a backend only, with a generated client); otherwise builds the web app first without asking, and offers the other front door at handoff.
argument-hint: [<app-description>]
allowed-tools: Bash, Read, Write, Glob, Grep, Edit
---

# app — Build a Reboot Application

Decide which front door to build first and defer to the matching
skill. The backend is always ready for both.

**A new app asks one thing before its design: how to build it.** Say
what will be built in one paragraph, then ask a feature at a time or
the whole app at once, each with its time; then say what to expect on
that path, take the recommended answer to every scope question, and
write the whole proposed design to `design/design.md`, as
[`references/design-first.md`](references/design-first.md) says. It
overrides the front door's round of scope questions. The whole app at
once builds every feature in the proposed design by the
[`one-shot` skill](../one-shot/SKILL.md)'s steps, without stopping.

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
- **How Reboot builds,** a second paragraph of its own, the same for
  every app and either path, these words exactly, as plain text like
  the first paragraph (never merged into it, never paraphrased, never
  a quote block, never broken across lines): "Reboot builds an app from its
  domain model, the objects it keeps and the rules they follow, each
  rule written as a scenario that proves it. It can build a feature at
  a time, each one working for you to try before the next, or the
  whole app at once, without stopping."

- **Then one dialog,** only once the two paragraphs are out as text of
  their own: the user reads the intent and how it's built first, then answers. Never the
  paragraph inside the dialog, and never the dialog alone. The dialog
  (`AskUserQuestion` where available; otherwise the same as one plain
  line), word for word but for the angle brackets:
  - Title: **How should it be built?**
  - "A feature at a time" (recommended): "<The first feature>, working
    to try, in about 15 minutes; then each next feature as you choose
    it, about 15 to 20 minutes each."
  - "The whole app at once": "Every feature in the design, each with
    its rules proven, built without stopping: an hour or more."
- **What to expect,** after the answer, the list for that path, word
  for word but for the angle brackets: a list, never folded into a
  paragraph.

For the hotel (the `>` marks the example here; the build writes plain
text):

> Maison Desk (working name) is an app for the staff of a 56-room
> boutique hotel: the front desk, housekeeping and the manager. It
> keeps track of the rooms and their status, the guests and their
> stays, the amenities they book, and who on the staff may do what.
> The first feature is a floor plan of every room, where a room can't
> be checked into until it's clean, built as a web app with the
> backend ready for an MCP UI too.
>
> Reboot builds an app from its domain model, the objects it keeps
> and the rules they follow, each rule written as a scenario that
> proves it. It can build a feature at a time, each one working for
> you to try before the next, or the whole app at once, without
> stopping.

Then the dialog. On **a feature at a time**:

> What to expect:
> - The proposed design, in a few minutes. Nothing to answer until
>   then.
> - After your go-ahead, the project is set up, the floor plan's rules
>   written as scenarios and its domain model built. Then the Reboot
>   dashboard's link, to check the model before the rest is built on
>   it.
> - The floor plan, working, in about 15 minutes, with its rules
>   proven by scenarios, for you to try.
> - Then each next feature, as you choose it, about 15 to 20 minutes.

On **the whole app at once**:

> What to expect:
> - The proposed design, in a few minutes. Nothing to answer until
>   then.
> - After your go-ahead, every feature in it, each with its rules
>   proven, built without stopping: an hour or more. The app is running
>   to try partway through; nothing to answer until it's done, then one
>   review of the whole app.

**2. Make the task list,** where the agent keeps one, with every item
now, filled in from the paragraph (`references/task-list.md` has the
rules, where the plugin has it), after the answer. For one feature at a
time:

1. Propose the design for <app>
2. Get your go-ahead on the design
3. Backend: build the <feature>'s domain model and rules
4. Your turn: check the domain model on the dashboard
5. Backend: build and prove the <feature>
6. Frontend: build the <feature>'s page and check it in a browser
7. Your turn: try the app and decide what to do next

Every item starts with a verb; `<feature>` is the first feature's full
name ("the room status floor plan"), lowercase inside an item.

**3. Time estimates,** from measured builds, always "about", only in
the opening's dialog and list, never a guess of the build's own: the proposed
design, a few minutes; the first feature after the go-ahead, about 15
minutes; each next feature, about 15 to 20 minutes; the whole app at
once (`one-shot`), an hour or more.

**4. Links at every major turn.** Once the app has started, every
major turn ends with one line linking both, on the ports they started
on, so the user never scrolls back for them:

> App: http://localhost:5173/ · Dashboard: http://127.0.0.1:9871/

Once a feature file exists, the dashboard part names its three pages
(`dashboard` skill, "Links to an Object or a Rule"):

> App: http://localhost:5173/ · Dashboard: [Models](http://127.0.0.1:9871/#/models) · [Features](http://127.0.0.1:9871/#/features) · [Changelog](http://127.0.0.1:9871/#/changelog)

The major turns: the app's first start (the `run` skill), each
handoff (in its **In short**), each feature finished, each change
made, and the build's last message. Before the app runs, the line has
the dashboard alone, once it is up.

**Open the dashboard in the app's Browser pane** where the host has
one (the Claude app's `preview_start`), the first time it is up and
whenever the build links into it at a turn the user acts on (the
model check, each review). The dashboard is already running, so
attach to it: a configuration in `.claude/launch.json` named
`dashboard` with only `"url": "http://127.0.0.1:<port>"`, the port it
started on, and no command (the origin only, no path); start it by
name, then navigate to the page the turn links (the domain model, a
feature's rules). The link line stays as well, for a host without a
pane and for later. Never start a second dashboard for the pane.

**The app, the same way.** When the app first runs for the user to
try, and at each review, open it in the pane too (a `launch.json`
configuration named `app` with only its URL, e.g.
`"url": "http://localhost:5173"`, started by name). In the Claude app
nothing opens in the user's external browser: not the app, not the
dashboard (`dashboard` skill, Step 4, starts it with `BROWSER=true`),
not an MCP UI's setup wizard. Outside the Claude app, the skills'
usual behaviour stands.

**5. After every answer, say what comes next.** Whenever the user
answers a dialog or a question (how to build, the go-ahead, the model
check, a feature's review, what to build next), the first thing after
the answer, before any tool call, is one or two sentences in the
plain words: what will be done now, in the user's nouns, and when
they'll next hear or be asked something, with the time when the
opening's estimates give one. For the go-ahead on a feature at a
time:

> Building the room status floor plan's domain model and rules now.
> The Reboot dashboard's link comes once the model is written, for you
> to check it before the rest is built on it.

Never a silent start after an answer, and never only a task list
update.

**Backend and frontend, named apart.** Every message about building
says which half it is about: the backend (the domain model, the
rules, the actions, who may do each, the proof) or the frontend (the
page and the browser check). The task list's items open with
"Backend:" or "Frontend:", and the messages under them follow suit
("Backend: running the floor plan's 9 scenarios." "Frontend: building
the floor plan page."), so the user always knows which half is being
worked on and which is done.

**Each question asked once, in the right place.** The Claude app
ends a working turn with a next-step box of its own (`wrap_up`: a
recap, one question, reply buttons), and that box also checks off the
whole task list. So:

- **Questions inside the build** (how to build, Ready to build?, Build
  on this model?) are dialogs (`AskUserQuestion`) asked while the
  turn goes on, never the box: the box would tick every item on the
  list before anything is built, and the list would then have to be
  made again.
- **The question at the end of a feature** (its review and what to
  build next), when the list's work is done, goes in the box only:
  its question in `ask`, its options as the buttons, the recommended
  one first. Never a dialog as well, which asks the same thing twice.
- A dialog the user skipped is not a reason to ask again in the box:
  end with the recap alone.

**"Not yet" means nothing happens.** At a feature's review the
options are "Yes, build <the next feature>" (record this one as kept,
then build the next) and "Not yet", whose reply is "Leave it as it is
for now." On "Not yet" the build does nothing more that turn: no
recording, no tags changed, no commands; one line says the app and
the dashboard stay up and what to say to go on. Keeping the feature
is recorded (`app/references/accept-design.md`) only when the user
says to keep it or to build the next one, and then the build says
first that recording takes a minute: the work-in-progress tags come
off, the design document becomes the accepted design, and the
decisions log gets its entry. Never write a reply button that joins
two moves ("keep it, but stop here").

**At every stage, say what is being done and what Reboot brings to
it.** Each task-list item that starts gets two or three sentences
before its work: what the build is doing now, in the user's nouns, and
the part Reboot does that a usual stack leaves to the developer. Plain
and specific, never a sales line, and each point said once in a build,
not repeated at every feature or in a wait note
(`references/while-you-wait.md`) later. What to draw on, at the stage it fits:

- **The design:** the app is described as domain objects and the rules
  they keep, before any code, so what's proposed is what gets built
  and checked.
- **The domain model:** each domain object is its own durable actor
  with its state kept by Reboot; there is no database to set up, no
  tables or migrations, and no cache to keep in sync.
- **The rules:** each rule is written as a scenario in plain words
  before the code, and the build isn't done until every scenario
  passes; a rule the code breaks shows up as a failing scenario, not
  a bug report.
- **Who may do what:** every action declares who may call it, checked
  by Reboot on each call, so a page can't reach what its user isn't
  allowed to.
- **Actions across objects:** a transaction changes several objects
  all or nothing, so a check-in can't half happen.
- **The dashboard:** the Reboot dashboard draws the domain model and
  the rules from the code itself, so what the user checks is what
  runs.
- **The page:** the page subscribes to its data and updates on its own
  when anything changes, with no refresh and no polling code.

**Show the first feature file's rules, the first time.** Once the
first feature file is written, show part of it in the chat, so the
user learns to read one: one rule with one of its scenarios, in a
```gherkin block, as written in the file (no more than about 15
lines), then two or three sentences on how to read it: a **Rule** is
one thing the app must keep true, in plain words; each **Scenario**
under it is an example that proves it, **Given** the situation,
**When** someone acts, **Then** what must be true after. Say that the
build isn't done until every scenario passes, and link the whole file
(on the dashboard's Features page once it's up). Once per build;
later features name their rules in a sentence and link the file.

For the hotel:

```gherkin
Rule: A room can't be checked into until it's inspected

  Scenario: The front desk can't check a guest into a dirty room
    Given room 202 is dirty
    When the front desk checks a guest into room 202
    Then the check-in is refused
    And room 202 is still dirty
```

**Fixes stay in the user's terms.** A fix while proving a feature is
said as what it changes for the user, in one sentence, or not at all
when it changes nothing they'd see ("A scenario was phrased in a way
the test steps don't accept; reworded, same rule."). Never the
mechanics: step libraries, `Given` restrictions, response paths,
field names.

For the go-ahead's next stage on the hotel:

> Building the room status floor plan's domain model and rules now.
> Each room is its own durable object in Reboot, its status kept for
> it, so there is no database to set up. Each rule, such as a room
> can't be checked into until it's clean, is written first as a
> scenario in plain words; the floor plan isn't done until every one
> passes.

**While a slow step runs,** a short true fact about Reboot that fits
it goes out first, once per build each:
[`references/while-you-wait.md`](references/while-you-wait.md).

**6. Read with the file tools.** This plugin's skills and references
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
