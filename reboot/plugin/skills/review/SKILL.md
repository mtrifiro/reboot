---
name: review
description: "The full review of a built Reboot app: its architecture, its domain model at scale, its tests and its look, each by its own review skill's method and side by side, then one report ranked by harm, one choice of what to fix, and each fix made by the skill that owns it. Use when the user asks to review the app ('/reboot:review', 'review my app', 'review everything', 'is it ready?'). For one area alone: review-architecture, review-domain, review-tests, review-ui."
argument-hint: '[optional: what to look at, e.g. "permissions" or "is it ready to deploy?"; the whole app by default]'
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion, Agent
---

# review — The Full Review

Four reviews, one report. Each area is judged by its own skill's
method, unchanged; this skill runs them side by side, puts what they
found in one order, and has the owning skill make each fix the user
picks.

| Area | Skill | Writes |
| --- | --- | --- |
| Architecture: structure, API, permissions, errors, readiness | [`review-architecture`](../review-architecture/SKILL.md) | `design/architecture-review.md` |
| The domain model at scale | [`review-domain`](../review-domain/SKILL.md) | `design/review.md` |
| The tests: what no scenario proves | [`review-tests`](../review-tests/SKILL.md) | `design/test-review.md` |
| The look, every page (a web app only) | [`review-ui`](../review-ui/SKILL.md) | `design/look-review.md` |

An argument narrows every area to it ("permissions": the
authorization findings, the refusals no scenario shows, the pages a
role can't reach), and the report's first line says so.

## 1. Before starting

Say one line: "Reviewing <app> four ways at once: architecture, the
domain model at scale, the tests, and the look. About ten minutes."

**Never while a build is working in the project:** no test run in
progress (`tests/.suite-running`, a `pytest` process in the project),
no other session's transcript for the project written to in the last
few minutes. If one is, say so in one line and wait, or ask the user.

For the look, the app must be running: start it with the
[`run` skill](../run/SKILL.md) if it isn't.

## 2. The four reviews, side by side

Start four sub-agents in one message (the Agent tool), one per area.
Each prompt says, in these words: "Read `<the skill>/SKILL.md` with
the Read tool for its method; don't load it with the Skill tool. Do
its sections up to and including the review: read the facts, judge,
and write the review to `<its file>`. Ask nothing, change nothing in
the project but that file, and stop before its dialog. For
review-domain, take the scale from `design/design.md`'s own counts
(its scale dialog's recommended answer, never asked). Reply with the
verdict in two lines and each finding as one line: its title, its
harm (money or access, done twice or lost, slow or down, confusing,
cosmetic), the file and line." Add the argument, if any, to each.

Where the host has no Agent tool, do the four one after another, by
the same words, in the order of the table.

When each finishes, say its verdict in one line as it arrives.

## 3. One report

One message, headed **Review: <app>**, written to
`design/full-review.md` too, and linked:

1. **Verdict,** three sentences: is it ready for the people it's
   for, what to fix first, and what is good.
2. **Fix first,** at most eight findings across the four, ranked by
   harm (money or a person's access, something done twice or
   lost, slow or down, confusing, cosmetic), then by how many people
   it reaches. Each: a title in the user's nouns, a sentence of what
   goes wrong, the area, and a link to its full text in the area's
   file. Two findings that are one problem (a permission no scenario
   refuses, from both architecture and tests) are one entry naming
   both.
3. **By area,** one line each: the verdict, the count of findings,
   and the link to its review.
4. **Well made,** up to three lines across the four.

Every number is from an area's review, never estimated here.

Then one dialog, several answers allowed:

- **What should I fix?** Up to four options: the top findings in
  order, each its title as the label and its area and harm as the
  description, the first marked "(Recommended)". No "None" option:
  ticking nothing is none. When nothing is chosen, one line pointing to
  `design/full-review.md`, then stop.

## 4. Each fix, by the skill that owns it

For each finding chosen, in the report's order: read the owning
skill's section for making a change (review-architecture's 3,
review-domain's 4, review-tests' 3, review-ui's 2 to 6 for a look
change) and make it exactly as it says: one at a time, every rule and
scenario still passing, the suite and mypy green, its own commit and
its own words in the commit. A fix that would change a rule or what a
user sees asks first, as the owning skill does.

After the last one, the whole suite once, as the
[`feature` skill](../feature/SKILL.md)'s "Report a full run once"
says, then one line per fix made. If findings are left, one dialog,
**Anything else from the review?**, its options the next findings (up
to three) and "Stop here"; otherwise a closing line naming
`design/full-review.md`.

## Never

- A finding of this skill's own: every finding is an area review's,
  linked to it.
- A method changed or skipped: a review that can't run (no web app
  for the look) is named in **By area** with why.
- More than one fix in flight.
- A number not counted by an area's review or a run.
- Never name or quote a person as the reviewer, or attribute
  words to anyone: the review speaks for itself.
