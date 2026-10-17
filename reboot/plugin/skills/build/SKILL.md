---
name: build
description: "Build exactly what the prompt says on Reboot, for someone who knows what they want: no questions, no proposed design, no narration, no task list; the domain model, the authorizers and the tests still right. Use only when the user asks for it by name (/reboot:build) or refused the design in the design skill's round ("just build it"), which hands over the prompt and any answers; never for a new app described in plain words, which goes to the app skill."
argument-hint: [<what to build>]
allowed-tools: Bash, Read, Write, Glob, Grep, Edit
---

# build — Exactly What the Prompt Says

The expert path. The `app` skill proposes a design, asks four
questions and explains as it goes; this skill builds the prompt as
written and stops. Nothing is asked, ever. Nothing is built that the
prompt doesn't name.

## What is assumed, not asked

- **The front door:** the one the prompt names, by the `app` skill's
  triggers: MCP, an AI host or "a tool for an agent" is an MCP UI
  (`/reboot:mcp-ui`); a URL, a route, "website", "web app", "SPA" or
  "in the browser" is a web app (`/reboot:web-app`); "an API", "a
  backend", "headless" or "for my mobile app" is a backend only
  (`app/references/backend-only.md`); nothing named is a web app.
  Load the door with the Skill tool, never by reading its file.
- **Sign-in:** anyone signed in can do everything; every method has
  an authorizer from day one, never `allow()`. Roles only when the
  prompt names them.
- **The look:** the house look, violet, unless the prompt names an
  accent from `web-app/references/ui-design.md`'s list or a brand.
- **Everything else** the prompt leaves open: the simplest choice,
  said in one line when it matters ("Rooms keyed by hotel and number;
  say so to change it"), never asked.

## What is built

The prompt, no more:

- A feature named in the prompt gets its feature file, its API, its
  servicer with its rules and authorizer, its scenarios, and a page
  only when the prompt names one. No demo data unless asked. No
  second feature, no "Not in this build", no roadmap.
- A Reboot-native instruction ("a `Transaction` on `Room` keyed by
  hotel and number, staff only") is built as written, not redesigned.
- Handed over from the `design` skill's round ("just build it"): the
  prompt as typed plus any answers given (the features ticked, in that order;
  who signs in; the accent) are the spec, built as written; the
  features are the only ones built.
- A `design/design.md` already in the project (the `design` skill's,
  proposed or accepted) is the spec: the prompt names the part of it
  to build ("the gig calendar"), or "the design" for all of it, built
  as it reads, nothing added; its **Assumed** lines are taken as
  decided.
- A change to a built app is made as asked (`feature` skill, "A fix,
  a bug report, a review finding", without its question): additive
  API changes (`python/references/api-schema-evolution.md`), the
  scenario first, then the code.
- The door's Build Flow supplies the steps for the part asked, with
  its reading list (the technical references, at the step that needs
  each); its Design Phase, scope round and every dialog are skipped,
  and so are the `app` skill's references, except
  `design-document.md` below.
- The reading list is read with the Read tool, one call per file,
  several in one response, never `cat`, `awk` or a loop in a shell: a
  shell result over about 30 KB comes back as a 2 KB preview and the
  references in it go unread (the `python` skill's "Read this
  plugin's own skills" paragraph).

## What is said

One line when a step starts, naming it ("API: `Room` and `Stay`.",
"Tests: 6 scenarios."); the test result, once, from the feature
skill's step 4 (the feature's own files in the foreground, the whole
suite when the prompt says "all"); then the links line and stop:

> App: http://localhost:5173/ · Dashboard: Models · Features · Changelog (each word a link, `dashboard` skill, "Links to an Object or a Rule")

No handoff frame, no "what Reboot does here", no wait notes, no task
list, no "What should I build next?". A refused scenario is said as
the rule it breaks and the fix, in one line each. The dashboard
starts once the API exists (`dashboard` skill), silently, and its
links appear in the line.

## The record

`design/design.md`, when none exists, is written silently, in the shape of
[`app/references/design-document.md`](../app/references/design-document.md),
once a domain model exists, and updated when it changes; one line
says where it is the first time. Nothing else of the design record
(no proposal, no review table, no decisions log) unless the user asks
for the Flywheel's record, which the `app` skill's
`accept-design.md` gives.

## Never

- A dialog, a question, or a line that ends in one.
- A proposed design, a plan, or a feature the prompt didn't name.
- A method without an authorizer, an API change that isn't additive,
  a servicer without `mcp=None` on each declaration, or a part called
  done before its scenarios pass.
- A whole file rewritten to change a part of it (the Edit tool; the
  door's rule).
- Generated or installed source read whole, or another skill's
  assets read as an example (the door's rule).
- A deploy, a merge, a push, a data reset or a dependency edit
  without the user's word for that action: say what it would take, in
  one line, and stop.
