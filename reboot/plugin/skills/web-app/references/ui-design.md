---
title: Design and Build the UI
impact: HIGH
impactDescription: Without a primary view chosen for the task and the house stylesheet, a first build ships a plain list for every domain and pages styled from scratch
tags: ui, design, primary view, visual, interactive, look, stylesheet, accent, theme toggle, sidebar, logo, favicon, dark mode
---

## Design and Build the UI

The design names each page's primary view and the palette; this is how
to build them. The user's words come first, then an existing design
system (their brand site, a tokens file), then this file. Wiring and
accessible markup are in [`react-client.md`](react-client.md). An MCP
UI view inside a host follows its primary view and the palette; the
navigation, theme toggle, fonts, logo and favicon are the web app's.

### One Signature View

The design named each page's primary view (a list or table with
filters, a board, a chart, a timeline, a plan, a map, a calendar) and
the app's signature view, the one that shows its main question at a
glance (`app/references/design-document.md`); the comp drew it and the
first page leads with it. Build what the design names: the domain's own
shape, its geometry from data, status in colour with a legend, summary
tiles with real numbers, the work done on the view itself (drag to
move, click to open a record and act), every view live from a reader.
Visual means the shape of the data, not decoration: no chart where a
list answers better, no gradient or glow. A spatial view takes the
page's width; a record's detail opens in a drawer or on its own route,
never reflowing the list. When the task is a list, the list stays the
primary view and the signature view leads above it, in the page's
width (a pipeline strip over a CRM's table, a heat calendar over the
bookings): it carries real numbers, updates live, and each mark opens
or filters what it stands for.

**Three dimensions, only where the domain has them,** drawn with CSS 3D
transforms or SVG in isometric projection: real elements, so each room
or rack has its role and its name and the browser scenarios click it,
and no library loads. A WebGL scene (three.js) only when the user asks
for one, loaded after the first record, with a 2D view or a list of the
same data beside it for the scenarios and for screen readers. Either
way the page keeps its budgets in [`vitals.md`](vitals.md): its first
record within 2 seconds, nothing shifting as the view fills.

### What the Eye Lands On

A page is read in one order, and is built in it: its answer first,
then the work, then the rest. The design's **Pages** line says, for
each page, what it leads with, which states carry colour and where the
accent goes; the look review checks each rule below on a screenshot
and fixes it.

- **One figure leads.** The page's question has a number, and it is
  the largest thing on the page after the title: a `stat` tile, or a
  `figure` in the heading's line ("38 ready · 4 waiting"). One a page,
  two when the question has two sides. Counts in 13 px pills or column
  heads lead nothing.
- **The resting state is plain.** In a view that colours status, the
  normal state (ready, done, in stock, on time) has no fill: the panel
  surface and the line. Colour goes to the states that need a person
  (dirty, overdue, leaving today), one hue each, named in the legend;
  the one state the page's question asks for ("which rooms are
  ready?") may take the good colour on its edge, so the answer shows.
  More than a third of a view coloured means the colours are the wrong
  way round (hotel-200's floor plan: 38 of 56 tiles green for "ready").
- **The accent marks one thing.** It marks the primary action and the
  selected state (the current page, a selected stat or cell) and
  nothing else: never a status, never every name that opens something.
  A name that opens is `name`: ink at the title weight, the pointer, an
  underline on hover. (hotel-200: fifteen plum names a page beside one
  plum button, and "occupied" in plum.)
- **Figures large, labels small.** A number read at a glance (a room
  number, a count, a balance, a time) is the display face at 18 or
  28 px with tabular figures (`figure`, `stat .value`), its label 12 or
  13 px and muted beside it. A cell of a plan or grid (`cells`, `cell`)
  is one figure and one word, its state on its left edge, a second
  fact at most a one-letter `corner` mark (K, Q, S), the rest in its
  drawer; two lines of 13 px text in fifty tiles is a list drawn as a
  grid. A plan's rows are its floors or aisles (`plan`, `plan-row`, a
  `plan-label` at the left), each row's count fixed with
  `--cells-cols` so eight rooms stay on one line, never a card per
  row.
