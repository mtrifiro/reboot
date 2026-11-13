---
name: look
description: "Change how a built Reboot web app looks: the action colour ('make it teal'), the page's tones, typefaces, corners, status colours, a brand to match ('match acme.com'), or a page's layout, each previewed first, with an undo; and review the look first (every page, from its browser scenarios' screenshots and at phone width, judged against the frontend skill's rules and measured for contrast). Works in either kind of web app (tokens.css, or the older house look's styles.css). Use when the user asks to change or review the look, colours, fonts, brand or style ('/reboot:look'). Not for the structure, the domain model or the tests (the review skill)."
argument-hint: '[optional: what to change, e.g. "make it teal" or "match acme.com"; every page by default]'
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion
---

# look — Change How the App Looks, With the User

A web app takes every colour, corner and typeface from one file of
tokens, in one of two kinds:

- **`frontend/web/src/tokens.css`**: built by the `frontend` skill
  ([`visual-interactive.md`](../frontend/references/visual-interactive.md),
  "The tokens"). One light scheme, system typefaces. Its script is
  [`assets/look.py`](assets/look.py).
- **`frontend/web/src/styles.css`**: the older house look, light and
  dark, its typefaces installed from `@fontsource`. Its script is
  [`assets/look-house.py`](assets/look-house.py) ("An App in the House
  Look", below).

This skill first reviews how the app looks, so its
advice rests on what the pages actually do, then changes the tokens'
values with the user, one choice at a time, each seen before it is
applied and each easy to undo. A token change reaches every page; a
page's own problem is fixed in the page.

Both scripts are standard library only, run from the project root,
with the same commands; `<look>` below is the one for the app's kind:

| Command | Does |
| --- | --- |
| `python3 <look> show` | The look now, and the choices |
| `python3 <look> check` | The contrast of every pair the pages draw text on, status colours included |
| `python3 <look> preview <kind> <a,b,c>` | Writes `frontend/web/public/look-preview.html`: each choice lettered and drawn as a piece of the app, with the app's own tokens |
| `python3 <look> set <kind> <choice>` | Applies one, after saving the files it touches; removes the preview; checks contrast (exit 3 on a failure) |
| `python3 <look> undo` | Puts back the files from before the last `set` |

For `tokens.css`, the kinds: **action** (a named colour, or a brand's hex, darkened until
its label reads), **neutrals** (warm, cream, cool, grey, white),
**type** (system, serif headings, rounded, humanist, book; system faces,
nothing to install), **corners** (sharp, soft, round). A status colour
is changed by hand, in place, in `tokens.css` (step 5).

## The Conversation

The user sees the app, not the stylesheet. Say every choice in their
words ("a warmer page", "a serif for the headings"), never token names,
hex values alone, or file paths. In the Claude app, questions are
dialogs (`AskUserQuestion`) and pages open in its Browser pane;
elsewhere, in the user's browser. Every page shown also gets its link
in the message.

### 1. Find the app and see it running

From the project root, find the app's kind: `frontend/web/src/tokens.css`
→ `look.py`; `frontend/web/src/styles.css` → `look-house.py`. Run its
`show`. With neither, there is no web app to review (an MCP App's UIs
are the host's to style): say so in one line and stop. With a web app
styled some other way, review it all the same (step 2) and make the
changes by hand in its stylesheet, saying once that there are no
previews or one-step undo for it.
The app must be running to show anything: if it isn't, start it with
the [`run` skill](../run/SKILL.md). Say what the look is now in one
line, in words: "Taskboard is in deep teal on a warm page, with a
serif for headings and soft corners."

### 2. Review the look before advising anything

No advice, and no choices offered, before the review. One line first:
"Reviewing how <app> looks: every page, at desktop and phone width."

1. **See every page.** Read the screenshots the browser scenarios
   recorded (`tests/*.recordings/**/*.png`, the Read tool, a feature's
   in parallel in one turn), as the
   [`frontend` skill](../frontend/SKILL.md)'s "Reviewing a web app's
   pages" does. With no recordings (an older app), or for phone width,
   a short Playwright script
   (`uv run python`, `playwright.sync_api`, headless, never the Browser
   pane) that signs in as the scenarios do
   ([`testing-web-app.md`](../frontend/references/testing-web-app.md))
   and screenshots each page of the navigation (at 1440×900 when there
   were no recordings, and at 375×812) into
   `frontend/web/.look-review/`. Look at each.
2. **Measure.** `<look> check` for contrast. Search the pages for raw
   colours and sizes (`#` and hex, `rgb(`, a `px` value) outside the
   token file: pages use tokens only.
3. **Judge,** against `visual-interactive.md` and the frontend skill's
   page review, and the app's people from `AGENTS.md` and the features:
   - Is each feature's view the one its things want (a board, a
     timeline, a plan, cards, a chart), and does the eye land first on
     the page's main question?
   - Is colour doing one job: the action colour on actions and the
     selected thing only; one status colour per state, each distinct
     at a glance and readable on its tint; neutrals for the rest?
   - Is it styled throughout (no browser defaults), one app across
     pages (spacing, type sizes, buttons, tables), with nothing
     overlapping, clipped or running off the page?
   - Does it hold at phone width, with nothing cut off or unreachable?
   - Does the look suit the domain and the people (a board watched all
     day, a client on a phone)?
4. **Say it,** one message headed **UI review: <app>**:
   - **Verdict,** two or three sentences: what works, and the one
     thing that would most improve it.
   - **Findings,** at most seven, most visible first, each titled with
     the consequence in plain words ("**1. A blocked task's label
     is hard to read.**"): what the user sees, on which page and width
     (its screenshot linked); why it matters, with a measured figure
     where there is one (a contrast ratio); the fix, and whether it is
     a token change or a page change; what it costs.
   - **What's right,** one line each.

   Write the same to `design/look-review.md`, the screenshots linked.

When the user already named a change ("make it teal"), the review still
runs, said in a few lines, and whatever it found that the change
touches goes with the choices.

### 3. Ask what to change

One dialog, several answers allowed:

- **What should I change?** The top findings (up to three), each its
  title as the label and its fix as the description, the first marked
  "(Recommended)", and "The look another way": "Colour, page tones,
  typefaces or corners, from previews." No "None" option: ticking
  nothing is none. When nothing is chosen, one line pointing to
  `design/look-review.md`, then stop.

"The look another way" gets one more dialog, **What would you like to
change about the look?** (several allowed): "Colour" (buttons, links,
the selected thing), "Page and text" (a cooler, warmer or plainer
page), "Typefaces", "Corners". The free answer takes anything else: a
brand, a layout, a page.

**Never while a build is working in the project.** Before changing a
file, check that nothing else is: no `pytest` process in the project,
no other session's transcript for the project written to in the last
few minutes. If one is, say so in one line and wait, or ask the user.

### 4. Show the choices, then ask

For each thing to change, in the order picked:

1. Pick two to four choices that fit what the user said and the
   domain, the one now first when it is a fair choice (a calm blue or
   teal for a clinic, a warm page and a serif for a bookshop). A
   brand's colour is a choice of its own, beside the nearest named one.
2. Run `<look> preview <kind> <choices>`, then **always show it and
   give its link** before the dialog: open
   `<web address>/look-preview.html` where the user sees it, and in the
   same message one line with the link: "Three action colours on a
   piece of the app: [the previews](<web address>/look-preview.html)."
   A dialog about previews the user hasn't been shown is never sent.
3. One dialog: **Which <action colour / page tone / typefaces /
   corners>?**, each option its letter and name ("A: teal") with what
   it is like, last "Keep it as it is". A choice described in the free
   answer gets a new preview.

### 5. Apply it and show the real app

Run `<look> set <kind> <choice>`. The dev server reloads: open the
app's main page where the user sees it, and say in one line what
changed, with the link. **Keep this look?** never comes before the
user has seen the changed app.

When the check fails (exit 3), say which text would be hard to read,
in words ("the 'blocked' label on its grey tint"), never leave it
so, and fix it: for the action colour, the nearest shade that passes;
for a status colour, its value or its tint darkened or lightened in
place in `tokens.css` with the Edit tool (one token at a time, `check`
after each) until it passes. When `show` notes a dark scheme, change
its block to match by hand.

Then one dialog: **Keep this look?** "Keep it" / "Undo it": "Put back
how it was." On "Undo it", `<look> undo`, reload, and back to step 4.
Each change in a row gets its own undo.

### 6. When the user keeps it

1. A typeface or corner change moves text: run the web app's browser
   scenarios, unpaced, as
   [`testing-web-app.md`](../frontend/references/testing-web-app.md)
   "Running" says, and read their new screenshots. After a page change
   too: the scenarios read the page's visible text, so a scenario that
   relied on the old text means the change isn't done, never that the
   scenario changes.
2. Make sure `.gitignore` has `frontend/web/.look-history/`,
   `frontend/web/.look-review/` and `frontend/web/public/look-preview.html`.
3. In a git repository, commit only the files the change touched
   (the token file, a page, `.gitignore`; for a house-look type change,
   `main.tsx`, `package.json` and its lock file), "Look: <what
   changed>". Undo
   after that is `git revert` of the commit, said in words.
4. One closing line: what the app looks like now, and that any of it
   can change again. No question.

## An App in the House Look (`styles.css`)

`look-house.py` drives the older house stylesheet. What differs:

- **Its kinds:** **accent** (navy, teal, cyan, blue, indigo, violet,
  purple, plum, rose, or a brand's hex; `--dark <hex>` gives the dark
  scheme its own), **neutrals** (cream, cool, warm, grey, white),
  **type** (house, classic, plain, geometric, bookish), **corners**
  (sharp, soft, round), and `set look house` to put back the house
  tones, type, corners and density together.
- **Light and dark:** every choice is previewed, set and checked in
  both schemes; the review screenshots both (`data-theme` on `<html>`).
- **Type installs fonts:** `set type` rewrites `main.tsx`'s font
  imports and `package.json`'s font packages; run `npm install` in
  `frontend/` after it, and commit the lock file with it.
- **Never read `styles.css` whole:** it is over 4,000 words. The script
  changes it; to see one class's rules, search for it.

## Beyond the Tokens

These change pages, so the scripts don't do them. Say the change in a
line, make it as the [`frontend` skill](../frontend/SKILL.md) and
`visual-interactive.md` say, and show it:

- **A feature's view** that doesn't fit its things (a table where a
  board belongs): a frontend change through the
  [app skill](../app/SKILL.md)'s Update Flow, never a restyle here.
- **The shell:** the masthead, the brand mark and the app's name, the
  working context.
- **A brand's site or style guide:** read its colours and typefaces,
  and offer them as choices beside the nearest named ones. A brand's
  own web font is a new dependency: ask before adding it.

## Never

- Never rename a token, add a second `:root` block, or put a raw hex
  or pixel size in a page: change the token's value in place.
- Never ship text that fails the contrast check.
- Never change a scenario to fit a look change.
- Never open the preview or the app in the user's own browser in the
  Claude app: the Browser pane, or a link elsewhere.
