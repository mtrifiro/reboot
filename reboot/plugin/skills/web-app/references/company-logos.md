---
title: Company Logos, Fetched Once and Kept
impact: MEDIUM
impactDescription: An app about companies looks unfinished without their logos, and fetching a site's icon from the browser leaks the user's address, breaks on bot protection and hits every site on every page view; fetched once on the backend and kept, every logo loads from the app
tags: logos, favicon, companies, organizations, accounts, crm, workflow, ssrf, images, kit
---

# Company Logos, Fetched Once and Kept

**Read when** the design's objects are companies or organizations
with a website (accounts, vendors, clients, partners): each is shown
with its own logo. Not for people (an `Avatar`, `ui-design.md`), and
not for an app whose records have no domain.

The pattern comes as a kit in `web-app/assets/logos/`, taken from an
app that runs it (reboot-crm): the scenarios that say what it does,
their custom steps, and the safety checks a build must not rewrite.
The rest, the servicers, the store, the route and the page's `Logo`,
the build writes until the scenarios pass.

## 1. Copy the kit

- `company_logos.feature` and `logo_steps.py` into `tests/`, and a
  module that runs them (`from logo_steps import *`, the
  `application` fixture, `scenarios("company_logos.feature")`; the
  steps' docstring has it). In `logo_steps.py`, `__pkg__` becomes the
  app's package; the feature file's header lists the names it assumes.
- `logo_safety.py` into `backend/src/`, and `logo_safety_test.py`
  into `tests/`. Copied as they are, never edited.

The scenarios fake the web through the app's `logos.get` and set the
clock through `logos.now`; the interface they need is at the top of
`logo_steps.py`. Never the network in a test.

## 2. Add the API types

| Type | Field or method | Kind | Notes |
| --- | --- | --- | --- |
| `Logo` (id: the host) | `host`, `status`, `source`, `checked_from`, `content_type` | `str` | `status` is `"kept"`, `"missing"` or blank; `source` is `"site"` or `"logo.dev"` |
| | `checked_at`, `fetch_asked_at` | `float` | epoch seconds |
| | `width`, `fetcher` | `int` | `fetcher`: the site fetcher's version behind a verdict |
| | `fetching` | `bool` | a fetch is under way |
| | `create` | factory writer, app-internal | called by `Logos.want_all` |
| | `want` | writer, app-internal | schedules `fetch` when due and none is under way |
| | `get` | reader, `allow()` | returns every field above but `fetch_asked_at` |
| | `fetch` | `Workflow`, app-internal | |
| `Logos` (singleton `"logos"`, no factory: `ask` constructs it) | `ask(hosts: list[str])` | writer, signed in | refuses with `InvalidHostError(host, reason)` when no host is public |
| | `want_all(hosts: list[str])` | `Workflow`, app-internal | `create` (catching `StateAlreadyConstructed`), then `want`, per host |

No field holds the image.

## 3. Write it until the scenarios pass

- **`Logos.ask`** normalizes each host (`logo_safety.normalize_host`),
  skips any that isn't `public_name`, and schedules `want_all` with the
  rest; with none left, the typed error.
- **Due** when never checked, checked from another source, found
  missing by an older `SITE_FETCHER`, kept 30 days ago, or found
  missing 7 days ago.
- **`Logo.fetch`** (`python/references/servicer-workflow.md`): the
  source read once in an `at_least_once` step, so a replay finishes
  from the source it started with; the fetch and the put into the
  store in one step, returning only the content type and width, so
  the image is never memoized; then the record.
- **The fetch,** in `backend/src/logos.py`: from the site, the home
  page read with `read_capped(…, MAX_PAGE_BYTES, keep_first=True)`,
  its `declared_icons`, then `/favicon.ico`, at most five, the widest
  `keepable` image winning; or logo.dev (`LOGO_SOURCE`, its key
  `LOGO_DEV_TOKEN` an application secret, asked with `fallback=404`),
  falling back to the site without its key. Every hop through `get`:
  `fetchable_url`, then `resolves_publicly`, redirects followed by
  hand and checked the same way, `BROWSER_HEADERS` sent (bot
  protection stalls a request that names itself). One URL failing
  takes only that URL out of the running.
- **The store,** `backend/src/logo_store.py`, keyed by the host: a
  directory in development and the tests (`LOGO_STORE=dir`), a bucket
  served from its public address in production.
- **The route,** `application.http.get("/__/logo")`: the host
  normalized and checked, then the store's image with `SERVE_HEADERS`,
  or a 404 with `NOT_KEPT_HEADERS`; a bucket's address is a 302 to it.
  Reading never fetches.

## In the page

A `Logo` beside the company's name, in this order:

1. **Initials first,** an `Avatar` tile from the company's name, so
   the row is never empty and nothing shifts when the image arrives
   (the image has the tile's fixed width and height).
2. **The kept image,** `<img loading="lazy">` from the app,
   `/__/logo?host=<host>`, the host normalized the same way as
   `normalize_host` (a `logoHost` in TypeScript). A personal address
   (a Gmail) has no company host: never looked up, or every badge
   scanned with one shows Google's logo.
3. **A 404 means "not kept yet".** The image's `onError` asks for it
   and shows the initials meanwhile.
4. **Asks are gathered,** 300 ms at a time, into one `Logos.ask` for
   the page, each host asked once a session, from inside the signed-in
   app.
5. **One look again,** a few seconds later, with `&retry=1` so the
   browser doesn't answer from its cached 404; still none, the
   initials stay.

## Never

- A logo fetched from the browser (a third-party favicon URL in an
  `<img>`): it tells that service who is looking, and fetches on every
  view.
- The image in a Reboot state, or memoized on a workflow.
- A fetch that skips `logo_safety`: a host that isn't a public name,
  an address that isn't public, a redirect followed unchecked, a body
  past its cap, an SVG, or a content type trusted over `sniff`.
- An edit to `logo_safety.py` or the scenarios to make a build pass.
- A blank where the logo goes, or a row that shifts when it arrives.