- **The first screen holds the view.** At desktop width the page
  head, the leading figure and the whole plan or board are on screen
  together, the last row included; a list may scroll. What doesn't
  fit is too loose (a card per row, a heading per row, padding), not
  too big: fifty-six rooms are seven rows of eight. (hotel-202's comp:
  seven floor cards, each wrapping to two rows, a page four screens
  tall.)
- **Columns are for things that move between them.** Lists side by
  side that nothing moves between (arrivals, in house, departures) are
  not a board: the page's work, what gets an action today, comes first
  and takes the width, what is only watched goes under or beside it as
  a table, and no third of the page stands empty at desktop width. A
  search alone is one row above its list at a field's height, never a
  panel of its own; `filter-panel` is for a search with two or more
  filters.

### Drag and Drop, Wherever Something Moves

Wherever a page moves something, it moves by drag and drop: an item
between stages or lists, a booking to another room or day, a shift
to another person, a card up or down in an order, a file onto the
thing it belongs to. The thing is draggable; every valid target
lights up on pick-up; the drop calls one existing method; a refused
drop snaps back with the rule's reason in one line; the page updates
from its subscription, not from the drop. Reordering is a drag too.
Choosing the new place from a dropdown, a "Move to…" dialog or an
edit form is the fallback, kept beside the drag for keyboard users
and for the scenarios, which click it (`testing-web-app.md`), never
the primary gesture; at phone width, where a drag is awkward, the
fallback shows. Built with the browser's own drag and drop
(`draggable`, `onDragStart`, `onDragOver`, `onDrop`) or pointer
events, no library.

### Whatever Names a Thing Opens It

On every page, a name is the way to the thing it names. A record's
name in a list, a card, a tile, a cell or a sentence opens that
record (its drawer or its route); a person's name opens the person; a
count opens what it counts ("12 rooms" opens those rooms); a status
or a tag narrows the view to it; a date opens that day; a column
header sorts by it; a summary tile opens what it sums; a dashboard
link in the chat opens that object. Nothing that reads like a link
is dead text, and nothing that is one looks like plain text: the
pointer cursor and a hover state say what opens. Each opens the way
the page already does (a drawer for a record, a filter for a status,
a route for a page), never a new tab, and every one is a `<button>`,
`<a href>` or a role the steps know, never a `<div onClick>`, so a
scenario clicks it by its text (`testing-web-app.md`). The first
browser check of a page clicks every name on it once.

Every view a person can narrow (a filter, a selection, a search, an
open drawer) shows that it is narrowed and has a visible way back: an
"All" option or a "Clear" control beside the filter, a close button
and Esc for a drawer. Clicking the same control again is not enough
on its own.

### Interaction Patterns

Six small patterns most staff apps want, each a component the starter
ships in `frontend/web/src/patterns/` with its class in `styles.css`
and its own use written at the top of its file: a hover card
(`HoverCard`) on a record's name in a list, whose body is the record's
reader; a clamp (`Clamp`) for text that is usually a sentence and now
and then an essay; tips (`InfoTip`, `TipWrap`) where a label needs a
sentence of why, never `title=` as the only explanation; a copy button
(`CopyButton`) beside a field people paste elsewhere; avatars
(`Avatar`) wherever a person is named; a job's status (`JobStatus`) on
anything that waits on an outside call, a failure always shown. Use
the component, don't rewrite it, and only where the design has the
case: a hover card on the names a person scans, not on every word.

Company logos, where the design's objects are companies with a
website, are [`company-logos.md`](company-logos.md)'s.

### Nothing Jumps, Every Tap Answers

