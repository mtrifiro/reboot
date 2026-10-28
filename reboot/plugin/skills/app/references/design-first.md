---
title: The Design First, Then How to Build It
impact: HIGH
impactDescription: After the app-design skill's round and proposed design, the app-guided skill asks the go-ahead (Ready to build this design?), then, in the first feature, the domain model check and the frontend question, each with its text just above it; the prompt-by-prompt path asks none of them.
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

## 3. The go-ahead

The proposed design (section 2) is in `design/design.md` and its
summary went out as text when the file was written, in the same response; for a web app built by the `app-guided` skill, the
mockup is made while the user reads it, and its line comes after
([`../../web-app/references/comp.md`](../../web-app/references/comp.md)):
a mockup of the main page in the look, served and opened in the pane. Then
one dialog (`AskUserQuestion` where available,
else one plain line), the only question between the prompt and code:
the go-ahead, where the user changes any assumed answer. The interactive build is the user's (the `app`
skill's default, or `/reboot:app-guided` by name), so it asks only for
the yes, never how to build.
Its options, word for word, filled from the design:

- Title: **Ready to build this design?**
- "Yes, start building": "Build <first feature> first, about 15
  minutes."
- "Not yet": "I want to change something first: a feature, who signs
  in, the palette, or anything in the design." Nothing more: what
  happens next is said after the answer.
- "Tell me more": "What happens first, before I decide."

No option is marked recommended: the answer stays in the chat as the
question and the option chosen, and a yes needs no recommendation.
No option for learning mode: the `guide` skill sets it, and the
design's opening names that skill; "explain as you
build" typed at any point still turns it on.

**On "Tell me more",** about 500 words in the chat (a length for the
build, never said to the user, as no word count ever is), in the user's
nouns, under short bold leads, then the same dialog again (a short
paragraph left the user with questions). The words are the response's
text, sent before the dialog's call, never drafted in thinking: the
user sees only text (hotel-302 wrote its answer in thinking and asked
again seven seconds later; the user saw a two-sentence paraphrase):

1. **What happens on a yes:** the first feature, step by step: its
   rules written as scenarios, the API, the domain model shown on the
   dashboard (a question only if it differs from the design), the
   actions and who may do each, proven by the scenarios, then its
   page, built from the mockup and tested in a browser; about 15
   minutes, then the handoff.
2. **What you do at each stop:** at the handoff, open the page and try
   it as the accounts it names; then say what to change, or pick the
   next feature. Nothing is accepted until you say so.
