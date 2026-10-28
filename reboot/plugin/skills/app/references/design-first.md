---
title: The Design First, Then How to Build It
impact: HIGH
impactDescription: After the app-design skill's round and proposed design, the app-guided skill builds with no go-ahead; in the first feature, the domain model said in a line with what changed, nothing asked; the prompt-by-prompt path asks none of them.
tags: go-ahead, domain model, frontend, dialogs, design, prompt by prompt
---

# The Design First, Then How to Build It

How the `app-guided` skill builds a new app, in either front door, once the
[`app-design` skill](../../app-design/SKILL.md) has said the opening and
shown the proposed design, asking nothing (the round's recommended
answers, under **Assumed**). It replaces the front
door's round of scope questions.

## 1–2. The opening, the round, the design

The `app-design` skill's, loaded first by the `app-guided` skill. Nothing is
asked before the design, nothing is read before the
design but what it needs, and the design is shown once, in the chat,
in the shape of [`design-messages.md`](design-messages.md).

## 3. The start, with no go-ahead

No **Ready to build this design?** (tried 2026-10-28: the `app`
skill's questions settle before the design what the go-ahead used to
ask). The design's summary goes out as text (section 2); for a web app
built by the `app-guided` skill, the mockup is made while the user
reads it and its line comes after
([`../../web-app/references/comp.md`](../../web-app/references/comp.md)),
ending "Building it now."; then the build, in the same response, with
no dialog and no stop between the design and the first code. The
`app-guided` skill's **What to expect** for step by step comes first.

- **The build:** the first feature by the front door's one-feature
  flow; its objects in `api/` and its feature file are the design from
  here (`design-document.md`), and nothing else is kept up to date
  with them. At the first handoff, the acceptance appends its entry to
  `design/decisions.md` (`accept-design.md`). The first
  handoff's review is the design's review too: what to change in the
  design is said there, or at any point.
