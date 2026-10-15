---
title: Ask Nothing Until the Design Document
impact: HIGH
impactDescription: A new app starts with no questions. The user reads what will be built at once, then the whole proposed design in design/design.md, and answers one question, build it or change something, before any code; a round of scope questions first only delays the design they could react to.
tags: questions, scope, design, design document, first feature, go-ahead
---

# Ask Nothing Until the Design Document

The `app` skill's build of a new app, in either front door, works this
way. It replaces the front door's round of scope questions.

## 0. Say what will be built, first

The first text, right after routing and before reading anything else:
one paragraph of at most four sentences, from the prompt alone, in
the user's nouns. What the app is and who uses it, what it will keep
track of, the first feature it will build, and which front door, then
"The full design comes next, in `design/design.md`; nothing to answer
yet." It replaces the decision flow's one sentence. No heading, no
list, no question. For the hotel:

> Maison Desk will run a 56-room boutique hotel for its staff: the
> rooms and their status, the guests' stays, and who on the staff may
> do what. The first feature is a floor plan of every room, where a
> room can't be checked into until it's clean. It's a web app, with
> the backend ready for an MCP UI too. The full design comes next, in
> `design/design.md`; nothing to answer yet.

Then make the task list, with the front door's items for one feature
at a time (`app/references/task-list.md`, where the plugin has it),
and "Wait for your go-ahead on the design" as the second item.

## 1. No scope questions

Where the front door's Design Phase asks its round of scope
questions, ask none. Work out the questions as it says, then take the
answer it would mark as recommended for each:

- **How to build:** one feature at a time, always.
- **Everything else** (who signs in and with which roles, what the
  app keeps track of): the recommended, simplest option.
- **The accent and the app's name,** when the prompt names none:
  picked to suit the domain.

Something else the prompt leaves open is decided the same way: the
simplest choice that fits, assumed, and listed. Times are in the
user's own time zone.

## 2. The design document

Read the references for the API as the front door says, then write the
whole proposed design to `design/design.md`, in the shape of
[`design-document.md`](design-document.md), with these differences
while nothing is built:

- **Status:** "proposed on <date>; nothing is built yet. The links
  open on the developer dashboard once the first feature runs."
- **Every feature** is in it, in build order, the first marked and why
  it comes first, each with its rules in plain words. The links are
  written now, from the package, type and method names and the
  feature files to come; `scripts/design_links.py` checks them after
  the first feature is built.
- **No review table** and **no Decisions** section yet: both come at
  the first acceptance.
- **Assumed**, a section after **Sign-in**: every answer taken in
  step 1, one line each, the question then the answer taken, so the
  user sees what to change.

Then show the proposed design in the chat as the front door says, and
say in one line where the document is, as a link.

## 3. One question

End with one plain line, not a dialog: build <the first feature> now,
or change something first. Nothing is built before the answer.

- **A yes** (or the first feature named): build it by the front
  door's one-feature flow. At the first handoff, `design/design.md`
  becomes the accepted design as `accept-design.md` says, and
  **Assumed** moves into the first decisions entry.
- **A change:** update the document and the design, show what
  changed, and ask the same line again.
- **No answer** is not a yes.

The task list's "Wait for your go-ahead on the design" stays in
progress until the user answers, and is done on the yes; a change
leaves it in progress while the design is updated.

From the first feature on, the build follows the front door
unchanged.

## Never

- Reading a reference, or listing the folder, before the paragraph
  that says what will be built.
- `AskUserQuestion`, or a question in plain text, before the design
  document is written.
- An answer taken in step 1 without its line under **Assumed**.
- Code, `rbt generate` or a project scaffold before the user's answer
  to the one question.
