---
title: Build the Look
impact: MEDIUM
impactDescription: Without the house stylesheet a build styles every page from scratch and ships browser defaults, an off-palette accent or Vite's favicon
tags: ui, look, stylesheet, palette, accent, theme toggle, sidebar, density, logo, favicon, dark mode
---

## Build the Look

Every web app starts from the house look: one stylesheet, designed
and tested once, in the accent the brief names. Don't design a look
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

2. Set the accent the brief names, from the project root:
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
