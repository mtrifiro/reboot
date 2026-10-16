---
name: design
description: Change how a Reboot web app looks, with the user choosing at each step - its accent color or a brand's colors, the page and text tones, the typefaces, the corners, the layout (top bar or sidebar), density, and the logo. Shows each set of choices as a preview page in the app's own pieces (light and dark side by side), applies the one picked to the house stylesheet's tokens with an undo, then shows the real app and checks contrast and layout. Use when the user asks to change the look, colors, theme, fonts, brand, style or feel of an app that is already built, or to make it match their brand or site. Not for what the app keeps track of, its rules or its features (the feature skill), and not during a build's first feature, where the look is picked for the user.
argument-hint: [what to change, e.g. "make it teal" or "match acme.com"]
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion
---

# design — Change the App's Look With the User

Every Reboot web app is built in the house look: one stylesheet,
`frontend/web/src/styles.css`, whose colors, typefaces and corners are
tokens (`web-app/references/ui-design.md`, "Build the Look"). This
skill changes those tokens' values with the user, one choice at a
time, each seen before it is applied and each easy to undo. The pages
never change for a new look: they use the tokens, so the whole app
follows.

The script that does the work is [`assets/look.py`](assets/look.py)
(standard library only), run from the project root:

| Command | Does |
| --- | --- |
| `python3 <this skill>/assets/look.py show` | The look now, and the choices |
| `python3 <this skill>/assets/look.py preview <kind> <a,b,c>` | Writes `frontend/web/public/look-preview.html`, each choice lettered and drawn as a piece of the app in light and dark |
| `python3 <this skill>/assets/look.py set <kind> <choice>` | Applies one, after saving the files it touches; removes the preview; checks contrast |
| `python3 <this skill>/assets/look.py undo` | Puts back the files from before the last `set` |
| `python3 <this skill>/assets/look.py check` | The contrast check alone |

The kinds and their choices:

- **accent:** teal, cyan, blue, indigo, violet, purple, plum, rose, or
  a brand's hex (`#0a6e5c`; add `--dark #5fd0bd` to give the dark
  scheme's own). From a hex, the script makes the whole family (deep
  shade for the top bar, pale tint for selection, both schemes) and
  darkens or lightens it until it is readable.
- **neutrals:** cool (the house default), warm, grey, white.
- **type:** house, classic (a serif for headings over Inter), plain
  (Inter throughout), geometric, bookish. Each is an
  `@fontsource-variable` package; `set type` rewrites `main.tsx`'s
  font imports and prints the `npm install` to run in `frontend/`.
- **corners:** sharp, soft (the house default), round.

## The Conversation

The user sees the app, not the stylesheet. Say every choice in their
words ("a warmer page", "a serif for the headings"), never token
names, hex values alone, or file paths. In the Claude app, questions
are dialogs (`AskUserQuestion`), and pages open in its Browser pane;
elsewhere, give the link.

### 1. Find the app and see it running

From the project root, run `look.py show`. If there is no
`frontend/web/src/styles.css`, the app has no web app in the house
look yet: say so in one line and stop (the `app` skill builds one).
The app must be running to show anything: if it isn't, start it with
the [`run` skill](../run/SKILL.md). Its web address is the one the
handoff gave (often `http://localhost:5173`).

Say what the look is now in one line, in words: "Maison Desk is in
plum, on a cool grey page, with a characterful grotesque for headings
and soft corners."

### 2. Ask what to change, unless they said

When the user's words already say what to change ("make it teal",
"use our brand, #0a6e5c", "a serif for the headings", "match
acme.com"), go straight to it. Otherwise one dialog:

- **What would you like to change about the look?** (multiple
  choice, several allowed)
  - "Color": "The accent: buttons, the top bar, selection."
  - "Page and text": "A cooler, warmer or plainer page behind it all."
  - "Typefaces": "The headings and text."
  - "Corners": "Sharper or rounder."

The dialog's own free answer takes anything else: the layout, how
dense the lists are, the logo, a brand ("Beyond the tokens", below).

### 3. Show the choices, then ask

For each thing to change, in the order they were picked:

