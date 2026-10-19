---
name: test-review
description: "Review a built Reboot app's test coverage (methods no scenario calls, errors never made to happen, rules no refused attempt proves, roles never refused, states never checked), recommend the scenarios that close each gap and the features the gaps point to, and add the ones the user picks. Use only when the user asks: '/reboot:test-review', 'review the tests', 'what isn't tested?'. Not for the structure (review) or a roadmap (what-next)."
argument-hint: '[blank for every test, or what to look at, e.g. "the front desk" or "permissions"]'
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion, Skill
---

# test-review — Review the Tests, Then Close the Gaps

The feature files are the app's specification: each rule, each
scenario proving it, run on every change. This review reads them
against the code and asks what a person could do, or be stopped from
doing, that no scenario shows. Each gap comes with the scenario that
would close it, already written; the user picks, and the build adds
it, runs it and says what it found.

## How the Review Judges

1. **A rule is proven by what it refuses.** A rule that forbids
   something needs a scenario where someone tries and is stopped
   (`attempts` … `the attempt aborts with`). A rule shown only by the
   path that works is a claim, not a proof.
2. **Every declared error happens somewhere.** An error in a method's
   `errors=[...]` is a promise to the caller; a scenario makes it
   happen and checks what the caller is told.
3. **Every boundary between people is tested from both sides.** For
   each role the design names, a scenario where it does its job and
   one where it is refused what isn't its job (`PermissionDenied`);
   for a signed-out visitor, what they see or are refused
   (`Unauthenticated`).
4. **Every state a thing can be in is reached and checked.** Each
   value the servicers set (a room's `dirty`, a booking's
   `cancelled`) appears in a scenario's `Then`, and so does the way
   out of it.
5. **A person's work, end to end, in a browser.** Each page's main
   job has one browser scenario, click by click
   ([`testing-web-app.md`](../python/references/testing-web-app.md)),
   not one per button.
6. **Two people at once.** Where two people can act on the same thing
   (two desks, one room), a scenario shows what the second one sees.
7. **A scenario that can't fail is worse than none.** It must name
   the value it expects, not only that a call returned; one that
   would pass whatever the code did is a finding.
8. **Gaps are ranked by who gets hurt.** Money, a person's access,
   something done twice or lost come first; a label nobody reads comes
   last. Count, don't guess: every number is from `coverage.py` or a
   run.
9. **A gap the tests can't close is a feature.** A state with no way
   out, a role with nothing to do, an error a person can't recover
   from, a step the design names that no method takes: these are
   missing behaviour, not missing tests, and are recommended as
   features. A roadmap is the
   [`what-next` skill](../what-next/SKILL.md)'s.

## The Conversation

In the Claude app, questions are dialogs (`AskUserQuestion`). Gaps are
in the user's nouns first ("no one is ever stopped from inspecting a
room they cleaned twice"), the code's names in backticks beside them.

### 1. Read the facts

Say one line first: "Reviewing <app>'s tests: what each rule refuses,
which errors and states a scenario reaches, and who is ever refused."

From the project root, `python3 <this skill>/assets/coverage.py`
prints the totals, each method with its scenarios, the errors no
scenario makes happen and whether a refusal is shown, each rule with
its scenarios, the state values the servicers set and those never
checked, the pages, and **signals** (T1, T2, ...), each with its
evidence and the question that decides it. A signal is where to look,
not a finding. Read `design/design.md` (who uses the app, the roles,
the rules), every feature file with the Read tool, one call per file,
and `tests/.last-run.json` for the last run. Read a servicer only
where a signal points; never generated code.

### 2. The review

One message, headed **Test review: <app>**:

1. **Verdict,** two or three sentences: how well the scenarios prove
   the rules, and the one gap to close first.
2. **By the numbers:** scenarios (in a browser), methods called by a
   scenario, declared errors made to happen, rules with a refused
   attempt, roles refused, from `coverage.py`.
