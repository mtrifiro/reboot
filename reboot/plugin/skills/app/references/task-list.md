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
  does in the user's nouns ("Room status floor plan", not "Floor
  plan"), so an item reads on its own.
- `<page>` is the page's name in the user's nouns.

Each item starts with what it belongs to, then what is being done,
from a verb. Inside an item a name is written as in a sentence ("Show
room status floor plan for your review"), capitalized only at the
start. Make the list once the design is proposed; mark each item done
as it finishes; a step that fails stays in progress, never done.

## One feature at a time

The first feature, in the order of the `web-app` Step-by-Step Build
Flow:

1. Propose the design for <app>
2. Set up the project
3. <feature>: write its rules as scenarios
4. <feature>: build the domain model
5. Start the developer dashboard to display the domain model
6. <feature>: build the actions, their rules and who may do each
7. <feature>: add demo data
8. <feature>: run the scenarios
9. <feature>: check the types
10. Set up the frontend
11. <feature>: build the <page> page
12. <feature>: add a browser scenario for the <page> page
13. Check the <page> page in a browser
14. Show <feature> for your review

Each next feature, when the user chooses it:

1. <feature>: show what it adds to the design
2. <feature>: write its rules as scenarios
3. <feature>: add to the domain model
4. <feature>: build the actions, their rules and who may do each
5. <feature>: add demo data
6. <feature>: run the scenarios
7. <feature>: check the types
8. <feature>: build the <page> page
9. Check the <page> page in a browser
10. Show <feature> for your review

A feature that changes an existing page says "change the <page>
page" at item 8; one with no page drops items 8 and 9.

## The whole app first

The full prototype (`web-app/references/full-build.md`) and an MCP UI
built whole (`mcp-ui`, Step-by-Step Build Flow):

1. Propose the design for <app>
2. Set up the project
3. Build the domain model
4. Start the developer dashboard to display the domain model
5. Build the actions, without their rules yet
6. Add demo data
7. Set up the frontend
8. Build every page of the design
9. Check the app in a browser
10. <feature>: write its rules as scenarios
11. <feature>: put its rules in the code and run its scenarios
12. Run all the scenarios and check the types
13. Show <app> for your review

Items 10 and 11 come once for each feature, in the design's order.

For an MCP UI, item 8 is "Build every UI of the design" and item 9
"Check the app in its AI client". An MCP UI built one feature at a
time follows the lists above, with the same two changes.

## A backend only

As one feature at a time (`app/references/backend-only.md`), without
the frontend, page and browser items, and with "Generate the
<platform> client" after the first feature's "check the types".

## A change to a built app

`<change>` is a short name for it in the user's nouns ("Early
check-in").

1. <change>: show what it changes in the design (only when it does)
2. <change>: write its scenarios
3. <change>: change the code
4. Run all the scenarios and check the types
5. Check the <page> page in a browser (when a page changed)
6. Show <change>

## Never

- An item named for a file or a tool (`main.py`, `pytest`, `mypy`,
  "servicer"), where an item above says it in the user's terms.
- Two steps folded into one item, or one step split across several:
  each item is one step of the build flow, so the list shows where the
  build is.
- Items added for reading references or scaffolding: they belong to
  the item they serve.
- "Done" on an item whose check failed.
