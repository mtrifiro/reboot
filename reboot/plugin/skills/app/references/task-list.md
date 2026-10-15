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

**The review comes last.** Every item stays on the list, in order:
none is dropped. Before the handoff's question, every item above
"Your turn: review …" is done (a step that couldn't be is named in
the handoff's **Notes**), and the review item is in progress while
the user answers: it is what tells the user the build is waiting for
them. The question never comes while an earlier item is still in
progress.

## One feature at a time

The first feature, in the order of the `web-app` Step-by-Step Build
Flow:

1. Propose the design for <app>
2. Wait for your go-ahead on the design
3. Scaffold the project
4. Write the <feature>'s rules as scenarios
5. Build the <feature>'s domain model
6. Start the Reboot dashboard to show the domain model
7. Your turn: check the domain model on the dashboard
8. Build the <feature>'s actions, who may do each, and demo data
9. Prove the <feature>'s rules (scenarios pass, types check)
10. Build the <feature>'s page, with a browser scenario
11. Start the app for you to see, and check it in a browser
12. Your turn: review the <feature>

Items 2 and 7 are the `app` skill's two questions before any code
(`app/references/design-first.md`); a front door's skill used on its
own, which doesn't ask them, leaves them off. Item 11 ends with the
line linking the app and the dashboard.

For the hotel's first feature, the list reads:

1. Propose the design for Maison Desk
2. Wait for your go-ahead on the design
3. Scaffold the project
4. Write the room status floor plan's rules as scenarios
5. Build the room status floor plan's domain model
6. Start the Reboot dashboard to show the domain model
7. Your turn: check the domain model on the dashboard
8. Build the room status floor plan's actions, who may do each, and demo data
9. Prove the room status floor plan's rules (scenarios pass, types check)
10. Build the room status floor plan's page, with a browser scenario
11. Start the app for you to see, and check it in a browser
12. Your turn: review the room status floor plan

Each next feature, when the user chooses it (the app keeps running):

1. Show what the <feature> adds to the design
2. Write the <feature>'s rules as scenarios
3. Add the <feature> to the domain model
4. Build the <feature>'s actions, who may do each, and demo data
5. Prove the <feature>'s rules (scenarios pass, types check)
6. Build the <feature>'s page, with a browser scenario
7. Check the <feature> in a browser
8. Your turn: review the <feature>

A feature that changes an existing page says "Change the <page> page
for the <feature>" at item 6; one with no page drops items 6 and 7.

## The whole app first

The full prototype (`web-app/references/full-build.md`) and an MCP UI
built whole (`mcp-ui`, Step-by-Step Build Flow):

1. Propose the design for <app>
2. Scaffold the project
3. Build the domain model
4. Start the Reboot dashboard to show the domain model
5. Build the actions, without their rules yet, and demo data
6. Build every page of the design
7. Start the app for you to see, and check it in a browser
8. Write the <feature>'s rules as scenarios
9. Prove the <feature>'s rules in the code
10. Prove every rule (all scenarios pass, types check)
11. Your turn: review <app>

Items 8 and 9 come once for each feature, in the design's order.

For an MCP UI, item 6 is "Build every UI of the design" and item 7
"Start the app and check it in its AI client". An MCP UI built one
feature at a time follows the lists above, with the same two changes.

## A backend only

As one feature at a time (`app/references/backend-only.md`), without
the page and browser items, with "Start the backend" in place of item
11, and with "Generate the <platform> client" after the first
feature's proof.

## A change to a built app

`<change>` is a short name for it in the user's nouns ("early
check-in").

1. Show what <change> changes in the design (only when it does)
2. Write <change>'s scenarios
3. Change the code for <change>
4. Prove every rule (all scenarios pass, types check)
5. Check the <page> page in a browser (when a page changed)
6. Your turn: review <change>

## Never

- An item named for a file or a tool (`main.py`, `pytest`, `mypy`,
  "servicer"), where an item above says it in the user's terms.
- An item added for a step inside another (reading references,
  installing packages, generating code): it belongs to the item it
  serves, so the list shows where the build is at a glance.
- "Done" on an item whose check failed.
