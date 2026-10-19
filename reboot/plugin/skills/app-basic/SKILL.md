---
name: app-basic
description: "Build the basic Reboot app, asking nothing: one feature, the heart of what the user typed, designed, built, reviewed and handed over once, about half an hour. The whole-app build (app-whole) limited to one feature. Loaded by the app skill on 'Automatically', or asked for by name (/reboot:app-basic); a prompt that asks for an app in plain words goes to the app skill, which asks how to build first."
argument-hint: '[the app, e.g. "a front desk for a 56-room hotel"]'
allowed-tools: Skill
---

# app-basic — One Feature, Asking Nothing

The whole-app build, limited to its first feature. Its first and only
act: load the [`app-whole` skill](../app-whole/SKILL.md) with the Skill
tool, never by reading its file, its argument the prompt as typed
followed by ", basic" (`/reboot:app-whole <the prompt>, basic`). Its
"Basic: one feature" section takes it from there: the design names
every feature, builds the one at the heart of the prompt, and lists
the rest under **Not in this build**.

Say nothing before loading it: the app-whole skill's opening is the
first thing the user reads.