Every action in a Reboot app is a call to the backend, and every page
fills from a live reader, so two things go wrong that a screenshot
never shows:

- **The page jumps while it loads.** Reserve the space live data will
  fill before it arrives: a list's rows at their real height, a
  figure's box, a board's columns, never a spinner the content then
  replaces at another size. Only what moves untouched counts: a panel
  the user's tap opens may open over the page or into it, since a
  shift within half a second of a tap is not a layout shift. Choose by
  the task: over the page for a quick task closed again (the view keeps
  its width), into the page beside the view for back-and-forth work
  (room after room on a floor plan), the view narrowing to make room
  and the panel below it on a phone.
- **A tap waits for the server.** The tapped control shows the action
  in the same frame (pressed, "Checking in…", disabled against a
  second tap), and the page changes when the reader brings the result;
  nothing on screen waits for the answer before showing that the tap
  was taken. A refusal replaces the pending state with its sentence.

Both are measured, with their budgets, in [`vitals.md`](vitals.md):
layout shift under 0.1, a tap's next paint under 200 ms.

### Build the Look

Every web app starts from one stylesheet, designed and tested once,
in the house look and the palette the design names. Don't design a look
from scratch. The house look is Reboot's own, as the Plugin Browser
uses it: cream paper, navy ink and accent, Space Grotesk over DM Sans,
soft corners, for every domain; the design picks only its palette.

