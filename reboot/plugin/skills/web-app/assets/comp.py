#!/usr/bin/env python3
"""The design's comp: the page the build drew, in the frame every comp shares.

    python3 '<the web-app skill>/assets/comp.py' --app 'Linden' --page 'floor plan' \\
        --nav 'Floor plan,Guests,Housekeeping' [--user 'Esi'] [--gallery] [DIR]

Run from the project root. DIR (default design/comp) holds comp.css,
the house stylesheet with the design's palette set (comp.md, step 1),
and page.part, which the build writes: everything between the app's
bar and the end of the page (the brand-band with the page head, the
stats, the primary view, the side panel), in the stylesheet's classes.
It may begin with the brand mark, an <svg data-mark ...>, shown beside
the app's name.

Writes DIR/mockup.html, one file that keeps its look however it is
opened: the head (title, the typefaces' Google Fonts link), comp.css
inside it, the top bar with the mark,
the name and --nav (the first current), the theme and sign-out buttons,
the page, the comp badge, and the note every click opens instead of
doing nothing. And DIR/index.html, one line that opens mockup.html, for
a pane that opens only the server's root. Run it again after any change
to page.part or comp.css. Standard library only.

With --gallery, also the same page in the four palettes the go-ahead
offers (palette.py's `gallery`: house, then three of different
families, by the project folder's name), each DIR/palettes/<name>.html,
and DIR/palettes.html showing the four side by side, numbered and named;
index.html opens the gallery instead. It prints the four, one a line:
the palette as palette.py takes it, a tab, its name and colours. Once
one is picked, set it on comp.css and run this again without --gallery:
mockup.html is then in that palette and index.html opens it again.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import palette  # noqa: E402  (beside this file)

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
  <p>It shows how the {page_name} will look, with sample rows. Only the
  Light / Dark button works, to see both schemes; nothing else is
  wired yet. The real page, with your data, replaces it at the
  frontend step.</p>
  <form method="dialog"><button class="primary">Got it</button></form>
</dialog>
<script>
  // The one working control: Light / Dark, as the real app's ThemeToggle
  // (data-theme on <html>); every other click opens the note.
  const root = document.documentElement;
  const toggle = document.querySelector("[data-theme-toggle]");
  const dark = () => root.dataset.theme
    ? root.dataset.theme === "dark"
    : matchMedia("(prefers-color-scheme: dark)").matches;
  const label = () => {{ if (toggle) toggle.textContent = dark() ? "Light" : "Dark"; }};
  label();
  const note = document.getElementById("comp-note");
  // The note closes on a click anywhere outside its box (the backdrop
  // is the dialog itself), on its button, and on Escape.
  document.addEventListener("keydown", (event) => {{
    if (event.key === "Escape" && note.open) note.close();
  }});
  document.addEventListener("click", (event) => {{
    if (note.open) {{
      const box = note.getBoundingClientRect();
      const outside = event.clientX < box.left || event.clientX > box.right
        || event.clientY < box.top || event.clientY > box.bottom;
      if (outside) {{
        event.preventDefault();
        event.stopPropagation();
        note.close();
      }}
      return;
    }}
    if (toggle && toggle.contains(event.target)) {{
      root.dataset.theme = dark() ? "light" : "dark";
      label();
      return;
    }}
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
  <button class="ghost" data-theme-toggle>Dark</button>
  <button class="ghost">{user} · Sign out</button>
</header>"""


