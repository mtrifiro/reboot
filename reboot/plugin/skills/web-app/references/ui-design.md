---
title: Design the UI
impact: HIGH
impactDescription: Without a design brief and a primary view chosen for the task, a first build ships unstyled controls, a plain list for every domain, and pages that read as a prototype
tags: ui, design, layout, visual, interactive, brand, color, contrast, dark mode, responsive, skeleton, empty state
---

## Design the UI

The aim is a UI a person can scan and operate. The user's words come
first, then an existing design system (their brand site, a tokens
file), then this file. Wiring and accessible markup are in
[`react-client.md`](react-client.md).

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

Write five lines into the design before any page:

```
Who: front-desk staff, on a desktop at the desk, between guests
Task: see which rooms are ready and assign arriving guests
Question: which rooms can take a guest right now?
Accent: teal #0f8a8a, from the hotel's site (or: none supplied, a neutral default)
Type: Editorial pair, for a warm, hospitable feel (or: the brand's typefaces)
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

### Lay Out Each Page the Same Way

Top bar (product name, account, theme toggle), then a page head (a
headline saying what the page is for, a line on what to do here, the
main action on its right), then the summary, then the controls, then
the content. Data never starts above the page head.

- **Summary:** counts as tiles, label and big number; a tile that
  filters is a button.
- **Controls** on one labeled surface: search, filters, view and sort.
- **Rows** about 44 to 56 px; the main text wraps, never cut off;
  identifiers never uppercased.
- **Containment by role:** border and shadow mark separate objects,
  not every block. One type scale, one radius, one shadow.

### Color

Define colors as CSS custom properties (tokens) and use them
everywhere; no raw hex in components. One accent marks primary
actions, selection and a highlighted tile. A brand replaces the whole
family: accent, page, ink, muted text and lines, in both schemes.

Saturated green, amber and red encode exactly one data dimension
(severity, health), as a dot or a pill; every other status is a
neutral pill with text. The accent is never green, amber or red. Keep
contrast high: body text 7:1 or better, secondary text 4.5:1.

Design light and dark, and give the first build a theme toggle in the
top bar: the OS setting until the user chooses, then remembered per
browser.

### Type

Pick one set from the brief unless the brand has its own typefaces,
and say why in the brief.

| Pair      | Headings            | Text            | Mono           | Suits                                   |
| --------- | ------------------- | --------------- | -------------- | --------------------------------------- |
| Friendly  | Bricolage Grotesque | Instrument Sans | JetBrains Mono | Teams, community, everyday tools        |
| Neutral   | Inter Tight         | Inter           | IBM Plex Mono  | Business tools, admin, finance          |
| Editorial | Fraunces            | Source Sans 3   | IBM Plex Mono  | Hospitality, food, retail, publishing   |
| Technical | Space Grotesk       | IBM Plex Sans   | IBM Plex Mono  | Operations, monitoring, developer tools |
| Warm      | DM Serif Display    | DM Sans         | DM Mono        | Health, education, personal services    |

Install them from npm, never a font CDN:
`npm install @fontsource/fraunces @fontsource/source-sans-3 @fontsource/ibm-plex-mono`,
then import the weights used in `main.tsx`
(`import "@fontsource/fraunces/500.css";`) and name the families in
three tokens, `--font-display`, `--font-text` and `--font-mono`.
Headings use weight 500 or 600.

### Logo and Favicon

- **The logo** is an inline SVG component beside the product name in
  the top bar: one simple mark from the domain (a table seen from
  above, a key, a leaf), filled with `var(--accent)` so it follows a
  restyle and the dark scheme.
- **The favicon** is the same mark as `web/public/favicon.svg`,
  linked from `index.html` with
  `<link rel="icon" type="image/svg+xml" href="/favicon.svg" />`,
  replacing Vite's default. It can't read CSS tokens, so it holds the
  accent's current hex.
- Set the page `<title>` to the product name.

### Live Data

Loading shows skeletons shaped like the content, never "Loading…" or
a bare spinner. An empty list says what to do next. A running workflow
shows as a pill on its object.

### Check It Running

Look at every route at desktop (1440×900) and phone (375×812) width,
light and dark. The web app scenarios record screenshots and open
either scheme ([`testing-web-app.md`](../../python/references/testing-web-app.md));
set Playwright's viewport for the phone. Compute contrast with a
script, not by eye.

### Never

- Browser default styling: an unstyled `<button>`, `<select>` or
  `<input>`, or the default serif.
- `alert()`, `confirm()` or `prompt()`: they block the scenarios too.
- A page broken at phone width (16 px gutters, wide tables in their
  own horizontal scroll) or in either color scheme.
- A placeholder as a control's only label.
- Page links in a row that scrolls with its scrollbar hidden; wrap
  them, then fold them into a menu.
- Vite's default favicon or page title.
- A restyle that appends a block redefining the tokens instead of
  changing their values: a later block silently wins over the edit.
