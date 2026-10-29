---
name: quick
description: "Build a Reboot app after one question, how to build it: Guided (a design to approve, then each part built), Learn Reboot as it builds, Shape the architecture, or Hands off; then the skill for that answer, with no questions before the design. Use when the user asks for it by name ('/reboot:quick')."
argument-hint: [<app-description>]
allowed-tools: Bash, Read, Write, Glob, Grep, Edit, AskUserQuestion
---

# quick — One Question, Then the Build

The response's first act (loading this skill was the first) is one
dialog (AskUserQuestion), before any text, read or plan, header "How
to build", question **How do you want to build <the app, in the
prompt's nouns>?**, these options word for word:

- **Guided (Recommended):** "A high-level design of what the app does
  and the rules it keeps, for you to approve; then each part built,
  and you can change any feature."
- **Learn Reboot as it builds:** "The same, with each step explained:
  the domain objects, the kinds of method, the rules and the scenarios
  that prove them."
- **Shape the architecture:** "Talk through the objects and the calls
  between them first, then approve the API before any code is
  written."
- **Hands off:** "The whole app a real product needs, designed, built
  and reviewed with no questions, handed over at the end."

The dialog carries the explanation, since text at the start of a
build is not reliably shown (hotel-300 to hotel-338 wrote the opening
only in thinking; every dialog was shown). With no description, the
response is instead one line asking what the app is for and who uses
it, and the dialog follows the answer.

Then load, with the Skill tool, its argument the prompt followed by
", chosen", and follow it from the top: Guided, the
[`app-guided` skill](../app-guided/SKILL.md); Learn, the
[`guide` skill](../guide/SKILL.md); Shape, the
[`build` skill](../build/SKILL.md); Hands off, the
[`vibe` skill](../vibe/SKILL.md). A free answer is matched to the
nearest (one feature only: `app-basic`; no design: `app-just`).

No questions come before the design: what the prompt leaves open is
assumed and listed under Assumed, a word away from changing. The
questions first are the `app` skill's way (`/reboot:app`).

Nothing is read, no folder is listed and no plan is made before the
dialog is answered.
