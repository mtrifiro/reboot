---
description: "No brand named: the accent dialog offers only the house list, and a themed look is never invented for the domain."
runs: 3
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, AskUserQuestion]
append_system_prompt: "You are in a planning-only session: you can read files and load skills but cannot write files or run commands. No one can answer a question in this session: state the assumptions you go on with and continue. Follow any skills that apply as far as you can without writing. End with a short summary stating what kind of app you are building (a web app, an MCP UI for an AI host, or both) and the design so far."
---

A web app on Reboot for a small-town newspaper's letters to the editor: readers send in letters, the editors read them, pick the ones to print and schedule each for an issue, and everyone can see which letters ran. Show me the design before writing any code.
