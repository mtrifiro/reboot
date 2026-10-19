---
title: The Design Document
impact: HIGH
impactDescription: design/design.md is where the user, and anyone after them, reads the accepted design. Each package, domain object, method, feature and rule in it is a link that opens that thing on the developer dashboard, drawn from the code, so the document can be checked against what was built.
tags: design, acceptance, dashboard, links, record
---

# The Design Document

`design/design.md` is first written as the proposed design (the
`app-design` skill, section 3; its **Methods** after the go-ahead),
then rewritten at the first acceptance and each later one
([`accept-design.md`](accept-design.md), "Once accepted"). After every
write, `python3 '<the app-design skill>/assets/design_page.py'` draws
it again as `design/design.html`, the page the user reads it in. It is the design as accepted, in the user's nouns, and
every package, domain object, method, feature and rule in it is a
dashboard link (`dashboard` skill, "Links to an Object or a Rule"):

- an object: `<dashboard>#/models?type=<package>.<Type>`, `<dashboard>`
  being `https://dashboard.<app>.localhost/` under portless or
  `http://127.0.0.1:9871/` on plain ports (`design_links.py --base`
  moves every link when that changes);
  a method appends `.<method>`;
- a feature: `#/features/<path>.feature`; a rule appends `/rules/<n>`,
  counted from 1 in file order.

The package is the folder under `api/`: `api/hotel/v1/` is `hotel.v1`.
Use the port the dashboard started on. A design proposed before anything
is built names these in code style instead, with no links, since the
dashboard has nothing to show yet; they become links once it does.

Each choice the decisions log explains links to its entry there,
`decisions.md#<anchor>`. The anchor is the entry's heading in
lowercase, with each space a hyphen and other punctuation dropped:
"## 2026-10-14: Design accepted: Front desk" is
`#2026-10-14-design-accepted-front-desk`.

## The shape

The headings in this order, word for word: the rules before the domain model that keeps them. Leave out **Architecture**
when there is one package and **Pages** for a backend only.

```markdown
# <App name>: the design

Status: accepted on <date>. Every object, method, feature and rule
below links to the developer dashboard, which draws them from the code.

## Brief

<Who uses <app name>, on what screen, the task, the one question the
main page answers, and the palette, one of the eleven by its
name. While the name is one the build picked, its first mention
here, in the first sentence, is followed by "(working name)".>

## Features and their rules

[<Feature title>](<feature link>)
- [<the rule's words, exactly as in the file>](<rule link>)
- …

Each rule's scenarios run as the test suite: <n> in all, <n> of them
driving the real page in a browser, with videos on the dashboard.

## Architecture: <n> packages

<Why it is split, and how the packages layer so none imports another
in a circle, linked to the entry that decided it.> ([see them on the dashboard](<#/models link>))

| Package | Objects | Imports from |
| --- | --- | --- |
| `<package>` | [<Type>](<link>), … | <packages, or nothing> |

## Domain model

- **[<Type>](<link>):** one per <what>, keyed by <id>. It holds
  <fields>. It is its own object because <the rule it keeps, or why>
  ([decided](decisions.md#<anchor of the entry that decided it>)).
- …

Each `<Type>` is named for what it holds, never for its key or its
time period: `AmenitySchedule` (one amenity's bookings for a day), not
`AmenityDay`; `DispatchBoard`, not `DispatchDay`
([`front-door-common.md`](front-door-common.md), "Names").

## Methods

Kinds: a **Reader** changes nothing; a **Writer** changes its own
object, one change at a time; a **Transaction** changes several
objects, all or nothing. <A **Workflow** runs until it is done, if any.>

**[<Type>](<link>)**

| Method | Kind | Who may call |
| --- | --- | --- |
| [`<method>`](<method link>) | <Kind> | <roles, in the user's words; "the app" for calls only the app makes> |

<Below each table, any kind or caller a decisions entry explains, one
line each, with its link: "`book` is a Transaction ([decided](…))".>

## Pages

- `<path>`: <what it shows and what the viewer can do there, naming
  what they drag where when something moves; what it leads with, which
  states carry colour and where the accent goes>. The main page's line
  names the app's signature view and the question it answers
  (`web-app/references/ui-design.md`, "One Signature View").

<When the build drew a comp (`web-app/references/comp.md`), the main
page's line ends with "([mockup](comp/mockup.html))", a link to the mockup
it is built to.>

## Sign-in

<Who signs in, how in development (the development sign-in's five
built-in accounts, Alice, Ben, Carlos, Dani and Esi) and at deploy.
Before Who may do what is built, one line: "Everyone signed in can do
everything for now; roles come with Who may do what." After it, the
role each account plays and what someone with no role sees.>

## What Reboot does for you here

<Three or four bullets, each said for this design, in its nouns,
naming what the developer doesn't write: each <Object> is a durable
object holding its own state (no database, tables or migrations); <the
rule that spans objects> is one transaction, all or nothing (no
rollback code); <the page> updates live when anyone changes it (no
polling or websocket code); each rule's scenarios are the tests (no
separate test harness); the same backend serves an MCP App for Claude
or ChatGPT (no second API).>

## Review table

<The review table from accept-design.md, one row per rule, the object,
rule and method cells links.>

## Decisions

Why the design is what it is, and what was assumed, is in
[`decisions.md`](decisions.md), one entry per acceptance:

- [<entry heading>](decisions.md#<anchor>): <one line, what it settled>.
- …
The design as accepted is copied to `accepted/`;
`python3 scripts/model_diff.py` lists anything changed since.
```

## Checking it

After writing it, run `python3 scripts/design_links.py` (copied from
this skill's `assets/scripts/`, beside `model_diff.py`) and fix what it
lists until it lists nothing:

- **Broken:** a link to an object, method, feature file or rule
  number the code doesn't have.
- **Renumbered:** a rule link whose words are no longer that rule's;
  a rule added above others renumbers them, so a later acceptance
  rewrites their links.
- **Not linked:** something in the code the document doesn't link,
  or a decisions entry it doesn't list.
- **Decisions:** a link to an entry `decisions.md` doesn't have, and
  in the newest entry, a link to nothing in the code or to a rule by
  its number.

When the dashboard runs on another port, `python3
scripts/design_links.py --port <port>` rewrites every link to it, in
`decisions.md` too (only the port changes).

## Never

- A name of an object, method, feature or rule in the document without
  its link.
- A choice the log explains, left without its link to the entry.
- A comp made and the main page's line without its link.
- A rule in other words than the feature file's: the link text is the
  rule's own words, so the check can see a renumbering.
- The document pasted into the chat: once written, say in one line
  where it is, as a link.
