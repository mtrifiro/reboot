---
name: guide
description: "Build a Reboot app while learning Reboot: the design to approve, then each part built and explained as it goes (domain objects, method kinds, rules and the scenarios that prove them), the explanations kept in design/exegesis.md. The guided build with learning mode on from the start. Use when the user asks for it by name ('/reboot:guide') or asks to be taught Reboot while building an app."
argument-hint: [<app-description>]
allowed-tools: Bash, Read, Write, Glob, Grep, Edit
---

# guide — Learn Reboot While It Builds

The response's first act is to load the
[`app-guided` skill](../app-guided/SKILL.md) with the Skill tool, its
argument the prompt as typed followed by ", verbose", and to follow it
from the top: learning mode is on. Nothing is said, read or asked first.
