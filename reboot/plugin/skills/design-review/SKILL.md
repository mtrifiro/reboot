---
name: design-review
description: Review how a Reboot web app looks, then change it with the user. First a design review of the running app - every main page at desktop and phone width, light and dark, measured for contrast, alignment, overflow and touching controls, and judged against the house design rules and the app's own users - with findings and what's right. Then the changes the user picks - its accent or a brand's colors, page and text tones, typefaces, corners, layout, density, logo - each shown as a preview in the app's own pieces before it is applied to the house stylesheet's tokens, with an undo. Use when the user asks to review, critique, improve or change the look, colors, theme, fonts, brand, style or feel of an app that is already built. Not for what the app keeps track of or its rules (the domain-review and feature skills), and not during a build's first feature, where the look is picked for the user.
argument-hint: [what to change, e.g. "make it teal" or "match acme.com"]
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion
---

# design-review — Review the App's Look, Then Change It With the User

Every Reboot web app is built in the house look: one stylesheet,
`frontend/web/src/styles.css`, whose colors, typefaces and corners are
tokens (`web-app/references/ui-design.md`, "Build the Look"). This
skill first reviews how the app looks, so its advice rests on what the
pages actually do, then changes those tokens' values with the user, one choice at a
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

- **look:** house, ledger or boutique: the tones, typefaces, corners
  and row density together, as
  [`web-app/references/ui-design.md`](../web-app/references/ui-design.md)
  ("Build the Look") describes them. `set look` also rewrites
  `main.tsx`'s font imports and `package.json`'s font packages; run
  `npm install` in `frontend/` after it.
- **accent:** one of the accents
  [`web-app/references/ui-design.md`](../web-app/references/ui-design.md)
  lists, or a brand's hex (`#0a6e5c`; add `--dark #5fd0bd` to give the
  dark scheme's own). From a hex, the script makes the whole family (deep
  shade for the top bar, pale tint for selection, both schemes) and
  darkens or lightens it until it is readable.
- **neutrals:** cream (the house default: cream page, navy ink),
  cool, warm, grey, white.
- **type:** house, classic (a serif for headings over Inter), plain
  (Inter throughout), geometric, ledger (Space Grotesk for headings
  and figures over Inter), bookish. Each is an
  `@fontsource-variable` package; `set type` rewrites `main.tsx`'s
  font imports and `package.json`'s font packages; run `npm install`
  in `frontend/` after it.
- **corners:** sharp, soft (the house default), round.

## The Conversation

The user sees the app, not the stylesheet. Say every choice in their
words ("a warmer page", "a serif for the headings"), never token
names, hex values alone, or file paths. In the Claude app, questions
are dialogs (`AskUserQuestion`), and pages open in its Browser pane;
elsewhere they open in the user's browser. Either way, every page
shown also gets its link in the message.

### 1. Find the app and see it running

From the project root, run `look.py show`. If there is no
`frontend/web/src/styles.css`, the app has no web app in the house
look yet: say so in one line and stop (the `app` skill builds one).
The app must be running to show anything: if it isn't, start it with
the [`run` skill](../run/SKILL.md). Its web address is the one the
handoff gave (often `http://localhost:5173`).

Say what the look is now in one line, in words: "Maison Desk is in
plum, on a cream page, with Space Grotesk for headings
and soft corners."

### 2. Review the look before advising anything

No advice, and no choices offered, before the review: it is what
every suggestion rests on. One line first: "Reviewing how <app> looks:
every page at desktop and phone width, light and dark."

1. **Capture.** In a headless browser, never the Browser pane: a short
   Playwright script (`uv run python`, `playwright.sync_api`) that
   signs in through the development picker as the web app's scenarios
   do (`python/references/testing-web-app.md`), as each role the app
   has, and screenshots every page in its navigation at 1440×900 and
   375×812, light and dark (`data-theme` on `<html>`), into
   `frontend/web/.look-review/`. Look at each screenshot.
2. **Measure.** On each page and width, run the pass-or-fail scripts
   in `web-app/references/ui-design.md` ("Measure what can be
   measured": uneven columns, spill, clipped text, touching controls,
   with every drawer and form opened), and `look.py check` for
   contrast in both schemes. Search the pages for raw colors
   (`#` followed by hex, `rgb(`) outside `styles.css`.
3. **Judge,** against `ui-design.md` and the app's users from
   `design/design.md`:
   - Does each page's primary view fit its task (a board, a floor
     plan, a calendar), and does the eye land first on the page's main
     question: the figure the design's page line says it leads with
     (`ui-design.md`, "What the Eye Lands On")?
   - Is color doing one job: the accent on the primary action and the
     selected state only, never on a status or on every name; status
     colors on the states that need a person and none on the resting
     state; neutrals for the rest?
   - Do the type sizes keep to the scale, and the spacing to the steps?
     Do repeated things (cards, rows, columns) line up?
   - Does it hold at phone width and in dark mode, with nothing cut
     off or unreachable?
   - Does the look suit the domain and the people (a front desk
     watched all day, a guest booking on a phone)?
