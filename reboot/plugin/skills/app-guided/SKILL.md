---
name: app-guided
description: "The guided build of a Reboot application: the app-design skill's proposed design, asking nothing first (the recommended features, sign-in and palette under Assumed), the go-ahead (Ready to build this design?, where any of them changes), then the build with each part explained; a design already proposed in design/design.md is built on without asking again. Loaded by the app skill by default, or asked for by name (/reboot:app-guided); a prompt that asks for an app in plain words goes to the app skill, which asks its questions first."
argument-hint: [<app-description>]
allowed-tools: Bash, Read, Write, Glob, Grep, Edit
---

# app-guided — Design First, Then Each Part Explained

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

**1. The design, by the [`app-design` skill](../app-design/SKILL.md).** The
response's first act, before any text or other tool call, is to load
it with the Skill tool (`/reboot:app-design <the prompt>`), never by
reading its file; when the host asks for a plan before anything, the
plan is one item, "Propose the design for <app>", and the path's list
comes after the go-ahead. Right after it loads, its opening goes out
as text. It says the opening, asks nothing (the round's recommended
answers go under **Assumed**), reads what the design needs and writes the whole proposed design once,
drawn as a page beside the chat, its summary in the chat. On a free answer that refuses the design ("just build
it") the app-design skill hands the prompt to the [`app-just`
skill](../app-just/SKILL.md) and this skill's part is over: no design, no
go-ahead, no **What to expect**.
The front door is never asked (the [`app` skill](../app/SKILL.md),
Routing). Then, for a web app, the comp
([`../web-app/references/comp.md`](../web-app/references/comp.md)):
a mockup of the main page in the look, served, opened in the pane, one line
with its link. Then, in the same response as the design, the go-ahead,
**Ready to build this design?**
([`../app/references/design-first.md`](../app/references/design-first.md),
section 3): a yes builds step by step (the interactive build),
and a change to the design is its free answer. The prompt-by-prompt path, asked for in those words at
the go-ahead or at any handoff, has no go-ahead dialog: the design's
closing line says what to do, and the user's next prompt is the build.

**A design already proposed:** when `design/design.md` is in the
project with the status "proposed" and the prompt asks to build it
("build it", "build it all at once", "build the gig calendar", or the
`app-design` skill handing over), it is the design and the words are the
go-ahead: no round, no proposal, no dialog. **Assumed** holds the
round's answers; the way of building is the prompt's ("build it" is
step by step), and **Assumed** gets its line. Start at **What to
expect**. A prompt that changes it first is a design change, made by
the `app-design` skill's rules, then the same.

**What to expect,** right after the go-ahead (after the design; on the
prompt-by-prompt path, right after the design's closing line), before any
other tool call: the chosen path's items, each its own line of a list
under "What to expect:", filled in from the design:

- **Step by step:** each feature in two parts, its backend tested
  against its rules, then its frontend tested in a browser ·
  <first feature>'s backend, its domain model shown on the dashboard
  (a question only where it differs from the design), then its
  actions tested against every rule · then its
  frontend (<its page>), about 15 minutes in all · then
  each next feature as you choose it, 15 to 20 minutes.
- **All at once:** every feature in the design, the pages built in
  parallel with the backend, then everything tested together, without
  stopping, about <time> · then the whole app to try. · "build the
  rest step by step" at any handoff switches.
- **Prompt by prompt:** each thing you ask for at the prompt, built and
  tested against its rules, then handed off with its links · the build
  asks nothing and waits for your next prompt · the design is in
  `design/design.md`, yours to change at any prompt.

**2. Before the design, nothing** beyond what the `app-design` skill
reads. **After the go-ahead (on the prompt-by-prompt path, after the
design), read
[`../app/references/conversation.md`](../app/references/conversation.md)**
once: what the build says, links, opens and asks at every stage from
there on. Each path's next steps are read when they start: the build's
dialogs
([`../app/references/design-first.md`](../app/references/design-first.md),
sections 3 to 5), the task list (`../app/references/task-list.md`),
and for the whole app, the [`app-whole` skill](../app-whole/SKILL.md)'s
steps 4 and 6 (its reviews, step 5, are the one-shot's own).

**3. Throughout the build:**

- **Task list:** until the go-ahead it has the `app-design` skill's one
  item, "Propose the design for <app>". The chosen path's list follows
  the go-ahead (on the prompt-by-prompt path, the design).
- **Times,** always "about", only in the opening's dialog and in
  **What to expect**: the design, a few minutes; the first feature,
  15; each next feature, 15 to 20; the whole app, about 10 a feature, more for a hard domain.
- **Never a minute without a line,** at every stage: in the design,
  one when the research ends (what it found), then the design itself,
  one message (the `app-design` skill); in the build, one as each part starts (the API, the servicers, the
  tests, the page), saying what Reboot does for this app at that step
  (`../app/references/conversation.md`, "Say what Reboot does here").
  Reading the plugin's references gets no line of its own. Before a
  slow step, one fact about Reboot said for this app
  ([`../app/references/while-you-wait.md`](../app/references/while-you-wait.md)).
- **Verbose,** when the argument carries ", verbose" (the `guide`
  skill, or "Yes, learning mode" in the `app` skill's questions), or
  the user asked in the prompt or at any point ("verbose", "explain as
  you build", "an exegesis"): each
  milestone report (the model check, the backend check, each handoff)
  ends with an **Exegesis** section, what was written and why, the
  same text appended to `design/exegesis.md`
  ([`../app/references/exegesis.md`](../app/references/exegesis.md)).
  Between reports, each step line gains one sentence of why, and
  nothing more.
- **Architect,** when the argument carries ", architect" (the `build`
  skill): read [`../app/references/architect.md`](../app/references/architect.md)
  first; the API is approved before any servicer, the first handoff
  shows the structure, and a short architecture review comes before
  the second feature.
- **Files a part at a time** with the Write tool, never every file in
  one shell command.
- **Read this plugin with the Read tool,** one call per file, several
  in one response, at each link's path from the skill's base directory
  (a bounded `find` through Bash to find one; the Claude app has no
  Glob or Grep tool); never `cat`, `awk`, `sed` or a loop in a shell: a shell result over about 30 KB comes back as a
  2 KB preview and a saved file, and the references in it go unread
  (the `python` skill has the rule in full).

## The front door

By the [`app` skill](../app/SKILL.md)'s Routing: the one the prompt
names, otherwise the web app, never asked. After the go-ahead, load it
with the Skill tool (`/reboot:web-app`, `/reboot:mcp-app`), never by
reading its `SKILL.md`, or read `../app/references/backend-only.md`,
and follow it from the top; at handoff, the other door is offered in
one line as the `app` skill says. Each capability is agreed in plain
English as a `@wip` feature file before its API exists
([`feature` skill](../feature/SKILL.md)). Both front doors load the
[`python` skill](../python/SKILL.md) themselves.
