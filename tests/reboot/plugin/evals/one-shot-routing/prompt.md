---
description: "One-shot by name: the one-shot skill loads the design skill, which asks nothing and designs the whole app (six or more features, roles among them), then goes straight on to the build with no question."
runs: 3
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, AskUserQuestion]
append_system_prompt: "You are in a planning-only session: you can read files and load skills but cannot write files or run commands. Follow any skills that apply as far as you can without writing. End with a short summary stating what kind of app you are building (a web app, an MCP UI for an AI host, or both), the design so far, and what you would do next."
---

/reboot:one-shot a web app for a dog-walking business: the owner books walks for clients' dogs, assigns each walk to a walker, and the walker marks it done; clients can see when their dog was walked.
