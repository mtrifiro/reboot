---
title: Company Logos, Fetched Once and Kept
impact: MEDIUM
impactDescription: An app about companies looks unfinished without their logos, and fetching a site's icon from the browser leaks the user's address, breaks on bot protection and hits every site on every page view; fetched once on the backend and kept, every logo loads from the app
tags: logos, favicon, companies, organizations, accounts, crm, workflow, ssrf, images
---

# Company Logos, Fetched Once and Kept

**Read when** the design's objects are companies or organizations
with a website (accounts, vendors, clients, partners): each is shown
with its own logo. Not for people (an `Avatar`, `ui-design.md`), and
not for an app whose records have no domain.

The pattern, from an app that runs it (reboot-crm,
`company_logos.feature`): the browser always shows something at once,
the backend fetches each logo once, safely, and keeps it, and nothing
is fetched again until it is due.

## In the page

A `Logo` beside the company's name, in this order:

1. **Initials first,** an `Avatar` tile from the company's name, so
   the row is never empty and nothing shifts when the image arrives
   (the image has the tile's fixed width and height).
2. **The kept image,** `<img loading="lazy">` from the app,
   `/__/logo?host=<host>`, the host the company's domain lower-cased,
   with no scheme, path, port or `www.`, the same on both sides. A
   personal address (a Gmail) has no company host: never looked up,
   or every badge scanned with one shows Google's logo.
3. **A 404 means "not kept yet".** The image's `onError` asks for it
   and shows the initials meanwhile.
4. **Asks are gathered,** 300 ms at a time, into one call for the
   page (`Logos.ask` with every host), each host asked once a session:
   a page of a hundred companies sends one call.
5. **One look again,** a few seconds later, with `&retry=1` so the
   browser doesn't answer from its cached 404; still none, the
   initials stay.

## In the backend

- **`Logo`,** one object per host (its id), holding only what the
  last check found: kept or none, the source, when, the content type,
  the width. Never the image: a state is loaded and written whole and
  goes into every reader's response. The image goes to a store keyed
  by the host: a directory the app serves at `/__/logo` in development
  (`application.http.get("/__/logo")`, a reader that anyone may call),
  a bucket served from its public address in production.
- **`Logos.ask`,** a writer on a singleton, takes a page's hosts,
  skips any that isn't a public name, and calls each `Logo`'s `want`,
  which schedules `fetch` only when one is due and none is under way.
- **`Logo.fetch`,** a `Workflow` (`python/references/servicer-workflow.md`,
  "Bucket 2"): the fetch and the put into the store in one
  `at_least_once` step, so the image is never memoized on the
  workflow; then the record. Its source is read once, inside a step,
  so a replay finishes from the source it started with.

## The fetch

From the company's own site: its home page read only as far as the
icons its `<head>` declares (the apple-touch-icon first, usually the
largest), then `/favicon.ico`; the widest image at least 32 px wide
wins (a 16 px icon blown up reads worse than initials), at most
512 KB, a few candidates at most. A logo API (logo.dev, a key as an
application secret) can be the source instead, one setting; without
its key the setting falls back to the site and says so in the log.

**Never a fetch the user's input can aim at the app's own network:**
every host fetched is a public name (no `localhost`, `.local`,
`.internal`, no address literal) that resolves only to public
addresses, checked again at each redirect. Send a browser's ordinary
headers: bot protection stalls a request that names itself until it
times out.

## When it is fetched again

| Found | Asked again |
| --- | --- |
| A logo | after 30 days; served meanwhile, even if a later check finds none |
| None | after 7 days |
| A change of source | at once |

## Its rules, proven

Its own feature file, `tests/company_logos.feature`, with a
fetcher the tests swap for a fake (never the network):

- A logo asked for is fetched and kept; the host is kept without its
  scheme, path or `www.`.
- The widest icon a site offers is the one kept; one under 32 px
  counts as none; a site with none is remembered as having none.
- A page's worth of companies is one ask.
- The image lives in the store; the record says only what was found.
- A fresh logo isn't fetched again; one older than 30 days is; a
  "none" is asked again after 7 days; a new source refetches.
- A host that isn't a public name is refused with its typed error.

## Never

- A logo fetched from the browser (a third-party favicon URL in an
  `<img>`): it tells that service who is looking, and fetches on every
  view.
- The image in a Reboot state, or memoized on a workflow.
- A fetch of a host that isn't a public name, or a redirect followed
  without the same check.
- A blank where the logo goes, or a row that shifts when it arrives.
