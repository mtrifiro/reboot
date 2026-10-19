---
description: "A backend for a React Native app: no pages, a client for the mobile app."
runs: 3
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, AskUserQuestion]
append_system_prompt: "You are in a planning-only session: you can read files and load skills but cannot write files or run commands. No one can answer a question in this session: state the assumptions you go on with and continue. Follow any skills that apply as far as you can without writing. End with a short summary stating what kind of app you are building (a web app, an MCP App for an AI host, both, or a backend only) and the design so far."
---

A backend API on Reboot for my React Native workout app: members log workouts, follow coaches, and see their weekly streaks. Show me the design before writing any code.
