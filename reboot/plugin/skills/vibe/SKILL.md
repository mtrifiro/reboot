---
name: vibe
description: "Build a whole Reboot app hands off, asking nothing: every feature a real product in the domain needs, designed, built, reviewed and handed over once, at the end. The app-whole skill by its short name. Use when the user asks for it by name ('/reboot:vibe', 'vibe it', 'just make it')."
argument-hint: [<app-description>]
allowed-tools: Bash, Read, Write, Glob, Grep, Edit
---

# vibe — The Whole App, Hands Off

The response's first act is to load the
[`app-whole` skill](../app-whole/SKILL.md) with the Skill tool, its
argument the prompt as typed (", basic" kept when the user wrote it),
and to follow it from the top. Nothing is said, read or asked first.
