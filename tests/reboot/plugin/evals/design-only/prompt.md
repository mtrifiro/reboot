---
description: "A design and nothing else: the app-design skill runs on its own, shows the whole design, and stops with where it is and how to build it, loading no front door."
runs: 3
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, AskUserQuestion]
append_system_prompt: "You are in a planning-only session: you can read files and load skills but cannot write files or run commands. No one can answer a question in this session: state the assumptions you go on with and continue. Follow any skills that apply as far as you can without writing. End with a short summary stating what kind of app you are building (a web app, an MCP UI for an AI host, or both) and the design so far."
---

Design, but don't build yet, a web app on Reboot for a dog-walking business: the owner books walks for clients' dogs, assigns each walk to a walker, and the walker marks it done; clients can see when their dog was walked.