**Not bland.** A page has one strong surface and one
voice: the page head sits in the `brand-band` (`--accent-deep`), with
the stats row overlapping its lower edge (the stylesheet's anatomy);
a brand mark in the accent stands beside the name; the display face
carries the title and every figure; a state that needs a person is
tinted as well as edged. White boxes on a grey field, the page head
loose above them and one typeface at one weight is the template look
the house exists to avoid (hotel-203's comp).

1. The house stylesheet, `theme.tsx`, `backend-check.tsx` and
   `reload-prompt.tsx` arrive with the starter (`render.py --web`,
   the web-app skill's step 1), in `frontend/web/src/`, and its
   `main.tsx` already imports the stylesheet and the three typefaces
   (in `package.json`) and applies a saved theme before the first
   render. Don't read the stylesheet: it is over 4,000 words, and
   every word read is sent again on every later turn.

2. Set the palette the design names, from the project root:
   `python3 '<this skill>/assets/palette.py' sage-teal` (with no name
   it lists them). The palettes: house (Reboot's own: cream paper, navy ink and accent), sand-bronze, sand-brown, sand-orange, sand-gold, olive-grass, sage-teal, slate-blue, slate-iris, mauve-plum and mauve-crimson. Each but house is a gray and
   an accent from Radix Colors: the page, text and lines from the
   gray, the page head's band a soft tint of the accent with the
   accent's darkest step for its text, the accent kept for the primary
   action and the selected state. The design's band and paper come
   with it (`palette.py sage-teal --band deep --paper tinted`): the
   band calm (that tint), deep (the gray's ink) or hue (the accent's
   darkest step, with the tint on it); the paper white or tinted (the
   gray one step up, the panels lifting off it). It rewrites those
   tokens in the light and dark blocks and names the palette, band
   and paper at the stylesheet's top (keep that line: it is the
   colors' license notice). That is the whole of the look's change:
   one of the eleven palettes with a band and a paper. Every
   other token keeps its value unless the user supplied a brand (a
   site or tokens to read); a theme the build invents for the domain
   ("newsprint", "ink on warm paper") is not a brand. Tokens a page
   adds (a set of player colours, a status the domain has) extend the
   stylesheet in the house's terms and change nothing above them.
3. Build the pages from the stylesheet's classes, listed in its
   opening comment (read only that: the file's first 49 lines, never
   the whole file; to see one class's rules, search for it): `topbar`, `brand-band` and `page-head`, `stats`,
   `filter-panel`, `list-card` and `row`, `board`, `cells` and `cell`,
   `feed`, `chart`, `drawer`, `kv`, `pill`, `figure`, `name`,
   `skeleton`, `empty` and the rest. Use its
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
in `web/public/favicon.svg` in the accent's light hex (`palette.py`
updates it), linked from `index.html` in place of Vite's. Set the
page `<title>` to the product name. Write `favicon.svg` (and any other
SVG asset) through Bash, `cat > frontend/web/public/favicon.svg
<<'EOF'`, never with the Write tool: the Claude app opens every SVG or
HTML file the Write tool saves in the Browser pane (hotel-252). Never
open it to check it either: it is seen where it is used, as the mark in
the app's own page and its tab, in the page check's screenshot.

The mark and the name together are always a link to the home page,
`/`, on every page, in the top bar or the sidebar:
`<a href="/" className="brand" aria-label="<Product> home">`, never a
plain `<span>` or `<div>`. It goes home the way the nav links do: with
a router, its `<Link to="/">`; with the path kept in state, an
`onClick` that calls `preventDefault()` and the app's own navigation
to `/`. People click the logo to get back to where they started, so a
logo that does nothing reads as a broken page.

**Check it running.** Look at every page at desktop and phone
(375×812) width, in light and dark. The web app scenarios record
screenshots and open either scheme
([`testing-web-app.md`](../../python/references/testing-web-app.md)).

**Measure what can be measured.** A screenshot looked at quickly lets
uneven layouts through; a check that returns pass or fail doesn't. In
the browser check (step 10), run the plugin's page check on every page
the feature adds or changes, not only the main page, from the project
root with the app running, and fix whatever it reports before the
handoff:

```shell
uv run python '<this skill>/assets/check_page.py' <app URL> '/=.cell' '/guests=.list-card .row' \
  --open '/=.cell.bad' --out "$TMPDIR/checks"
```

Each `PAGE=SELECTOR` is a page's path and one record of its main view;
`--tap` names the page's main action when it isn't opening the first
record, `--open` each drawer or form beyond it, `--as` the development
picker's account (Alice by default). Headless, at desktop (light), the
Claude app's Browser pane width (800, layout only) and phone width
(dark), signed in, it times the page
([`vitals.md`](vitals.md)), and checks that nothing spills out of its
container or is cut off, nothing scrolls sideways, a board's columns
and headers and a plan's rows and cells are each one height, the plan
or board is on the first screen at desktop, no text or control touches
another (at rest, after the tap, with each `--open` target open), and
the console is clean. One line per check, PASS or FAIL with what to
fix; a screenshot per page and width in `--out`. While fixing what it
found, rerun it with `--quick`: one load a page, not timed, a third of
the time (hotel-260: ten full runs, 5 minutes). The last run before
the handoff is the full one. Never write a check
script of your own for these: the plugin's is tested, and retyping it
costs every build minutes.

**A button's visible label is short:** "Cancel", "Remove", "Edit".
What tells one row's button from the next ("Cancel invitation for
carlos@example.com") goes in its `aria-label`, which is its accessible
name, so a scenario still clicks it by that name; written out on the
button, it crowds the row it sits in (vet-1's Team page).

Never: browser default styling (an unstyled `<button>`, `<select>` or
`<input>`), `alert()`, `confirm()` or `prompt()` (they block the
scenarios too), a page broken at phone width or in either scheme, a
placeholder as a control's only label, a resting state filled with
colour, the accent on a status or on every name, a page that leads
with nothing, or a layout that doesn't line up: the columns of a
board, and the rows and cells of a grid or floor plan, are each the
same height, headers too, and a card or cell is only as tall as its
contents, never stretched to fill spare space; or two pieces of text
or controls that touch, stacked or side by side. The stylesheet's
classes keep their distances (a drawer's sections, a form's fields and
its buttons, a plan's cells, tabs, a funnel's segments); a page that
spaces things by hand is where the page check finds them touching.
