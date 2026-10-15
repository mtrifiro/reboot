---
title: Ask Nothing Until the Design Document
impact: HIGH
impactDescription: A new app asks one question first, a feature at a time or the whole app at once, each with its time. The user reads what will be built at once, then the whole proposed design in design/design.md, and gives the go-ahead or changes something before any code; a round of scope questions first only delays the design they could react to.
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

- **Status:** "proposed on <date>; nothing is built yet. Names become
  links to the developer dashboard once it shows them."
- **Every feature** is in it, under **Proposed features, in build
  order**, with the line "Only the first is built next; the rest, and
  their order, are yours to change at any point.": the first marked
  and why it comes first, each with its rules in plain words.
- **No links yet.** Packages, domain objects, methods, features and
  rules are named in code style (`Room`, `Room.check_in`), never as
  dashboard links: nothing exists on the dashboard before it is built,
  and a link to nothing reads as broken. The links are added once the
  dashboard shows the domain model (the first feature's "Build on this
  model?"), and `scripts/design_links.py` checks them from then on.
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
same as one plain line), the build's second and last question before any code:

- Title: **Ready to build?**
- "Build it" (recommended): on a feature at a time, "Build a first
  working version of <the first feature> to try, then change what you
  like."; on the whole app at once, "Build every feature in the design
  without stopping, an hour or more, then review the whole app."
- "Not yet": "I want to review or revise the design." Nothing more:
  what happens next is said after the answer.

The path was chosen before the design, in the opening's dialog
(`app/SKILL.md` step 1); this one only gives the go-ahead. A change is
typed as the dialog's own free answer, so no option only means
"change something". Nothing is built before the answer. It comes in
addition to the first handoff's review: this one decides the design
before any code, that one the feature as built.

- **A yes, on the whole app at once:** build every feature in the
  design by the [`one-shot` skill](../../one-shot/SKILL.md)'s steps 4
  and 5, from the design already proposed (no features added to it):
  the whole-app flow, no stops, one handoff at the end. The task list
  is the whole-app list (`task-list.md`, where the plugin has it), its
  first two items done.
- **A yes, on a feature at a time** (or the first feature named): build
  it by the front door's one-feature flow. At the first handoff,
  `design/design.md` becomes the accepted design as `accept-design.md`
  says, and **Assumed** moves into the first decisions entry.
- **Not yet:** first say so in one line, before any tool call:
  "Making the whole design into a page you can read in your browser.
  It opens in a moment. Tell me to continue when you're ready, or
  what to change." Then turn `design/design.md` into one readable
  page, `design/design.html`, and open it in the user's browser
  (`open` on macOS, `xdg-open` on Linux, `start` on Windows), give its
  path on a line of its own, and stop: no dialog now. A "continue" (or
  "go", "build it") is the go-ahead; a change updates the design, the
  page with it, and asks **Ready to build?** again.
  The page is self-contained and made for reading, not a dump of the Markdown: the
  app's name as its title, a short contents list from the headings,
  the text at a comfortable width, and tables as plain tables. Its own
  short stylesheet, inline: a system font, the text about 70
  characters wide, table cells with padding and a rule between rows,
  headers in the table's first row. Never the web app's stylesheet,
  whose sticky headers and app layout break a document. Before the
  app is built nothing in the design exists on the dashboard yet, so
  every dashboard link becomes plain text (names in code style), never
  a link that leads nowhere; once the dashboard shows the model, a
  regenerated page keeps them as links. It is regenerated from `design/design.md` whenever the user
  asks for it again; `design/design.md` stays the design, and the page
  is never edited by hand.

- **A change:** update the document and the design, show what
  changed, and ask the same dialog again.
- **No answer** is not a yes.

The task list's "Get your go-ahead on the design" stays in
progress until the user answers, and is done on the yes; a change
leaves it in progress while the design is updated.

## 4. The domain model, once

In the first feature only, once the front door has started the
dashboard on the new domain model, and before any servicer code, turn
the code-style names in `design/design.md` that now exist into
dashboard links (the rest stay plain until built), then end
the turn with one line linking each domain object on the dashboard
(`dashboard` skill, "Links to an Object or a Rule"), then one dialog:

> The room status floor plan's domain model is on the dashboard:
> [Room](<link>), [Floor](<link>), [Hotel](<link>).

- Title: **Build on this model?**
- "Build on it" (recommended): "Build its actions, rules and page on
  this model."
- "Not yet": "I want to look at it more. Ask me again later."

When the model differs from the proposed design, one line before the
dialog says how, in the user's nouns. A change is typed as the
dialog's free answer: change the API, `rbt generate`, say what
changed, and ask again. The task list's "Your turn: check the domain
model on the dashboard" stays in progress until the yes. If the
dashboard didn't come up, don't ask: say so in one sentence and go on;
the model is checked at the first handoff. Each next feature doesn't
ask, and `one-shot` never does.

From the first feature on, the build follows the front door
unchanged, but for this one question.

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
