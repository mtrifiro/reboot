#!/usr/bin/env python3
"""The browser check's measurements, for any web app in the house look.

    uv run python '<the web-app skill>/assets/check_page.py' URL PAGE=FIRST ... \\
        [--tap PAGE=SELECTOR] [--open PAGE=SELECTOR] [--as Alice] [--out DIR]

Run from the project root (its venv has Playwright), with the app
running. URL is the app's address (https://<project>.localhost, or
http://localhost:9991 on plain ports). Each PAGE=FIRST is a page's
path and a selector for one record of its main view: `/=.cell`,
`/accounts=.list-card .row`, `/board=.board-card`.

For each page, headless, at desktop (1440x900, light) and phone
(375x812, dark), signed in through the development picker as --as:

  * timing, three loads (web-app/references/vitals.md): the first
    record, FCP, LCP, CLS, and INP for a tap on the page's main action
    (--tap, default its first record), judged on the second and third
    loads;
  * layout (web-app/references/ui-design.md, "Measure what can be
    measured"): nothing spills out of its container or is cut off, no
    sideways scroll, a board's columns and headers and a plan's rows
    and cells each one height, and at desktop the plan or board on the
    first screen;
  * touching: no text or control touches another, on the page as it
    loads, with the tap's panel open, and with each --open target open;
  * console errors.

Prints one line per check, PASS or FAIL with what to fix, writes
DIR/report.json and a screenshot per page and width (DIR defaults to
a new temporary folder), and exits 1 when anything fails.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

BUDGET = {"first": 2000, "lcp": 2500, "cls": 0.1, "inp": 200, "fcp": 1800}
WIDTHS = (("desktop", 1440, 900, "light"), ("phone", 375, 812, "dark"))

VITALS = """
window.__vitals = { lcp: 0, cls: 0, inp: 0 };
new PerformanceObserver((l) => { for (const e of l.getEntries()) window.__vitals.lcp = e.startTime; })
  .observe({ type: "largest-contentful-paint", buffered: true });
new PerformanceObserver((l) => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__vitals.cls += e.value; })
  .observe({ type: "layout-shift", buffered: true });
new PerformanceObserver((l) => { for (const e of l.getEntries()) if (e.interactionId) window.__vitals.inp = Math.max(window.__vitals.inp, e.duration); })
  .observe({ type: "event", buffered: true, durationThreshold: 16 });
