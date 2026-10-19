---
name: manual
description: "Write the user manual for a built Reboot web app, for the people who use it: a section per role, each job as numbered steps with a screenshot, what the app refuses and what to do instead, in docs/manual.md, drawn from the design and the browser scenarios. Use when the user asks ('/reboot:manual', 'write a user manual', 'a guide for my staff') or picks it at a handoff. Not for developers (AGENTS.md is theirs)."
argument-hint: '[blank for every role, or who it is for, e.g. "the housekeepers"]'
allowed-tools: Bash, Read, Write, Edit, Glob
---

# manual — The User Manual

A manual for the people the app is for, in their words: what to tap
to do their job, and what to do when the app says no. It is drawn from
what the build already proved: the design names the people and the
pages, the browser scenarios are the steps, their recordings are the
screenshots, and the rules say what is refused. A step is in the
manual because a test took it.

## 1. Read the facts

Say one line first: "Writing <app>'s user manual: a section per role,
each job step by step, from the scenarios that test it."

Read, with the Read tool, one call per file:

- `design/design.md`: **Brief** (who uses it, for what), **Pages**,
  **Sign-in** (the roles, and who each development account is),
  **Features and their rules**, **Assumed**.
- Every browser feature file (`tests/*_web.feature`): each scenario is
  a job, its steps the clicks, in the labels the page shows.
- Every other feature file's `Rule:` lines and the refusals under
  them (`attempts` … `the attempt aborts with`).
- `frontend/web/src/errors.ts`: the sentence a person reads for each
  refusal.

The screenshots: `design/screens/*.png` (each page, as the build
checked it), and under `tests/<feature>.recordings/<scenario>/<digest>/`
a `<n>.png` after the step that opened the app and after each
assertion step, `<n>` the step's position among the scenario's own
steps, from one (the `Background` not counted). Look at the ones you use with
the Read tool. Never read generated code or the servicers.

If an argument names a role or a page, the manual covers only that,
and says so in its first line.

## 2. Write `docs/manual.md`

In the user's nouns, second person, present tense ("Tap the room. Its
panel opens."). Never a code name, a method, a file, "Reboot",
"scenario", "feature" or "rule": the reader runs a hotel, not the app.
Labels are quoted exactly as the page shows them, in bold ("tap
**Check in**").

```markdown
# <App>: user manual

<One paragraph: what the app is for and who uses it, from the Brief.>

Written on <date> from the app as it stands; ask for the manual again
after a change.

## Signing in

<How a person signs in, and what someone not yet invited sees.>

| You are | You use | You can't |
| --- | --- | --- |
| <role, in the design's words> | <the pages they see> | <the main thing refused them> |

## <Role>

### To <job, as a verb: "check a guest in">

1. <step, from the scenario's When lines, in order>
2. ...

![<what the screen shows>](manual/<scenario>-<n>.png)

<What changes when it works, from the Then lines: "The room turns
plain: it's occupied.">

**If the app says no:** <each refusal of this job, in errors.ts's own
sentence, and what to do instead>

## Pages at a glance

<Each page: what it leads with, what each colour or mark means, where
its main action is. From Pages and design/screens.>

## Good to know

<The Assumed lines a user would trip on, as plain facts: "A booking is
for a specific room, not a room type.">
```

One section per role, in the order of the Sign-in table; a job two
roles share is written once, under the first, and named under the
other ("To check a guest out: as the front desk does, above"). One
screenshot per job, the step where the result shows; copy each into
`docs/manual/` (the recordings are not committed) and link it
relatively. A page with no recording uses its `design/screens/` shot.

**A job no browser scenario takes** (a page's action only the
backend scenarios prove) is written from the page itself: start the
app with the [`run` skill](../run/SKILL.md) if it isn't running, take
the job's steps once in a headless browser (Playwright, as the
`web-app` skill checks a page), and screenshot the result into
`docs/manual/`. A step that doesn't work as the design says is not
written: it goes to the closing message.

## 3. Hand it over

Commit `docs/manual.md` and `docs/manual/` as one commit, "Docs: the
user manual". Then one message, no dialog:

- a link to `docs/manual.md`, and in a line what it
  covers ("5 roles, 14 jobs, 12 screenshots");
- each job left out and why (no page for it yet; a step that didn't
  work, with what happened);
- one line: "Ask for the manual again after a change, and it is
  rewritten from the app as it is then."

## Never

- A step a test didn't take or you didn't take in the running app.
- A label paraphrased: the reader looks for the words on the screen.
- Code, the dashboard, or how the app is built: that is `AGENTS.md`'s.
- An app file changed: the manual reads the app, it never fixes it.
  A step that fails is reported, and the `feature` skill fixes it if
  the user asks.
- While a build is working in the project (a test run in progress,
  another session writing to it in the last few minutes): say so in
  one line and wait.
