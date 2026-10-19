#!/usr/bin/env python3
"""The proposed design as a page: design/design.md drawn as design/design.html.

    python3 '<the app-design skill>/assets/design_page.py' [design/design.md]

Run from the project root, after design/design.md is written and after
every change to it. Writes design/design.html beside it (and
design/index.html, one line that opens it from the server's root): one file, its
styles and the Reboot wordmark inside, in the developer dashboard's
look (Reboot's brand: cream, navy, the mono eyebrows, the cards, a
coloured dot for each kind of method). The build opens it in the
Browser pane, so the user reads the whole design laid out, and the chat
carries only its summary; no model writes the design twice.

Reads the Markdown the design document uses (headings, paragraphs,
bold, italics, code, links, lists, tables) and nothing more. Standard
library only.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# The dashboard's tokens (reboot/dashboard/web/dashboard.css), light
# only, as the dashboard is.
STYLE = """
:root{--background:47 36% 95%;--foreground:211.1 71.7% 22.2%;--card:0 0% 100%;--primary:211 72% 22%;
--primary-foreground:355.7 100% 97.3%;--muted:240 4.8% 95.9%;--muted-foreground:240 3.8% 46.1%;
--accent:166 47% 61%;--border:240 5.9% 90%;--sidebar:47 30% 92%;--prose:211 40% 30%;
--reader:166 55% 35%;--writer:211 72% 45%;--transaction:275 50% 50%;--workflow:36 85% 42%;
--mono:ui-monospace,SFMono-Regular,Menlo,monospace;color-scheme:light}
*{box-sizing:border-box}
html,body{margin:0}
body{font:15px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;background:hsl(var(--background));
color:hsl(var(--foreground));-webkit-font-smoothing:antialiased}
a{color:hsl(var(--primary));text-decoration:none}
a:hover{color:hsl(166 47% 41%);text-decoration:underline}
::selection{background:hsl(var(--accent)/.35)}
.app{display:grid;grid-template-columns:250px minmax(0,1fr);min-height:100vh}
aside.nav{position:sticky;top:0;height:100vh;background:hsl(var(--sidebar));border-right:1px solid hsl(var(--border));
display:flex;flex-direction:column;padding:16px 0}
.logo{display:flex;align-items:center;justify-content:space-between;padding:0 18px 14px}
.logo svg{width:62px;height:auto}
.state{font:10.5px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:hsl(var(--muted-foreground))}
.state i{display:inline-block;width:6px;height:6px;border-radius:50%;background:hsl(36 85% 52%);margin-left:6px;vertical-align:1px}
aside.nav nav{display:flex;flex-direction:column;gap:2px;padding:0 8px}
aside.nav nav a{font:600 11.5px var(--mono);letter-spacing:.06em;text-transform:uppercase;color:hsl(var(--muted-foreground));
padding:7px 10px;border-radius:6px}
aside.nav nav a:hover{color:hsl(var(--foreground));background:hsl(var(--card)/.6);text-decoration:none}
.foot{margin-top:auto;border-top:1px solid hsl(var(--border));padding:10px 18px 0;font:9.5px var(--mono);letter-spacing:.06em;
text-transform:uppercase;color:hsl(var(--muted-foreground))}
main{max-width:920px;padding:40px 32px 64px;min-width:0}
.eyebrow{font:10.5px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:hsl(var(--muted-foreground));margin:0 0 6px}
h1{font-size:34px;line-height:1.15;font-weight:700;margin:0 0 10px;letter-spacing:-.01em;text-wrap:balance}
.status{color:hsl(var(--prose));max-width:70ch;margin:0 0 28px}
.status p{margin:0}
section{margin:0 0 32px;scroll-margin-top:24px}
section>.eyebrow{max-width:none;border-bottom:1px solid hsl(var(--border));padding-bottom:6px;margin-bottom:14px}
.card{padding:16px 18px;border:1px solid hsl(var(--border));border-radius:10px;background:hsl(var(--sidebar));margin:0 0 14px}
.card.white{background:hsl(var(--card))}
p{margin:0 0 10px;max-width:72ch;color:hsl(var(--prose))}
strong{color:hsl(var(--foreground));font-weight:700}
h3{font-size:16px;font-weight:700;margin:16px 0 8px}
ul,ol{margin:0 0 10px;padding-left:1.15em;display:grid;gap:5px;color:hsl(var(--prose))}
.label{font-size:11px;font-weight:600;letter-spacing:.04em;text-transform:uppercase;color:hsl(var(--muted-foreground));margin:12px 0 6px}
.rules{padding-left:1.15em}
.rules li{font-weight:600;color:hsl(var(--foreground))}
.rules a,.feature-name a{color:inherit}
.feature-name{font-size:16px;font-weight:700;margin:0 0 6px}
code,.chip{font:12px var(--mono);padding:1px 7px;border-radius:4px;background:hsl(var(--muted));color:hsl(var(--foreground))}
a code{color:hsl(var(--primary))}
.table{overflow-x:auto;margin:0 0 14px;border:1px solid hsl(var(--border));border-radius:10px;background:hsl(var(--card))}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:left;padding:8px 14px;border-bottom:1px solid hsl(var(--border));vertical-align:top}
tr:last-child td{border-bottom:0}
th{font:600 11px ui-sans-serif,system-ui,sans-serif;letter-spacing:.04em;text-transform:uppercase;color:hsl(var(--muted-foreground));
background:hsl(var(--sidebar))}
.kind{white-space:nowrap}
.kind::before{content:"";display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:7px;vertical-align:1px;
background:hsl(var(--muted-foreground))}
.kind.reader::before{background:hsl(var(--reader))}.kind.writer::before{background:hsl(var(--writer))}
.kind.transaction::before{background:hsl(var(--transaction))}.kind.workflow::before{background:hsl(var(--workflow))}
.model-name{font-size:15px;font-weight:700;margin:14px 0 6px}
@media (max-width:760px){.app{grid-template-columns:1fr}aside.nav{position:static;height:auto;flex-direction:row;
flex-wrap:wrap;align-items:center;padding:10px 8px}.logo{padding:0 10px}aside.nav nav{flex-direction:row;flex-wrap:wrap}
.foot{display:none}main{padding:24px 16px 48px}h1{font-size:28px}}
"""

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{style}</style>
</head>
<body>
<div class="app">
<aside class="nav">
<div class="logo">{logo}<span class="state">Proposed<i></i></span></div>
<nav>{nav}</nav>
<div class="foot">Not built yet<br>Opens on the dashboard once it is</div>
</aside>
<main>
<p class="eyebrow">The proposed design</p>
<h1>{h1}</h1>
{status}
{sections}
</main>
</div>
</body>
</html>
"""

LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
KINDS = ("reader", "writer", "transaction", "workflow")


def inline(text: str) -> str:
    """Bold, italics, code and links in one line of Markdown."""
    out = []
    for part in re.split(r"(`[^`]+`)", text):
        if part.startswith("`") and part.endswith("`") and len(part) > 1:
            out.append(f"<code>{html.escape(part[1:-1])}</code>")
            continue
        s = html.escape(part, quote=False)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
        out.append(s)
    return LINK.sub(lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>', "".join(out))


def cell(text: str, header: str) -> str:
    """A table cell; a Kind column's value gets its kind's dot."""
    if header.lower() == "kind" and text.strip().lower() in KINDS:
        return f'<td class="kind {text.strip().lower()}">{inline(text)}</td>'
    return f"<td>{inline(text)}</td>"


def blocks(lines: list[str], section: str) -> str:
    """A section's body: paragraphs, lists (with continuation lines),
    tables and ### headings, in the dashboard's shapes."""
    out: list[str] = []
    i = 0
    features = section.startswith("features")
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("### "):
            out.append(f"<h3>{inline(line[4:])}</h3>")
            i += 1
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            head, body = rows[0], rows[1:]
            th = "".join(f"<th>{inline(c)}</th>" for c in head)
            tb = "".join("<tr>" + "".join(cell(c, head[k] if k < len(head) else "") for k, c in enumerate(r)) + "</tr>"
                         for r in body)
            out.append(f'<div class="table"><table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>')
        elif re.match(r"\s*(?:[-*]|\d+\.) ", line):
            ordered = bool(re.match(r"\s*\d+\. ", line))
            items: list[str] = []
            while i < len(lines) and lines[i].strip():
                cur = lines[i]
                if re.match(r"\s*(?:[-*]|\d+\.) ", cur):
                    items.append(re.sub(r"^\s*(?:[-*]|\d+\.) ", "", cur))
                elif items:
                    items[-1] += " " + cur.strip()
                i += 1
            tag = "ol" if ordered else "ul"
            cls = ' class="rules"' if features else ""
            if features:
                out.append('<p class="label">Rules</p>')
            out.append(f"<{tag}{cls}>" + "".join(f"<li>{inline(t)}</li>" for t in items) + f"</{tag}>")
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(("|", "### ")) \
                    and not re.match(r"\s*(?:[-*]|\d+\.) ", lines[i]):
                para.append(lines[i].strip())
                i += 1
            text = " ".join(para)
            # A paragraph that is only a bold name (or a link to one) heads
            # what follows it: an object's methods, a feature.
            if re.fullmatch(r"\*\*[^*]+\*\*", text):
                out.append(f'<p class="model-name">{inline(text[2:-2])}</p>')
            elif features and re.fullmatch(r"\[[^\]]+\]\([^)]+\)", text):
                out.append(f'<p class="feature-name">{inline(text)}</p>')
            else:
                out.append(f"<p>{inline(text)}</p>")
    return "\n".join(out)


def slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def main(argv: list[str]) -> int:
    source = Path(argv[0]) if argv else Path("design/design.md")
    if not source.is_file():
        print(f"design_page: no {source}; write the design first", file=sys.stderr)
        return 2
    lines = source.read_text(encoding="utf-8").splitlines()
    h1 = next((l[2:].strip() for l in lines if l.startswith("# ")), "The design")
    first = next((k for k, l in enumerate(lines) if l.startswith("## ")), len(lines))
    intro = [l for l in lines[:first] if not l.startswith("# ")]
    status = f'<div class="status">{blocks(intro, "")}</div>' if any(l.strip() for l in intro) else ""
    sections, nav = [], []
    k = first
    while k < len(lines):
        title = lines[k][3:].strip()
        k += 1
        body = []
        while k < len(lines) and not lines[k].startswith("## "):
            body.append(lines[k])
            k += 1
        rendered = blocks(body, title.lower())
        wrap = title.lower() in ("brief", "assumed", "domain model", "sign-in", "what reboot does for you here") \
            or title.lower().startswith("features")
        if wrap:
            rendered = f'<div class="card{" white" if title.lower() == "brief" else ""}">{rendered}</div>'
        sections.append(f'<section id="{slug(title)}"><p class="eyebrow">{html.escape(title)}</p>\n{rendered}</section>')
        nav.append(f'<a href="#{slug(title)}">{html.escape(title)}</a>')
    name = re.sub(r":.*$", "", h1).strip() or "The app"
    logo_file = HERE / "reboot-logo.svg"
    logo = logo_file.read_text(encoding="utf-8") if logo_file.is_file() else "<strong>Reboot</strong>"
    page = PAGE.format(title=html.escape(f"{name} · the proposed design"), style=STYLE, logo=logo,
                       nav="".join(nav), h1=inline(h1), status=status, sections="\n".join(sections))
    dest = source.with_suffix(".html")
    dest.write_text(page, encoding="utf-8")
    # The server's root opens the page, for a pane that opens only the
    # origin; a folder that already has an index of its own keeps it.
    index = dest.parent / "index.html"
    if not index.exists() or "url=design.html" in index.read_text(encoding="utf-8"):
        index.write_text('<!doctype html><meta http-equiv="refresh" content="0; url=design.html">\n', encoding="utf-8")
    print(f"wrote {dest}: the design as a page in the dashboard's look, to open in the Browser pane")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
