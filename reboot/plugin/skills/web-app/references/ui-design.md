---
title: Design and Build the UI
impact: HIGH
impactDescription: Without a primary view chosen for the task and the house stylesheet, a first build ships a plain list for every domain and pages styled from scratch
tags: ui, design, primary view, visual, interactive, look, stylesheet, accent, theme toggle, sidebar, logo, favicon, dark mode
---

## Design and Build the UI

The design names each page's primary view and the accent; this is how
to build them. The user's words come first, then an existing design
system (their brand site, a tokens file), then this file. Wiring and
accessible markup are in [`react-client.md`](react-client.md). An MCP
UI view inside a host follows its primary view and the accent; the
navigation, theme toggle, fonts, logo and favicon are the web app's.

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

Every view a person can narrow (a filter, a selection, a search, an
open drawer) shows that it is narrowed and has a visible way back: an
"All" option or a "Clear" control beside the filter, a close button
and Esc for a drawer. Clicking the same control again is not enough
on its own.

### Build the Look

Every web app starts from the house look: one stylesheet, designed
and tested once, in the accent the design names. Don't design a look
from scratch.

1. Copy `assets/styles.css` and `assets/theme.tsx` from this skill
   into `frontend/web/src/`. In `main.tsx`, import the stylesheet and
   its typefaces, and apply a saved theme before the first render:

   ```tsx
   import "@fontsource-variable/bricolage-grotesque";
   import "@fontsource-variable/instrument-sans";
   import "@fontsource-variable/jetbrains-mono";
   import "./styles.css";
   import { applySavedTheme } from "./theme";

   applySavedTheme();
   ```

   Install the three packages:
   `npm install @fontsource-variable/bricolage-grotesque @fontsource-variable/instrument-sans @fontsource-variable/jetbrains-mono`.

2. Set the accent the design names, from the project root:
   `python3 <this skill>/assets/accent.py teal` (with no name it lists
   the palettes: teal, cyan, blue, indigo, violet, purple, plum, rose).
   It rewrites the accent's family in the light and dark blocks.
3. Build the pages from the stylesheet's classes, listed in its
   opening comment: `topbar`, `brand-band` and `page-head`, `stats`,
   `filter-panel`, `list-card` and `row`, `board`, `feed`, `chart`,
   `drawer`, `kv`, `pill`, `skeleton`, `empty` and the rest. Use its
   tokens, never raw hex. Extend the stylesheet when a page needs
   something new, in the same tokens.

**Layout.** A top bar by default. For seven or more pages, or a tool
people keep open all day, use the sidebar layout: `<div class="shell
sidebar">` holding an `<aside class="sidebar-nav">` and a
`<div class="shell-main">`; it folds into a top bar on narrow screens.
For dense tables watched all day, add `density-compact` to the list or
the page.

**Theme toggle.** `ThemeToggle` from `theme.tsx`: a small sun or moon
icon in the bar or the sidebar, with an accessible label. In a menu,
spell it out as "Dark mode" or "Light mode" instead.

**A brand** replaces the house look: set its colors in the accent's
family and the page, ink, muted and line tokens, in `:root` and both
dark blocks, and its typefaces in `--font-display`, `--font-text` and
`--font-mono`. Change the values in place; never append a block that
redefines them, since a later block silently wins.

**Logo and favicon.** A simple mark from the domain beside the product
name, as an inline SVG filled with `var(--accent)`. The same mark goes
in `web/public/favicon.svg` in the accent's light hex (`accent.py`
updates it), linked from `index.html` in place of Vite's. Set the
page `<title>` to the product name.

**Check it running.** Look at every page at desktop and phone
(375×812) width, in light and dark. The web app scenarios record
screenshots and open either scheme
([`testing-web-app.md`](../../python/references/testing-web-app.md)).

Never: browser default styling (an unstyled `<button>`, `<select>` or
`<input>`), `alert()`, `confirm()` or `prompt()` (they block the
scenarios too), a page broken at phone width or in either scheme, or a
placeholder as a control's only label.
