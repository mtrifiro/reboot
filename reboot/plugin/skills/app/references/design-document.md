---
title: The Proposed Design, Saved
impact: HIGH
impactDescription: The design is shown once, in the chat, and saved once, as the first entry of design/decisions.md, never edited after; from then on the code is the design (api/ and the feature files, drawn live by the developer dashboard), so nothing can drift from it, and the handoff says where the build departed from the proposal
tags: design, proposal, decisions log, dashboard, drift
---

# The Proposed Design, Saved

There is no `design/design.md`. The design is:

- **Shown** once, in the chat: the summary
  ([`design-messages.md`](design-messages.md), "The proposed design"),
  the response's own text, before any tool call of that response.
- **Saved** once, right after it, in the same response: the first
  entry of `design/decisions.md`, headed `## <date>: Design proposed:
  <App name>`, written with the Write tool (`mkdir -p design` first).
  Like every entry in the log it is never edited: it records what was
  proposed that day, and later entries say what changed.
- **Then the code.** The domain objects go into `api/` and the
  features into `tests/*.feature` (tagged `@wip`) as the build starts;
  from then on they are the design. The developer dashboard draws both
  live (**Models**, **Features**), so the design on screen is never out
  of date, and no document is kept up to date beside them (hotel-300
  to hotel-351: 23 of 24 `design.md` files still said "proposed",
  most with 5 to 21 code and test files newer than the document).

The summary is sent first and the entry written from it, never the
other way round: a build that wrote the whole design to a file then
went straight to the mockup, and the user never saw it (hotel-350,
hotel-351).

## The entry

The headings in this order, word for word, in the user's nouns, every
object, method, feature and rule named in code style (`Room`,
`Room.check_in`), never as a link: the entry is never edited, and a
link would break as the code moves.

```markdown
# <App name>: decisions

Why <app name> is what it is, one entry per decision, newest last. No
entry is edited: a later one that changes an earlier one names it. What
the app is now is the code, on the developer dashboard.

## <date>: Design proposed: <App name>

**Brief.** <Who uses <app name> ("(working name)" after it unless the
user named the app), on what screen, the task, the one question the
main page answers, and the palette by its name and colours ("House:
cream and navy").>

**Features, in build order**
1. **<First feature> (first)**: <user story in one line; what it lets
   them do, with the lifecycle of what it adds>. Rules: <each in plain
   words, as its feature file will say it>.
2. …

**Not in this build:** <what else a real app in the domain needs, one
line each; **Who may do what** among them until it is built>.

**Domain model**
- `<Type>`: one per <what>, keyed by <id>. It holds <fields>. It is its
  own object because <the rule it keeps, or why>.
- …
<More than six objects: the packages by area, and how they layer
(`design-packages.md`).>

**Pages**
- `<path>`: <what it shows and what the viewer can do there; the main
  page's line names its signature view and the question it answers
  (`web-app/references/ui-design.md`, "One Signature View"), and ends
  with "([mockup](comp/mockup.html))" once the comp is drawn.>

**Sign-in:** <who signs in, how in development (the development
sign-in's accounts Alice, Ben, Carlos, Dani and Esi). Before Who may
do what is built: "Everyone signed in can do everything for now; roles
come with Who may do what.">

**What Reboot does for you here:** <three or four clauses, in this
design's nouns: each object keeps its own state (no database); the
rule spanning objects is one transaction; the page is live; the
scenarios are the tests.>

- **Decided by you:** <every answer the user gave before the design
  (`design/interview.md`), the question and the answer, or "nothing
  asked">.
- **Assumed:** <every answer the build took without asking: the name,
  the palette, counts, hours, time zone; at most the five that shape
  the app most first>.
- **How:** <step by step | all at once | prompt by prompt | not chosen
  yet>.
```

The file's opening paragraph is written with the first entry only; a
later entry is appended under the last one.

## The mockup

The comp's line (`([mockup](comp/mockup.html))`) is the one addition
the entry may get after it is written, in the same build, before the
first handoff: the mockup is made right after the entry.

## Where the build departed from it

At each handoff, **Notes** says in a line each what the build changed
from the proposal ("`Room` gained `inspected_at`"; "Check-in's rule
became two: inspected, and not already occupied"; "`Stay` is new: a
guest's nights in one room"), read from the entry beside `api/` and the
feature files. Nothing changed: no line. The acceptance entry that
follows ([`accept-design.md`](accept-design.md), "The decisions log")
records the same, and `python3 scripts/model_diff.py` measures any
later change from that acceptance.

## Never

- `design/design.md`, or a document of the design kept beside the code
  and edited to match it.
- The entry written before the summary is sent, or in place of it.
- The proposal entry edited after the first handoff: a change is a
  new entry, or the code.
- The entry pasted into the chat: say in one line where it is, as a
  link.
