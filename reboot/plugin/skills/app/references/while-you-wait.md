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
nothing beyond what the line says.

| Step | Fact |
| --- | --- |
| Installing dependencies (`uv sync`, `npm install`) | One package brings the whole backend: Reboot runs the servers, the routing between them and the storage itself, so there's nothing else to install or run. |
| Generating code (`rbt generate`) | The API is written once, in Python. Reboot generates the typed server code, the React hooks and the MCP tools from it. |
| Starting the dashboard | The dashboard draws the domain model and its rules from the code itself, so what you check there is what runs. |
| Running the scenarios | Each rule is a scenario in plain words, and that scenario is the test: a rule the code breaks shows up as a failing scenario, not a bug report. |
| Building an action that changes several objects | A transaction changes several objects all or nothing, so a check-in can't half happen, even if a server stops partway. |
| Building a page | Pages subscribe to their data and update on their own when anything changes: no refresh button and no polling code. |
| Checking the page in a browser | The same backend serves this web app and an MCP UI for ChatGPT or Claude, with no second API. |
| Restarting the app | The dev loop restarts on every save and keeps the data, so test data isn't re-entered after each change. |
| Building a workflow | Workflows survive a crash: a step that already called a payment or an LLM isn't called again when the work resumes. |
| Before a deploy | Deploying is `rbt cloud up`: the same app, with nothing to provision. |

## Inside the Backend and Frontend items

It is the longest item on the list, often ten minutes or more, so it
never runs silent. As each part inside it starts, one line in the
user's nouns says where it is, the task list item staying in
progress, and a fact from the table above goes with the part it fits:

1. The actions: "Backend: writing the room status floor plan's actions:
   checking in, marking a room cleaned, inspecting it."
2. Who may do each: "Backend: now who may do each: only housekeeping marks a
   room cleaned, only the supervisor inspects."
3. Demo data: "Backend: adding demo data: 56 rooms across seven floors, a few
   in each state, so the floor plan has something to show."
4. The proof: "Backend: running the floor plan's 9 scenarios." Then, as they
   pass, the count ("6 of 9 pass; the rest are the check-in rules").
   A failure is said as which rule isn't kept yet, never its stack
   trace, and the fix in one sentence.
5. The page, under its own Frontend item: "Frontend: building the floor plan page."
6. The browser check: "Frontend: checking the page in a browser, as a person
   would use it."

One line each, and a fact only where the table has one that fits and
hasn't been said. No line for a part that takes seconds.

A step not in the table gets no note. When no fact is left that fits,
say nothing extra.