"""

FIRST = """(sel) => new Promise((resolve) => {
  const poll = setInterval(() => {
    const ms = performance.now();
    if (document.querySelector(sel)) { clearInterval(poll); resolve(Math.round(ms)); }
    if (ms > 30000) { clearInterval(poll); resolve(-1); }
  }, 25);
})"""

READ = """() => ({
  fcp: Math.round(performance.getEntriesByName("first-contentful-paint")[0]?.startTime ?? -1),
  lcp: Math.round(window.__vitals.lcp),
  cls: Number(window.__vitals.cls.toFixed(3)),
  inp: Math.round(window.__vitals.inp),
})"""

LAYOUT = """() => {
const heights = (els) => [...new Set(els.map((e) => Math.round(e.getBoundingClientRect().height)))];
const label = (e) => (typeof e.className === "string" && e.className) || e.tagName;
const spill = [...document.querySelectorAll("main *")].filter((e) => {
  const r = e.getBoundingClientRect(), p = e.parentElement?.getBoundingClientRect();
  return p && r.width > 0 && (r.right > p.right + 1 || r.left < p.left - 1) &&
    getComputedStyle(e.parentElement).overflowX === "visible";
}).map(label).slice(0, 5);
const clipped = [...document.querySelectorAll("main *")].filter((e) =>
  e.scrollWidth > e.clientWidth + 1 && getComputedStyle(e).overflow === "hidden" &&
  getComputedStyle(e).textOverflow !== "ellipsis").map(label).slice(0, 5);
const cols = [...document.querySelectorAll(".board-col")];
const view = document.querySelector(".plan, .board");
return {
  spill, clipped,
  sideways: document.documentElement.scrollWidth > innerWidth + 1,
  columns: heights(cols),
  headers: heights(cols.map((c) => c.querySelector(".board-col-head")).filter(Boolean)),
  planRows: heights([...document.querySelectorAll(".plan-row")]),
  cells: heights([...document.querySelectorAll(".plan .cell, .cells .cell")]),
  viewBottom: view ? Math.round(view.getBoundingClientRect().bottom + scrollY) : null,
  screen: innerHeight,
};
}"""

TOUCH = """() => {
const own = (e) => [...e.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
const boxes = [...document.querySelectorAll("main *, [role=dialog] *")]
  .filter((e) => e.offsetParent && (own(e) || e.matches("input, select, textarea, button")))
  .filter((e) => !e.parentElement?.closest("button, label"))
  .map((e) => ({ e, r: e.getBoundingClientRect() }));
const inline = (e) => getComputedStyle(e).display === "inline";
const name = (e) => `${e.tagName} "${e.textContent?.trim().slice(0, 20)}"`;
const touching = [];
for (let i = 0; i < boxes.length; i++)
  for (let j = i + 1; j < boxes.length; j++) {
    const a = boxes[i], b = boxes[j];
    if (a.e.contains(b.e) || b.e.contains(a.e)) continue;
    if (inline(a.e) && inline(b.e) && a.e.parentElement === b.e.parentElement) continue;
    const overlapX = Math.min(a.r.right, b.r.right) - Math.max(a.r.left, b.r.left);
    const overlapY = Math.min(a.r.bottom, b.r.bottom) - Math.max(a.r.top, b.r.top);
    const gapX = Math.max(a.r.left, b.r.left) - Math.min(a.r.right, b.r.right);
    const gapY = Math.max(a.r.top, b.r.top) - Math.min(a.r.bottom, b.r.bottom);
    if (overlapX > 0 && gapY < 4) touching.push(`${name(a.e)} / ${name(b.e)} stacked, ${Math.round(gapY)}px apart`);
    else if (overlapY > 0 && gapX < 8) touching.push(`${name(a.e)} / ${name(b.e)} side by side, ${Math.round(gapX)}px apart`);
  }
return touching.slice(0, 10);
}"""


def pairs(values: list[str], flag: str) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for value in values:
        path, sep, selector = value.partition("=")
        if not sep or not path.startswith("/") or not selector:
            raise SystemExit(f"check_page: {flag} {value!r}: PAGE=SELECTOR, the page's path first: /=.cell")
        found.setdefault(path, []).append(selector)
    return found


class Report:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.failed = 0
        self.data: dict = {}

    def check(self, where: str, ok: bool, what: str, fix: str = "") -> None:
        self.lines.append(f"{'PASS' if ok else 'FAIL'}  {where}  {what}" + ("" if ok or not fix else f": {fix}"))
        self.failed += not ok


def sign_in(page, url: str, who: str, sign_in_label: str) -> None:
    page.goto(url)
    button = page.get_by_role("button", name=sign_in_label, exact=True)
    try:
        button.wait_for(timeout=10000)
    except Exception:
        return  # already signed in, or an app with no sign-in
    button.click()
    page.get_by_role("link", name=who, exact=True).click()
    page.wait_for_url(re.compile("^" + re.escape(url.rstrip("/"))), timeout=30000)


def layout_checks(report: Report, where: str, layout: dict, width: str) -> None:
    report.check(where, not layout["spill"], "nothing spills out of its container",
                 f"spills: {', '.join(layout['spill'])}")
    report.check(where, not layout["clipped"], "no text cut off", f"cut off: {', '.join(layout['clipped'])}")
    report.check(where, not layout["sideways"], "no sideways scroll", "the page is wider than the screen")
    for key, what in (("columns", "a board's columns one height"), ("headers", "a board's column headers one height"),
                      ("planRows", "a plan's rows one height"), ("cells", "a plan's cells one height")):
        if layout[key]:
            report.check(where, len(layout[key]) <= 1, what, f"heights {layout[key]} px")
    if width == "desktop" and layout["viewBottom"] is not None:
        report.check(where, layout["viewBottom"] <= layout["screen"], "the plan or board on the first screen",
                     f"it ends at {layout['viewBottom']} px of {layout['screen']}")


def touch_check(report: Report, where: str, page, state: str) -> list[str]:
    touching = page.evaluate(TOUCH)
    report.check(where, not touching, f"nothing touches ({state})", "; ".join(touching[:4]))
    return touching


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("url", help="the app's address: https://<project>.localhost or http://localhost:9991")
    p.add_argument("pages", nargs="+", help="PAGE=FIRST: a page's path and a selector for one record of its main view")
    p.add_argument("--tap", action="append", default=[], help="PAGE=SELECTOR: the page's main action (default: its first record)")
    p.add_argument("--open", action="append", default=[], help="PAGE=SELECTOR: a drawer or form to open for the touching check")
    p.add_argument("--as", dest="who", default="Alice", help="the development picker's account to sign in as (default Alice)")
    p.add_argument("--sign-in", default="Sign in", help="the sign-in button's label (default: Sign in)")
    p.add_argument("--out", help="where the report and screenshots go (default: a new temporary folder)")
    args = p.parse_args(argv)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("check_page: no Playwright here; run it with `uv run python` from the project root "
              "(and `uv run playwright install chromium` once)", file=sys.stderr)
        return 2

    url = args.url.rstrip("/")
    pages = {path: sels[0] for path, sels in pairs(args.pages, "PAGE").items()}
    taps = {path: sels[0] for path, sels in pairs(args.tap, "--tap").items()}
    opens = pairs(args.open, "--open")
    out = Path(args.out) if args.out else Path(tempfile.mkdtemp(prefix="check-page-"))
    out.mkdir(parents=True, exist_ok=True)
    report = Report()

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for width, w, h, scheme in WIDTHS:
            ctx = browser.new_context(viewport={"width": w, "height": h}, color_scheme=scheme, ignore_https_errors=True)
            page = ctx.new_page()
            errors: list[str] = []
            page.on("console", lambda m: m.type == "error" and errors.append(m.text))
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.add_init_script(VITALS)
            sign_in(page, url, args.who, args.sign_in)
            for path, first in pages.items():
                where = f"{path} {width}"
                tap = taps.get(path, first)
                runs = []
                for _ in range(3):
                    page.goto(url + path)
                    shown = page.evaluate(FIRST, first)
                    page.wait_for_timeout(1000)
                    loaded = page.evaluate(READ)
                    loaded["first"] = shown
                    if shown >= 0 and page.locator(tap).count():
                        page.locator(tap).first.click()
                        page.wait_for_timeout(500)
                        loaded["inp"] = page.evaluate(READ)["inp"]
                    runs.append(loaded)
                judged = runs[1:]
                if any(r["first"] < 0 for r in runs):
                    report.check(where, False, "the first record appears",
                                 f"no {first!r} within 30 s: the page is empty, broken, or the selector is wrong")
                    report.data[where] = {"runs": runs}
                    continue
                else:
                    worst = {k: max(r[k] for r in judged) for k in ("first", "fcp", "lcp", "cls", "inp")}
                    report.check(where, worst["first"] <= BUDGET["first"], f"first record {worst['first']} ms (budget 2 s)",
                                 "the page waits on its data (vitals.md, Reading the numbers)")
                    report.check(where, worst["lcp"] <= BUDGET["lcp"], f"LCP {worst['lcp']} ms (budget 2.5 s)",
                                 "the largest thing on the first screen paints late")
                    report.check(where, worst["cls"] <= BUDGET["cls"], f"CLS {worst['cls']} (budget 0.1)",
                                 "reserve the space live data fills")
                    report.check(where, worst["inp"] <= BUDGET["inp"], f"INP {worst['inp']} ms for {tap!r} (budget 200 ms)",
                                 "show the pending state in the same frame")
                    report.lines.append(f"note  {where}  FCP {worst['fcp']} ms (reported, 1.8 s)")
                # The page as it rests, then with its panels open.
                page.goto(url + path)
                page.wait_for_selector(first, timeout=30000)
                page.wait_for_timeout(800)
                layout = page.evaluate(LAYOUT)
                layout_checks(report, where, layout, width)
                touched = {"at rest": touch_check(report, where, page, "at rest")}
                page.screenshot(path=str(out / f"{path.strip('/').replace('/', '-') or 'home'}-{width}.png"),
                                full_page=width == "phone")
                for state, selector in [("after the tap", tap)] + [(f"with {s!r} open", s) for s in opens.get(path, [])]:
                    if not page.locator(selector).count():
                        report.check(where, False, f"{selector!r} is on the page", "nothing to open")
                        continue
                    page.locator(selector).first.click()
                    page.wait_for_timeout(500)
                    touched[state] = touch_check(report, where, page, state)
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(300)
                report.data[where] = {"runs": runs, "layout": layout, "touching": touched}
            report.check(width, not errors, "no console errors", "; ".join(errors[:3]))
            report.data[f"{width} console errors"] = errors
            ctx.close()
        browser.close()

    (out / "report.json").write_text(json.dumps(report.data, indent=1), encoding="utf-8")
    print("\n".join(report.lines))
    print(f"\n{report.failed} failed; report and screenshots in {out}")
    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
