---
title: Ask Nothing Until the Design Document
impact: HIGH
impactDescription: A new app asks one question first, Mixed (the first feature with the user, then the rest without stopping), a feature at a time, or the whole app at once, each with its time. The user reads what will be built at once, then the whole proposed design in design/design.md, and gives the go-ahead or changes something before any code; a round of scope questions first only delays the design they could react to.
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
- **Everything else** (who signs in, what the app keeps track of):
  the recommended, simplest option. Roles wait for Who may do what.
- **The accent and the app's name,** when the prompt names none:
  picked to suit the domain.

Something else the prompt leaves open is decided the same way: the
simplest choice that fits, assumed, and listed. Times are in the
user's own time zone.

## 2. The design document

Read the references for the API as the front door says, then write the
proposed design to `design/design.md`, in the shape of
[`design-document.md`](design-document.md), **in three parts, each its
own write, each after its own line to the user** (message text, before
the write):

1. "Writing the design: first the features and their rules." Then
   write the title, status, **Brief** and **Proposed features, in build
   order**.
2. "<N> features, the first <feature>. Now the domain model that keeps
   its rules." Then add **Domain model**, each object introduced by the
   rule it keeps ("`Room` holds its own bookings, so no night is booked
   twice").
3. "Domain model written: <the objects>. Now the methods, pages and
   sign-in." Then add the rest: the first feature's methods, **Pages**,
   **Sign-in** and **Assumed**.

Each part is less to work out at once than the whole design, and the
user sees it take shape instead of minutes of silence (one build spent
3 minutes thinking before writing it whole). With these differences
while nothing is built:

- **Status:** "proposed on <date>; nothing is built yet. Names become
  links to the developer dashboard once it shows them."
- **Every feature** is in it, under **Proposed features, in build
  order**, with the line "Only the first is built next; the rest, and
  their order, are yours to change at any point.": the first marked
  and why it comes first, each with its rules in plain words. The
  first is one page for one side (`app` skill, step 1); an app with a
  customer side lists that side's page as its own feature, right
  after the first. **Who may do what** is a feature of its own, before
  any deploy; until it is built, **Sign-in** says in one line
  "Everyone signed in can do everything for now; roles come with Who
  may do what.", and the first feature has no roles, roster or role
  rules.
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

Then show the proposed design in the chat as the front door says:
the whole design but its methods, in the shape of `design-messages.md`,
"The proposed design", about 500 words; the methods stay in
`design/design.md`. The user signs off on what they see, so a
summary that points to `design/design.md` is not enough. Its
assumptions name what the build picked, so nothing feels hidden:

> Assumed, all easy to change: the name Groom Room, opening hours
> 9:00 to 17:00, and an hour per appointment.

At most five assumptions, the ones that shape the app most (its name,
counts, hours), in the user's nouns.

## 3. One question

First the proposed design, as text in the same response, just above
the dialog: the message in [`design-messages.md`](design-messages.md),
"The proposed design", the whole design but its methods, every
heading filled, its features and rules before its domain model, about
500 words. Then end with one dialog
(`AskUserQuestion` where available; otherwise the same as one plain
line), the build's second and last question before any code:

- Title: **Ready to build?**
- "Build it" (recommended): on a feature at a time, "Build a first
  working version of <the first feature> to try, then change what you
  like."; on Mixed, "Build <the first feature> for you to try, then
  the rest of the design without stopping."
- "Not yet": "I want to review or revise the design." Nothing more:
  what happens next is said after the answer.

The path was chosen before the design, in the opening's dialog
(`app/SKILL.md` step 1); this one only gives the go-ahead. A change is
typed as the dialog's own free answer, so no option only means
"change something". Nothing is built before the answer. It comes in
addition to the first handoff's review: this one decides the design
before any code, that one the feature as built.

- **A yes, on Mixed:** build the first feature by the front door's
  one-feature flow, its backend and then its frontend with no stop
  between them (no "Build on this domain model?", no "Build the frontend: the <screen>?"),
  to its first handoff. That handoff's dialog, in place of "What
  should I build next?", is **Build the rest?**: "Build the rest"
  (recommended), "<the other features, in the user's nouns>, built and
  tested without stopping, an hour or more", then "Not yet": "I want
  to try it first, or change something." A change typed as its free
  answer goes into the first feature, and the same dialog follows. On
  its yes, build every other feature in the
  design by the [`one-shot` skill](../../one-shot/SKILL.md)'s steps 4
  and 5, from the design already proposed (no features added to it):
  no stops, one handoff at the end. The task lists are the first
  feature's (`task-list.md`, where the plugin has it) without their
  "Your turn" items but the last, then the whole-app lists for the
  rest.
- **A yes, on a feature at a time** (or the first feature named): build
  it by the front door's one-feature flow. At the first handoff,
  `design/design.md` becomes the accepted design as `accept-design.md`
  says, and **Assumed** moves into the first decisions entry.
- **Not yet:** no tool call; one short reply that links the design
  document so the user can open it and read it whole:
  "The whole design is in design/design.md." with that path as a
  Markdown link to the file in the user's project, then "Tell me to
  continue when you're ready, or what to change." Then stop: no
  dialog now. A "continue" (or "go", "build it") is the go-ahead; a
  change updates the design and asks **Ready to build?** again.
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

> The room status floor plan's [domain model](<the Models page link>) is open on the dashboard
> (on 9874, since other projects hold 9871 to 9873): the things the
> app keeps track of ([Room](<link>), [Floor](<link>), [Hotel](<link>))
> and what each one holds. Everything else is built on top of it, so
> this is the cheapest moment to change it.
>
> Dashboard: [Models](<link>) · [Features](<link>) · [Changelog](<link>)

This is the dashboard's whole hand-over at this point: the lead line,
naming the port only when it isn't 9871, then the Models · Features ·
Changelog line. No separate "the developer dashboard is at …" line
before it, and no second list of the same objects.

The lead line and the link line are message text, written in the same
response as the dialog, just above it; never drafted only in thinking.
The dialog says what it asks about on its own, so it reads right even
when the text above has scrolled away:

- Title: **Build on this domain model?**
- "Build on it" (recommended): "Next: the actions for “<feature>”,
  tested against its rules. <The objects, in the user's nouns: Hotel,
  Room and Stay> can still change later; now is when it's cheapest."
- "Walk me through it": "A short tour here in the chat: what <the
  objects> each hold, and the rule each one keeps."

The question works for whoever reads it: someone who opened the
dashboard confirms what they saw, someone who didn't can take the
tour or go on, and neither is asked which they are. A change goes in
the free answer ("a stay should also hold the guest's room").

**The tour,** on "Walk me through it": one short paragraph per object,
in the user's nouns, each its name linked on the dashboard: what it
holds, why it is its own object, and the rule it keeps ("Room holds
its housekeeping state and its stays, so no guest is put in a room
that isn't inspected"). Then one line on how they connect, and the
same dialog again.

When the model differs from the proposed design, one line before the
dialog says how, in the user's nouns. A change is typed as the
dialog's free answer: change the API, `rbt generate`, say what
changed, and ask again. The task list's "Your turn: check the domain
model on the dashboard" stays in progress until the yes. If the
dashboard didn't come up, don't ask: say so in one sentence and go on;
the model is checked at the first handoff. Each next feature doesn't
ask, Mixed doesn't, and `one-shot` never does.

## 5. The backend, before the page

In the first feature only, once its actions pass every
scenario (and types check), and before any page, stop and show the
backend, in this order, as text in the same response as the dialog
and above it. The dialog is never asked without it:

1. One line: what was built and how to look at it, for example "The
   amenity booking's backend is done: every rule holds, tested by its
   scenarios. See it on the dashboard's Features page."
2. One line per rule, ✓ with its scenario count, the rule's words a
   link to it on the Features page.
3. The dashboard's line: Models · Features · Changelog, each a link.
4. In the Claude app, the Features page opened in the Browser pane.

Then one dialog:

- Title: **Build the frontend: the <screen>?**, naming both the step
  (the frontend, the half after the backend) and the screen as its
  users would name it ("Build the frontend: the room board?").
- "Build the <screen>" (recommended): "Next, the page <its users>
  use: <what they can do there, as a sentence about them>, <and what
  you'll see change elsewhere, if anything>. About <n> minutes." For
  example: "Next, the page guests use: they can turn on Do Not Disturb
  or ask for their room to be made up, and you'll see their requests
  appear on the floor plan as they come in. About 10 minutes." Written
  to a person, not as a spec: no paths (`/stay`), no parts of the page
  by their build names (tile, drawer, modal), no "frontend" or
  "backend" beyond the title.
- "Not yet": "I want to look at the backend first."

Each next feature goes from its backend straight on to its page, with
no stop between them: the user has seen the backend's half once, and
the feature's handoff shows both, its rules on the dashboard and its
page to try.

The backend is the half the rules live in, so the user sees it work,
on the dashboard, before any time goes into the page. A change typed
as the free answer goes back to the rules or the actions, which are
tested again, and the same dialog follows. "Not yet" does nothing
more: one line says the dashboard stays up and what to say to go on.
The task list's "Your turn: check the backend, then say to build the
frontend (<screen>)" stays in progress until
the answer. A backend only (no front door), Mixed and `one-shot` skip
it.

From the first feature on, the build follows the front door
unchanged, but for these questions.

## Never

- "Ready to build?" without the proposed design written just above
  it, as text (section 3): the question asks the user to judge it. A
  sentence that the design is in `design/design.md`, or the message
  drafted only in thinking, is not it; one build asked with nothing
  shown but a line of its thinking.
- "Build on this domain model?" without its lead line and the
  dashboard's links written just above it, as text (section 4). One
  build drafted the line in thinking and asked "Does this look right?"
  alone, with nothing to say what "this" was.
- "Build the frontend: the <screen>?" without the backend's results and the
  dashboard's links shown just above it (section 5): the question asks
  the user to judge what those show.

- Reading a reference, or listing the folder, before the paragraph
  that says what will be built; reading this plugin's files with a
  shell command instead of the file tools.
- A question before the design document is written, other than the
  opening's "How should it be built?".
- An answer taken in step 1 without its line under **Assumed**.
- Code, `rbt generate` or a project scaffold before the user's answer
  to the one question.
