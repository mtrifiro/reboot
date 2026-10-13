---
title: Design the UI
impact: HIGH
impactDescription: Without a design brief and a primary view chosen for the task, a first build ships unstyled controls, a plain list for every domain, and pages that read as a prototype
tags: ui, design, brief, primary view, visual, interactive, brand, look
---

## Design the UI

The aim is a UI a person can scan and operate. The user's words come
first, then an existing design system (their brand site, a tokens
file), then this file. Wiring and accessible markup are in
[`react-client.md`](react-client.md); building the look is in
[`ui-look.md`](ui-look.md). An MCP UI view shown inside a host
follows the brief, the primary view and the accent; the navigation,
theme toggle, fonts, logo and favicon are the web app's.

### Highly Visual and Interactive by Default

Unless the user asks for plain, the first build draws the domain's
own shape as its primary view: a floor plan of the rooms, a board of
the orders, a timeline of the bookings, a calendar of the shifts.
Status shows in color, with a legend; summary tiles carry real
numbers. The work happens on that view: drag to move, click to open
a record and act, edit in place. Every view updates live, since a
Reboot reader pushes each change to the page. Visual means the shape
of the data, not decoration: no chart where a list answers better,
no gradient or glow.

### Start with a Brief

Write these lines into the design before any page:

```
Who: front-desk staff, on a desktop at the desk, between guests
Task: see which rooms are ready and assign arriving guests
Question: which rooms can take a guest right now?
Accent: plum, warm and quiet for a boutique hotel (or: the brand's, from its site)
```

Look for a brand first: the user's words, a tokens file, the
product's site, the organization's site. Read a site's computed
styles in a browser, never from memory. With no brand, say so; never
name a source nobody gave.

### Pick the Primary View by Task

| Task                                 | Primary view                         |
| ------------------------------------ | ------------------------------------ |
| Triage, lookup, review of many items | A grouped list or table with filters |
| A few items moving through stages    | A board                              |
| Amounts over time                    | A chart                              |
| Events over time                     | A timeline                           |
| Places and dates                     | A floor plan, a map, a calendar      |

A spatial view takes the page's width, its geometry from data. A
drag calls one existing method per drop, lights the target first and
snaps a refused drop back; keep a button for keyboard users. A
record's detail opens in a drawer or on its own route, never
reflowing the list.

### Name the Accent in the Brief

Every web app uses the house look ([`ui-look.md`](ui-look.md)), so
the look's one choice is the accent: teal, cyan, blue, indigo, violet,
purple, plum or rose. Pick one that suits the domain and say why in a
few words; keep it off green, amber and red, which mean status. A
brand's own colors and typefaces replace the house look. Name the
layout too when it isn't the default top bar: a sidebar for seven or
more pages or a tool kept open all day.
