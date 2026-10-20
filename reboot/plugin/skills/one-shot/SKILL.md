---
name: one-shot
description: Build a complete Reboot application in one go, asking nothing. Designs every feature a real product in the domain needs, not only those the prompt names, builds the whole app with every rule and scenario without stopping, and hands it over once, at the end. Use only when the user asks for it by name ("/reboot:one-shot", "one-shot", "one shot"); otherwise the app skill builds apps one feature at a time.
argument-hint: [<app-description>]
allowed-tools: Bash, Read, Write, Glob, Grep, Edit, Agent
---

# one-shot: a Complete Reboot Application, Asking Nothing

Load the [`app` skill](../app/SKILL.md) for its routing, then the
front door it routes to, and build the **whole app at once**: for a
web app, [`web-app/references/full-build.md`](../web-app/references/full-build.md);
for an MCP UI, its Step-by-Step Build Flow. The differences below
override them, and `app/references/design-first.md`'s go-ahead does
not apply: nothing stops the build until the end.

## 0. Say what will be built, first

The `app` skill's "First, Before Reading Anything" applies, before any
tool call, with three differences:

- **The paragraph** describes the complete app: who uses it, its
  features in one sentence, and which front door. **What to expect**
  is four lines:

  > What to expect:
  > - The proposed design, in a few minutes.
  > - Once the domain model is written, the Reboot dashboard opens with
  >   its link: the app's domain model and rules, updated as they're
  >   built.
  > - Then the whole app, every feature with its rules proven by
  >   scenarios, in an hour or more, without stopping.
  > - Nothing to answer until it's done; then one question: accept it
  >   as built, or change something.
- **The task list** has the whole-app items, with no go-ahead:

  1. Propose the design for <app>
  2. Scaffold the project
  3. Build the domain model
  4. Start the Reboot dashboard to show the domain model
  5. Build the actions, without their rules yet, and demo data
  6. Build every page of the design
  7. Start the app for you to see, and check it in a browser
  8. Write the <feature>'s rules as scenarios
  9. Prove the <feature>'s rules in the code
  10. Prove every rule (all scenarios pass, types check)
  11. Your turn: review <app>

  Items 8 and 9 come once for each feature, in the design's order,
  each named in full; for an MCP UI, item 6 is "Build every UI of the
  design" and item 7 "Start the app and check it in its AI client".
- **`app/references/design-first.md` does not apply:** no go-ahead.

## 1. Ambitious scope

Design the app a team in this domain would run its work on end to
end, not the smallest app that fits the prompt:

- **Every feature the prompt names,** and every feature a real product
  for these users needs to do their whole job: for a hotel, the rooms
  and housekeeping, reservations and the front desk, staff roles,
  guest profiles, amenity bookings, concierge requests, and the
  folio and billing. Aim for six to ten features, each with the rules
  that make it trustworthy.
- **Every role** that does that work, with what each may do.
- **Pages** for each role's daily work, each with its primary view.

Each feature added beyond the prompt goes under **Assumed** with one
line on why a real product needs it.

## 2. No questions

Ask nothing, from start to finish: no scope questions, no go-ahead on
the design, no acceptance between features. Take the answer the front
door would mark as recommended for each scope question, and decide
anything else the same way: the simplest choice that fits the
ambitious scope, listed under **Assumed**. Times are in the user's own
time zone.

## 3. The design document

Write the whole proposed design to `design/design.md` in the shape of
[`app/references/design-document.md`](../app/references/design-document.md),
status "proposed on <date>; being built now", with an **Assumed**
section after **Sign-in**. Show the proposed design in the chat as the
front door says, with the document's link, and go straight on to the
build in the same turn.

## 4. The build, without stopping

Build by the whole-app flow: the prototype first (with sub-agents for
the frontend where the host has them), then every feature in the
design's order, each with its rules and scenarios. Between features,
say in one line which is finished and go on; never wait for an
answer.

- **A failure:** fix it and go on. A scenario that can't pass after a
  real attempt is tagged `@blocked` with its reason, and the build
  goes on to the next feature; it is named at the handoff.
- **Something the design got wrong:** change the design document and
  the feature, note it for the handoff, and go on.
- **The prototype's "try it" message** is said in one line with the
  URL; the build doesn't wait for it.

## 5. One handoff, at the end

When every feature is built, every scenario passes or is `@blocked`
with its reason, and mypy is clean: the handoff in the shape of
[`app/references/design-messages.md`](../app/references/design-messages.md),
covering every feature, with `design/design.md` rewritten as built
and its links checked by `scripts/design_links.py`. Then the one
question the whole build asks: accept it as built, or change something.
On a yes, record the acceptance as
[`app/references/accept-design.md`](../app/references/accept-design.md)
says, with **Assumed** in the first decisions entry.

## Never

- A question, a dialog or a wait for an answer before the handoff.
- A smaller app than the domain needs because the prompt was short.
- A feature dropped silently: a feature that can't be finished is in
  the handoff, with what blocks it.
- A feature added without its line under **Assumed**.
