---
title: While You Wait
impact: LOW
impactDescription: A build has many slow steps (installs, code generation, the dashboard starting, the suite, browser checks) where nothing visible happens. One short, true fact about Reboot before each makes the wait feel like progress and shows what Reboot does that a usual stack leaves to the developer.
tags: progress, waiting, narration, reboot capabilities
---

# While You Wait

Before a step that usually takes more than about 20 seconds, send one
note, one or two sentences, before the tool call that starts it. Pick
the fact below that fits the step; each is said at most once in a
build, and a fact already said at a stage's start (`app` skill, "At
every stage") is not said again here.

The tone is a good release note: plain, specific, true. No exclamation
marks, no "Did you know", no comparison by name with another product,
nothing beyond what the line says. In the build's voice.

| Step | Fact |
| --- | --- |
| Installing dependencies (`uv sync`, `npm install`) | There's no database to set up. Reboot keeps each domain object's state for it, so there are no tables, migrations or cache to keep in sync. |
| Generating code (`rbt generate`) | The API is written once, in Python. Reboot generates the typed server code, the React hooks and the MCP tools from it. |
| Starting the dashboard | The dashboard draws the domain model and its rules from the code itself, so what you check there is what runs. |
| Running the scenarios | Each rule is a scenario in plain words, and that scenario is the test: a rule the code breaks shows up as a failing scenario, not a bug report. |
| Building an action that changes several objects | A transaction changes several objects all or nothing, so a check-in can't half happen, even if a server stops partway. |
| Building a page | Pages subscribe to their data and update on their own when anything changes: no refresh button and no polling code. |
| Checking the page in a browser | The same backend serves this web app and an MCP UI for ChatGPT or Claude, with no second API. |
| Restarting the app | The dev loop restarts on every save and keeps the data, so test data isn't re-entered after each change. |
| Building a workflow | Workflows survive a crash: a step that already called a payment or an LLM isn't called again when the work resumes. |
| Before a deploy | Deploying is `rbt cloud up`: the same app, with nothing to provision. |

A step not in the table gets no note. When no fact is left that fits,
say nothing extra.