3. **What was assumed, and how to change it:** each line under
   **Assumed** (the features and their order, who signs in, the
   palette by name), with the words that change it ("add guest
   requests", "staff roles from the start", "use Harbour").
4. **What Reboot does for you here:** three or four lines from the
   design's own section of that name, in this app's nouns
   (`conversation.md`, "Say what Reboot does here").
5. **Where things are:** `design/design.md`, the mockup, the dashboard once the API exists;
   and the other ways to go on: prompt by prompt, or the rest at once
   at any handoff.

No new facts about the design: everything is from it, said at more
length.

Nothing is built before the answer. The go-ahead adds to the first
handoff's review: this decides the design before any code, that the
feature as built. After the answer, the `app-guided` skill's **What to
expect** for the chosen path, then the build.

**The prompt-by-prompt path** (asked for in those words, at the
go-ahead or at a handoff) **asks nothing,** here or later: no go-ahead
dialog (the design's closing line is "The design is in
design/design.md (linked). Say what to build first.", `design.md`
written just before it, and the build stops), no model check (section
4), no frontend question (section 5), no **What should
I build next?**. Each prompt is built as asked by the front door's
flow for that part, tested against its rules, and handed off in the
handoff's shape with its links (`design-messages.md`), **Your turn**
ending in the plain line "Say what's next.", the next-step box
carrying only the recap. The acceptance is recorded when the user
asks for the next thing (`accept-design.md`). A prompt that changes
the design (an object, a rule, who may call) is a design change: the
design document and decisions log follow it, no question first; the
user's words are the agreement.

- **All at once,** typed as the free answer ("build it all"): every feature under **Proposed features, in build
  order**, none from **Not in this build**, by the
  [`app-whole` skill](../../app-whole/SKILL.md)'s steps 4 and 6, from
  the design as proposed, no features added: no stops, one handoff at
  the end. The task list is the whole-app list (`task-list.md`, where
  the plugin has it), its first item done.
- **Yes, start building** (or the first feature named): the
  first feature's **Methods** go into `design/design.md`
  (`design-document.md`), then build it by the
  front door's one-feature flow. At the first handoff,
  `design/design.md` becomes the accepted design (`accept-design.md`),
  and **Assumed** moves into the first decisions entry.
- **Not yet, or the dialog skipped:** one short reply: "The whole
  design is in design/design.md.", the path a
  Markdown link to the file in the
  user's project, then "Tell me to continue when you're ready, or
  what to change." Then stop: no dialog now.
  "Continue" (or "go", "build it") asks **Ready to build this design?**
  again; a change updates the design and asks again.
- **A change,** typed as the free answer (so no option means only
  "change something"): update the document and the design, show what
  changed, and ask the same dialog again.
- **No answer** is not a yes.
- **A message about something else** in place of the answer (the host
  says the user "sent a message instead": a photo, a look change, a
  question): do it or answer it, say so in a line, then ask the same
  dialog again, its text above it. It is never a yes, nor a no: only
  an answer that says to go on ("go", "build it", "looks good") is a
  yes. The same holds for **Build on this domain model?** below
  (hotel-214, 2026-10-19: a banner photo sent in place of the domain
  model's answer was taken as "Build on it").

No task item marks the wait: the dialog is the signal, and "Propose
the design for <app>" is done once the design is shown.

## 4. The domain model, once

In the first feature only, once the front door has the dashboard up
on the new domain model and before any servicer code: turn the
code-style names in `design/design.md` that now exist into dashboard
links (the rest stay plain until built). With the design's objects
and fields unchanged, say the lead line below and go on. Only when one
was added, dropped or renamed, end the turn with the lead line, a line
per difference, and one dialog:

> The room status floor plan's [domain model](<the Models page link>) is open on the dashboard
> (on 9874, since other projects hold 9871 to 9873): the things the
> app keeps track of ([Room](<link>), [Floor](<link>), [Hotel](<link>))
> and what each one holds. Everything else is built on top of it.
>
> Dashboard: [Models](<link>) · [Features](<link>) · [Changelog](<link>)

That is the dashboard's whole hand-over here, the lead line (the port
named only when it isn't 9871) and the Models · Features · Changelog
line: no separate "the developer dashboard is at …" line, no second
list of the objects. Both are message text just above the dialog,
never drafted only in thinking; in a verbose build, the **Exegesis**
of the rules file and the API comes between them and the dialog, and
after the lead line when no dialog is asked: the model unchanged skips
the question, never the exegesis ([`exegesis.md`](exegesis.md)). The dialog says on its own what it
asks about:

- Title: **Build on this domain model?**
- "Build on it" (recommended): "Next: the actions for “<feature>”,
  tested against its rules."
- "Walk me through it": "A tour, one object at a time, each opened on
  the dashboard: what it holds, what it does, who may do it, and the
  rule it keeps."

It serves whoever reads it, dashboard opened or not, and neither is
asked which they are.

**The tour,** on "Walk me through it": the domain model one object at
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
   model."

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
dialog); once every object and the connections are shown, **Build on
this domain model?** again, without "Walk me through it": its second
option is "Change something": "Say what to change about <the objects>,
in your own words." A tour stopped early keeps "Walk me through it",
which resumes at the next object not yet shown. Three objects and their connections are
four stops; a message that sums any of them up in a paragraph is not
a tour (hotel-203 and hotel-204, 2026-10-18: "How they connect"
answered in four lines, and the tour ended there with two objects
unshown).

When the model differs from the proposed design, one line before the
dialog says how, in the user's nouns. A change goes in the free
answer ("a stay should also hold the guest's room"): change the API,
`rbt generate`, say what changed, ask again. A message about
something else is done and the dialog asked again, as for the
go-ahead (section 3). No task item marks the
wait: the dialog is the signal. If the dashboard didn't come up, don't ask: say so in
one sentence and go on; the model is checked at the first handoff.
Later features don't ask; `app-whole` and the prompt-by-prompt path never
do.

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

- "Ready to build this design?" without the design's summary just
  above the dialog (section 3): the question asks the user to judge
  it. A message drafted only in thinking is not it.
- A dialog on the prompt-by-prompt path: the user chose to be asked
  nothing.
- "Build on this domain model?" without its lead line and the
  dashboard's links as text just above it (section 4): nothing says
  what "this" is.
- A question between the backend and the page (section 5): the page
  is part of the feature the user already chose.

- Reading this plugin's files with a shell command instead of the
  file tools.
- A second go-ahead, or any question before the design: the go-ahead
  is asked once, after the design, and takes any
  change to the features.
- Code, `rbt generate` or a project scaffold before the go-ahead (on
  the prompt-by-prompt path, before the user's first build prompt).
