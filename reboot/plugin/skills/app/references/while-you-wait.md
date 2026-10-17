---
title: While You Wait
impact: LOW
impactDescription: A build has many slow steps (installs, code generation, the dashboard starting, the suite, browser checks) where nothing visible happens. One short, true fact about Reboot before each makes the wait feel like progress and shows what Reboot does that a usual stack leaves to the developer.
tags: progress, waiting, narration, reboot capabilities
---

# While You Wait

Before a step that usually takes more than about 20 seconds, send one
note, one or two sentences, before the tool call that starts it. Pick
the fact below that fits the step and say it **for this app**: the
table gives what Reboot does; the note names this app's object, rule
or page doing it, and what the developer didn't have to write ("Each
account is its own durable object, so there's no database to set up,
no tables or migrations", not "Reboot stores state for you"). Each
fact is said at most once in a build, and one already said at a
stage's start ([`conversation.md`](conversation.md), "At every
stage") is not said again here. The tone is a good release note:
plain, specific, true. No exclamation marks, no "Did you know", no
comparison by name with another product, nothing beyond what the line
says. A step not in the table gets no note; when no fact is left that
fits, say nothing extra.

| Step | Fact |
| --- | --- |
| Installing dependencies (`uv sync`, `npm install`) | One package brings the whole backend: Reboot runs the servers, the routing between them and the storage itself, so there's nothing else to install or run. |
| Generating code (`rbt generate`) | The API is written once, in Python. Reboot generates the typed server code, the React hooks and the MCP tools from it. |
| Writing the design, with the line before it when research ran long | The design comes before any code, and it stays true after: once the app runs, every object, rule and method in it links to the dashboard, which draws them from the code. In Reboot each object keeps its own state, so the domain model is also the storage: there's no database schema to design beside it. |
| Writing the rules as a feature file (`tests/<feature>.feature`) | Each feature is one file, `tests/<feature>.feature`: its rules in plain words, and under each rule its scenarios, written Given, When, Then ("Given room 204 is booked for Friday, when Carlos books it for Friday, then he's told it's taken"). That is behavior-driven development (BDD): the spec, written before the code, in words you can check. |
| Starting the dashboard | The dashboard draws the domain model and its rules from the code itself, so what you check there is what runs. Its Features page reads the feature files: each rule, its scenarios and their last run. |
| Running the scenarios | The feature file is also the test suite: each scenario runs against the real backend, so the spec can't drift from the code. A rule the code breaks shows up as a failing scenario, in the rule's own words, not as a bug report. |
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
progress, and a fact from the table goes with the part it fits; one
line each, no line for a part that takes seconds:

1. The rules: "Backend: writing the floor plan's rules as scenarios
   in `tests/room_status_floor_plan.feature`", the file a link
   (`conversation.md`, "A feature file"), and its dashboard page
   linked too once the dashboard is up.
2. The actions: "Backend: writing the room status floor plan's
   actions: checking in, marking a room cleaned, inspecting it."
3. Who may do each: "Backend: now who may do each: only housekeeping
   marks a room cleaned, only the supervisor inspects."
4. Demo data: "Backend: adding demo data: 56 rooms across seven
   floors, a few in each state, so the floor plan has something to
   show."
5. The proof: "Backend: running the floor plan's 9 scenarios." Then
   nothing per scenario: one line when the run ends, every rule kept
   or which aren't yet (`feature` skill, Step 4). A failure is said
   as which rule isn't kept yet, never its stack trace, and the fix
   in one sentence.
6. The page, in the frontend list: "Frontend: building the floor plan
   page."
7. The browser check: "Frontend: checking the page in a browser, as a
   person would use it."

Never a stretch of more than about a minute with nothing said, at any
stage (builds have gone ten minutes silent after the go-ahead, reading
references and then writing every file in one shell command, and six
minutes between starting their research and showing the design). So:

- In the design: when the research ends, one line on what it found
  that the design uses ("Kenmore Air flies Beavers, Otters and a
  Caravan from Lake Union and Kenmore; the design uses those."),
  carrying the table's fact for writing the design; the design itself
  follows as one message (the `design` skill).
- The go-ahead's line goes out before the references are read, and
  the reading gets no line of its own: when it is long, the next
  step's Reboot line goes before it ("Backend: next, the board's
  actions. Moving an account is one transaction, the account and the
  book together or not at all.").
- Each part's files are written with the Write tool, a part at a
  time, its line first: the API, then the servicers, then the
  scenarios, then the demo data. Never one Bash call with every file
  in heredocs.
- A step that has run a minute with no output to report gets a line
  saying what it is still doing; a suite run, once, after about
  three minutes.
