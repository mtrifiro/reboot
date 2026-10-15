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
- `<feature>` is the feature's name exactly as the design's feature
  list gives it, never shortened: a name that says what the feature
  does in the user's nouns ("the room status floor plan", not "the
  board"), so an item reads on its own.
- `<page>` is the page's name in the user's nouns.

Every item starts with a verb. Inside an item every name is
lowercase, as in a sentence ("Build the room status floor plan's
domain model"), unless it is a proper noun. Make the list once the
design is proposed; mark each item done as it finishes; a step that
fails stays in progress, never done.

**Short, and the user's turn last.** The list says where the build
is and where the user comes in, not every step inside it: scaffolding,
scenarios, tests, pages and the browser check all sit inside the
Backend and Frontend items. Every item stays on the list, in order: none is dropped. Before
the handoff's question, every item above "Your turn: try the app and
decide what to do next" is done (a step that couldn't be is named in the handoff's
**Notes**), and that item is in progress while the user answers: it is
what tells the user the build is waiting for them. The question never
comes while an earlier item is still in progress.

## One feature at a time

The first feature, in the order of the `web-app` Step-by-Step Build
Flow:

1. Propose the design for <app>
2. Get your go-ahead on the design
3. Backend: build the <feature>'s domain model and rules
4. Your turn: check the domain model on the dashboard
5. Backend: build the <feature>'s actions and test them against its rules
6. Your turn: check the backend, then say to build the page
7. Frontend: build the <feature>'s page and check it in a browser
8. Your turn: try the app and decide what to do next

Item 3 covers the scaffold, the rules as scenarios, the domain model
and starting the dashboard. Item 5 covers the actions, who may do
each, demo data and the tests (scenarios pass, types check). Item 7
covers the page, its browser scenario and starting the app; it ends
with the line linking the app and the dashboard. "Backend:" and
"Frontend:" open the items that build one or the other, so the user
always knows which half is being worked on. Items 2 and 4 are the `app` skill's
two questions before any code, and item 6 its question before any page
(`app/references/design-first.md`); a front door's skill used on its
own, which doesn't ask them, leaves them off.

For the hotel's first feature, the list reads:

1. Propose the design for Maison Desk
2. Get your go-ahead on the design
3. Backend: build the room status floor plan's domain model and rules
4. Your turn: check the domain model on the dashboard
5. Backend: build the room status floor plan's actions and test them against its rules
6. Your turn: check the backend, then say to build the page
7. Frontend: build the room status floor plan's page and check it in a browser
8. Your turn: try the app and decide what to do next

Each next feature, when the user chooses it (the app keeps running):

1. Show what the <feature> adds to the design
2. Backend: add the <feature>'s domain model and rules
3. Backend: build the <feature>'s actions and test them against its rules
4. Your turn: check the backend, then say to build the page
5. Frontend: build the <feature>'s page and check it in a browser
6. Your turn: try the app and decide what to do next

## The whole app first

The full prototype (`web-app/references/full-build.md`) and an MCP UI
built whole (`mcp-ui`, Step-by-Step Build Flow):

1. Propose the design for <app>
2. Get your go-ahead on the design
3. Backend: build the domain model and rules
4. Frontend: build every page of the design
5. Backend: build every feature and test it against its rules
6. Your turn: try the app and decide what to do next

Item 2 is left off where no go-ahead is asked (`one-shot`). Item 3
covers the scaffold, the dashboard, the actions without their rules
yet and demo data; item 4 the pages and starting the app; item 5 each
feature's rules as scenarios and their proof, then the whole suite and
types. For an MCP UI, item 4 is "Frontend: build every UI of the
design".

## A backend only

As one feature at a time (`app/references/backend-only.md`), without
the Frontend item, with item 5 "Backend: build the <feature>'s
actions and test them against its rules, with the backend running", the last item "Your turn: decide
what to do next" (no app to try), and "Generate the <platform> client"
after the first feature's proof.

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