3. **Scenarios to add,** at most seven gaps, most harmful first, each
   titled with what could go wrong unseen ("**1. Housekeeping could
   check a guest in, and no scenario would notice.**"):
   - the gap and its evidence (`file:line`, the signal);
   - the scenario or two that close it, in full, in the built-in steps
     of [`testing-features.md`](../python/references/testing-features.md)
     (or [`testing-web-app.md`](../python/references/testing-web-app.md)
     in a browser), under the rule it proves, in a fenced `gherkin`
     block;
   - what it would catch if the code went wrong.
4. **Features the tests point to,** at most three, one short paragraph
   each: the gap the tests can't close, who it hurts, and the feature
   that would close it, with "`/reboot:what-next` weighs the whole
   roadmap".
5. **Well proven,** one line each for the rules the scenarios prove
   well.

Write the whole review to `design/test-review.md` too, and link it.
Then one dialog, several answers allowed:

- **What should I add?** Up to four options: the top scenario gaps,
  each its title as the label and the number of scenarios as the
  description ("3 scenarios under 'Only a supervisor inspects'"), the
  first marked "(Recommended)", and a feature when one is worth more
  than a fourth gap. No "None" option: ticking nothing is none. When
  nothing is chosen, one line pointing to `design/test-review.md`,
  then stop.

**Never while a build is working in the project.** Before changing a
file, check that nothing else is: no test run in progress
(`tests/.suite-running`, a `pytest` process in the project), no other
session's transcript for the project written to in the last few
minutes. If one is, say so in one line and wait, or ask the user.

### 3. Add each one, one at a time

For each scenario gap chosen, in the review's order:

1. **Add the scenarios** to their feature file with the Edit tool,
   under the rule they prove; a scenario that proves no rule yet goes
   under a new `Rule:` only with the user's yes, since a new rule is a
   design change
   ([`accept-design.md`](../app/references/accept-design.md)).
2. **Run that feature's file** in the foreground, as the
   [`feature` skill](../feature/SKILL.md) says ("A feature's own
   scenarios run in the foreground"), its output never filtered.
3. **Read the result:**
   - **It passes:** the app already keeps the rule, and now it is
     proven. One line: "Proven: housekeeping is refused a check-in."
   - **It fails:** the review found a bug. Say which rule is broken,
     what the app did instead, and the fix in a sentence; then one
     dialog, **Fix it?**, "Fix the code (Recommended)" or "Keep the
     scenario `@blocked` with the reason". A fix is made as the
     `feature` skill makes any change, with every other scenario still
     passing. Never change the new scenario to make it pass.
4. **Commit** the scenarios (and any fix) as one commit, "Tests:
   <what is now proven>".

For each feature chosen, load the `feature` skill with the Skill tool
(`/reboot:feature <the feature, in the user's words>`), never by
reading its file; it designs the feature's rules and builds it as any
feature.

### 4. After the last one

Run the whole suite once, as the `feature` skill's "Report a full run
once" says, then `coverage.py` again, and say the numbers before and
after in a line each ("Declared errors made to happen: 10 of 16 → 15
of 16"). If gaps are left, one dialog, **Anything else from the
review?**, its options the gaps not done (up to three) and "Stop here".
Otherwise a closing line naming `design/test-review.md`.

## Never

- Never a scenario that would pass whatever the code does: each names
  the value or the error it expects.
- Never a custom step where a built-in one says it
  ([`testing-custom-steps.md`](../python/references/testing-custom-steps.md)
  only when none does).
- Never change, weaken or delete an existing scenario or rule without
  the user's yes; a failing new scenario is a finding, not a typo.
- Never filter a run's output (`| grep`, `| tail`).
- Never a number that wasn't counted by `coverage.py` or a run.
- Never more than one gap in flight: each is run and committed before
  the next starts.
- Never name or quote a person as the reviewer, or put words in
  anyone's mouth: the review speaks for itself.
