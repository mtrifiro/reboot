---
title: The Build's Task List
impact: MEDIUM
impactDescription: The user watches the build through its task list. Fixed wording in the user's nouns, the same in every build, says where the build is and what comes next; a list worded fresh each time names code steps the user can't place.
tags: task list, todo, progress, build steps, handoff
---

# The Build's Task List

Where the agent keeps a task list (a to-do tool), its items are these,
word for word, with the angle brackets filled in:

- `<app>` is the app's name, as the design gives it.
- `<feature>` is the feature's name as a short noun phrase in the
  user's nouns, in curly quotes: “room booking”, “room status floor
  plan”, never a verb phrase (“booking a room on the room board”) and
  never so short it needs explaining (“the board”). The task list
  shows no bold or italics, so the quotes set the name apart, and it
  follows "for", never a possessive ("the rules for “room booking”",
  not "room booking's rules").
- `<page>` is the page's name in the user's nouns.

Every item starts with a verb. Inside an item every name is
lowercase, as in a sentence ("Build the domain model for “room
status floor plan”"), unless it is a proper noun. Make the list after the user answers how to build, never in the
same response as that question (before it, a list has only "Propose
the design for <app>"); mark each item done as it finishes; a step that
fails stays in progress, never done.

**Short, and the user's turn last.** The list says where the build
is and where the user comes in, not every step inside it: scaffolding,
scenarios, tests, pages and the browser checks all sit inside the
items of the two parts below. Every item stays on the list, in order: none is dropped. Before
the handoff's question, every item above "Your turn: try the app and
decide what to do next" is done (a step that couldn't be is named in the handoff's
**Notes**), and that item is in progress while the user answers: it is
what tells the user the build is waiting for them. The question never
comes while an earlier item is still in progress.

## Two parts, two lists

Every build is in two parts, and the task list shows one part at a
time: **the backend**, built and tested against its rules, then **the
frontend**, built and tested in a browser. When the user says to
build the frontend, the backend list is done and replaced by the
frontend list. Each part reads only its own references: the backend
part the Python ones, the frontend part the React, stylesheet and
browser-testing ones.

## One feature at a time

The first feature's backend:

1. Propose the design for <app>
2. Get your go-ahead on the design
3. Build the domain model and rules for “<feature>”
4. Your turn: check the domain model on the dashboard
5. Build the actions for “<feature>” and test them against its rules
6. Your turn: check the backend, then say to build the frontend (<screen>)

Item 3 covers the scaffold, the rules as scenarios, the domain model
and starting the dashboard. Item 5 covers the actions, who may do
each, demo data and the tests (scenarios pass, types check). Items 2,
4 and 6 are the `app` skill's questions
(`app/references/design-first.md`); a front door's skill used on its
own, which doesn't ask them, leaves them off.

Its frontend, once the user says so:

1. Build the page for “<feature>”
2. Test it in a browser
3. Your turn: try the app and decide what to do next

Item 1 covers the frontend scaffold, the page and starting the app.
Item 2 covers the browser scenario, the first-paint time
(`web-app/references/first-paint.md`) and the layout checks
(`web-app/references/ui-design.md`, "Measure what can be measured"),
at desktop and phone width; it ends with the line linking the app and
the dashboard. A first feature seen from both sides (`app` skill,
step 1) has "Build the two pages for “<feature>”, <the customers'>
and <the staff's>" and "Test them side by side in a browser".

For the hotel's first feature, the two lists read:

1. Propose the design for Maison Desk
2. Get your go-ahead on the design
3. Build the domain model and rules for “room status floor plan”
4. Your turn: check the domain model on the dashboard
5. Build the actions for “room status floor plan” and test them against its rules
6. Your turn: check the backend, then say to build the floor plan

1. Build the page for “room status floor plan”
2. Test it in a browser
3. Your turn: try the app and decide what to do next

Each next feature, when the user asks for it (the app keeps running),
one list, backend and frontend with no stop between them:

1. Show what “<feature>” adds to the design
2. Add the domain model and rules for “<feature>”
3. Build the actions for “<feature>” and test them against its rules
4. Build the page for “<feature>”
5. Test it in a browser
6. Your turn: try the app and decide what to do next

## The whole app at once

The same two parts, for every feature at once
(`web-app/references/full-build.md`, `mcp-ui` built whole). The
backend:

1. Propose the design for <app>
2. Get your go-ahead on the design
3. Build the domain model and rules
4. Start every page of the design in parallel (a sub-agent)
5. Build every feature's actions and test them against its rules

then, with no stop between them, the frontend:

1. Finish every page of the design
2. Test them in a browser
3. Your turn: try the app and decide what to do next

Item 2 of the backend is left off where no go-ahead is asked
(`one-shot`), and item 4 only where the host has no Agent tool
(`web-app/references/full-build.md`, "The prototype, built in two
parts at once"); then the frontend's item 1 is "Build every page of
the design". For an MCP UI, the frontend's item 1 is "Build every UI
of the design" and item 2 "Test them in their AI client".

## A backend only

The backend list alone (`app/references/backend-only.md`), its item 5
"Build the actions for “<feature>” and test them against its rules, with
the backend running", item 6 "Your turn: decide what to do next" (no
app to try), and "Generate the <platform> client" after the first
feature's tests pass.

## A change to a built app

`<change>` is a short name for it in the user's nouns ("early
check-in").

1. Show what <change> changes in the design (only when it does)
2. Make <change> and test it against the rules
3. Your turn: try the app and decide what to do next

## Never

- An item named for a file or a tool (`main.py`, `pytest`, `mypy`,
  "servicer"), where an item above says it in the user's terms.
- An item added for a step inside another (reading references,
  installing packages, generating code): it belongs to the item it
  serves, so the list shows where the build is at a glance.
- "Done" on an item whose check failed.
