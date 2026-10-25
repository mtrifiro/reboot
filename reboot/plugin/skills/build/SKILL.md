---
name: build
description: "Build a Reboot app as an architect would: the architecture talked through first (or skipped), the design on it, then the build stopping where the structure is decided: the API approved before any servicer code, the calls between objects and what runs on its own shown at the first handoff, and a short architecture review before the second feature. For a developer who reads code: file paths and signatures, no teaching. Use when the user asks for it by name ('/reboot:build') or asks to control the architecture of an app being built."
argument-hint: [<app-description>]
allowed-tools: Bash, Read, Write, Glob, Grep, Edit, AskUserQuestion
---

# build — The Architect's Path

> **The user sees only message text.** What this skill says goes out
> as the response's own text, never only in thinking.

## 1. Where to start

One line, as text: "An app for <what it is>, used by <who>, built the
architect's way: you approve the design, then the API before any
servicer is written." Then the dialog (AskUserQuestion), header
"Start", question **Talk through the architecture first?**:

- **Yes, brainstorm it first (Recommended):** "The domain objects,
  the calls between them and what runs on its own, decided together
  and written down; the design starts from it."
- **No, straight to the design:** "I know the shape I want; propose a
  design and I'll change it there."

With no description, the line asks what the app is for and who uses
it, and the dialog waits for the answer.

## 2. Then

- **Brainstorm:** load the [`brainstorm` skill](../brainstorm/SKILL.md)
  with the Skill tool, its argument the prompt followed by ",
  architect". Its closing dialog hands on with ", architect" kept.
- **Straight to the design:** load the
  [`app-guided` skill](../app-guided/SKILL.md), its argument the prompt
  followed by ", architect".

Either way the build is the guided build with the architect's
checkpoints ([`../app/references/architect.md`](../app/references/architect.md)).
