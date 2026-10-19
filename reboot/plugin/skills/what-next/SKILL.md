---
name: what-next
description: Suggest the next 4 to 6 features for a Reboot app from evidence - every feature and rule already built, the design and its decisions, and original research on the app's domain (how comparable products and real businesses of this kind work, what their users expect, what they complain about, the rules of the trade), each source linked. Finds the gaps (people the design names with nothing to do, cycles left open, states no action reaches), weighs each candidate by who it serves, how often, what it unblocks, its size and what Reboot does well for it, writes design/what-next.md and asks which to build next. Use when the user asks what to build next, for a roadmap, for feature ideas, for what's missing, or how the app compares with others like it. Not for reviewing the domain model (domain-review) or the look (ui-review).
argument-hint: '[optional: a focus, e.g. "for the front desk" or "what competitors have"; the whole app by default]'
allowed-tools: Bash, Read, Write, Glob, Grep, WebSearch, WebFetch, AskUserQuestion
---

# what-next — What to Build Next, From Evidence

Suggests the next four to six features for an app that is already
built, each one argued from three kinds of evidence: what the app has
(its features, rules and design), what it is missing (gaps the design
itself reveals), and what the world says (original research, linked).
A suggestion with no evidence behind it isn't made.

## 1. Take stock of what's built

One line first: "Looking at what <app> does today, then at how
<domain> works elsewhere, to suggest what to build next."

From the project root, run
`python3 <this skill>/assets/features.py`. It lists every feature,
its rules and how many scenarios each has, with their tags (`@wip`,
`@blocked`; the [`feature` skill](../feature/SKILL.md)), and from `design/design.md` the
people the brief names, the cycles it names (*booked → checked in →
checked out*) and every name still in code style, which the design
uses for what isn't built yet. It also lists what
`design/decisions.md` records as ruled out. Then read
`design/design.md` itself, and any `design/review.md` or
`design/look-review.md`. Never read generated code.

## 2. Find the gaps

From the inventory, one list, each gap with where it shows:

- **People with nothing to do.** Each person or role the brief names,
  against the features that serve them. (For a hotel: housekeeping
  and the concierge are named, with no feature yet.)
- **Cycles left open.** Each cycle, against the actions that move it:
  a stay that can be booked but never checked out, a state no action
  reaches or leaves.
- **Things kept and never used.** A field or object the design keeps
  that no feature reads or shows.
- **Rules a real business needs** that the features don't state: a
  cancellation deadline, a deposit, a limit.
- **What the design already promised:** the code-style names, and the
  handoff's earlier **Build next** list.

## 3. Original research

Research the domain the way a product lead would before a planning
meeting, with WebSearch and WebFetch: five to ten searches, a few
pages read in full. Say what is being looked up in one line before
the first search ("Looking up how boutique hotels run housekeeping
and guest requests.") and, after, one line on what was found.

- **The business itself,** when the prompt names a real one: what it
  offers, its size, what its customers say (reviews, its own site).
- **Comparable products:** the established tools for this kind of
  business (for a hotel: property-management and guest-messaging
  systems), what they treat as basic, and what they charge extra for.
- **The people's own words:** what staff and customers of businesses
  like this complain about or ask for (reviews, forums, trade press).
- **The rules of the trade:** regulations and conventions that shape
  what the app must do (guest registration, payments, accessibility,
  privacy).

Every fact used later carries its source, linked, and the date it was
read. A fact that can't be found is said as not found, never filled
from memory. Recall is fine for where to look; it is never evidence.

## 4. Weigh the candidates

Gather the candidates from the gaps and the research, then judge each
on:

- **Who it serves and how often:** the people, and whether they would
  use it hourly, daily or rarely.
- **What it closes or unblocks:** a cycle it completes, a person it
  gives work to, features that need it first.
- **The evidence:** the gap it fills and the research behind it.
- **Its size:** the domain objects and methods it adds, said in the
  measured times (a feature is about 15 to 20 minutes; one that adds a
  new kind of person or a workflow, more).
- **What Reboot does well for it:** a scheduled job that survives a
  restart (a nightly audit), a workflow that calls a payment or an
  email once (a deposit), live pages (housekeeping's board), the same
  backend in Claude or ChatGPT (a concierge an AI can act for). Say it
  only where it is true of this feature.

Drop a candidate that is already built, that `decisions.md` ruled out,
or that only restates another. Order the rest: first what closes an
open cycle or gives a named person their first job, then by how often
it is used, then by size.

## 5. The analysis

One message, headed **What next: <app>**:

1. **Where it stands,** two or three sentences: what the app does
   today, for whom, and the biggest gap.
2. **What the research found,** three to six facts that change what to
   build, each with its linked source.
3. **The next features,** four to six, in order. Each:
   - its name, as the user would ask for it, and who it is for;
   - what it adds, with its rules in plain words (two to four);
   - why now: the gap it closes and the evidence;
   - what it builds on, and its size;
   - what Reboot brings to it, where that is true.
4. **Considered and left out,** one line each, with why.

Write the same to `design/what-next.md` with the date and the
sources. Change no other file.

Then one dialog:

- **What should I build next?** The top three or four suggestions,
  each its name as the label and its one-line reason as the
  description, the first marked "(Recommended)". The free answer
  takes another, or none.

A feature chosen is built as the app's front door builds each next
feature (the `web-app` or `mcp-ui` skill's Update Flow, through the
[`feature` skill](../feature/SKILL.md)), and choosing it accepts the
current one, as `app/references/accept-design.md` says.

## Never

- A suggestion without evidence from the app or the research.
- A research fact without its link, or one taken from memory.
- A feature `decisions.md` ruled out, or one already built, suggested
  again.
- More than six suggestions: the point is to choose.
- Editing the app: the analysis writes only
  `design/what-next.md`. Never while a build is working in the
  project (a test run in progress, another session writing to it).
