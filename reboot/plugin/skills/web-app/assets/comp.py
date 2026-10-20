#!/usr/bin/env python3
"""The design's comp: the page the build drew, in the frame every comp shares.

    python3 '<the web-app skill>/assets/comp.py' --app 'Linden' --page 'floor plan' \\
        --nav 'Floor plan,Guests,Housekeeping' [--sidebar] [--user 'Esi'] [DIR]

Run from the project root. DIR (default design/comp) holds comp.css,
the house stylesheet with the design's palette set (comp.md, step 1),
and page.part, which the build writes: everything between the app's
bar and the end of the page (the brand-band with the page head, the
stats, the primary view, the side panel), in the stylesheet's classes.
It may begin with the brand mark, an <svg data-mark ...>, shown beside
the app's name.

Writes DIR/mockup.html, one file that keeps its look however it is
opened: the head (title, the typefaces' Google Fonts link), comp.css
inside it, the top bar (or, with --sidebar, the sidebar) with the mark,
the name and --nav (the first current), the theme and sign-out buttons,
the page, the comp badge, and the note every click opens instead of
doing nothing. And DIR/index.html, one line that opens mockup.html, for
a pane that opens only the server's root. Run it again after any change
to page.part or comp.css. Standard library only.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

FRAME = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{app} · {Page} (design comp)</title>
{fonts}
<style data-inlined="comp.css">
{css}
</style>
</head>
<body>
{shell_open}
{page}
{shell_close}
<aside class="comp-badge"><strong>Design comp</strong><span>A mockup of the {page_name}, not the running app; the real page replaces it at the frontend step.</span></aside>
<dialog class="comp-note" id="comp-note">
  <strong>This is a design mockup</strong>
  <p>It shows how the {page_name} will look, with sample rows. Nothing
  on it is wired yet, so buttons and links don't do anything. The
  real page, with your data, replaces it at the frontend step.</p>
  <form method="dialog"><button class="primary">Got it</button></form>
</dialog>
<script>
  document.addEventListener("click", (event) => {{
    const note = document.getElementById("comp-note");
    if (note.contains(event.target)) return;
    event.preventDefault();
    event.stopPropagation();
    note.showModal();
  }}, true);
</script>
</body>
</html>
"""

TOPBAR = """<header class="topbar">
  <a class="brand" href="#">{mark}{app}</a>
  <nav>{nav}</nav>
  <span class="spacer"></span>
  <button class="ghost">Dark</button>
  <button class="ghost">{user} · Sign out</button>
</header>"""

SIDEBAR = """<div class="shell sidebar">
<aside class="sidebar-nav">
  <a class="brand" href="#">{mark}{app}</a>
  <nav>{nav}</nav>
  <span class="spacer"></span>
  <button class="ghost">Dark</button>
  <button class="ghost">{user} · Sign out</button>
</aside>
<div class="shell-main">"""

MARK = re.compile(r"^\s*(<svg\b[^>]*\bdata-mark\b.*?</svg>)", re.S)


def fonts_link(css: str) -> str:
    """The <link> that loads the stylesheet's typefaces from Google Fonts."""
    families = []
    for role in ("display", "text", "mono"):
        found = re.search(r'--font-%s:\s*"([^"]+?)(?: Variable)?"' % role, css)
        if found and found.group(1) not in families:
            families.append(found.group(1))
    if not families:
        return ""
    q = "&".join("family=" + f.replace(" ", "+") + ":wght@400;500;600" for f in sorted(families))
    return f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{q}&display=swap">'


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--app", required=True, help="the app's name as shown: Linden")
    p.add_argument("--page", required=True, help="the page in words, lower case: floor plan")
    p.add_argument("--nav", required=True, help="every page in the design, comma-separated, this one first")
    p.add_argument("--sidebar", action="store_true", help="the sidebar layout (seven or more pages, or a tool kept open all day)")
    p.add_argument("--user", default="Alice", help="the signed-in person's name in the bar (default Alice)")
    p.add_argument("dir", nargs="?", default="design/comp", help="the comp's folder (default design/comp)")
    args = p.parse_args(argv)

    folder = Path(args.dir)
    css_file, page_file = folder / "comp.css", folder / "page.part"
    missing = [str(f) for f in (css_file, page_file) if not f.is_file()]
    if missing:
        print(f"comp: no {', '.join(missing)} (comp.md: step 1 makes comp.css, the build writes page.part)", file=sys.stderr)
        return 2

    css = css_file.read_text(encoding="utf-8").replace("</style", "<\\/style")
    page = page_file.read_text(encoding="utf-8").strip()
    mark = ""
    found = MARK.match(page)
    if found:
        mark, page = found.group(1) + " ", page[found.end():].strip()
    problems = []
    # What follows the band goes in <main>, as on the real page, so the
    # stat tiles overlap the band and the panels keep the page's width.
    if "<main" not in page:
        band = re.search(r"<section[^>]*\bbrand-band\b.*?</section>\s*", page, re.S)
        if band:
            page = page[:band.end()] + "<main>\n" + page[band.end():].rstrip() + "\n</main>\n"
    if "brand-band" not in page:
        problems.append("no brand-band: the page head sits in the band (ui-design.md, Not bland)")
    if not re.search(r'class="[^"]*\bprimary\b', page):
        problems.append("no primary button: the page's main action is the one primary")
    if re.search(r"<script\b", page):
        problems.append("a script in page.part: the comp's only script is its note's")
    if re.search(r"<(?:page|app|feature)>|\{\{|TODO", page):
        problems.append("a placeholder left in page.part")

    names = [n.strip() for n in args.nav.split(",") if n.strip()]
    active = ' class="active"'
    nav = "".join(
        f'<a{active if i == 0 else ""} href="#">{html.escape(n)}</a>' for i, n in enumerate(names)
    )
    fill = {"mark": mark, "app": html.escape(args.app), "nav": nav, "user": html.escape(args.user)}
    shell_open = (SIDEBAR if args.sidebar else TOPBAR).format(**fill)
    shell_close = "</div>\n</div>" if args.sidebar else ""
    page_name = html.escape(args.page)
    out = FRAME.format(
        app=html.escape(args.app), Page=page_name[:1].upper() + page_name[1:], fonts=fonts_link(css), css=css,
        shell_open=shell_open, page=page, shell_close=shell_close, page_name=page_name,
    )
    (folder / "mockup.html").write_text(out, encoding="utf-8")
    (folder / "index.html").write_text('<!doctype html><meta http-equiv="refresh" content="0; url=mockup.html">\n',
                                       encoding="utf-8")
    print(f"wrote {folder / 'mockup.html'} (one file, its stylesheet inside) and {folder / 'index.html'}")
    for problem in problems:
        print(f"comp: {problem}", file=sys.stderr)
    return 3 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