- **A change typed while it builds** ("roles from the start", "use
  Harbour"): a design change, made by the `app-design` skill's rules,
  the code following it and a line in the next handoff's **Notes**; work already done that it changes
  is redone, said in a line.
- **Learning mode:** the `guide` skill sets it, and the design's
  opening names that skill; "explain as you build" typed at any point
  turns it on.

**The prompt-by-prompt path** (asked for in those words, in the
prompt or at a handoff) **asks nothing,** here or later: the design's
closing line is "The design is saved in design/decisions.md (linked).
Say what to build first.", the entry written just before it, and the build
stops; no model check (section 4), no frontend question (section 5),
no **What should I build next?**. Each prompt is built as asked by the
front door's flow for that part, tested against its rules, and handed
off in the handoff's shape with its links (`design-messages.md`),
**Your turn** ending in the plain line "Say what's next.", the
next-step box carrying only the recap. The acceptance is recorded when
the user asks for the next thing (`accept-design.md`). A prompt that
changes the design (an object, a rule, who may call) is a design
change: the code follows it, and the next handoff's **Notes** says so, no question
first; the user's words are the agreement.

**All at once** (asked for in the prompt or at a handoff, "build it
all"): every feature under **Proposed features, in build order**, none
from **Not in this build**, by the
[`app-whole` skill](../../app-whole/SKILL.md)'s steps 4 and 6, from the
design as proposed, no features added: no stops, one handoff at the
end. The task list is the whole-app list (`task-list.md`, where the
plugin has it), its first item done.

**A message about something else** at a dialog later in the build
(the host says the user "sent a message instead": a photo, a look
change, a question): do it or answer it, say so in a line, then ask
the same dialog again, its text above it. It is never a yes, nor a no:
only an answer that says to go on ("go", "build it", "looks good") is
a yes (hotel-214, 2026-10-19: a banner photo sent in place of a
dialog's answer was taken as a yes).

## 4. The domain model, once

In the first feature only, once the front door has the dashboard up
on the new domain model and before any servicer code: compare
`api/` with the proposal's **Domain model** (`design/decisions.md`'s
first entry, never edited). Say the lead line below, then, when an
object was added, dropped or renamed, one line per difference with its
reason, in the user's nouns ("`Hotel` is gone: check-in needs none of
the hotel's settings"), and go on to the servicers in the same
response. Nothing is asked: a change the build made is the build's to
make, the next handoff's **Notes** list it again, and the user can
say "change it" or "walk me through it" at any point (hotel-355 asked
**Build on this domain model?** with no word of what had changed, and
the stop cost the build its pace):

> The room status floor plan's [domain model](<the Models page link>) is open on the dashboard
> (on 9874, since other projects hold 9871 to 9873): the things the
> app keeps track of ([Room](<link>), [Floor](<link>), [Hotel](<link>))
> and what each one holds. Everything else is built on top of it.
>
> Dashboard: [Models](<link>) · [Features](<link>) · [Changelog](<link>)

That is the dashboard's whole hand-over here, the lead line (the port
named only when it isn't 9871) and the Models · Features · Changelog
line: no separate "the developer dashboard is at …" line, no second
list of the objects. Both are message text, never drafted only in
thinking; in a verbose build, the **Exegesis** of the rules file and
the API follows them ([`exegesis.md`](exegesis.md)).

**The tour,** only when the user asks for it ("walk me through it",
"explain the model"), at any point: the domain model one object at
a time, at the user's pace. Never one paragraph for all of them, and
never a recap of what the chat already said: a tour shows each thing
where it lives. For each object, in build order, one message:

1. The Browser pane opens that object on the dashboard
   (`#/models?type=<package>.v1.<Object>`, the one time the pane
   shows a single object; `conversation.md`).
2. In the chat, in the user's nouns, every name a dashboard link: what
   the object stands for and why it is its own object (what changes
   on its own, what runs one at a time); what it holds, field by
   field, in words; each action by name, its kind in plain words (a
   writer changes this object, a transaction changes several at once
   or none, a reader only looks), what it does and who may call it;
   the rule it keeps and the scenario that proves it, the rule linked
   on the Features page. In a verbose build the decisive lines are
   quoted (`exegesis.md`). About 150 to 250 words an object.
3. One dialog, **Next on the tour?**: "Next: <the next object>"
   (recommended), "How they connect": "One moment of the day, followed
   through every object it touches.", "Stop the tour": "Back to the
   build."

**How they connect** is a stop of its own, as long as an object's, never
a line or a paragraph, whether chosen or reached after the last
object. The pane shows the whole model (`#/models`). In the chat, one
or two moments of the user's day, each followed call by call as a
numbered list in the user's nouns, every name a link: who does what
("Carlos marks 304 cleaned"), which action runs and its kind, what it
reads or changes on which object and why there, what it refuses and
the rule behind it, who sees the result and how (the floor plan
updates on everyone's screen through its reader). Then what does not
connect, and why: what each object never touches. After it, the tour
goes on where it was (the next object not yet shown, with the same
dialog); once every object and the connections are shown, the build
goes on where it stopped. Three objects and their connections are
four stops; a message that sums any of them up in a paragraph is not
a tour (hotel-203 and hotel-204, 2026-10-18: "How they connect"
answered in four lines, and the tour ended there with two objects
unshown).

A change the user asks for ("a stay should also hold the guest's
room"): change the API, `rbt generate`, say what changed, go on. If
the dashboard didn't come up, say so in one sentence and go on; the
model is shown at the first handoff. Later features say nothing here;
`app-whole` and the prompt-by-prompt path say the lead line only.

## 5. The backend, then the page

In the first feature only, once its actions pass every scenario (and
types check) and before any page, show the backend as text, then go
straight on to the frontend; nothing is asked:

1. One line: what was built and where to see it, for example "The
   amenity booking's backend is done: every rule holds, tested by its
   scenarios. See it on the dashboard's Features page."
2. One line per rule, ✓ with its scenario count, the rule's words a
   link to it on the Features page.
3. The dashboard's line: Models · Features · Changelog, each a link.
4. In the Claude app, the Features page opened in the Browser pane.
5. In a verbose build, the **Exegesis** of the servicers, the demo
   data and the tests ([`exegesis.md`](exegesis.md)).

Then one line on what comes next, to a person, not as a spec
("Frontend: the page housekeeping and the front desk use, where they
see every room on its floor and tap one for its next step; about 10
minutes."), the frontend's task list in place of the backend's, and
the page. The rules live in the backend, so the user sees them hold
on the dashboard before any time goes into the page, and can say
"stop" or ask for a change at any point; later features go from
backend to page the same way, their handoff showing both. A backend
only (no front door) ends here with its handoff; `app-whole` and the
prompt-by-prompt path say the backend's lines and go on the same.

From the first feature on, the build follows the front door
unchanged, but for these questions.

## Never

- "Ready to build this design?", or any stop between the design and
  the first code (section 3).
- The design's summary drafted only in thinking: the user sees only
  text.
- A dialog on the prompt-by-prompt path: the user chose to be asked
  nothing.
- A question about the domain model (section 4): the build says what
  it built and what changed, and goes on.
- A question between the backend and the page (section 5): the page
  is part of the feature the user already chose.

- Reading this plugin's files with a shell command instead of the
  file tools.
- A question before the design other than the `app` skill's.
- Code, `rbt generate` or a project scaffold before the design's
  summary and the mockup's line (on the prompt-by-prompt path, before
  the user's first build prompt).
