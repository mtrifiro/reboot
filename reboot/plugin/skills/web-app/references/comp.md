---
title: The Comp, Before the Go-Ahead
impact: MEDIUM
impactDescription: Without a comp the user signs off on a design they have only read and sees the frontend's direction after the backend is built; with one, the main page's look and hierarchy are judged with the design
tags: comp, mockup, preview, main page, go-ahead, look, design/comp.html
---

# The Comp, Before the Go-Ahead

A comp is the main page drawn once, as a static page in the look the
design names, with believable rows and no data behind it: where the
frontend is going, shown with the design so the go-ahead judges both.
The `guided` skill makes it for a web app after the proposed design
and before **Build on this design?**. The `one-shot` and the
prompt-by-prompt path don't (no stop to show it at), an MCP UI doesn't
(its views live in a host), and a host that can't run commands skips
it with no line.

**Make it,** about a minute, one line first: "Drawing the <page> as a
comp: in <look>, in <accent>."

1. The stylesheet, copied unread, and the look set on the copy:

   ```shell
   mkdir -p design && cp '<the web-app skill>/assets/starter/frontend/web/src/styles.css' design/comp.css
   python3 '<the design-review skill>/assets/look.py' --css design/comp.css set accent <accent>
   python3 '<the design-review skill>/assets/look.py' --css design/comp.css set look <look>   # Ledger or Boutique only
   python3 '<the design-review skill>/assets/look.py' --css design/comp.css fonts
   ```

   The last prints the `<link>` that loads the typefaces from Google
   Fonts: the comp is served outside the bundle, so it needs one.
2. `design/comp.html`, with the Write tool: `<!doctype html>`, the
   fonts link, `<link rel="stylesheet" href="comp.css">`, then the
   page in the stylesheet's own classes (its opening comment lists
   them, `ui-design.md`, "Build the Look", step 3; read nothing else):
   the shell (a top bar, or the sidebar as the layout rule says) with
   the brand and the nav of every page in the design; the page head
   with its eyebrow, title and lede; the leading figure as a `stat` or
   a `figure`; the primary view in the domain's shape (`cells` for a
   plan, `list-card` rows, a `board`, a table) with six to twelve
   believable rows in the design's own nouns and names; the side panel
   when the page has one; the primary action as the one `primary`
   button. What the eye lands on is as the design's Pages line says:
   the resting state plain, colour on the states that need a person,
   the accent on the primary action and the current nav item only.
   Nothing is wired: no script, no drawer open, the theme toggle drawn
   and inert. No raw colour outside `comp.css`.
3. Serve `design/` and open it: `python3 -m http.server <port>
   --directory design` in the background, the port the first free one
   from 9860, its pid written to `design/.comp.pid`. In the Claude
   app, open `http://localhost:<port>/comp.html` in the Browser pane
   (a `launch.json` configuration named `comp` with only that URL,
   `conversation.md`); elsewhere, the link alone, never the user's
   external browser.
4. One line in the chat, then the go-ahead dialog: "**Where it is
   going:** [the <page>, as a comp](http://localhost:<port>/comp.html),
   drawn in <look>, in <accent>, with no data behind it; the real page
   replaces it at the frontend step." A change to it typed as the
   go-ahead's free answer ("the waiting list on the left", "quieter")
   is a change to the design's Pages line: made, redrawn, the same
   dialog again.

**After the go-ahead** the comp is the page's target: the web-app
skill's step 8 builds the page as the comp shows, the same classes and
composition, its rows from the reader, and the look review reads the
main page's screenshot against it. The comp's server is stopped when
the app starts (step 10, the `run` skill): `kill $(cat
design/.comp.pid)`. `design/comp.html` stays as the record of the
direction; `comp.css`, `.comp.pid` and `.look-history/` beside it are
git-ignored by the starter, and the comp is redrawn from the steps
above when it is wanted again.

## Never

- A comp of any page but the main one, or more than one comp.
- A script, a wired control or data behind it: it is a drawing.
- The go-ahead dialog before the comp's line, or a minute between the
  design and the line without "Drawing the <page> as a comp".
- The comp opened in the user's external browser in the Claude app.
- A comp on the one-shot or prompt-by-prompt path, for an MCP UI, or
  where commands can't run.
