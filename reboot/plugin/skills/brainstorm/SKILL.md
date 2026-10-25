---
name: brainstorm
description: "Brainstorm a Reboot app's architecture in conversation, before any design or code: the domain objects and what each keeps, who calls whom, which calls must be one transaction, what runs on its own (workflows, schedules, outside services, AI agents), where it gets busy, and the front doors, each weighed as two or three shapes with what they cost, the user deciding. Ends with the decisions in design/architecture.md, which the app-design skill builds the design on. Use only when the user asks: '/reboot:brainstorm', 'brainstorm the architecture', 'talk through the architecture first'. Not the design (app-design), not a build (app), not a review of a built app (review-architecture)."
argument-hint: [<app-description>]
allowed-tools: Read, Write, Glob, Grep, AskUserQuestion
---

# brainstorm — Talk Through the Architecture First

A conversation with an architect who knows Reboot, before the design.
The `app` skill's design is high level: features, rules, pages, the
domain model drawn from them. This skill is for a user who wants to
shape the architecture underneath first, out loud: the objects, their
boundaries, the calls between them and what must never half-happen.
Nothing is built here: no code, no scaffold, no `rbt`, no
`design/design.md`. The user leads; the architect proposes, weighs and
asks.

> **The user sees only message text.** What the brainstorm proposes and
> why goes out as the response's own text, never only in thinking.

## 1. The opening

One short paragraph, sent as text before any tool call but the Skill
load:

1. "An app for <what it is>, used by <who>." (the user's nouns)
2. A first sketch in plain words: the three to six things it keeps
   track of, one line each, and the one place the architecture is
   decided ("the hard part is <it>").
3. "Let's shape the architecture together before anything is designed
   or built. Nothing here is code; when we're done I'll write down
   what we decided, and the design starts from it."

Then the first question, on the hard part. With no description, the
opening is one line asking what the app is for and who uses it.

## 2. The conversation

Read, with the Read tool, only when the topic comes up:
[`state-collections.md`](../python/references/state-collections.md)
and [`api-methods.md`](../python/references/api-methods.md) before the
first sketch is refined;
[`state-actor-decomposition.md`](../python/references/state-actor-decomposition.md),
[`patterns-cross-actor-reads.md`](../python/references/patterns-cross-actor-reads.md),
[`servicer-transaction.md`](../python/references/servicer-transaction.md),
[`servicer-workflow.md`](../python/references/servicer-workflow.md),
[`scheduling-recurring.md`](../python/references/scheduling-recurring.md),
[`agent-pydantic-ai.md`](../python/references/agent-pydantic-ai.md),
[`auth-roles.md`](../python/references/auth-roles.md) and
[`design-packages.md`](../app/references/design-packages.md) for their
own topics. Never read out; what they say becomes the trade-offs.

The topics, taken in the order the conversation reaches them, never as
a checklist read to the user:

- **The domain objects.** One per what, keyed by what, holding what.
  The hub keeps only its own job; each list a page reads is an index
  object of its area; the roster is its own object; one object holds
  one concern, since writers on one object take turns.
- **Who calls whom.** No object called by more than four others, no
  two that call each other. Reads across objects, and what each page
  reads to draw itself.
- **What must never half-happen.** The steps that are one transaction
  across objects (a booking and the room it holds), and those that
  may run apart.
- **What runs on its own.** Workflows that wait, retry or run for days;
  schedules; calls to outside services (each at most once or at least
  once, said); an AI agent and the tools it may call.
- **Where it gets busy.** How many of each object, the one many people
  write at once, and how it splits if it must.
- **The front doors and who signs in.** A web app, an MCP App for
  Claude and ChatGPT, or a backend only; the roles, if any.
- **Packages,** when there are more than six objects: by area, layered
  so none imports another in a circle.

Each turn:

- **Short.** A few lines, or a small table of objects (object, one per,
  keeps, called by) when the shape changed.
- **A decision is two or three shapes,** each in a line with what it
  costs now and later, and a recommendation. A choice between named
  shapes is a dialog (AskUserQuestion, the recommendation first); an
  open question is one plain line.
- **Reboot's terms explained once,** in a clause, the first time:
  domain object, reader, writer, transaction, workflow.
- **The user's word decides.** A shape the user picks against the
  recommendation is taken, with its cost said once.

## 3. Writing it down

When the user says they are done, asks for the design or the build, or
every topic above has been decided or set aside, write
`design/architecture.md` in one write:

```markdown
# <the app>: architecture notes

From a brainstorm on <date>. The design builds on these; each is
open to change until the design is approved.

## Domain objects

| Object | One per | Keeps | Called by |
| --- | --- | --- | --- |

## Decisions

- **<the decision>.** <what was chosen>, over <the alternatives>,
  because <why>.

## Open

- <what was set aside, and what would decide it>
```

Then one line, "Saved the architecture to design/architecture.md; the
design starts from it.", and in the same response the dialog
(AskUserQuestion), header "Next", question **Build it now?**:

- **Design and build it (Recommended):** "The guided build: a design on
  these decisions to approve, then each part built and explained."
- **Design it only:** "The design and its page, nothing built yet."
- **Keep talking:** "More to decide first."

On the first, load the [`app-guided` skill](../app-guided/SKILL.md)
with the Skill tool; on the second, the
[`app-design` skill](../app-design/SKILL.md); either's argument is the
app's description followed by ", from the brainstorm". A free answer
that asks to build or design it is the same. On the third, or a free
answer about the architecture, the conversation goes on and the notes
are rewritten when it next ends.

## Never

- Code, a project scaffold, `rbt`, a dependency, or `design/design.md`.
- A long lecture: a turn the user must scroll is too long.
- A decision taken for the user without saying so.
