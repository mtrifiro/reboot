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

The line just above the dialog says what choosing does, in these
words: "Choosing what's next keeps this part as built. Keeping it
changes nothing in the app: it records these rules as the agreed
version, so a later change to them comes back to you first."

On "Not yet", one line: "Tell me when you're ready, or what to
change." Then stop, and nothing is recorded. A part chosen is built
straight away, with no further question. On the prompt-by-prompt path there
is no dialog: **Your turn** ends with the plain line "Say what's
next.", and the acceptance is recorded the same way, when the user
asks for the next thing.

What the user says next decides: choosing or asking for a next part,
or saying to keep this one, accepts what was reviewed, recorded as below before
the next part starts; a change goes back into the build. A switch of path ("build the rest all at
once", "step by step from here", "prompt by prompt from here") is taken as said, from the next part
on, and the first handoff's **Your turn** says in one line that it can
be. Nothing is
recorded while the user only tries the app. When nothing is left to
build, the closing line says so and that the user can ask for changes.
No reply, or a dialog skipped, is not acceptance. Never put "feature",
"@wip" or "design" in the closing line: the user judges what they see.

### What accepting means, said every time it is asked

Wherever the build asks the user to accept, keep or lock in what was
built (a dialog option, a closing line, a reply to "is it done?"), it
says once, right there, what that means, in these words or as close as
the sentence allows:

> Accepting it changes nothing in the app. It records what you've
> seen as the agreed version: its rules are marked finished on the
> dashboard, `design/design.md` and the decisions log say so, and it
> is saved as the point later changes are compared to. After that, a
> change to one of these rules, or to what the app keeps, comes back to
> you for a yes before it is built. You can still change anything.

A dialog option's description says the short form: "Changes nothing
in the app; records these rules as agreed, so a later change to them
comes to you first." Never "lock in", "kept" or "recorded" alone, and
never "measured against", without what it means for the user.

**No question before building** a part the user chose, or a change
they asked for in their own words: the choice is the agreement. The
user judges it running at the next handoff.

### Starting a part

A part the user chose starts with one message, before its feature
file or any other file of it, opened with the step line ("Starting
reservations and check-in"): what it adds, in the user's nouns; its
rules, a line each; anything assumed; and "Say stop to keep working on
what's here instead." A task item is not this message, and neither is
a line after the work has begun (hotel-214, 2026-10-19: the feature
file was written with no word in the chat, and the first mention came
nine minutes later, with its backend done).

### Changes first

A change to what is built, asked for after a handoff (before the next
part is chosen, with the choice, or just after it), is made before the
next part starts, and said done in one line ("The widths are fixed at
every size"); only then the part's opening message. A change asked
for once the part is underway is made at the end of the step in
progress, said done, then one line, "Back to <the part>", before its
next step. Never two kinds of work woven together without a word: the
user should always be able to tell whether the build is fixing what
they have or building something new (hotel-214: width, colour and name
changes were made between the steps of a new feature that hadn't been
announced). The one question
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

### Names

When `model_diff.py` lists a domain object under _Names_ (named for
its time period, `AmenityDay`), rename it before the handoff, while it
is the build's own name and nothing is deployed: the API, the
servicers, the pages, the scenarios and `design.md`, the suite green,
and one line in the handoff's **Notes** with the old and the new name.
A name the user chose is theirs: say it in **Notes** instead.

### Packages

When `model_diff.py` lists a package under _Packages_ (six domain
objects or more, or packages importing each other in a circle), the
split is a suggestion in the handoff's **Notes**, never done unasked:
[`design-packages.md`](design-packages.md).

## Limits

- `model_diff.py` reads `api/`, the servicers' `authorizer()` methods
  and `tests/*.feature` statically. A domain model built at import
  time (types generated in a loop), or an authorizer assigned rather
  than defined as a method, is not seen.
- The reasons are what the agent wrote in the log: anything said only
  in the conversation is lost with it.
