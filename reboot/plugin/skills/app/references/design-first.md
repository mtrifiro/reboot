---
title: The Design First, Then How to Build It
impact: HIGH
impactDescription: A new app asks one short round of scope questions first (which features the first build includes, ticked from four; who signs in; the accent; how to build, all at once, step by step or as a power user who directs every step and is asked nothing; never the front door, which is the web app unless the prompt names another), then shows the whole proposed design and asks for the go-ahead, before any code.
tags: questions, scope, design, design document, first feature, go-ahead
---

# The Design First, Then How to Build It

How the `app` skill builds a new app, in either front door. It
replaces the front door's round of scope questions.

## 0. Say what will be built, first

Done already, as the `app` skill's "First, Before Reading Anything"
says: the opening, then the task list, before any reading.

## 1. One round of questions, then none until the design

Where the front door's Design Phase asks its scope questions, ask only
the opening's round (`app` skill, step 1): the first build's features,
who signs in, the accent, and how to build (all at once, step by step,
or the power-user path: the user directs every step and is asked
nothing). The front door is never asked (`app` skill, Routing).
Everything else is decided as the front door says, taking its
recommended answer:

- **Everything else** (what the app keeps track of, counts, layouts,
  hours): the simplest option, assumed and listed. Roles wait for Who
  may do what unless the round chose them.
- **The app's name,** when the prompt names none: one that suits the
  domain, a working name in the design.

Times are in the user's time zone.

## 2. The design: shown first, written to the file after

Before the design, read only what it needs: the domain model's shape
rules (`python/references/state-collections.md`, `api-methods.md`)
and `design-messages.md`'s "The proposed design". `conversation.md`,
`design-document.md`, `task-list.md` and the front door's references
are read after the answer.

