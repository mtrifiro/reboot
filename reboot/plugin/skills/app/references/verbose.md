# Verbose Mode — Explain the Build as It Happens

Read this only when verbose mode is on. It is on when the prompt or a
later message asks for it: "verbose", "explain as you build", "teach
me as you go", "walk me through it". It is off again on "quiet" or
"stop explaining". When it comes on, say so in one line ("Verbose:
each step's report ends with what I built, links to see it live, and
what Reboot did for you."), then build exactly as without it: the same
steps, questions and checks. Verbose changes the reports, nothing else.

## Where It Speaks

Only at the end of a milestone's report, as one section headed
**Explained**, never as commentary between tool calls. The milestones:

| After | Explain | Link to |
|---|---|---|
| The design (Design Phase step 2) | each domain object and why it is its own actor; what the features ask of each | nothing yet |
| The API, generated (build steps 4–5) | each method's kind (reader, writer, transaction, workflow) and why that kind | the Models page, each state type, its methods |
| Servicers and `main.py` (6–7) | the rule each writer or transaction enforces, what is scheduled, who may call what | the methods that enforce a rule; a transaction's pane shows what it calls |
| The frontend, built (11–12) | which page reads and calls which method; what updates live | the methods the pages call |
| Scenarios green (13) | which rule each scenario proves, in a line each | each feature, its rules, the scenarios that prove them |
| The handoff (15) | the whole app in about 300 words, then the tally below | the app, the Features page, the changelog |
| A later feature (`feature` skill, scenarios green) | the new methods and rules | its feature, rules, scenarios and new methods |

## The Section: Three Parts, 150–300 Words

1. **What I built.** Each decision in plain English, the way the
   design says it: a sentence per object, method or page, with the
   reason. Quote the one or two lines that decide it (at most eight
   lines a quote). Explain a Reboot term the first time it appears in
   the build, never again.
2. **See it live.** Two to six links, each followed by what to look
   at: "[Plot.log_harvest](…): its pane shows it creating the Harvest
   inside one transaction." Take every link from the dashboard's
   `links.py`, never write one by hand — the ids and hash routes are
   the dashboard's own:

   ```sh
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/dashboard/scripts/links.py" . --only api/<pkg>/v1/<name>.py tests/<feature>.feature
   ```

   (Outside Claude Code the script is at `../../dashboard/scripts/links.py`
   from this file.) `--only` keeps the files this milestone wrote;
   without it, it lists everything. When the dashboard is not running,
   leave the links out and say so in one line. Once the app runs,
   the handoff adds the app's own URL.
3. **What Reboot did for you.** For each Reboot capability this
   milestone used for the first time in the build, one sentence: what
   it gave the app, and the work that would otherwise be the
   developer's. The entries are in [`what-reboot-does.md`](what-reboot-does.md);
   say them in this app's nouns ("Reserving a plot updates the plot
   and the member together or not at all: no locks, no rollback
   code"). Name a capability only where this app's code uses it, and
   only once a build.

## The Handoff's Tally

The handoff's section ends with every capability the build used, one
line each, in the order they first appeared: what Reboot did, in the
app's nouns. No counts of lines or hours saved — nothing measured them.

## Saved

Append each section to `design/explained.md` under a heading naming
the milestone (`## The API`, `## Scenarios`, …), so the explanation
outlives the chat. The handoff links the file.

## Voice

The build's own voice: plain words, the app's nouns, no selling.
Never "powerful", "seamless", "effortless", "out of the box". A claim
the code does not show is left out.
