---
title: The Reboot Flywheel
impact: HIGH
impactDescription: Without it the agent builds past a design the user never accepted, or sends a change to what the app does through as a code fix
tags: flywheel, design, prove, observe, accept, merge, promote, routing
---

## The Reboot Flywheel

Every app these skills build moves through three stages, in a loop.
Each ends in a decision that belongs to the user:

| Stage | The question | Where it happens | Ends with |
| --- | --- | --- | --- |
| **Design** | Does the design say what the user means? | The scope questions, the proposed design, and the first feature or the full prototype, running (the front door's Workflow and build flow) | **Accept**: the user accepts the design, from the running app |
| **Prove** | Does the code do what the accepted design says? | The full suite and mypy on the developer's machine (the `feature` skill, Step 4), then the pull request if the team uses them | **Merge**, then **Promote** (the `deploy` skill) |
| **Observe** | What is the running app doing, and why? | Stored state, read with the `inspect` skill | A finding becomes a ticket, and a scenario that reproduces it |

Read this when it is unclear which stage a piece of work is in, when a
change might alter the design, or when the user asks where things
stand.

### Design includes the prototype

Design is not a diagram drawn before the code. The agent builds the
design as a working app, because a running app is what lets the user
judge it: the objects, the rules, the pages. Design ends when the user
accepts that design, not when the code is written.

The user comes in one of two ways, and both end the same way:

- **Spec first:** the user brings a ticket or a spec. Check the domain
  objects and the feature files against it, and name each place the
  design departs from it.
- **Build first:** the user asks for the app and corrects what it got
  wrong. The prototype is the spec.

### Prove starts on the developer's machine

Evidence starts locally, before any pull request: the full suite and
mypy at the commit being proposed. A partial run (`-k`, one module,
`-m wip`) is evidence for the work in progress, never for a merge or a
deploy. The same revision then moves through the team's pull request
and CI, staging if they have it, and production.

### The Flywheel follows the team's process

The team keeps its tracker, its pull requests and CI, its deploy and
its observability product. The skills add evidence where each of those
decisions is already made, and never accept, merge or deploy for the
user. Follow what the project already does: `main` or a branch per
change, its CI, its ticket ids. The evidence for a merge and a deploy,
and the files that carry it, are in [`evidence.md`](evidence.md).

### Git

The Flywheel needs no repository: acceptance is the files in `design/`.
Commits, branches and pushes follow the user and the team's own
process; the build commits, pushes or adds a remote only when asked. A
pull request asked for carries the evidence
([`evidence.md`](evidence.md)).

### The routing rule

Every change, from a ticket, a failed scenario or a production
finding, goes to one stage, measured from the design the user
accepted: the copy in `design/accepted/`
([`accept-design.md`](accept-design.md)):

| Change | Goes to |
| --- | --- |
| A domain object, field, method, method kind, request or response, or `description=` added, removed or changed under `api/` | **Design**: accept again |
| Who may call a method: a servicer's `authorizer()` added, removed or changed, or a check it calls | **Design** |
| A `Feature:` or `Rule:` added, removed or reworded, or a feature's description | **Design** |
| A scenario removed, or an existing scenario's steps changed | **Design** |
| Other code under `backend/`, `web/` or `frontend/` | **Prove** |
| A new scenario under a `Rule:` that already exists (a fix's reproducing case) | **Prove** |
| `@wip` taken off a scenario, with the user's agreement | **Prove** |

`python3 scripts/model_diff.py` sorts every change by this rule,
measured from the acceptance (`<base>` names a git revision instead;
`--head` measures committed work only). Use it; never judge by eye. It lists
each change as `[design]` or `[prove]`, under the domain model, who
may call and the feature files, and says whether a full test run
happened since the acceptance. An authorizer is design written as
code, so every change to one is listed as Design, even one that only
carries out the accepted design; say which.

A design change the user asked for in their own words ("no check-in
before 3 pm") needs no question first: their words are the agreement.
Say which rule changes, build it, and the user judges it at the next
handoff ([`accept-design.md`](accept-design.md)). A design change they
didn't ask for, such as a fix that turns out to need a reworded rule or
a looser authorizer, stops before more code: say which rule or
declaration changes and why, show the slice of the model it touches,
and ask in the question dialog before writing more. Ask
nothing the build can assume: a time such as "3 pm" is in the
user's own time zone unless they say otherwise.

### At each decision: the stage cards

Each decision's message opens with a heading naming the stage and what
it asks, in the user's nouns: **Reboot Design · <App name>, the
proposed design**,
**Reboot Design · ready for your review**, **Reboot Prove · built and
tested**, **Reboot Prove · ready to deploy**, **Reboot Observe**. The
heading appears once per decision, never as a label on every message.

The first time a project reaches one of these moments, say where the
work stands with a short card under the heading, in the user's own
nouns and two or three of their own rules; after that, the moment gets
one line ("11 of 12 pass; the merge needs the last one"). The models
below are the hotel; write yours.

The two Design messages, the proposed design and the handoff, are
not cards: they follow [`design-messages.md`](design-messages.md) word
for word, and the handoff's ask is as
[`accept-design.md`](accept-design.md) says.

> **Reboot Prove · built and tested.** The full test suite ran at this
> commit: 11 of 12 scenarios pass; the one that doesn't is "A guest
> cancels the day before check-in". This is the stage where the code
> is checked against the design you accepted. If you open a pull
> request, its description lists the rules the change touched first,
> so you can decide how much code you want to read.

> **Reboot Prove · ready to deploy.** The dry run shows what would
> ship: two commits since the last deploy, no change to the design,
> and a full passing run of this exact commit. Deploying is yours to
> call.

Then the question dialog: deploy now, or not yet.

> **Reboot Observe · live.** The app is running in production. If a
> report comes in, `rbt inspect` reads the stored state behind it, and
> the fix starts from a scenario that reproduces it.

A fix closes with its own card, **Reboot Prove · the fix is in**: the
reproducing scenario, now passing, and the full suite's count. The pull
request sentence appears only when the work is on a branch.

When a card stops for the user's call (the design, the deploy), the
ask is a question dialog (`AskUserQuestion` where available;
elsewhere, one plain line as the message's last), the recommended
answer first. Every dialog already has a free answer with a text box,
so never offer an option that only means "say what to change" ("Something's
different", "Something's off"). Say what the user gains, not what the build withholds:
"the cheapest moment to change it", never "nothing is built until you
accept".

### Where the work stands

Asked where things are, answer with the stage and the next decision:
"Prove: 11 of 12 scenarios pass; the merge needs the last one", not a
list of files touched.

## Never

- Writing a later feature's implementation before its slice of the
  design is agreed, unless the user said up front to build on. No
  answer is not acceptance.
- Folding a rule change into a "fix": a reworded `Rule:`, a changed
  declaration or a loosened authorizer is a Design change however
  small the diff.
- Accepting, merging, deploying or pushing for the user: they decide;
  the skills show the evidence.
- Treating a partial test run as evidence for a merge or a deploy.

## Limits

- Acceptance is `design/accepted.json` and the copy in
  `design/accepted/`, with the reasons in `design/decisions.md`
  ([`accept-design.md`](accept-design.md)). `model_diff.py` does not see a
  domain model built at import time.
- Observe today is stored state only: `rbt inspect` and the
  `/__/inspect` page. There are no per-request traces.
