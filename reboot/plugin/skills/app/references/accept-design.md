---
title: Accept the Design
impact: HIGH
impactDescription: Without a recorded acceptance there is nothing to measure a later change from, and the reasons for the design are lost with the conversation
tags: flywheel, design, accept, review table, decisions log, model diff
---

## Accept the Design

Acceptance ends the Reboot Flywheel's Design stage
([`flywheel.md`](flywheel.md)). It happens at each handoff that asks
for it: each feature built one at a time, or the full prototype. The
user decides from the running app; this is what to put in front of
them, and what to record once they say yes.

### What the user reviews

The handoff, written as
[`design-messages.md`](design-messages.md) shows, puts the running app
and its rules in front of the user. The **review table** is the
record of the same rules, one row per rule, written to
`design/design.md` at acceptance, not shown in the chat.

| Domain object | ID | Rule | Method | Kind | Who may call | Scenario |
| --- | --- | --- | --- | --- | --- | --- |
| `Room` | hotel and room number | booked at most once per night | `book` | Writer | the app itself (from `Reservation.create`) | "A second guest requests a booked room" |

Every rule in a feature file gets a row. A rule with no owner, method
or scenario is a gap to name in the handoff's **Notes**, not to fill
silently, as is each interaction, rule or status the design adds to or
changes from what the user asked for, with its reason. Then the
close.

**Every handoff** ends with its **Your turn** section
([`design-messages.md`](design-messages.md)): what to try first, the
dashboard's pages and the design, and the parts to build next, the
recommended one first with why and its time. Then one multiple-choice
dialog (`AskUserQuestion`, never the next-step box), the only tool
call after the message:

- **Question:** "What should I build next?"
- **Options:** the parts under **Build next**, up to three, each its
  name as the label and its one line as the description, the
  recommended one first and marked "(Recommended)". When fewer than
  three parts are left and the other front door isn't built, the MCP
  UI is one. Last: "Not yet": "I want to try it first, or change
  something."
- The dialog's own free-text answer takes a change in the user's
  words.

On "Not yet", one line: "Tell me when you're ready, or what to
change." Then stop, and nothing is recorded. A part chosen is built
straight away, with no further question.

What the user says next decides: choosing or asking for a next part,
or saying to keep this one, accepts what was reviewed, recorded as below before
the next part starts; a change goes back into the build. Nothing is
recorded while the user only tries the app. When nothing is left to
build, the closing line says so and that the user can ask for changes.
No reply, or a dialog skipped, is not acceptance. Never put "feature", "@wip", "design" or
"accept" in the closing line: the user judges what they see, and the
build records what that means.

**No question before building** a part the user chose, or a change
they asked for in their own words: the choice is the agreement. Say in
a few lines what it adds, its rules, and anything assumed, then build
it; the user judges it running at the next handoff. The one question
before code is a design change the user didn't ask for
([`flywheel.md`](flywheel.md), the routing rule).

Later handoffs show only the slice the feature adds, under the same
headings, and `design/design.md` gains its objects, methods, rules
and rows of the table, as [`design-document.md`](design-document.md)
says.

### After the review

A change goes back to its slice, through the `feature` skill or the
proposed design, then here again. A later part waits for the user's
reply to the closing line unless they said up front to build on; then
the record says which slices were not accepted. No answer is not
acceptance. The acceptance is recorded when the user chooses the next
part, in the dialog or in reply to the closing line, before that part
is built.

### Once accepted

1. Write or update `design/design.md` in the shape
   [`design-document.md`](design-document.md) gives, status "accepted
   on <date>". Run `python3 scripts/design_links.py` and fix what it
   lists until it lists nothing.
2. Append an entry to `design/decisions.md` (below).
3. Run `python3 scripts/model_diff.py --accept`. It writes
   `design/accepted.json` (the date and a fingerprint of `api/` and the
   feature files) and copies the accepted design to `design/accepted/`:
   the base every later `model_diff.py` measures from, with or without
   git.

The first handoff copies `scripts/model_diff.py`,
`scripts/design_links.py` and `tests/last_run.py` from this skill's
`assets/` (`python/references/testing-project-setup.md`), and the
evidence files with them ([`evidence.md`](evidence.md)).

