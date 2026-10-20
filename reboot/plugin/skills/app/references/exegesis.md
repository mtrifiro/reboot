---
title: Verbose, an Exegesis at Each Milestone
impact: MEDIUM
impactDescription: Asked for it, the user wants to learn from the build, not only receive it; without a fixed shape the explanation is a lecture between every tool call, or nothing
tags: verbose, exegesis, explain, teach, learning, commentary, design/exegesis.md
---

# Verbose, an Exegesis at Each Milestone

**On when the user asks for it,** in the prompt or at any point
("verbose", "explain as you build", "give me an exegesis of your
work", "teach me as you go"), and off when they say so ("quiet", "no
more exegesis"). One line says it is on: "Verbose: each milestone
report ends with an exegesis of what was written and why, the same
text kept in design/exegesis.md." Two things change, and nothing
else (the task list, the dialogs and the reports are as they are):
each milestone report ends with its exegesis, and each step line
between milestones gains one sentence of why ("Backend: writing the
floor plan's rules as scenarios first, because the rules are the
contract the code must keep."). Nothing more between reports.

**Where.** The last section of each milestone report, set apart as
its own document: a horizontal rule (`---`) on its own line, the
heading `### Exegesis · <the part>` ("Exegesis · the domain model"),
the text, and a closing rule, before the report's dialog; in a
handoff, the rule before **Your turn** closes it.

- In a guided build: the domain model check (the rules file and the
  API; shown after its lead line even when the model is unchanged and
  no question is asked), the backend check (the servicers, the demo data, the tests),
  the handoff (the page and its browser scenarios), then each later
  feature's handoff.
- On the prompt-by-prompt path and in the `app-just` skill: after each
  part's links line.
- In the one-shot: written feature by feature to the file as the
  build goes; the handoff's section covers the whole app in about 400
  words and links the file.

The same text is appended to `design/exegesis.md`, each under a
heading with the milestone and the date, so the record outlives the
chat. The file is created at the first one and linked from the
handoff's **Look closer** line beside the design.

**What it explains.** An exegesis reads the text that was written and
says what each part is for, in this order, 600 to 900 words a
milestone, always in the chat as well as the file (a milestone whose
exegesis is only in the file has none):

1. **Each object or page, as a decision.** Why it is its own object
   (what changes on its own, what runs one at a time), what its id is
   and why, which fields are state and which are derived; for a page,
   why this primary view, what it leads with, which reader feeds it.
2. **Each method's kind.** Writer, reader, transaction or workflow,
   and why that kind: what it changes, what else it touches, what
   would break with another ("`check_in` is a transaction because the
   stay and the room change together, or neither does").
3. **The rule and its proof.** Which scenario proves which rule, what
   each step does in the harness, and which refusal in the servicer
   it corresponds to.
4. **Who may call it,** and the line of the authorizer that says so.
5. **What was not done,** and why: the alternative considered (a field
   instead of an object, a workflow instead of a transaction) and its
   cost.

Each point quotes the decisive lines, at most eight a quote, in a
fenced block: an exegesis explains a text, so the text is shown.
Reboot's terms are named and explained once each in a build (a
durable object, an authorizer, effect validation, a reader's
subscription), then used plainly. Links as `conversation.md` says:
each object and rule to the dashboard, each file to the project.

**Voice.** The user's nouns first, Reboot's second; one idea a sentence. Not a tutorial on Reboot
and not a changelog: what this app's code means and why it is shaped
so.

## Never

- Commentary between reports beyond the step line's one sentence of
  why, or an exegesis of a reading step, a typo fix or a tool call.
- An exegesis in a build that did not ask for one.
- A whole file quoted: the decisive lines only.
- A milestone's report delayed to write it: the report, then the
  exegesis as its last section, in the same message.
