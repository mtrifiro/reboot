---
description: "A restaurant host stand: the first page draws the room, and hosts work on it."
runs: 3
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, AskUserQuestion]
append_system_prompt: "You are in a planning-only session: you can read files and load skills but cannot write files or run commands. No one can answer a question in this session: state the assumptions you go on with and continue. Follow any skills that apply as far as you can without writing. End with a short summary stating what kind of app you are building (a web app, an MCP App for an AI host, or both) and the design so far."
---

A web app on Reboot for the host stand of a restaurant with 30 tables: hosts see which tables are free, seat walk-ins and parties with reservations, and mark tables cleared when guests leave. Show me the design before writing any code.