### The decisions log

`design/decisions.md` keeps why the design is what it is after the
conversation that settled it is gone. Each acceptance appends one
entry, newest last. No entry is edited or removed: a later change that
overturns one adds its own entry naming it.

```markdown
## 2026-10-10: Design accepted: Front desk

- **Decided by you:** staff only, one role.
- **Why:** "Staff only, one role" (scope question: who signs in).
- **Decided by the build:** each
  [Room](http://127.0.0.1:9871/#/models?type=hotel.v1.Room) is its own
  domain object, keyed by hotel and room number;
  [`book`](http://127.0.0.1:9871/#/models?type=hotel.v1.Room.book) is a
  Writer on Room.
- **Why:** a room is booked at most once per night, and one Room's
  Writer is the lock that keeps it so.
- **Set aside:** rooms as a list on Hotel: every booking would lock
  the whole hotel.
- **Assumed:** 56 rooms on floors 2 to 8; check-in times in the
  user's own time zone. Nobody was asked; check these first.
- **Left open:** the production sign-in provider and who may sign in,
  at deploy; housekeeping assignments, not built yet.
- **The user's words:** "One feature at a time" (how to build); "Staff
  only, one role" (who signs in); "housekeeping never sees guest
  names."
- **Replaces:** nothing (first design).
```

One **Decided** and **Why** pair per choice the user would need
explained later: a domain object, a container, a method kind, who may
call, the primary view, a departure from the brief. Each says who
decided: **Decided by you** for what the user chose or said, **Decided
by the build** for the rest; the user's choices are the firm ones.
**Set aside** only for alternatives raised. **Assumed** lists what the
build made up without asking: counts, names, times and time zones,
units, the name of the app and its look. It is where a wrong guess
hides, so it is never folded into Decided. **Left open** lists what was
put off on purpose: a deploy setting, a provider, a feature skipped or
not built yet. **The user's words** quotes every answer the user gave
since the last entry, the scope questions included in the first, as
the question and the answer, or "accepted without comment". **Replaces**
names the entries overturned, by heading, or "nothing". A build the
user told to go on without stopping gets its entry, headed "Design not
accepted: <title>".

Each domain object or method an entry names is its dashboard link,
as in `design.md`; a rule is its words, linked to its feature file
(`#/features/<path>.feature`), never to its number: the log is never
edited, and a rule added later renumbers the rules below it. The
headings are the anchors `design.md` links to, so each is unique.
`python3 scripts/design_links.py` checks the newest entry's links.

Before a change, read the log: a change against an entry says so to
the user first, naming the entry and its why.

### Packages

`model_diff.py` lists, under _Packages_, a package that holds six
domain objects or more, and packages that import each other in a
circle. Either goes into the handoff's **Notes** as a suggestion, one
line each, never as a question of its own and never done unasked:

- **Split by area:** one package per area of the work (for a hotel,
  `rooms.v1`, `reservations.v1`, `staff.v1`), and one on top that
  joins them (`hotel.v1`), imported by none. The dashboard's Models
  page then shows each area on its own, and the calls between them as
  the joins.
- **A circle:** layer the packages so the one on top imports the
  others and none imports back.
- **What it costs,** said with it: a method can't declare an error
  from another package (reboot#258), so the top package keeps its own
  copy of each error it passes on; each package needs its own
  `.mypy.ini` entry; the dashboard links and `design.md` move to the
  new names.
- **When:** before the first deploy, while the data is demo data. A
  domain object's full name includes its package, so moving one after
  deploy is likely a rename, which
  `python/references/api-schema-evolution.md` counts as a delete and
  an add.

On the user's yes it is a design change like any other: the split,
`design.md` with the new names, a decisions entry, and acceptance.

## Limits

- `model_diff.py` reads `api/`, the servicers' `authorizer()` methods
  and `tests/*.feature` statically. A domain model built at import
  time (types generated in a loop), or an authorizer assigned rather
  than defined as a method, is not seen.
- The reasons are what the agent wrote in the log: anything said only
  in the conversation is lost with it.
