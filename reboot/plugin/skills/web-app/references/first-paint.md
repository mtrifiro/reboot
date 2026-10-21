# Timing the First Paint

The browser check times the main page: from navigation to its first
record on screen. A page that appears is not yet a page that appears
fast, and a wait that passes (`wait .board`, "within 15 seconds") says
nothing about speed: a 7-second page passes it.

Open the main page as a signed-in user three times, and after each
navigation run this in the page, with a selector for one record of the
page's main list, board or grid:

```js
new Promise((resolve) => {
  const poll = setInterval(() => {
    const ms = performance.now(); // since this page's navigation began
    if (document.querySelector("<first record selector>")) {
      clearInterval(poll);
      resolve(Math.round(ms));
    }
    if (ms > 30000) {
      clearInterval(poll);
      resolve("timeout");
    }
  }, 25);
});
```

The first load after Vite starts can be slow while it prepares the
dependencies; note it, and judge the page on the second and third.

**The budget is 2 seconds** under `rbt dev run` with the demo data. A
page over it is a defect to find and fix before the handoff, not a
note in it: look for many calls or connections per record, a reader
that returns more than the page shows, or a backend still starting.
The handoff says the time the page took
([`app/references/design-messages.md`](../../app/references/design-messages.md),
**What it does**).
