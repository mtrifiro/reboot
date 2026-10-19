---
name: review-architecture
description: "A senior architect's review of a built Reboot app's structure (code shape and boundaries, the API and who calls it, permissions method by method, errors and restarts, rules proven, production readiness), then the recommendations the user picks, made one at a time with every rule passing. Use only when the user asks: '/reboot:review-architecture', 'review the architecture', 'review the code'. Not for scale (review-domain), test coverage (review-tests) or the look (review-ui)."
argument-hint: '[optional: what to look at, e.g. "the API" or "is it ready to deploy?"; the whole app by default]'
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion
---

# review-architecture — Review the App's Structure, Then Improve It

A review of the whole app as it stands, by the standard of an
architect who has built and run large systems: simple over clever,
boundaries that match the work, failure treated as normal, and every
claim backed by the code or a number. Each finding says what goes
wrong, when, and what the fix costs now against later. The user picks;
the build makes each change and proves every rule still holds.

## How the Review Judges

1. **Simplest structure that does the job.** Every layer, helper,
   package and abstraction must pay for itself today. More moving
   parts than the work needs is a finding; so is one file doing three
   jobs. Delete before adding.
2. **Boundaries follow the work.** A module, package or page has one
   reason to change. Packages split by area of the work
   ([`design-packages.md`](../app/references/design-packages.md)),
   never one per object; a page file holds one page; a servicer serves
   one domain object's job. Code repeated in two places is one idea
   with two homes.
   **A file too big to split is an app ready for packages.** When a
   finding splits a file that holds several areas (the API file, a
   servicer module, `App.tsx`), the pieces are the areas, and each is
   a package, cut the same way in every layer: the API one package
   per area with a top package joining them, imported by none
   (`api/rooms/v1/`, `api/reservations/v1/`, `api/hotel/v1/`, as
   `design-packages.md` says); the servicers in a folder per area
   (`backend/src/servicers/rooms/`); the pages in a folder per area
   (`frontend/web/src/rooms/`); the feature files, already one per
   area, unchanged. The finding names each package and the objects,
   servicers and pages that go in it, and says `design-packages.md`'s
   costs. Never a split by kind (the models in one file, the errors in
   another), and never packages that import each other in a circle.
3. **The API is a contract.** Every method has a caller (a page, a
   test, another object, an AI caller the design names) and the
   smallest surface that serves them. Failures a caller can act on are
   declared errors, not plain exceptions. Once deployed the API only
   grows
   ([`api-schema-evolution.md`](../python/references/api-schema-evolution.md)),
   so a method to drop or rename is cheap only before the first deploy.
4. **Least privilege, method by method.** Each method's callers are
   named in its `authorizer()`
   ([`servicer-authorizer.md`](../python/references/servicer-authorizer.md)).
   One `_default` rule for every method is a finding once the design
   has roles; `allow()` is a finding unless the method is public by
   design; a method left out of the authorizer with no `_default` is
   internal only, which is right for a step another object takes.
