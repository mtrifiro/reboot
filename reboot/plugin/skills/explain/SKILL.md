---
name: explain
description: "Explain how a built Reboot app's code works and why it is shaped so, after the build: an exegesis of each feature (its objects, each method's kind, the rules and the scenarios that prove them, who may call what, what was not done and why), written to design/exegesis.md from the code as it is, and summed up in the chat. Use when the user asks ('/reboot:explain', 'explain the code', 'how does this work?', 'walk me through the code') or picks it at a handoff. It reads and writes one file; it changes nothing in the app."
argument-hint: '[optional: what to explain, e.g. "reservations" or "the authorizers"; the whole app by default]'
allowed-tools: Bash, Read, Write, Glob, Grep
---

# explain — How the Code Works, and Why

The exegesis a verbose build writes as it goes
([`app/references/exegesis.md`](../app/references/exegesis.md)),
written after the fact, from the code as it stands now. Nothing in the
app changes: this skill reads, and writes `design/exegesis.md`.

## 1. Read

Say one line first: "Explaining how <app>'s code works: each feature's
objects, actions, rules and who may do what."

Read, with the Read tool, one call per file:

- `design/design.md` (the features, the rules, who uses the app) and
  `design/decisions.md` (why it is shaped so);
- the API files under `api/`, every servicer under
  `backend/src/servicers/`, `backend/src/main.py`;
- every feature file under `tests/`;
- each page under `frontend/web/src/` the design names.

Never generated code (`*_rbt.py`, `*_rbt_react.ts`). An argument
narrows this to the feature or the subject it names, and the first
line says so.

## 2. Write `design/exegesis.md`

One section per feature, in the order the design lists them, each
under `## <the feature> (<date>)`, in the shape and the five points of
`exegesis.md`'s "What it explains": each object or page as a decision;
each method's kind and why; each rule and the scenario that proves
it; who may call it, with the authorizer's line; what was not done
and why. 250 to 450 words a feature, the decisive lines quoted, at
most eight a quote. Reboot's terms explained once each in the file.

When the file exists (a verbose build wrote it, or an earlier run of
this skill), each section is rewritten from the code as it is now,
and a section for a feature the code no longer has is removed: the
file explains this code, not a history of it.

## 3. In the chat

One message:

- a link to `design/exegesis.md`, and in a line what it covers ("5
  features, 9 objects, 31 methods");
- **The shape of the app,** about 300 words: how the features fit
  together, the one or two decisions everything else follows from
  (the object every booking goes through, why the rooms own their
  nights), each object linked on the dashboard (`dashboard` skill,
  "Links to an Object or a Rule");
- one line: "Ask about any part, or for the exegesis again after a
  change."

No dialog.

## Never

- A change to any file but `design/exegesis.md`.
- A claim the code doesn't show: each point quotes or links its lines.
- A tutorial on Reboot, or a changelog: what this app's code means.
- Generated code read or quoted.
