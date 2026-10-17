---
name: help
description: Help with a Reboot app, on one screen - where the project stands (its stage, its features, what is running and on which ports, the last test run), links to the app, the dashboard and the design, and four to eight things the user can ask for next, chosen for where they are, ending with a multiple-choice question. Also answers "how do I..." and "what is..." in a few plain lines with a link to see it, and "something's broken" by checking the usual causes first. Reads only (assets/status.py); starts and changes nothing unless asked. Use when the user says help, asks what they can do, what now, how to do something, where something is, or why the app isn't working.
argument-hint: [a question, e.g. "how do I add a role?" or "the app won't load"]
allowed-tools: Bash, Read, Glob, Grep, AskUserQuestion
---

# help — Where You Are, and What You Can Ask For

One screen, in the user's words. Never a list of every skill: only
what fits where the user is. Help reads; it starts, stops and changes
nothing unless the user asks for that afterwards.

## 1. Where the user is

From the folder the user is in, run
`python3 <this skill>/assets/status.py`. It prints the stage (no
project, design only, backend built, frontend built, deployed), the
app's name, each feature with its rule count and whether it is in
progress, what runs in this project (the app, the dashboard, the web
dev server) with their ports, the last test run, and the reviews
written so far. It reads files and the process table only.

## 2. What the user asked

- **Just "help", "what can I do?", "what now?"** → the overview (3).
- **"How do I…?", "what is…?", "where is…?"** → the answer (4).
- **"It's broken", "it won't load", an error** → the check (5).

## 3. The overview

One message, no longer than a screen:

1. **Where you are,** two lines: "Fifty-Six Keys: room booking is
   built, superman mode is in progress. The app is running; the last
   test run passed (5 of 5)."
2. **Links,** one line, only to what is running or exists: the app
   (its main page), the dashboard's Models, Features and Changelog
   pages, `design/design.md` and any review.
3. **What you can ask for,** four to eight items for this stage, each
   an example of the words to use and what happens, in one line:

| Stage | Pick from |
| --- | --- |
| No project | "Build me a <kind of app> for <who>" (the `app` skill); "Design me a <kind of app>, don't build it yet" (the `design` skill); "Show me an example first" (the `quickstart` skill) |
| Design only | "Build it" (go on from the design); "Change the design: <what>" |
| Backend built | "Build the <screen>" (the next page, named as its users would); "Show me the domain model" (the dashboard); "Will it scale?" (`domain-review`) |
| Frontend built | "Build <the next feature from the last Build next list>" ; "What should I build next?" (`what-next`); "Review the look" (`design-review`); "Will it scale?" (`domain-review`); "Put it in Claude and ChatGPT" (an MCP UI, when only the web app exists); "Deploy it" (`deploy`); "Stop the app" or "Restart it" (`run`) |
| Deployed | "What's happening in production?" (`inspect`); "Deploy the latest" (`deploy`); the frontend-built items |

   Leave out what doesn't apply: no "Review the look" without a web
   app, no "Stop the app" when nothing runs, no "Build the <screen>"
   once it is built. A feature in progress (`@wip`) comes first:
   "Finish <feature>".

4. **One question,** a single-choice dialog: **What would you like to
   do?**, the three items most likely next as options, the first
   marked "(Recommended)". Its free answer takes anything else. The
   choice is then done as that item says, through its skill.

## 4. How do I, what is, where is

A few plain lines in the user's nouns, and a link to see it, never a
lecture:

- **What is…:** a domain object ("Each room is its own object; it
  keeps its own state, and the dashboard's Models page draws it"), a
  rule and its scenarios, a dashboard page, a Flywheel stage. Point to
  the page that shows it.
- **How do I…:** the words to ask with, and the skill that does it
  ("Say 'add a housekeeper role'; the build adds it as a change to the
  design, with its rule and a scenario").
- **Where is…:** the file or page, linked, from `status.py` and the
  project's files.

When the answer needs a reference the user's question names, search
it for the section instead of reading it whole.

## 5. Something's broken

Check before answering, and say what was found:

1. `status.py`: is the app running? On which port? Is a test run in
   progress (a run stops the app on purpose)?
2. The page or error the user names: open it headless or call it, and
   read its message.
3. The plugin's `KNOWN-ISSUES.md` and `python/references/errors.md`:
   search for the error's words; never read either whole.

Then one plain sentence on what's wrong and one on the fix, with the
skill that makes it (usually `run`, to start or restart the app). Ask
before starting, stopping or changing anything.

## Never

- More than one screen, or every skill listed.
- Starting, stopping or editing anything as part of the help itself.
- An item that doesn't apply to where the user is.
- A link to something that isn't running or doesn't exist.
