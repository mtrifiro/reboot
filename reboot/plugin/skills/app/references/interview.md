---
title: Questions First, When the User Asks for Them
impact: MEDIUM
impactDescription: Without questions the design guesses what the prompt leaves open and the user corrects it at the go-ahead; asked for, a short interview settles it first, but asked badly it is twenty questions the design would have answered the same way
tags: interview, questions, clarify, ask first, design/interview.md
---

# Questions First, When the User Asks for Them

Only when the `app` skill's opening dialog was answered **Yes, ask me
first** (or the prompt asks for questions first: "ask me questions",
"interview me", "ask me up to 20 clarifying questions"). Otherwise
nothing is asked before the design: it assumes, and lists what it
assumed.

## The rounds

Each round is one dialog (`AskUserQuestion`; where there is none, the
same as plain lines): up to four questions, each two to four options,
the recommended one first and marked "(Recommended)", so accepting
every recommendation is one answer. The free answer is always there
for anything the options miss.

- **Up to 20 questions in all,** so at most five rounds. Stop sooner,
  the moment nothing left would change the design: twenty is a
  ceiling, never a target.
- **Only what the prompt leaves open,** never what it says, and never
  a question whose recommended answer any builder would pick. Each
  round is written from the answers before it.
- **The most consequential first:**
  1. What the first build does: the features, a multi-select, in the
     user's nouns ("Nothing ticked builds the recommended set.").
  2. Who uses it: who signs in, and the roles if any ("front desk,
     housekeeping, managers").
  3. The rules the domain turns on, where the prompt is ambiguous ("Can
     a room be booked while it is being cleaned?").
  4. The data: how much, and where it comes from (typed in, imported,
     another system).
  5. What it connects to: payments, email, a calendar, an existing
     system.
  6. The look: a brand, or a palette (house first,
     `app-design` skill, "Which palette?").
  7. The name, when the prompt gives none.
- **Every dialog explains itself:** a question says what its answer
  changes when that isn't obvious ("Roles add a sign-in per person and
  rules on who may do what.").
- **Nothing read before the first round,** as with the opening: the
  questions come from the prompt alone. Nothing built, no folder made.
- **"That's enough", Skip, or "just build it"** ends the interview at
  once: every question not yet asked takes its recommended answer.

## After the last round

Write `design/interview.md` with the Write tool (`mkdir -p design`
first): every question asked and its answer, one line each, in the
order asked, under the heading `# Questions before the design`. Then
load the path skill as the `app` skill says. The `app-design` skill
reads the file first: its answers are the user's, taken as given.

## Never

- Asked unasked: on `/reboot:vibe`, `/reboot:app-whole` or any skill
  named in the prompt, and on the opening's **No**, nothing is asked.
- Twenty questions because twenty were allowed.
- A question the design asks again: the go-ahead confirms the design,
  never repeats the interview.
