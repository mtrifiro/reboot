# The company logos kit's scenarios (web-app/references/company-logos.md).
# Copied into the project's tests/ as it stands; the custom steps are in
# logo_steps.py, copied beside it.
#
# The names below are the kit's, and the API table in the reference uses
# them. An app that keeps them changes nothing here. One that must name
# something else substitutes it everywhere, here and in logo_steps.py:
#   - `Logos`, the singleton the web app asks through, and its id "logos";
#   - `Logo`, one per company, whose id is the company's host;
#   - `ask` and its `hosts` field, and `get` on `Logo`;
#   - `InvalidHostError`, the typed error an ask with no public host gets;
#   - "alice", a signed-in development account, and "ben", who is not
#     signed in (the starter's accounts).
# The record's fields (`status`, `source`, `width`, `content_type`,
# `checked_at`, `fetching`) and the settings (`LOGO_SOURCE`,
# `LOGO_DEV_TOKEN`) are the kit's own and stay as they are.

Feature: Company logos come from the app, not from a third party
  Every company the app draws shows its logo. Fetched by each user's
  browser from a favicon service, a logo tells that service every
  company in the book as people scroll, and depends on an endpoint
  with no terms and no promise it stays up.

  So the app fetches each company's logo once, in the background,
  keeps it, and serves it itself.

  - The first time the web app draws a company with no logo kept, it
    asks for one and draws the initials meanwhile. Asks are gathered
    into one call to `Logos.ask` per page, not one per company.
  - The fetch is a workflow, `Logo.fetch`, so a restart finishes it
    rather than losing it, and asking again while one runs does not
    start another.
  - Where logos come from is one setting, `LOGO_SOURCE`: the company's
    own site (the widest of its apple-touch-icon, its declared icons and
    its /favicon.ico), or logo.dev with the key in `LOGO_DEV_TOKEN`.
    Each logo remembers which source was last asked; switching the
    setting refetches from the new source as logos are next asked for.
  - A logo is kept for thirty days, then refetched when next asked for.
    A company with none is asked about again after seven days, not on
    every page. Smaller than 32px counts as none: the initials read
    better than a blur.
  - A kept logo lives in the logo store, keyed by its host, and a page
    loads it from there: in production a bucket's public address, in
    development and the tests a directory the app serves at
    `/__/logo?host=`. The `Logo` record keeps what the check found (the
    source, when, the content type, the width) and never the image: a
    state is loaded and written whole, rides in every read and goes into
    every export, and an image belongs in none of those. Anyone with
    the address may read a logo; they are the companies' own public
    icons. Reading one never fetches; only a signed-in user's asking
    does.
  - Only a public host name is fetched: no IP addresses, no localhost,
    nothing under a private or reserved top level, nothing resolving to
    a private network, nothing over 512 KB, and no SVG, which can carry
    script.

  Background:
    Given the application is up
    And "alice" is an authenticated user

  Rule: Asking fetches a logo once, and keeps it
    @important
    Scenario: A logo asked for is fetched and kept
      Given the company site "acme.dev" offers a 180px icon
      When "alice" does an `ask` with `hosts=["acme.dev"]` on `Logos` of "logos"
      Then the logo of "acme.dev" eventually has `status="kept"` and `source="site"` and `width=180` and `content_type="image/png"` within 10 seconds

    Scenario: The address is kept without its scheme, path or www
      Given the company site "acme.dev" offers a 180px icon
      When "alice" does an `ask` with `hosts=["https://www.acme.dev/about"]` on `Logos` of "logos"
      Then the logo of "acme.dev" eventually has `status="kept"` within 10 seconds

    Scenario: The widest icon a site offers is the one kept
      Given the company site "acme.dev" offers a 32px icon and a 180px icon
      When "alice" does an `ask` with `hosts=["acme.dev"]` on `Logos` of "logos"
      Then the logo of "acme.dev" eventually has `status="kept"` and `width=180` within 10 seconds

    @important
    Scenario: A company with no icon is remembered as having none
      Given the company site "quiet.dev" offers no icon
      When "alice" does an `ask` with `hosts=["quiet.dev"]` on `Logos` of "logos"
      Then the logo of "quiet.dev" eventually has `status="missing"` and `width=0` within 10 seconds

    Scenario: An icon smaller than 32px counts as none
      Given the company site "tiny.dev" offers a 16px icon
      When "alice" does an `ask` with `hosts=["tiny.dev"]` on `Logos` of "logos"
      Then the logo of "tiny.dev" eventually has `status="missing"` within 10 seconds

    Scenario: A site whose page never answers is still asked for its favicon
      A site behind bot protection can stall its home page and still
      serve `/favicon.ico`. One URL failing takes only that URL out of
      the running, not the site.

      Given the company site "stall.dev" never answers for its page, and serves a 48px favicon
      When "alice" does an `ask` with `hosts=["stall.dev"]` on `Logos` of "logos"
      Then the logo of "stall.dev" eventually has `status="kept"` and `width=48` within 10 seconds

    Scenario: A page's worth of companies is one ask
      Given the company site "acme.dev" offers a 180px icon
      And the company site "globex.dev" offers a 64px icon
      When "alice" does an `ask` with `hosts=["acme.dev", "globex.dev"]` on `Logos` of "logos"
      Then the logo of "acme.dev" eventually has `status="kept"` within 10 seconds
      And the logo of "globex.dev" eventually has `status="kept"` and `width=64` within 10 seconds

  Rule: The image lives in the store, not on the record
    @important
    Scenario: A kept logo is put in the store, and the record says only what was found
      Given the company site "acme.dev" offers a 180px icon
      When "alice" does an `ask` with `hosts=["acme.dev"]` on `Logos` of "logos"
      Then the logo of "acme.dev" eventually has `status="kept"` within 10 seconds
      And the store holds a 180px "image/png" for "acme.dev"
      And as "alice", `get` on the `Logo` for "acme.dev" has `content_type="image/png"` and `width=180`

    Scenario: A fresher logo replaces the one in the store
      Given the logo of "acme.dev" was kept from "site" 31 days ago
      And the company site "acme.dev" offers a 64px icon
      When "alice" does an `ask` with `hosts=["acme.dev"]` on `Logos` of "logos"
      Then the logo of "acme.dev" eventually has `width=64` within 10 seconds
      And the store holds a 64px "image/png" for "acme.dev"

  Rule: A kept logo is asked for again only when it is due
    Scenario: Asking again for a fresh logo fetches nothing
      Given the logo of "acme.dev" was kept from "site" 1 days ago
      When "alice" does an `ask` with `hosts=["acme.dev"]` on `Logos` of "logos"
      Then the logo of "acme.dev" was last checked 1 days ago

    Scenario: A logo older than thirty days is fetched again
      Given the logo of "acme.dev" was kept from "site" 31 days ago
      When "alice" does an `ask` with `hosts=["acme.dev"]` on `Logos` of "logos"
      Then the logo of "acme.dev" is eventually checked again within 10 seconds

    Scenario: A company with none is not asked about again within seven days
      Given the logo of "quiet.dev" was found missing 2 days ago
      When "alice" does an `ask` with `hosts=["quiet.dev"]` on `Logos` of "logos"
      Then the logo of "quiet.dev" was last checked 2 days ago

    Scenario: A company an older fetcher found none for is asked about again at once
      The fetcher learns: a newer one finds icons an older one missed.
      A verdict of none from before it learnt is not worth waiting
      seven days on, so each verdict records the fetcher's version.

      Given the logo of "learnt.dev" was found missing by an older fetcher 1 days ago
      And the company site "learnt.dev" offers a 180px icon
      When "alice" does an `ask` with `hosts=["learnt.dev"]` on `Logos` of "logos"
      Then the logo of "learnt.dev" eventually has `status="kept"` and `width=180` within 10 seconds

    Scenario: A company with none is asked about again after seven days
      Given the logo of "quiet.dev" was found missing 8 days ago
      When "alice" does an `ask` with `hosts=["quiet.dev"]` on `Logos` of "logos"
      Then the logo of "quiet.dev" is eventually checked again within 10 seconds

  Rule: The source is one setting, and switching it refetches
    @important
    Scenario: With logo.dev set, logos come from logo.dev
      Given logos come from "logo.dev"
      And logo.dev offers a 128px logo for "acme.dev"
      When "alice" does an `ask` with `hosts=["acme.dev"]` on `Logos` of "logos"
      Then the logo of "acme.dev" eventually has `status="kept"` and `source="logo.dev"` and `width=128` within 10 seconds

    Scenario: A logo kept from the old source is refetched from the new one
      Given the logo of "acme.dev" was kept from "site" 1 days ago
      And logos come from "logo.dev"
      And logo.dev offers a 128px logo for "acme.dev"
      When "alice" does an `ask` with `hosts=["acme.dev"]` on `Logos` of "logos"
      Then the logo of "acme.dev" eventually has `source="logo.dev"` and `width=128` within 10 seconds

    Scenario: logo.dev without its key falls back to the site
      Given logos come from "logo.dev" without a key
      And the company site "acme.dev" offers a 180px icon
      When "alice" does an `ask` with `hosts=["acme.dev"]` on `Logos` of "logos"
      Then the logo of "acme.dev" eventually has `status="kept"` and `source="site"` within 10 seconds

  Rule: Only public hosts are fetched, and only a signed-in user's asking fetches
    Scenario Outline: A host that is not a public name is refused
      When "alice" attempts an `ask` with `hosts=["<host>"]` on `Logos` of "logos"
      Then the attempt aborts with `InvalidHostError`

      Examples:
        | host                     |
        | 127.0.0.1                |
        | localhost                |
        | 10.0.0.5                 |
        | metadata.google.internal |
        | northwind.test           |

    Scenario: A bad host among good ones is skipped, and the rest fetched
      Given the company site "acme.dev" offers a 180px icon
      When "alice" does an `ask` with `hosts=["localhost", "acme.dev"]` on `Logos` of "logos"
      Then the logo of "acme.dev" eventually has `status="kept"` within 10 seconds

    Scenario: Someone who is not signed in cannot ask for logos
      Given "ben" is an unauthenticated user
      When "ben" attempts an `ask` with `hosts=["acme.dev"]` on `Logos` of "logos"
      Then the attempt aborts with `Unauthenticated`

    Scenario: Anyone can read a kept logo
      Given "ben" is an unauthenticated user
      And the company site "acme.dev" offers a 180px icon
      When "alice" does an `ask` with `hosts=["acme.dev"]` on `Logos` of "logos"
      Then the logo of "acme.dev" eventually has `status="kept"` within 10 seconds
      And as "ben", `get` on the `Logo` for "acme.dev" has `status="kept"` and `width=180`
