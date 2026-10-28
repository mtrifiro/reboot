---
title: What Both Front Doors Share: the Proposal, the Scope Round, Names, Writing for a Reader, Routing a Change, What Never to Read
impact: HIGH
impactDescription: Shared by both front doors, so each rule is stated once. The design is a proposal until the user accepts it; the scope round, when a door is invoked directly; names for what a type holds; the design written in the domain's terms with a reason for every choice; a change routed to Design or Prove; generated or installed source never read whole, another skill's assets never read as an example, and an existing file changed by an edit, never a rewrite.
tags: design, proposal, scope round, names, writing, routing, generated code, reading budget, edits
---

## The Design Is a Proposal

**Always work out the design before writing code.** The state model
is the foundation: an entity, a field type or a method type wrong
means regenerating everything across the project. The design is a
proposal until the user accepts it: call it, and every part of it such
as the data model, proposed, never settled, set or final, in the
design and in every status line. One round of scope questions comes
before it (below), then the build runs without waiting again: one
feature at a time, each seen running, understood and accepted before
the user chooses the next; or the whole app first, accepted at its
handoff with the running app in front of them.

This is the first stage of the **Reboot Flywheel**: Design, then
Prove, then Observe, each ending in a decision that is the user's.
[`flywheel.md`](flywheel.md) has the stages, the heading each decision
opens with, and the routing rule that sends a change to the design
back to Design.

## The Scope Round

Ask one round of scope questions first, from the prompt alone, before
reading any reference or showing a design: one question dialog
(`AskUserQuestion` where available). Built from the
[`app-guided` skill](../../app-guided/SKILL.md), nothing is asked before the
design (the `app-design` skill takes the round's recommended answers,
under **Assumed**), and the
build starts right after the design, with no go-ahead
([`design-first.md`](design-first.md), section 3). Invoked directly,
the first question is how to build it, unless the prompt already says;
its options, the first recommended, are in the door's step 2, with
"Prompt by prompt: I say what to build at each step; ask me nothing" as the
last.
Then at most three more, on what the prompt left open and an answer
would change most, such as who signs in with which roles and what the
app keeps track of. Give each question two to four options, the
simplest first and marked as recommended, so accepting every
recommendation is one answer. Never an option that only means "say
what": every dialog has its own free answer. Don't ask about the look:
when the user named no brand or colours, take the house palette
(cream and navy, [`ui-design.md`](../../web-app/references/ui-design.md),
"Build the Look"), and say
in the brief that it is Reboot's own and easy to change later,
to another palette or to
their brand. Name the app too,
unless the prompt gives a name, and say the same of it. Don't ask what
the design can decide well on its own. Never ask about time zones:
every date and time is in the user's own time zone unless they say
otherwise, and it goes under **Assumed** in the decisions log. Ask
nothing more until the handoff.

## Names

Name each type for what it holds and is for, in the domain's own
words, never for its key or its time period. A type keyed by a gate
and a date is `GateSchedule` (one gate's flights and closures for a
day), not `GateDay`; a type keyed by a date is `DispatchBoard` (the
day's flights, and the rule that no aircraft or pilot is
double-booked), not `DispatchDay` or `Day`. The key says how an
instance is found; the name says what it is. Test each name: would
someone in the domain know what it holds without being told its id?
If not, rename it before the API is written, when a rename costs one
line.

## Writing the Design for a Human Reader

The design is read by a **human who has not read the skill files**.
They are judging the design — entities, collections, methods,
pages or tools, auth — not verifying that you followed the skill. Write
so it stands on its own.

**Don't quote skill-internal terms** when presenting the design.
They mean nothing outside this skill:

- `Shape A` / `Shape B` / `Shape C` — name the actual data
  structure: `list[Sub]` of inline sub-records, `list[str]` of
  foreign state IDs, `OrderedMap` of foreign state IDs.
- "non-state `Model`" — say "a flat sub-record created and
  deleted with its parent" or "no identity of its own", in domain
  terms.
- `Gotcha #N` and filenames like `state-collections.md` /
  `api-pydantic.md` —
  drop the citation; if the rule matters to the design, explain
  it inline.
- `factory=True`, `Field(tag=N)`, raw pydantic spellings — fine
  to mention briefly when the spelling itself is the design
  decision, but never as the explanation.

**For every design choice, give the what + the why.** The _what_
is the concrete data structure, method type, page or tool. The _why_
is a one-clause reason rooted in the user's domain ("grows
without bound, so we need pagination"; "no methods or auth of
its own, so it lives inline"; "logged-in users only, because the
document is per-account").

**Examples.**

Collection shape — BAD:

> `documents_index_id: str` — ID of an OrderedMap actor that
> holds this user's Documents (Shape C from
> state-collections.md — unbounded).

Collection shape — GOOD:

> `documents_index_id: str` — points to an OrderedMap that
> holds this user's Documents. An OrderedMap (rather than an
> inline list) because the document collection grows without
> bound and the dashboard will paginate / sort by recency.

Nested model — BAD:

> Comment and Revision are non-state Models — Shape A.

Nested model — GOOD:

> Comment and Revision live inline on Document as
> `list[Comment]` / `list[Revision]`. They don't get their own
> state actors because they have no lifecycle, methods, or auth
> independent of the Document they belong to.

**Exception.** When the precise type name _is_ what the reader
needs to see ("I'm proposing `OrderedMap` here, not `list[str]`"),
name the type — but pair it with the plain-English reason in the
same sentence. The rule is "no bare jargon", not "no technical
terms".

## Routing a Change

To change an existing app, route the change by the Flywheel's routing
rule ([`flywheel.md`](flywheel.md), "The routing rule";
`python3 scripts/model_diff.py` sorts it): a change to a domain
object, a rule or who may call goes back to Design; anything else
stays in Prove. A design change the user asked for is built and judged
at the next handoff; one they didn't ask for is shown and asked about
before code ([`accept-design.md`](accept-design.md)).

## Never Read Generated or Installed Source in the Main Thread

`*_rbt.py`, `*_rbt_react.ts`, `site-packages/`, `node_modules/`,
and codegen templates run to tens of thousands of lines. Every one
you open is re-sent on every remaining turn, which makes reading
them the most expensive way in the system to learn a fact.

The generated surfaces you need are written out in these
references: the generated client in the front door's own references
(`web-app/references/react-client.md`,
`python/references/react-generated-client.md` for an MCP App) and the
backend shapes in `python/references/`. Use them.

If something isn't covered, bound the output hard: a
targeted `grep -n … | head -40`, or `sed -n '<start>,<end>p'` over
a known range. Never a whole generated file, never an unbounded
recursive grep.

Another skill's assets are never read as an example, the quickstart's
hotel app included, and neither is another project on the machine (a
sibling folder, an earlier build): the starter `render.py` writes is
the example, already in the project and in the design's own names,
and the references say the rest. An asset is copied or rendered where
a step says to, never opened for its content.

## A Change Is an Edit, Never a Rewrite

A file that exists is changed with the Edit tool, the lines that
change and nothing more: taking `@wip` off a feature file is one
edit, adding a method to the API is one edit, a servicer's new rule
is one edit. Rewriting a whole file to change a part of it costs the
file's length in output every time (one build wrote seven feature
files and two servicers twice over), and a shell heredoc or a
`python3 -` script that rewrites a file costs the same and hides the
change from review. The Write tool is for a file that doesn't exist
yet.
