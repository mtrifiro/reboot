---
title: Accept the Design
impact: HIGH
impactDescription: Without a recorded acceptance there is nothing to measure a later change from, and the reasons for the design are lost with the conversation
tags: design, accept, review table, decisions log, model diff
---

## Accept the Design

Acceptance is the user's yes to the design, recorded so a later
change can be measured from it. It happens at each handoff that asks
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
changes from what the user asked for, with its reason.

The handoff ends with one question, in plain text: accept what was
just shown and build the recommended next part (named, with why it
comes next), build another from the list, or change something first.
A yes, or the next part named, is the acceptance. A change is made,
shown, and the question asked again. No answer is not acceptance.

Later handoffs show only the slice the feature adds, under the same
headings, and `design/design.md` gains its rows of the table.

### After the review

A change goes back to its slice, through the `feature` skill or the
proposed design, then here again. A later part waits for the user's
answer to the handoff's question unless they said up front to build
on; then the record says which slices were not accepted. No answer is
not acceptance. The acceptance is recorded when the user says yes,
before the next part is built.

### Once accepted

1. Write or update `design/design.md`: the design as accepted, with the
   review table, its status
   "accepted on <date>".
2. Append an entry to `design/decisions.md` (below).
3. Run `python3 scripts/model_diff.py --accept`. It writes
   `design/accepted.json` (the date and a fingerprint of `api/` and the
   feature files) and copies the accepted design to `design/accepted/`:
   the base every later `model_diff.py` measures from, with or without
   git.

The first handoff copies `scripts/model_diff.py` from this skill's
`assets/`. After acceptance, `python3 scripts/model_diff.py` lists
what has changed in the domain model, who may call each method and
the feature files since then: read it before a change, and say which
of its lines the user has not yet accepted.

### The decisions log

`design/decisions.md` keeps why the design is what it is after the
conversation that settled it is gone. Each acceptance appends one
entry, newest last. No entry is edited or removed: a later change that
overturns one adds its own entry naming it.

```markdown
## 2026-10-10: Design accepted: Front desk

- **Decided by you:** staff only, one role.
- **Why:** "Staff only, one role" (scope question: who signs in).
- **Decided by the build:** each Room is its own domain object, keyed
  by hotel and room number; `book` is a Writer on Room.
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

Before a change, read the log: a change against an entry says so to
the user first, naming the entry and its why.

## Limits

- `model_diff.py` reads `api/`, the servicers' `authorizer()` methods
  and `tests/*.feature` statically. A domain model built at import
  time (types generated in a loop), or an authorizer assigned rather
  than defined as a method, is not seen.
- The reasons are what the agent wrote in the log: anything said only
  in the conversation is lost with it.
