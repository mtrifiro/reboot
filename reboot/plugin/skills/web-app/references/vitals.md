# Timing the Page: First Record and the Web Vitals

The browser check times every page the feature adds or changes, as a
person meets it: how soon there is something on screen, how soon the
page's own content is there, whether it jumps while it loads, and how
quickly it answers a tap. A page that appears is not yet a page that
appears fast, and a wait that passes (`wait .board`, "within 15
seconds") says nothing about speed: a 7-second page passes it.

The numbers are [web.dev's](https://web.dev/articles/vitals), measured
in the lab: one headless browser on this machine under `rbt dev run`,
not the field's real users. They catch a page that got slower or
jumpier; they don't promise what users on slow phones will see.

| Measure | Budget | What it says |
| --- | --- | --- |
| **First record**: the page's first record of its main list, board or grid on screen | 2 s | The page's own content is there |
| **LCP**, Largest Contentful Paint | 2.5 s | The biggest thing on the first screen is painted |
| **CLS**, Cumulative Layout Shift | 0.1 | How much the page jumped as it loaded (0 is none) |
| **INP** (lab), the main action's tap to the next paint | 200 ms | The page answers a tap at once |
| **FCP**, First Contentful Paint | 1.8 s, reported | Anything painted at all; says where a slow page's time went |

## The script

In the Playwright script of the browser check (the `web-app` skill,
step 10), add this before the first navigation, so it watches every
page from its start:

```python
page.add_init_script("""
window.__vitals = { lcp: 0, cls: 0, inp: 0 };
new PerformanceObserver((l) => { for (const e of l.getEntries()) window.__vitals.lcp = e.startTime; })
  .observe({ type: "largest-contentful-paint", buffered: true });
new PerformanceObserver((l) => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__vitals.cls += e.value; })
  .observe({ type: "layout-shift", buffered: true });
new PerformanceObserver((l) => { for (const e of l.getEntries()) if (e.interactionId) window.__vitals.inp = Math.max(window.__vitals.inp, e.duration); })
  .observe({ type: "event", buffered: true, durationThreshold: 16 });
""")
```

Then, for each page, signed in, three times: navigate, and time the
first record with a selector for one record of the page's main view:

```python
FIRST = """(sel) => new Promise((resolve) => {
  const poll = setInterval(() => {
    const ms = performance.now(); // since this page's navigation began
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

first = page.evaluate(FIRST, "<first record selector>")
page.wait_for_timeout(1000)  # live data still arriving can still shift the page
loaded = page.evaluate(READ)  # fcp, lcp, cls: before any tap, which ends LCP
page.click("<the page's main action>")  # a real click, so the browser times it
page.wait_for_timeout(500)
inp = page.evaluate(READ)["inp"]
```

The main action is the one the design's page line puts the accent on,
or opening the first record (a room's drawer): one that changes the
page without leaving it. One that submits a form is timed once its
fields are filled.

The first load after Vite starts can be slow while it prepares the
dependencies; note it, and judge each page on its second and third
runs.

## Reading the numbers

Each number over its budget is a defect to find and fix before the
handoff, not a note in it:

- **First record or LCP late, FCP early:** the page is up and waiting
  on data. Look for many calls or connections per record, a reader
  that returns more than the page shows, a sign-in round trip before
  the first read, or a backend still starting.
- **FCP late:** the screen stays blank while the bundle loads and
  React starts. Look for a heavy import on the first page, or put the
  app's band and page title in `index.html` so they paint before any
  script runs.
- **CLS over 0.1:** something moved under the reader's eye. Reserve
  the space live data will fill (a list's rows at their height, a
  figure's box) before it arrives, never a spinner that the content
  then replaces at a different size, and open drawers over the page,
  not into it ([`ui-design.md`](ui-design.md), "Nothing Jumps, Every
  Tap Answers").
- **INP over 200 ms:** the tap's own handler is slow (work done before
  the page repaints). Show the action's pending state in the same
  frame and do the work after; never wait for the backend's answer
  before anything on screen changes.

The handoff says the first record's time and any vital near its
budget ([`app/references/design-messages.md`](../../app/references/design-messages.md),
**What it does**).
