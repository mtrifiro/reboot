---
name: 2app
description: Build a Reboot application from a user description as the app skill does, but asking nothing until the design document is written. Takes every recommended answer to the scope questions, writes the whole proposed design to design/design.md, then asks one thing, build it or change something first, before any code. Use only when the user asks for it by name ("/reboot:2app", "2app"); otherwise the app skill builds apps.
argument-hint: [<app-description>]
allowed-tools: Bash, Read, Write, Glob, Grep, Edit
---

# 2app: Build a Reboot Application, the Design Document First

Load the [`app` skill](../app/SKILL.md) and follow it, and the
front-door skill it routes to, with these differences. The first
question the user sees is about the design document; nothing before
it asks.

## 1. No scope questions

Where the front door's Design Phase asks its round of scope
questions, ask none. Work out the questions as it says, then take the
answer it would mark as recommended for each:

- **How to build:** one feature at a time.
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
[`app/references/design-document.md`](../app/references/design-document.md),
with these differences while nothing is built:

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

From the first feature on, the build follows the front door
unchanged.

## Never

- `AskUserQuestion`, or a question in plain text, before the design
  document is written.
- An answer taken in step 1 without its line under **Assumed**.
- Code, `rbt generate` or a project scaffold before the user's answer
  to the one question.
