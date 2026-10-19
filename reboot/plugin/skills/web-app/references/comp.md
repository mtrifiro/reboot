---
title: The Comp, Before the Go-Ahead
impact: MEDIUM
impactDescription: Without a comp the user signs off on a design they have only read and sees the frontend's direction after the backend is built; with one, the main page's look and hierarchy are judged with the design
tags: comp, mockup, preview, main page, go-ahead, look, design/comp/mockup.html
---

# The Comp, Before the Go-Ahead

A comp is a mockup of the main page, made once as a static page in the look the
design names, with believable rows and no data behind it: where the
frontend is going, shown with the design so the go-ahead judges both.
The `app-guided` skill makes it for a web app after the proposed design
and before **Build on this design?**. On the first-feature-only path
(`app-basic`, `app-whole` with ", basic") it is a preview with no stop:
made right after `design/design.md`, its line said, and the build goes
straight on, the page built from it. The whole app, hands off, and the
prompt-by-prompt path don't make one (the user sees the app at the
end), an MCP App doesn't (its views live in a host), and a host that
can't run commands skips it with no line.

**Make it,** about a minute, one line first: "Making a mockup of the <page>,
in <palette>."

1. The stylesheet, copied unread, and the palette set on the copy:

   ```shell
   mkdir -p design/comp && cp '<the web-app skill>/assets/starter/frontend/web/src/styles.css' design/comp/comp.css
   python3 '<the review-ui skill>/assets/look.py' --css design/comp/comp.css set palette <palette>
   ```
2. `design/comp/page.part`, with the Write tool (named `.part`: the
   Claude app opens every `.html` the Write tool saves in the Browser
   pane, and this is only a fragment): the page only, in the
   stylesheet's own classes (its opening comment lists them,
   `ui-design.md`, "Build the Look", step 3; read nothing else); the
   bar, the badge, the note and the head are step 3's. First the brand
   mark, an inline `<svg data-mark ...>` from the domain; then the page
   head with its eyebrow, title and lede inside the
   `brand-band`; the leading figure as a `stat` in
   the `stats` row that overlaps the band's lower edge, or a `figure`;
   the signature view the design's main page line names
   (`ui-design.md`, "One Signature View"), drawn with believable
   numbers; the primary view in the domain's shape (`cells` for a
   plan, `list-card` rows, a `board`, a table) with six to twelve
   believable rows in the design's own nouns and names; the side panel
   when the page has one; the primary action as the one `primary`
   button. What the eye lands on is as the design's Pages line says:
   the resting state plain, colour on the states that need a person,
   the accent on the primary action and the current nav item only.
   A plan is `plan` rows, one a floor or aisle with its `plan-label`
   at the left and `--cells-cols` set to the row's count, each cell
   its number, one word and at most a one-letter `corner` mark; never
   a card or a heading per floor. The whole first screen at desktop
   width holds the head, the figures and the plan or board together
   (`ui-design.md`, "The first screen holds the view"). Nothing is
   wired: no drawer open, no script, no raw colour outside `comp.css`.
3. The comp, framed and made one file:

   ```shell
   python3 '<the web-app skill>/assets/comp.py' --app '<name>' --page '<page, in words>' --nav '<every page, this one first>' [--sidebar]
   ```

   It writes `design/comp/mockup.html`: the head with the typefaces'
   link, `comp.css` inside it (so the mockup keeps its look however it
   is opened: served, cached in the pane after its server stops, from
   disk; hotel-252's open mockup lost its styling when its server
   stopped), the top bar or, with `--sidebar` (the layout rule), the
   sidebar, with the mark, the name and the nav, the theme toggle and
   sign-out shown and inert, the page, the comp badge, and the note
   every click opens instead of doing nothing. And
   `design/comp/index.html`, one line that opens it where the pane
   opens only the server's root (hotel-205 showed a directory
   listing). Exit 3 names what the page lacks (the band, a primary
   action, a placeholder left in); fix `page.part` and run it again,
   as after any change to it or `comp.css`.
4. Serve `design/comp/` and open it, on a server and address of its
   own, never the design's: the pane keeps one tab per address, and
   hotel-256's mockup, opened at the design's address, replaced the
   design in its tab. In the background, its pid in
   `design/.comp.pid`, the mode by `portless doctor` as the
   [`run` skill](../../run/SKILL.md) says, never asked. Under
   portless, `<project>` the project folder's name:

   ```sh
   portless mockup.<project> sh -c 'exec python3 -m http.server "$PORT" --bind 127.0.0.1 --directory design/comp' &
   echo $! > design/.comp.pid
   ```

   at `https://mockup.<project>.localhost/`; on plain ports,
   `python3 -m http.server <port> --directory design/comp`, the next
   free port after the design's, at `http://localhost:<port>/`. The
   root opens the mockup (`design/comp/index.html`, step 3). Call that
   address `<mockup>`. In the Claude app, open it in the Browser pane:
   a `launch.json` configuration named `comp` whose `url` is that
   address alone, with no path; elsewhere the link alone, never the
   user's external browser.
5. One line in the chat, then the go-ahead dialog: "**Where it is
   going:** [a mockup of the <page>](<mockup>),
   in <palette>, with no data behind it; the real page
   replaces it at the frontend step." On the first-feature-only path
   the line ends there, with no dialog: "Building it now." follows,
   and the build goes on. A change to it typed as the
   go-ahead's free answer ("the waiting list on the left", "quieter")
   is a change to the design's Pages line: made, the mockup remade, the same
   dialog again.

**After the go-ahead** the comp is the page's target: the web-app
skill's step 8 builds the page as the comp shows, the same classes and
composition, its rows from the reader, and the look review reads the
main page's screenshot against it. Both servers, the design's and the
mockup's, keep running through the build, so what is open in the pane
stays there beside the real page; they are stopped only when the user
asks to stop the app (the `run` skill). `design/comp/mockup.html` stays as the record of
the direction, whole on its own since it holds its stylesheet, linked from the main page's line in `design/design.md`
(`app/references/design-document.md`); `comp.css` and `.look-history/` beside it and
`design/.design.pid` and `design/.comp.pid` are
git-ignored by the starter, and the comp is remade from the steps
above when it is wanted again.

## Never

- A comp of any page but the main one, or more than one comp.
- A card or a heading per row of a plan, or a plan whose rows wrap:
  the page's first screen holds the whole view.
- The page head loose on the grey page instead of in the brand band,
  a name with no mark, or boxes on grey as the whole look
  (`ui-design.md`, "Not bland").
- A script but the comp note's, a wired control or data behind it:
  it is a mockup.
- A comp without its `comp-badge`, or the badge on a real page.
- A mockup written whole instead of `page.part` framed by `comp.py`
  (step 3), or named anything but `mockup.html`.
- The go-ahead dialog before the comp's line, or a minute between the
  design and the line without "Making a mockup of the <page>".
- The comp opened in the user's external browser in the Claude app.
- A comp on the whole-app (hands off) or prompt-by-prompt path, for
  an MCP App, or where commands can't run; or a stop to wait on it on
  the first-feature-only path.
