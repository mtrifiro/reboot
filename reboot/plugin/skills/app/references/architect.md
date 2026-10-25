---
title: The Architect's Checkpoints
impact: HIGH
impactDescription: An architect who can't see and approve the API before servicers are written gets a structure they would have changed while it was cheap.
tags: build, architect, api, checkpoints, review
---

## The Architect's Checkpoints

Read by the `app-guided` skill when its argument carries ", architect"
(the [`build` skill](../../build/SKILL.md)). Everything in the guided
build holds; these change it.

**The reader.** A developer who reads code. Step lines name the files
and signatures they touch (`api/rooms/v1/room.py`: `Room.check_in`,
a transaction); no fact about Reboot while waiting
([`while-you-wait.md`](while-you-wait.md)), no **Exegesis** unless
asked. Reboot's terms are used, not explained.

**1. The API, approved before any servicer.** In the first feature,
once the API is written and `rbt generate` passes (the design-first
reference's section 4 on the domain model happens here too), end the
turn with the API as text and one dialog. The text: per domain object,
its file, what one is keyed by, its fields, then one line per method:
its name, its kind (reader, writer, transaction, workflow), who may
call it (its authorizer's rule) and, for a transaction or workflow, the
objects it calls. Then the dashboard's Models link. The dialog, header
"API", question **Write the servicers on this API?**: "Yes, write
them (Recommended)" and "Change it first" (its free answer is the
change). A change is made to the API, regenerated and shown again the
same way. Later features show only what their API adds, as text, and
ask nothing unless a method changes kind or an object splits or
merges.

**2. The first handoff shows the structure.** Beside the handoff's
usual lines: who calls whom (one line per call between objects, and
none the design didn't name), what runs on its own (each workflow and
schedule, and each outside call with its at-most-once or at-least-once
guard), and where each lives in the code.

**3. A short review before the second feature.** Before the second
feature's design change, load the
[`review-architecture` skill](../../review-architecture/SKILL.md) with
the Skill tool, its argument "brief: the structure so far, before the
second feature", and follow it: its findings, the user's picks made,
every rule still passing. Then the second feature. Once per build.

**Never** a servicer written before the API's yes; never the review
skipped because the first feature is small.
