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

Done already, as the `app` skill's "First, Before Reading Anything"
says: the paragraph, then the task list, before any reading.

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
- **Every feature** is in it, under **Proposed features, in build
  order**, with the line "Only the first is built next; the rest, and
  their order, are yours to change at any point.": the first marked
  and why it comes first, each with its rules in plain words. The links are
  written now, from the package, type and method names and the
  feature files to come; `scripts/design_links.py` checks them after
  the first feature is built.
- **No review table** and **no Decisions** section yet: both come at
  the first acceptance.
- **Assumed**, a section after **Sign-in**: every answer taken in
  step 1, one line each, the question then the answer taken, so the
  user sees what to change.

Then show the proposed design in the chat as the front door says, and
end with one line that names what was assumed, so nothing feels
hidden, then where the rest is:

> Assumed, all easy to change: the name Groom Room, opening hours
> 9:00 to 17:00, and three roles (owner, groomer, front desk). The
> rest is in design/design.md.

At most five assumptions, the ones that shape the app most (its name,
counts, hours, roles), in the user's nouns; the path a link to the
file. In the build's voice throughout, never "I made" or "Should I".

## 3. One question

End with one dialog (`AskUserQuestion` where available; otherwise the
same as one plain line), the build's first question:

- Title: **Ready to build?**
- "Build it" (recommended): "Build a first working version of <the
  first feature> to try, then change what you like."
- "Not yet": "I want to study the design more. Ask me again later."

A change is typed as the dialog's own free answer, so no option only
means "change something". Nothing is built before the answer. It
comes in addition to the first handoff's review: this one decides the
design before any code, that one the feature as built.

- **A yes** (or the first feature named): build it by the front
  door's one-feature flow. At the first handoff, `design/design.md`
  becomes the accepted design as `accept-design.md` says, and
  **Assumed** moves into the first decisions entry.
- **Not yet:** wait; when the user comes back, ask the same dialog
  again.
- **A change:** update the document and the design, show what
  changed, and ask the same dialog again.
- **No answer** is not a yes.

The task list's "Wait for your go-ahead on the design" stays in
progress until the user answers, and is done on the yes; a change
leaves it in progress while the design is updated.

From the first feature on, the build follows the front door
unchanged.

## Never

- Reading a reference, or listing the folder, before the paragraph
  that says what will be built; reading this plugin's files with a
  shell command instead of the file tools.
- `AskUserQuestion`, or a question in plain text, before the design
  document is written.
- "I" or "Should I" in the design or its question: the build speaks
  as the build.
- An answer taken in step 1 without its line under **Assumed**.
- Code, `rbt generate` or a project scaffold before the user's answer
  to the one question.