GALLERY = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{app} · four palettes (design comp)</title>
<style>
  :root {{ color-scheme: light; --ink: #1d2433; --muted: #5b6475; --line: #d9dde4; }}
  body {{ margin: 0; background: #f4f4f2; color: var(--ink);
         font: 15px/1.45 ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }}
  header {{ max-width: 1280px; margin: 0 auto; padding: 20px 16px 4px; }}
  h1 {{ font-size: 20px; margin: 0 0 4px; }}
  header p {{ margin: 0; color: var(--muted); }}
  .grid {{ max-width: 1280px; margin: 0 auto; padding: 12px 16px 32px;
          display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20px; }}
  figure {{ margin: 0; }}
  figcaption {{ display: flex; justify-content: space-between; gap: 12px; margin-bottom: 6px; }}
  figcaption strong {{ font-size: 16px; }}
  figcaption a {{ color: var(--muted); white-space: nowrap; }}
  .frame {{ position: relative; aspect-ratio: 16 / 10; overflow: hidden; border: 1px solid var(--line);
           border-radius: 8px; background: #fff; }}
  .frame iframe {{ position: absolute; top: 0; left: 0; width: 1440px; height: 900px; border: 0;
                  transform-origin: 0 0; pointer-events: none; }}
  @media (max-width: 720px) {{ .grid {{ grid-template-columns: minmax(0, 1fr); }} }}
</style>
</head>
<body>
<header>
  <h1>{app}: the {page_name} in four palettes</h1>
  <p>The same mockup in each. Pick one in the chat; any can change later.</p>
</header>
<main class="grid">
{figures}
</main>
<script>
  // Each mockup is drawn at 1440 x 900 and scaled to its frame.
  const fit = () => document.querySelectorAll(".frame").forEach((frame) => {{
    frame.querySelector("iframe").style.transform = `scale(${{frame.clientWidth / 1440}})`;
  }});
  addEventListener("resize", fit);
  fit();
</script>
</body>
</html>
"""

FIGURE = """<figure>
  <figcaption><strong>{n}. {label}</strong><a href="{href}">Open full size</a></figcaption>
  <div class="frame"><iframe src="{href}" title="{label}" loading="eager" tabindex="-1"></iframe></div>
</figure>"""

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
    p.add_argument("--user", default="Alice", help="the signed-in person's name in the bar (default Alice)")
    p.add_argument("--gallery", action="store_true", help="also the page in the four palettes the go-ahead offers, and the page that shows them")
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
    shell_open = TOPBAR.format(**fill)
    shell_close = ""
    page_name = html.escape(args.page)

    def framed(css: str) -> str:
        return FRAME.format(
            app=html.escape(args.app), Page=page_name[:1].upper() + page_name[1:], fonts=fonts_link(css), css=css,
            shell_open=shell_open, page=page, shell_close=shell_close, page_name=page_name,
        )

    (folder / "mockup.html").write_text(framed(css), encoding="utf-8")
    opens = "mockup.html"
    if args.gallery:
        found = palette.palettes()
        (folder / "palettes").mkdir(exist_ok=True)
        figures = []
        for n, (name, band, paper) in enumerate(palette.gallery(Path.cwd().name, found), 1):
            href = f"palettes/{name}.html"
            (folder / href).write_text(framed(palette.styled(css, name, band, paper, found)), encoding="utf-8")
            label = html.escape(palette.describe(name, found))
            figures.append(FIGURE.format(n=n, label=label, href=href))
            spec = name if name == "house" else f"{name} --band {band} --paper {paper}"
            print(f"{spec}\t{palette.describe(name, found)}")
        (folder / "palettes.html").write_text(
            GALLERY.format(app=html.escape(args.app), page_name=page_name, figures="\n".join(figures)),
            encoding="utf-8")
        opens = "palettes.html"
    (folder / "index.html").write_text(f'<!doctype html><meta http-equiv="refresh" content="0; url={opens}">\n',
                                       encoding="utf-8")
    print(f"wrote {folder / 'mockup.html'} (one file, its stylesheet inside)"
          + (", the four palettes and palettes.html" if args.gallery else "")
          + f", and {folder / 'index.html'}, which opens {opens}", file=sys.stderr if args.gallery else sys.stdout)
    for problem in problems:
        print(f"comp: {problem}", file=sys.stderr)
    return 3 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