1. Pick two to four choices that fit what the user said and the app's
   domain, the one now first when it is a fair choice: a calm blue or
   teal for a clinic, a warm page and a serif for a restaurant or a
   bookshop. A brand's color or a site's colors are a choice of their
   own, beside the nearest house palettes.
2. Say one line ("Here are three accents on the front desk's page,
   light and dark."), run `look.py preview <kind> <choices>`, and open
   `<web address>/look-preview.html` in the Browser pane.
3. One dialog: **Which <accent / page tone / typefaces / corners>?**,
   each option its letter and name as the label ("A: teal") and what
   it is like as the description, last "Keep it as it is". A choice
   described in the free answer gets a new preview.

### 4. Apply it and show the real app

Run `look.py set <kind> <choice>`. For typefaces, run the `npm
install` it prints, in `frontend/`. The dev server reloads the page on
its own: open the app's main page in the Browser pane and say in one
line what changed ("The app is in teal now, the top bar and buttons
with it.").

When the contrast check fails (exit 3), say which text would be hard
to read, in words ("white on the new green buttons"), never leave it
so, and offer the nearest shade that passes: for a brand color, a
darker or lighter shade of it given with `--dark`, or a hex the user
approves. When a note says the accent is close to green, amber or
red, say once that status colors (a late arrival's pill) may read as
the accent, and that a different shade avoids it.

Then one dialog: **Keep this look?** "Keep it" / "Undo it": "Put back
how it was." On "Undo it", run `look.py undo`, reload the pane, and go
back to step 3's choices. Several changes in a row each get their own
undo.

### 5. When the user keeps it

1. Check the layout: a typeface or corner change moves text. Run the
   pass-or-fail checks in `web-app/references/ui-design.md`
   ("Measure what can be measured"), headless, at desktop and phone
   width, and fix what they report before saying it is done.
2. Update the accent's sentence in `design/design.md` (its opening
   names the accent), and the look's other choices beside it, in a
   few words.
3. Make sure `.gitignore` has `frontend/web/.look-history/` and
   `frontend/web/public/look-preview.html`.
4. When the project is a git repository, commit only the files the
   change touched (`styles.css`, `main.tsx`, `favicon.svg`,
   `package.json` and its lock file, `design/design.md`,
   `.gitignore`), with the message "Look: <what changed>". Undo after
   this is `git revert` of that commit, said in words.
5. One closing line: what the app looks like now and that any of it
   can change again. No question.

## Beyond the Tokens

These change the pages, not the tokens, so `look.py` doesn't do them.
Say the change in one line, make it as
`web-app/references/ui-design.md` says, and show it in the pane:

- **Layout:** the top bar, or the sidebar for seven or more pages or
  a tool kept open all day ("Layout" in `ui-design.md`).
- **Density:** `density-compact` on a list or a page, for rows watched
  all day.
- **Logo and name:** the inline SVG mark and the product name, the
  same mark in `favicon.svg` ("Logo and favicon").
- **A brand's site or style guide:** read its colors (theme color,
  buttons, links, header) and typefaces, then offer them as a choice
  beside the nearest house ones. A brand's own typeface that isn't in
  the type list is set by hand in `--font-display`, `--font-text` and
  `--font-mono` in the light `:root` block, with its `@fontsource`
  package when there is one ("A brand" in `ui-design.md`).
- **A whole new look the tokens can't reach** (a different shape of
  page): this is a frontend change, made through the
  [`feature` skill](../feature/SKILL.md)'s page step, never by
  restyling page by page here.

## Never

- Never read `styles.css` whole: it is over 4,000 words and every word
  read is sent again on each later turn. `look.py` changes it; to see
  one class's rules, search for it.
- Never add a block that redefines tokens after the first ones (a
  later block silently wins), never rename a token, and never put a
  raw hex in a page: change the token's value in place.
- Never ship text that fails the contrast check, and never change one
  scheme without the other: every choice is shown and applied in light
  and dark.
- Never change the look during a build's first feature to ask about
  it: the build picks the accent and says it is easy to change; this
  skill is for afterwards, when the user asks.
- Never open the preview or the app in the user's own browser in the
  Claude app: the Browser pane, or a link elsewhere.
