---
name: review
description: "Review a built Reboot app, then fix what the user picks: its architecture (code shape, the API and who calls it, permissions method by method, errors and restarts, production readiness), its domain model at scale (the actor everyone waits on, collections, fan-out reads, wide transactions; measured before and after), and its tests (methods, errors, rules and roles no scenario proves; the scenarios that close each gap). With no area named, all of them and the look side by side, in one report ranked by who gets hurt. Use when the user asks to review the app or a part of it ('/reboot:review', 'review my app', 'is it ready?', 'review the code', 'will it scale?', 'what isn't tested?'). The look alone is the look skill."
argument-hint: '[optional: architecture, domain, tests or look; or what to look at, e.g. "permissions"; the whole app by default]'
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion, Agent, Skill
---

# review — Review the App, Then Fix What the User Picks

Four areas, each judged by its own method:

| Area | Method | Writes |
| --- | --- | --- |
| Architecture: structure, API, permissions, errors, readiness | [`references/architecture.md`](references/architecture.md) | `design/architecture-review.md` |
| The domain model at scale | [`references/domain.md`](references/domain.md) | `design/domain-review.md` |
| The tests: what no scenario proves | [`references/tests.md`](references/tests.md) | `design/test-review.md` |
| The look, every page (a web app only: `frontend/web/src/tokens.css`) | the [`look` skill](../look/SKILL.md) | `design/look-review.md` |

## Which review

- **One area,** when the argument or the user's words name it:
  `architecture` ("review the code", "the structure", "the API",
  "permissions"), `domain` ("will it scale?", "the data model") or
  `tests` ("what isn't tested?", "the scenarios"). Read that area's
  page with the Read tool and do all of it, from its section 1 to its
  end: its review, its dialog and the changes the user picks. Nothing
  below applies.
- **The look alone** ("the look", "the colours", "make it teal"):
  load the `look` skill with the Skill tool and pass the words on.
- **Otherwise the full review:** the four areas side by side, as
  below.

## The full review

An argument narrows every area to it ("permissions": the
authorization findings, the refusals no scenario shows, the pages a
role can't reach), and the report's first line says so.

### 1. Before starting

Say one line: "Reviewing <app> four ways at once: architecture, the
domain model at scale, the tests, and the look. About ten minutes."

**Never while a build is working in the project:** no test run in
progress (a `pytest` process in the project),
no other session's transcript for the project written to in the last
few minutes. If one is, say so in one line and wait, or ask the user.

For the look, the browser scenarios' screenshots must be there
(`tests/*.recordings/`); the phone-width capture needs the app
running: start it with the [`run` skill](../run/SKILL.md) if it
isn't.

### 2. The four reviews, side by side

Start four sub-agents in one message (the Agent tool), one per area.
Each prompt says, in these words: "Read `<the area's method>` (its
full path) with the Read tool; don't load a skill with the Skill
tool. Do its sections up to and including the review: read the
facts, judge, and write the review to `<its file>`. Ask nothing,
change nothing in the project but that file, and stop before its
dialog. For the domain, take the scale from the app's own numbers in
`AGENTS.md`, the features or the sample data (its scale dialog's
recommended answer, never asked). Reply with the verdict in two lines
and each finding as one line: its title, its harm (money or access,
done twice or lost, slow or down, confusing, cosmetic), the file and
line." Add the argument, if any, to each.

Where the host has no Agent tool, do the four one after another, by
the same words, in the order of the table.

When each finishes, say its verdict in one line as it arrives.

### 3. One report

One message, headed **Review: <app>**, written to
`design/full-review.md` too, and linked:

1. **Verdict,** three sentences: is it ready for the people it's
   for, what to fix first, and what is good.
2. **Fix first,** at most eight findings across the four, ranked by
   who gets hurt (money or a person's access, something done twice or
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

### 4. Each fix, by its area's method

For each finding chosen, in the report's order: read its area's section for making a change (`architecture.md`'s 3,
`domain.md`'s 4, `tests.md`'s 3, the `look` skill's 2 to 6 for a
look change) and make it exactly as it says: one at a time, every rule and
scenario still passing, the suite and mypy green, its own commit and
its own words in the commit. A fix that would change a rule or what a
user sees asks first, as its area's method does.

After the last one, the whole suite once, as the
[app skill](../app/SKILL.md)'s Update Flow step 7 says, then one line
per fix made. If findings are left, one dialog,
**Anything else from the review?**, its options the next findings (up
to three) and "Stop here"; otherwise a closing line naming
`design/full-review.md`.

## Never

- In the full review, a finding of its own: every finding is an area
  review's, linked to it.
- A method changed or skipped: a review that can't run (no web app
  for the look) is named in **By area** with why.
- More than one fix in flight.
- A number not counted by an area's review or a run.
- Never name or quote a person as the reviewer, or put words in
  anyone's mouth: the review speaks for itself.