5. **Failure is the normal case.** Ask what happens when a call fails,
   runs twice, or the app restarts mid-way: a broad `except` that
   swallows a Reboot error, a workflow's outside call without
   `at_most_once`, a retry that isn't idempotent
   (`python/references/servicer-workflow.md`, "Bucket 2 — Calling an
   External System": search for it, never read the whole file).
6. **The rules are the specification.** Every rule has a scenario
   that proves it, every writing method is reached by one, and
   nothing finished is left `@wip`. A test that passes whatever the
   code does is a finding. Coverage gap by gap, with the scenarios
   that would close them, is the
   [`review-tests` skill](../review-tests/SKILL.md)'s: one line points
   to it when the structure's signals show gaps.
7. **Numbers over adjectives.** Line counts, call counts, method
   counts, measured times: a finding says how much. Load and
   contention (single actors, collections, fan-out reads, wide
   transactions) are the [`review-domain`
   skill](../review-domain/SKILL.md)'s; when its `review.py` shows a
   signal worth weighing, one line says so and points to it, and the
   finding isn't repeated here.
8. **Ready to run elsewhere.** Configuration from the environment
   with a dev default, secrets never in the code, the app able to
   start clean from its seed, and enough in the logs and the
   dashboard to see what happened
   ([`inspect` skill](../inspect/SKILL.md)).
9. **Rank by risk, then by cost of waiting.** What breaks or misleads
   first comes first; among equals, the fix that gets dearer after the
   first deploy or the next feature comes first. Taste is never a
   finding: a name the user chose, a layout that works.

## The Conversation

In the Claude app, questions are dialogs (`AskUserQuestion`). Findings
are in the user's nouns first ("every room action shares one
permission rule"), the code's names in backticks beside them.

### 1. Read the facts

Say one line first: "Reviewing <app>'s structure: its code, its API
and who calls it, its permissions, its tests, and what it needs to
run in production."

From the project root:

- `python3 <this skill>/assets/structure.py` prints the files and
  functions by size, the servicers, the API surface with who uses each
  method, each authorizer, the scenario counts and the last run, and
  **signals** (A1, A2, ...), each with its evidence and the question
  that decides it.
- `python3 <the review-domain skill>/assets/review.py` prints the
  domain model's facts and its signals (S1, S2, ...), for the scale
  line only.

A signal is where to look, not a finding. Read `design/design.md` for
who uses the app and what it is for, and `design/decisions.md` for
choices already made on purpose: a choice the log explains is not a
finding unless its reason no longer holds. Then read the files the
signals point to, with the Read tool, one call per file; never
generated code (`*_rbt.py`, `*_rbt_react.ts`, `backend/api/`), never
`node_modules`. Check whether it is deployed (`deploy/ledger.jsonl`).

### 2. The review

One message, headed **Architecture review: <app>**:

1. **Verdict,** two or three sentences: is the structure sound for
   what the app is and where it is going, and the one thing to fix
   first.
2. **By the numbers,** a short block: files and lines by layer
   (API, backend, frontend, tests), domain objects and methods,
   methods with no caller, rules and scenarios, the last run.
3. **Findings,** at most seven, most urgent first, each a short
   paragraph titled with the consequence in plain words ("**1. Anyone
   signed in can take a room out of order.**"):
   - what the code does, the evidence linked (`file:line`);
   - what goes wrong and when: the next feature, the first deploy, the
     first second user, a restart;
   - the recommendation, in a sentence or two, and what the code looks
     like after it;
   - the cost: the files touched, whether the API changes, whether the
     demo data is reset, and that every rule stays as it is;
   - when: now, before the first deploy, or not until a named event.
4. **Scale,** one line: the review-domain signals worth a look, with
   "`/reboot:review-domain` weighs them with the numbers", or "nothing
   in the domain model's shape is a risk at this size".
5. **What's right,** one line each for the choices that hold up and
   should stay.

Write the whole review to `design/architecture-review.md` too, and
link it. Then one dialog, several answers allowed:

- **Which should I do?** The top three findings, each its title as
  the label and its cost as the description, the first marked
  "(Recommended)". No "None" option: ticking nothing is none. When
  nothing is chosen, one line pointing to
  `design/architecture-review.md`, then stop.

**Never while a build is working in the project.** Before changing a
file, check that nothing else is: no test run in progress
(`tests/.suite-running`, a `pytest` process in the project), no other
session's transcript for the project written to in the last few
minutes. If one is, say so in one line and wait, or ask the user.

### 3. Make each change, one at a time

For each finding chosen, in the review's order:

1. **Say it** in a few lines: before and after, in the user's nouns,
   and what will be reset.
2. **Rules are the contract.** A structural change keeps every
   `Rule:` and every scenario as it is; the full suite passing
   unchanged is the proof. A recommendation that changes a rule, who
   may do what, or what a user sees is a design change: say which and
   why, and ask before going on.
3. **Change it,** as the [`feature` skill](../feature/SKILL.md) makes
   any change (a split into packages one package at a time, the suite
   green after each, `design.md`'s names and links moved with it): the API (additive only once deployed), `rbt generate`,
   the servicers, the seed, the pages that call what moved, each file
   changed with the Edit tool. Before the first deploy, reset the demo
   data with the `run` skill's expunge when the state's shape changed.
4. **Prove it:** the full test suite and mypy as the `feature` skill
   says (its result once), and `npm run build` when the frontend
   changed. Then `structure.py` again: the signal the finding came
   from is gone, in one line ("`Room`'s authorizer: one rule for 11
   methods before, 4 rules by role now").
5. **Record it** as a design change
   ([`accept-design.md`](../app/references/accept-design.md)): a
   `design/decisions.md` entry with the finding, the evidence and the
   reason, the model diff accepted when the API changed, and one
   commit, "Architecture: <what changed>".

### 4. After the last change

One line per change made, with its before and after. If findings are
left, one dialog, **Anything else from the review?**, its options the
findings not done (up to three) and "Stop here". Otherwise a closing
line naming `design/architecture-review.md`.

## Never

- Never a finding without its evidence (`file:line`, a count, a
  measured number) and its consequence: a recommendation says what it
  buys.
- Never a number that wasn't counted or measured.
- Never change a rule, a scenario, who may do what, or what a user
  sees as part of a structural change without the user's yes.
- Never more than one change in flight: each is proven and committed
  before the next starts.
- Never a finding on taste, or one the decisions log already answers
  with a reason that still holds.
- Never read generated code, or `servicer-workflow.md` or `errors.md`
  whole: search for the section.
- Never name or quote a person as the reviewer, or put words in
  anyone's mouth: the review speaks for itself.
