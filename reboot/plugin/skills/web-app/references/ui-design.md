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
[`react-client.md`](react-client.md). An MCP UI view shown inside a
host follows the brief, the primary view, color and live data; the
top bar, theme toggle, fonts, logo and favicon are the web app's.

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
Accent: teal #0f8a8a, from the hotel's site (or: none supplied, a neutral default)
Type: Editorial pair, for a warm, hospitable feel (or: the brand's typefaces)
Look: top bar, comfortable, soft
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

### Layout, Density and Style

Pick one of each from the brief and name them on its Look line.

| Layout  | When                                                                       |
| ------- | -------------------------------------------------------------------------- |
| Top bar | The default: up to about six pages; the links sit in the bar               |
| Sidebar | Seven or more pages, or a tool people keep open all day and move around in |

| Density     | Rows     | When                                                    |
| ----------- | -------- | ------------------------------------------------------- |
| Comfortable | 44–56 px | The default; touch screens and occasional use           |
| Compact     | 32–40 px | Dense tables watched all day: operations, finance, logs |

| Style | Radius  | Surfaces                                  | Suits                             |
| ----- | ------- | ----------------------------------------- | --------------------------------- |
| Soft  | 10–14px | Gentle shadow, generous padding           | Hospitality, consumer, community  |
| Crisp | 4–6px   | Hairline borders, no shadow               | Business tools, admin, finance    |
| Bold  | 0–2px   | Strong borders, high contrast, flat fills | Operations, technical, data-heavy |

Each is a few tokens (`--radius`, `--shadow`, `--row-h`, `--pad`), so
a later change of mind is a change of values.

### Lay Out Each Page the Same Way

The navigation (a top bar or a sidebar, with the product name,
account and theme toggle), then a page head (a
headline saying what the page is for, a line on what to do here, the
main action on its right), then the summary, then the controls, then
the content. Data never starts above the page head.

- **Summary:** counts as tiles, label and big number; a tile that
  filters is a button.
- **Controls** on one labeled surface: search, filters, view and sort.
- **Rows** at the density's height; the main text wraps, never cut off;
  identifiers never uppercased.
- **Containment by role:** border and shadow mark separate objects,
  not every block. One type scale, one radius, one shadow.

### Color

Define colors as CSS custom properties (tokens) and use them
everywhere; no raw hex in components. One accent marks primary
actions, selection and a highlighted tile. A brand replaces the whole
family: accent, page, ink, muted text and lines, in both schemes.
With no brand, pick an accent from this palette; each has a shade
for the light scheme and one for the dark, both checked for contrast:

| Accent | Light     | Dark      | Suits                           |
| ------ | --------- | --------- | ------------------------------- |
| Plum   | `#6b3a63` | `#d9a3cd` | Hospitality, beauty, wine       |
| Indigo | `#3346c8` | `#9fb0ff` | Productivity, education         |
| Teal   | `#0e6f72` | `#5fcfcf` | Health, outdoors, sport         |
| Ink    | `#1f4e79` | `#8fbbe6` | Finance, legal, public services |
| Slate  | `#45556b` | `#b0bfd2` | Operations, internal tools      |
| Violet | `#6440c8` | `#b9a6f5` | Creative, community, events     |

Saturated green, amber and red encode exactly one data dimension
(severity, health), as a dot or a pill; every other status is a
neutral pill with text. The accent is never green, amber or red. Keep
contrast high: body text 7:1 or better, secondary text 4.5:1.

Design light and dark, and give the first build a theme toggle: the
OS setting until the user chooses, then remembered per browser. In
the bar it is a small icon button (a sun or a moon for the scheme it
switches to) with an accessible label such as "Switch to dark mode",
never a text button. Inside a menu it is a labeled item, "Dark mode"
or "Light mode".

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
