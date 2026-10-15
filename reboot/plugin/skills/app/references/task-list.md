---
title: The Build's Task List
impact: MEDIUM
impactDescription: The user watches the build through its task list. Fixed wording in the user's nouns, the same in every build, says where the build is and what comes next; a list worded fresh each time names code steps the user can't place.
tags: task list, todo, progress, build steps, handoff
---

# The Build's Task List

Where the agent keeps a task list (a to-do tool), its items are these,
word for word, with the angle brackets filled in: `<feature>` is the
feature's name as the design gives it, `<page>` the page's name in the
user's nouns. Make the list once the design is proposed; mark each
item done as it finishes; a step that fails stays in progress, never
done.

## One feature at a time

The first feature (`web-app`, Step-by-Step Build Flow):

1. Propose the design
2. Set up the project and the developer dashboard
3. <feature>: the domain model and its rules
4. <feature>: scenarios pass and types check
5. <feature>: the <page> page
6. Check <page> in a browser
7. Show <feature> for your review

Each next feature, when the user chooses it:

1. <feature>: what it adds to the design
2. <feature>: the domain model and its rules
3. <feature>: scenarios pass and types check
4. <feature>: the <page> page
5. Check <page> in a browser
6. Show <feature> for your review

A feature that changes an existing page names that page; one with no
page drops items 4 and 5.

## The whole app first

The full prototype (`web-app/references/full-build.md`) and an MCP UI
(`mcp-ui`, Step-by-Step Build Flow):

1. Propose the design
2. Set up the project and the developer dashboard
3. The domain model and the demo data
4. Every page of the design
5. Check the app in a browser
6. <feature>: its rules and scenarios (one item per feature, in the
   design's order)
7. All scenarios pass and types check
8. Show the app for your review

For an MCP UI, item 4 is "Every UI of the design" and item 5 "Check
the app in its AI client".

## A backend only

As one feature at a time (`app/references/backend-only.md`), without
the page and browser items, and "Generate the <platform> client" after
the first feature's scenarios.

## A change to a built app

1. <the change>: what it changes in the design (only when it does)
2. <the change>: the code
3. All scenarios pass and types check
4. Check it in a browser (when a page changed)
5. Show the change

## Never

- An item named for a file or a tool (`main.py`, `pytest`, `mypy`,
  "servicer"), where an item above says it in the user's terms.
- Items added for reading references or scaffolding: they belong to
  the item they serve.
- "Done" on an item whose check failed.