4. **Say it,** one message headed **Design review: <app>**:
   - **Verdict,** two or three sentences: what works, and the one
     thing that would most improve it.
   - **Findings,** at most seven, most visible first, each its title
     the consequence in plain words ("**1. The room board's late
     arrivals look like selections.**"): what the user sees, on which
     page, width and scheme (its screenshot linked); why it matters,
     with a measured figure where there is one (a contrast ratio, a
     clipped label); the fix, and whether it is a token change
     (`look.py`) or a page change; what it costs.
   - **What's right,** one line each.

   Write the same to `design/look-review.md`, with the screenshots
   linked.

When the user already named a change ("make it teal"), the review
still runs, said in a few lines, and anything it found that the change
touches (a status color the new accent would clash with, a label that
would clip in a wider typeface) goes with the choices.

### 3. Ask what to change

One dialog, several answers allowed:

- **What should I change?** The top findings, each its title as the
  label and its fix as the description, the first marked
  "(Recommended)" (up to three), and "The look another way": "Color,
  page tones, typefaces or corners, from previews." No "None" option:
  in a list of checkboxes, ticking nothing is none. A skipped dialog,
  or an answer that wants nothing changed, changes nothing.

A finding chosen is fixed as it says: a token change goes through
step 4's preview, a page change is made as "Beyond the Tokens" says,
then shown in the pane. "The look another way" gets one more dialog:

- **What would you like to change about the look?** (several allowed)
  - "The whole look": "House, Ledger or Boutique: tones, typefaces,
    corners and density together."
  - "Color": "The accent: buttons, the top bar, selection."
  - "Page and text": "A cooler, warmer or plainer page behind it all."
  - "Typefaces": "The headings and text."
  - "Corners": "Sharper or rounder."

The free answer takes anything else: the layout, how dense the lists
are, the logo, a brand ("Beyond the Tokens", below). When nothing is
chosen, one line pointing to `design/look-review.md`, then stop.

**Never while a build is working in the project.** Before changing a
file, check that nothing else is: no test run in progress
(`tests/.suite-running`, a `pytest` process in the project), and no
other session's transcript for the project written to in the last few
minutes. If one is, say so in one line and wait for it to finish, or
ask the user: two sessions editing one app break each other's runs.

### 4. Show the choices, then ask

For each thing to change, in the order they were picked:

1. Pick two to four choices that fit what the user said and the app's
   domain, the one now first when it is a fair choice: a calm blue or
   teal for a clinic, a warm page and a serif for a restaurant or a
   bookshop. A brand's color or a site's colors are a choice of their
   own, beside the nearest house palettes.
2. Run `look.py preview <kind> <choices>`, then **always show it and
   always give its link**, before the dialog:
   - open `<web address>/look-preview.html` where the user sees it:
     the Browser pane in the Claude app; elsewhere, their browser
     (`open <url>` on macOS, `xdg-open` on Linux, `start` on Windows);
   - and in the same message, one line with the link itself: "Here
     are three accents on the front desk's page, light and dark:
     [the previews](<web address>/look-preview.html)."

   A dialog asking to choose from previews the user hasn't been shown
   is never sent.
3. One dialog: **Which <look / accent / page tone / typefaces / corners>?**,
   each option its letter and name as the label ("A: teal") and what
   it is like as the description, last "Keep it as it is". A choice
   described in the free answer gets a new preview.

### 5. Apply it and show the real app

Run `look.py set <kind> <choice>`. For a look or typefaces, run
`npm install` in `frontend/` after it. The dev server reloads the page on
its own: open the app's main page where the user sees it (the Browser
pane, or their browser, as step 4 says), and say in one line what
changed, with the page's link: "The app is in teal now, the top bar
and buttons with it: [the room board](<web address>/desk)." The
**Keep this look?** dialog never comes before the user has been
shown the changed app.

When the contrast check fails (exit 3), say which text would be hard
to read, in words ("white on the new green buttons"), never leave it
so, and offer the nearest shade that passes: for a brand color, a
darker or lighter shade of it given with `--dark`, or a hex the user
approves. When a note says the accent is close to green, amber or
red, say once that status colors (a late arrival's pill) may read as
the accent, and that a different shade avoids it.

Then one dialog: **Keep this look?** "Keep it" / "Undo it": "Put back
how it was." On "Undo it", run `look.py undo`, reload the pane, and go
back to step 4's choices. Several changes in a row each get their own
undo.

### 6. When the user keeps it

1. Check the layout: a typeface or corner change moves text. Run the
   pass-or-fail checks in `web-app/references/ui-design.md`
   ("Measure what can be measured"), headless, at desktop and phone
   width, and fix what they report before saying it is done.
   After a page change, also run the web app's browser scenarios
   (`uv run pytest -m browser`, as the `feature` skill says): they
   read the page's visible text, so a shortened label or a moved
   button can break a rule's proof. A scenario that relied on the old
   text means the change isn't done, never that the scenario changes.
2. Update the accent's sentence in `design/design.md` (its opening
   names the accent), and the look's other choices beside it, in a
   few words.
3. Make sure `.gitignore` has `frontend/web/.look-history/` and
   `frontend/web/public/look-preview.html` and
   `frontend/web/.look-review/`.
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
