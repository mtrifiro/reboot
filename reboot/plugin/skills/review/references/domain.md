# Domain — Review the Domain Model at Scale, Then Improve It

This is one area of the [review skill](../SKILL.md). Read it when the
review skill sends you here; the scripts it names are the review
skill's (`<this skill>/assets/`).

The review judges from numbers, not taste. Every finding says what
breaks first as the app grows, by how much, and what the fix costs now
against later. The user picks; the build makes each change, proves the
rules still hold, and shows the numbers moved.

## How the Review Judges

1. **Start from the numbers.** Before any finding, a few lines of
   arithmetic the user can check: people at the busiest hour, domain
   objects of each kind after a year, writes a second to each, pages
   open at once. Orders of magnitude, each with its source (the
   design, the user's answer, an assumption named as one).
2. **Find the one actor everyone waits on.** Writes to one actor run
   one at a time (`python/references/servicer-writer.md`): a fixed-id
   actor that every new task, comment or sign-in writes to caps the app
   at its pace. The fix splits it by the key the writes already carry
   (a project, a day, a member)
   ([`state-actor-decomposition.md`](../../python/references/state-actor-decomposition.md)).
3. **Hold at ten times, plan for a hundred.** Recommend the simplest
   shape that holds at ten times the expected load; say what would
   change at a hundred, and don't build it now.
4. **Simplest first.** Derive what can be computed instead of storing
   it; keep together what one action must change all or nothing
   ([`state-actor-decomposition.md`](../../python/references/state-actor-decomposition.md));
   prefer one writer to a transaction when one actor suffices; split
   packages by area of the work, never one per object. More
   complicated than it needs to be is a finding.
5. **Collections by their real bound.** A collection inside an actor
   is rewritten whole on every write. Its bound is a fact of the
   domain (a project has its few columns; its tasks grow forever), never
   a cap added to fit
   ([`state-collections.md`](../../python/references/state-collections.md)).
6. **Reads that fan out.** A reader over many actors re-runs when any
   changes and ships all it returns: a list page wants a summary
   reader, aggregated one level deep
   ([`rpc-forall.md`](../../python/references/rpc-forall.md), "Use for
   Read-Mostly Fan-Out").
7. **What happens on a restart.** A workflow's call to a payment,
   email or model runs again after a restart unless wrapped
   (`python/references/servicer-workflow.md`, "Bucket 2 — Calling an
   External System": search for it, never read the whole file).
8. **Measure, never guess.** A finding about speed or contention
   comes with a probe, run before and after the change. A number in
   the review is computed or measured, never made up.
9. **Cost of change grows.** Before the first deploy the data is demo
   data and reshaping is cheap. After it the schema only grows
   ([`api-schema-evolution.md`](../../python/references/api-schema-evolution.md)):
   a split or a move is a migration. Rank findings by what breaks
   first at ten times, then by how much dearer the fix gets later.

## The Conversation

In the Claude app, questions are dialogs (`AskUserQuestion`). Everything in the user's nouns ("every
new task waits on the one workspace"), the code's names in backticks only
beside them.

### 1. Read the facts

From the project root, `python3 <this skill>/assets/review.py` prints
the domain objects (methods by kind, collections and their shape), the
calls between them from the servicers, the packages, and **signals**,
each with its evidence and the question that decides it. A signal is
where to look, not a finding. Read `AGENTS.md` and the feature files
for who uses the app and how much. Whether it is deployed decides what
a change costs: `.rbtrc` with a `cloud up` line and a `Dockerfile`
means it is set up for Reboot Cloud; nothing records whether it is
live, so ask when a finding's cost depends on it. Read a servicer only
where a signal points, never generated code (`*_rbt.py`,
`backend/api/`).

Say one line while it runs: "Reviewing <app>'s domain model: its
objects, who writes to each, and how it holds up as it grows."

### 2. Ask the scale, unless it is known

When neither the user, `AGENTS.md` nor the features say how big the
app must get, one dialog:

- **How big should <app> be ready for?**
  - "One <place> (Recommended)": "<the app's own number, from its
    features or sample data>, a few dozen people at once."
  - "A business": "Several <places>, hundreds at once."
  - "A public product": "Anyone can sign up: thousands at once."

### 3. The review

One message, headed **Domain review: <app>**:

1. **Verdict,** two or three sentences: is the shape right for the
   scale, and the one thing to fix first.
2. **The numbers,** the arithmetic from "Start from the numbers", in
   a short block.
3. **Findings,** at most seven, most urgent first, each a short
   paragraph titled with the consequence in plain words ("**1. Every
   new task waits on the one workspace.**"):
   - what the code does, the evidence linked (`file:line`);
   - what happens at ten times, in numbers;
   - the fix, in a sentence or two, and the domain model after it;
   - the cost: the API, the servicers, the pages, whether the demo
     data is reset, and that every rule stays as it is;
   - when: now, before the first deploy, or not until a named number.
4. **What's right,** one line each for the choices that hold up and
   should stay.

Write the whole review to `design/domain-review.md` too, and link it. Then
one dialog, several answers allowed:

- **Which should I do?** The top three findings, each its title as
  the label and its cost and time as the description, the first
  marked "(Recommended)", and "Measure first" when a finding rests on
  an assumed figure. No "None" option: in a list of checkboxes,
  ticking nothing is none. When nothing is chosen, one line pointing
  to `design/domain-review.md`, then stop.

**Never while a build is working in the project.** Before changing a
file, check that nothing else is: no test run in progress (a
`pytest` process in the project), no other
session's transcript for the project written to in the last few
minutes. If one is, say so in one line and wait, or ask the user.

### 4. Make each change, one at a time

For each finding chosen, in the review's order:

1. **Say it** in a few lines: the domain model before and after, in
   the user's nouns, and what will be reset.
2. **Measure first** when the finding is about load: a probe with the
   Reboot test harness
   ([`testing-harness.md`](../../python/references/testing-harness.md)) in
   `tests/probe_<name>_test.py`, marked `@pytest.mark.probe` and left
   out of the default run (`addopts = -m "not probe"` in `pytest.ini`,
   the marker registered), sending N concurrent calls to the hot
   method and printing how long they took and how many failed. Run it
   with `uv run pytest -m probe -s` and keep the numbers. Size it to
   finish in about a minute, and say the size in the line before it
   ("840 new tasks at once, about a minute"); a wait on it is one call
   of at most two minutes, and between waits a line of what it is
   doing. A probe that would take longer is made smaller, never waited
   on.
3. **Rules are the contract.** An architecture change keeps every
   `Rule:` and every scenario as it is; the full suite passing
   unchanged is the proof. A fix that would change a rule is a design
   change for the user: say which rule and why, and ask before going
   on.
4. **Change it,** as the [app skill](../../app/SKILL.md)'s Update Flow
   makes any change: the API (additive only once deployed, as
   `api-schema-evolution.md` says), `rbt generate`, the servicers, the
   seed and the pages that call what moved. Before the first deploy,
   reset the sample data with `uv run rbt dev expunge` (`.rbtrc`
   already names the application: never pass `--application-name`
   twice).
5. **Prove it:** the whole suite and mypy, as the Update Flow's step 7
   says (its result once, at the end), then the probe again. Before and after in one line: "50
   new tasks at once: 6.1 s before, 0.4 s now, none failed."
6. **Record it:** a line in `AGENTS.md` when the change teaches a
   rule the next session needs, and, in a git repository, one commit,
   "Domain: <what changed>", whose message gives the finding, the
   numbers and the reason. Link the dashboard's Models page, which now
   shows the new shape.

### 5. After the last change

One line per change made, with its numbers. If findings are left, one
dialog, **Anything else from the review?**, its options the findings
not done (up to three) and "Stop here". Otherwise a closing line
naming `design/domain-review.md`.

## Never

- Never a finding without its numbers or its domain reason, and never
  a split made by habit: each one says what it buys.
- Never a number that wasn't computed or measured.
- Never change a rule, a scenario or what a user sees as part of an
  architecture change without the user's yes.
- Never more than one change in flight: each is proven and committed
  before the next starts.
- Never read generated code, or `servicer-workflow.md` or
  `errors.md` whole: search for the section.
- Never name or quote a person as the reviewer, or put words in
  anyone's mouth: the review speaks for itself.
