---
title: The Design First, Then How to Build It
impact: HIGH
impactDescription: A new app asks one short round of scope questions first (which features the first build includes, ticked from four; who signs in; the accent; never the front door, which is the web app unless the prompt names another), then shows the whole proposed design, and only then asks how to build it, before any code.
tags: questions, scope, design, design document, first feature, go-ahead
---

# The Design First, Then How to Build It

The `app` skill's build of a new app, in either front door, works this
way. It replaces the front door's round of scope questions.

## 0. Say what will be built, first

Done already, as the `app` skill's "First, Before Reading Anything"
says: the opening, then the task list, before any reading.

## 1. One round of questions, then none until the design

Where the front door's Design Phase asks its round of scope
questions, ask only the opening's round instead (`app` skill, step
1): which features the first build includes, who signs in, the
accent; the
front door is never asked (the `app` skill's Routing). Work out anything else as the
front door says, then take the answer it would mark as recommended:

- **How to build:** asked after the design (section 3), never here.
- **Everything else** (what the app keeps track of, counts, layouts,
  hours): the recommended, simplest option. Roles wait for Who may do
  what unless the round chose them.
- **The app's name,** when the prompt names none: picked to suit the
  domain, proposed in the design as a working name.

Something else the prompt leaves open is decided the same way: the
simplest choice that fits, assumed, and listed. Times are in the
user's own time zone.

## 2. The design: shown first, written to the file after

Before the design, read only what it needs: the domain model's shape
rules (`python/references/state-collections.md` and
`api-methods.md`) and `design-messages.md`'s "The proposed design".
Nothing else yet: `conversation.md`, `design-document.md`,
`task-list.md` and the front door's references are read after the
answer, while the user isn't waiting on them.

Then write the proposed design **once, in the chat**: the message in
the shape of `design-messages.md`, "The proposed design", the whole
design but its methods, about 500 words, with one line before it only
when research ran long. Then ask **How should it be built?** (section
3). `design/design.md` is written after the answer, before any code,
in the shape of [`design-document.md`](design-document.md), in one
write: the same design, plus the first feature's methods. On "Not
yet", it is written before the reply that links it. Writing the
design twice, in parts and then again for the chat, kept the user
waiting for the file (crm-15 showed its design at 1 m 58 s; hotel-7,
which wrote it once in the chat, at 47 s).

What the design holds while nothing is built, in the chat and in the
file:

- **Status:** "proposed on <date>; nothing is built yet. Names become
  links to the developer dashboard once it shows them."
- **Four or five features** under **Proposed features, in build
  order** (`app` skill, step 1): the first marked and why it comes
  first, each with its rules in plain words. The first is one page for
  one side; a customer feature, only when the prompt implies
  customers who use the app, comes right after the first. Then **Not
  in this build**: what else a real app in the domain needs, one line
  each, built only when the user asks. **Who may do what** is listed
  there, before any deploy; until it is built, **Sign-in** says in one line
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

The user signs off on what they see, so a summary that points to
`design/design.md` is not enough. Its assumptions name what the build
picked, so nothing feels hidden:

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
line), the build's first and only question before any code. It
chooses how to build and gives the go-ahead at once, with the design
in view. Its options, word for word, filled in from the design (<n>
the features' count; <time> about 7 minutes a feature, rounded to
the nearest quarter hour and said "about 45 minutes", "about an hour";
7 is what whole-app builds measured, 1.6.0's hotel-6 and main's
hotel-7, until a build on these skills is measured):

- Title: **How should it be built?**
- "All at once": "All <n> features without stopping, about <time>;
  you see it at the end." <n> is the features under **Proposed
  features, in build order**, never the ones under **Not in this
  build**.
- "Step by step": "A feature at a time, about 15 minutes each. You
  check each part: great for learning Reboot."
- "Not yet": "I want to review or revise the design." Nothing more:
  what happens next is said after the answer.
- "Tell me more": "What each way involves, before I choose."

**On "Tell me more",** answer in the chat, then ask the same dialog
again. One short paragraph per way, in the user's nouns: All at once,
what is built in what order, that the pages are built alongside the
backends, that it stops only at the end, and what to watch meanwhile
(the task list, the dashboard filling in); Step by step, the stops and
what the user does at each (the domain model on the dashboard, the
first feature's backend before its page, each feature's handoff to
try); Not yet, that the design is written to `design/design.md` to
read and change. One line on what Reboot does for them either way
(`conversation.md`, "Say what Reboot does here"). No new facts about
the design, and no recommendation.

Neither way of building is marked recommended: that is the user's
choice. A change is typed as the dialog's own free answer, so no
option only means "change something". Nothing is built before the answer. It comes in
addition to the first handoff's review: this one decides the design
before any code, that one the feature as built. After the answer, the
`app` skill's **What to expect** for the chosen path, then the build.

- **All at once:** build every proposed feature, the ones under
  **Proposed features, in build order** and none from **Not in this
  build**, by the
  [`one-shot` skill](../../one-shot/SKILL.md)'s steps 4 and 5, from
  the design already proposed (no features added to it): no stops,
  one handoff at the end. The task list is the whole-app list
  (`task-list.md`, where the plugin has it), its first two items done.
- **Step by step** (or the first feature named): build
  it by the front door's one-feature flow. At the first handoff,
  `design/design.md` becomes the accepted design as `accept-design.md`
  says, and **Assumed** moves into the first decisions entry.
- **Not yet, or the dialog skipped:** write `design/design.md` (section 2), then one short reply that links the design
  document so the user can open it and read it whole:
  "The whole design is in design/design.md." with that path as a
  Markdown link to the file in the user's project, then "Tell me to
  continue when you're ready, or what to change." Then stop: no
  dialog now. A "continue" (or "go", "build it") asks **How should it
  be built?** again; a change updates the design and asks it again.
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
ask, and `one-shot` never does.

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
- "Tell me more": "What the page will do, and how it is built."

**On "Tell me more",** answer in the chat, then ask the same dialog
again: what the page shows and lets its users do, in their nouns; how
it stays current (it reads the backend through Reboot's generated
React hooks, so a change anyone makes appears without a reload); and
how it is checked (its scenarios in a browser, and the layout check).

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
the answer. A backend only (no front door) and `one-shot` skip it.

From the first feature on, the build follows the front door
unchanged, but for these questions.

## Never

- "How should it be built?" without the proposed design written just above
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

- Reading a reference, or listing the folder, before the opening that
  says what will be built; reading this plugin's files with a
  shell command instead of the file tools.
- Any question before the design other than the opening's round;
  "How should it be built?" is asked once, after the design, and takes
  any change to the features.
- An answer taken in step 1 without its line under **Assumed**.
- Code, `rbt generate` or a project scaffold before the user's answer
  to the one question.