First, in thought, walk every workflow: each person who uses the app,
the jobs they come to do (user stories: "as the front desk, I move a
guest to another room when theirs isn't ready"), and each job's every
step from start to end, not the first click. Each thing the app keeps
track of has a whole lifecycle, which the feature that adds it
covers: created, seen in a list and on its own, found (a filter, a
search), changed (every field a person could get wrong has an edit),
corrected (a mistake undone, a cancel), and ended (done, cancelled,
archived or deleted, as the domain says). "Edit" is the part builds
miss most. A part left for later is named under **Not in this
build**, never silently absent.

Then the proposed design, **once, in the chat**, in the shape of
`design-messages.md`, "The proposed design": the whole design but its
methods, about 500 words, one line before it only when research ran
long. Then the go-ahead, **Build on this design?** (section 3); on
the power-user path no dialog: the design's closing line is "The
design is in design/design.md (linked). Say what to build first." and
the build stops. `design/design.md` is written after the answer (on
the power-user path, right after the design, before that line),
before any code, in the shape of
[`design-document.md`](design-document.md), in one write: the same
design plus the first feature's methods. On "Not yet", it is written
before the reply that links it. Writing it twice, in parts then for
the chat, made the user wait (crm-15 showed its design at 1 m 58 s;
hotel-7, writing it once in the chat, at 47 s).

What the design holds while nothing is built, in chat and file:

- **Status:** "proposed on <date>; nothing is built yet. Names become
  links to the developer dashboard once it shows them."
- **Four or five features** under **Proposed features, in build
  order** (`app` skill, step 1): the first marked, with why; each a
  job for a named person, walked start to finish (user story in one
  line, then what it lets them do, with the lifecycle of what it
  adds), its rules in plain words. The first is one page for one
  side; a customer feature, when the prompt implies customers who use
  the app, comes second. Then **Not in this build**: what else a real
  app in the domain needs, one line each, built only when asked.
  **Who may do what** is listed there, before any deploy; until it is
  built, **Sign-in** says in one line "Everyone signed in can do
  everything for now; roles come with Who may do what.", and the
  first feature has no roles, roster or role rules.
- **No links yet.** Packages, domain objects, methods, features and
  rules are named in code style (`Room`, `Room.check_in`), never as
  dashboard links: a link to nothing reads as broken. Links come with
  section 4; `scripts/design_links.py` checks them from then on.
- **No review table** and **no Decisions** section yet: both come at
  the first acceptance.
- **Assumed**, after **Sign-in**: every answer taken in step 1, one
  line each, question then answer, so the user sees what to change.

The user signs off on what they see, so the assumptions say what the
build picked:

> Assumed, all easy to change: the name Groom Room, opening hours
> 9:00 to 17:00, and an hour per appointment.

At most five, the ones that shape the app most (its name, counts,
hours), in the user's nouns.

## 3. The go-ahead

The proposed design (section 2) sits as text just above the dialog,
in the same response, every heading filled, features and rules before
the domain model. Then one dialog (`AskUserQuestion` where available,
else one plain line), the only question between the opening's round
and code: the go-ahead for the chosen way of building. Its options,
word for word, filled from the design (<n> the features'
count; <time> about 10 minutes a feature, more for a hard domain, as
whole-app builds measured,
rounded to the quarter hour: "about 45 minutes", "about an hour"):

- Title: **Build on this design?**
- "Build it" (recommended): for All at once, "All <n> features
  without stopping, about <time>; you see it at the end."; for Step
  by step, "<First feature>'s backend first, about 15 minutes: you
  check its domain model on the dashboard, then its actions, then say
  to build its page." <n> is the features under **Proposed features,
  in build order**, never the ones under **Not in this build**.
- "Not yet": "I want to review or revise the design." Nothing more:
  what happens next is said after the answer.
- "Tell me more": "What happens first, before I say go."

**On "Tell me more",** one short paragraph in the chat for the chosen
way, in the user's nouns, then the same dialog again. All at once:
the build order, pages alongside backends, one stop at the end, what
to watch meanwhile (the task list, the dashboard filling in). Step by
step: each stop and what the user does there (the domain model on the
dashboard, the first feature's backend before its page, each
feature's handoff to try). Both: the design goes to
`design/design.md` to read and change, and one line on what Reboot
does for them (`conversation.md`, "Say what Reboot does here"). No
new facts about the design.

Nothing is built before the answer. The go-ahead adds to the first
handoff's review: this decides the design before any code, that the
feature as built. After the answer, the `app` skill's **What to
expect** for the chosen path, then the build.

**The power-user path asks nothing,** here or later: no go-ahead
dialog (section 2's closing line, then the build stops), no model
check (section 4), no frontend question (section 5), no **What should
I build next?**. Each prompt is built as asked by the front door's
flow for that part, tested against its rules, and handed off in the
handoff's shape with its links (`design-messages.md`), **Your turn**
ending in the plain line "Say what's next.", the next-step box
carrying only the recap. The acceptance is recorded when the user
asks for the next thing (`accept-design.md`). A prompt that changes
the design (an object, a rule, who may call) is a design change: the
design document and decisions log follow it, no question first; the
user's words are the agreement.

- **All at once:** every feature under **Proposed features, in build
  order**, none from **Not in this build**, by the
  [`one-shot` skill](../../one-shot/SKILL.md)'s steps 4 and 5, from
  the design as proposed, no features added: no stops, one handoff at
  the end. The task list is the whole-app list (`task-list.md`, where
  the plugin has it), its first two items done.
- **Step by step** (or the first feature named): build it by the
  front door's one-feature flow. At the first handoff,
  `design/design.md` becomes the accepted design (`accept-design.md`),
  and **Assumed** moves into the first decisions entry.
- **Not yet, or the dialog skipped:** write `design/design.md`
  (section 2), then one short reply: "The whole design is in
  design/design.md.", the path a Markdown link to the file in the
  user's project, then "Tell me to continue when you're ready, or
  what to change." Then stop: no dialog now.
  "Continue" (or "go", "build it") asks **Build on this design?**
  again; a change updates the design and asks again.
- **A change,** typed as the free answer (so no option means only
  "change something"): update the document and the design, show what
  changed, and ask the same dialog again.
- **No answer** is not a yes.

The task list's "Get your go-ahead on the design" stays in progress
until the answer, done on the yes; a change keeps it in progress
while the design is updated.

## 4. The domain model, once

In the first feature only, once the front door has the dashboard up
on the new domain model and before any servicer code: turn the
code-style names in `design/design.md` that now exist into dashboard
links (the rest stay plain until built), then end the turn with one
line linking each domain object on the dashboard (`dashboard` skill,
"Links to an Object or a Rule") and one dialog:

> The room status floor plan's [domain model](<the Models page link>) is open on the dashboard
> (on 9874, since other projects hold 9871 to 9873): the things the
> app keeps track of ([Room](<link>), [Floor](<link>), [Hotel](<link>))
> and what each one holds. Everything else is built on top of it, so
> this is the cheapest moment to change it.
>
> Dashboard: [Models](<link>) · [Features](<link>) · [Changelog](<link>)

That is the dashboard's whole hand-over here, the lead line (the port
named only when it isn't 9871) and the Models · Features · Changelog
line: no separate "the developer dashboard is at …" line, no second
list of the objects. Both are message text just above the dialog,
never drafted only in thinking. The dialog says on its own what it
asks about:

- Title: **Build on this domain model?**
- "Build on it" (recommended): "Next: the actions for “<feature>”,
  tested against its rules. <The objects, in the user's nouns: Hotel,
  Room and Stay> can still change later; now is when it's cheapest."
- "Walk me through it": "A short tour here in the chat: what <the
  objects> each hold, and the rule each one keeps."

It serves whoever reads it, dashboard opened or not, and neither is
asked which they are.

**The tour,** on "Walk me through it": one short paragraph per object,
in the user's nouns, its name linked on the dashboard: what it holds,
why it is its own object, the rule it keeps ("Room holds its
housekeeping state and its stays, so no guest is put in a room that
isn't inspected"). Then one line on how they connect, and the same
dialog again.

When the model differs from the proposed design, one line before the
dialog says how, in the user's nouns. A change goes in the free
answer ("a stay should also hold the guest's room"): change the API,
`rbt generate`, say what changed, ask again. The task list's "Your
turn: check the domain model on the dashboard" stays in progress
until the yes. If the dashboard didn't come up, don't ask: say so in
one sentence and go on; the model is checked at the first handoff.
Later features don't ask; `one-shot` and the power-user path never
do.

## 5. The backend, before the page

In the first feature only, once its actions pass every scenario (and
types check) and before any page, stop and show the backend, in this
order, as text just above the dialog, which is never asked without
it:

1. One line: what was built and where to see it, for example "The
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
React hooks, so anyone's change appears without a reload); how it is
checked (its scenarios in a browser, and the layout check).

The rules live in the backend, so the user sees them work on the
dashboard before any time goes into the page; later features go from
backend straight to page, no stop between, their handoff showing
both, rules on the dashboard and page to try. A change typed as the
free answer goes back to the rules or actions, tested again, then the
same dialog. "Not yet" does nothing more: one line says the dashboard
stays up and what to say to go on. The task list's "Your turn: check
the backend, then say to move on to the frontend" stays in progress
until the answer. A backend only (no front door), `one-shot`
and the power-user path skip it.

From the first feature on, the build follows the front door
unchanged, but for these questions.

## Never

- "Build on this design?" without the proposed design as text just
  above it (section 3): the question asks the user to judge it. A
  sentence that the design is in `design/design.md`, or a message
  drafted only in thinking, is not it.
- A dialog on the power-user path: the user chose to be asked
  nothing.
- "Build on this domain model?" without its lead line and the
  dashboard's links as text just above it (section 4): nothing says
  what "this" is.
- "Build the frontend: the <screen>?" without the backend's results
  and the dashboard's links just above it (section 5): the question
  asks the user to judge what they show.

- Reading a reference or listing the folder before the opening that
  says what will be built; reading this plugin's files with a shell
  command instead of the file tools.
- Any question before the design other than the opening's round; the
  go-ahead is asked once, after the design, and takes any change to
  the features.
- An answer taken in step 1 without its line under **Assumed**.
- Code, `rbt generate` or a project scaffold before the go-ahead (on
  the power-user path, before the user's first build prompt).
