---
name: design
description: "Design a Reboot application from a description, without building it: one round of questions about what to build (the first features, who signs in, the look), then the whole proposed design in the chat and in design/design.md, where the guided and build skills pick it up; loaded by the one-shot skill, no round and a whole-app scope. Use when the user asks for a design, a proposal or a plan for an app and not yet the app, or asks for it by name (/reboot:design); a prompt that asks to build an app goes to the app skill, which asks how to build first and, on Guided, runs this skill through the guided skill."
argument-hint: [<app-description>]
allowed-tools: Read, Write, Edit, Glob, Grep
---

# design — The Design, Before Any Code

The Reboot Flywheel's Design stage on its own: the opening, one round
of questions, the research, and the proposed design, shown once in the
chat and written to `design/design.md`. Nothing is built here: no
code, no `rbt generate`, no project scaffold, no dependency installed.

> **The user sees only message text.** Thinking is shown at most as a
> paraphrase that drops and rewords what you wrote. The opening, what
> the research found and the design itself go out as the response's
> own text, in these words, before that response's tool calls.
> Drafting them in thinking is not saying them.

## How this skill runs

- **On its own** (`/reboot:design <description>`, or a prompt that
  asks for a design, a proposal or a plan and not yet the app):
  everything below, ending with the closing line in section 4.
- **Loaded by the [`guided` skill](../guided/SKILL.md)** (the guided
  build): everything below but the closing line. The opening
  goes out as text right after this skill loads: the Skill loads and the
  `app` skill's one question are the only tool calls before it, and the round's
  dialog is the next. The guided skill's go-ahead, **Build on this design?**, follows the design in
  the same response
  ([`app/references/design-first.md`](../app/references/design-first.md),
  section 3); on the prompt-by-prompt path, that section's closing line.
- **Loaded by the [`one-shot` skill](../one-shot/SKILL.md)** (it
  loaded first): no round and no question, ever. Its section 1 gives
  the scope (every feature a real product in the domain needs, every
  role) and the answers the round would have asked, and overrides
  "Four or five features" and "No roles first" below; everything
  else below holds. The opening goes out as text right after this
  skill loads: the Skill loads are the response's only tool calls
  before it, and the first read comes after it. Its third sentence is
  "No questions: the whole app is designed, then built, tested and
  handed over when it is done." word for word, and the design follows
  in the same response, with no dialog between them.
- Read this plugin's files with the Read tool, one call per file and
  several in one response, never a shell command: a long shell result
  is cut to a preview and the rest goes unread (the `python` skill's
  rule).

## 1. The opening, before reading anything

The build's first words: one short paragraph of three sentences, in
the user's nouns, sent as text. When nothing is sent, the Claude app
shows a paraphrase of the build's thinking in its place (hotel-200 saw
one sentence and never the opening), so it is sent, and it carries
everything that matters on its own, the most important first. No name yet: the app is named in the
design, as a working name.

1. "An app for <what it is>, used by <who>." (the rules below)
2. "I'd start with <feature>: <its rule, in plain words>."
3. "First, a few questions about what to build; then I'll design it,
   starting from its rules." word for word.

Example: "An app for a 56-room boutique hotel, used by its front desk
and housekeeping. I'd start with the room status floor plan: every
room from occupied to dirty to cleaned to inspected, and no guest put
in a room that isn't inspected. First, a few questions about what to
build; then I'll design it, starting from its rules."

Rules for that response:

- Written as the response's text right after this skill loads (the
  Skill loads and the `app` skill's question are the only tool calls
  before it) and before any other
  tool call, and the same three sentences wherever it is drafted:
  never a longer or different version in thinking, since that is what
  the user may see instead.
- Nothing more in it: what the app keeps track of, the front door and
  the rest are in the design, minutes later. Then the dialog, the
  response's next tool call.
- Nothing about how it will be built beyond the dialog's own options:
  **What to expect** is the `guided` skill's, after the go-ahead.
- **No name before the design.** The design proposes one, with the
  look and accent, under what the build assumed. Its first mention in the
  Brief, the Brief's first sentence, in the chat and in
  `design/design.md`, is followed by "(working name)": "**Brief.**
  Halftime (working name) is used by …", never only a later "The name
  is Halftime (working name)". It stays until the user names the app
  or keeps the name.
- **The first feature:** the feature at the centre of the named
  side's day, on one page: the main page's central object and a rule
  the user can see it keep. "Manage a hotel" names its staff, and
  their day is the rooms: the room status floor plan, each room moving
  occupied → dirty → cleaned → inspected, with no guest put in a room
  that isn't inspected.
- **A sale first only when the prompt is about selling:** a booking
  site, a shop, a ticket office.
- **Customer features last**, and never first unless the prompt is
  about selling: they need both the staff's side and the customer's to
  be worth trying.
- **A staff tool has no customer side:** a prompt that names the
  staff's tool ("an operations app", "a back office", "a dispatch
  tool") offers no customer feature; its customers use someone else's
  system.
- **No roles first,** unless "Who signs in?" chose them: the first
  feature has sign-in (the development accounts) and an authorizer on
  every method, "anyone signed in", never `allow()`; no roles, roster
  or role rules. Who may do what is its own feature, **Who may do
  what**, in the build order before any deploy.

## 2. One round of questions, then none until the design

One dialog (`AskUserQuestion`; where there is none, the same as plain
lines), from the prompt alone, before reading any reference. Two or
three questions, each two to four options, the simplest first and
marked "(Recommended)" where one is recommended, so accepting every
recommendation is one answer:

- **"Which features should the first build include?"** (multi-select,
  the question ending "Nothing ticked builds the recommended set."):
  four features worked out from the prompt, each its name in the
  user's nouns as the label and its rule in a few words as the
  description, in this order: the one sentence 2 names, first, marked
  "(Recommended)" (a multi-select starts with nothing ticked, so it
  leads); then the staff's other features; last, only when the prompt
  implies customers who use the app themselves ("a hotel where guests
  book online"), a feature for them, its description starting with who
  it is for. The features ticked are the build, in that order; nothing
  ticked, or Skip, is the recommended one.
- **"Who signs in?"**, when the prompt leaves it open: "Anyone signed
  in can do everything; roles later (Recommended)" or "Staff roles from
  the start", naming the roles in the user's nouns ("front desk, vets
  and techs"). Roles chosen are in the first build; otherwise they are
  **Who may do what**, before any deploy.
- **"Which look?"**, only when the prompt names no brand: two or
  three that suit the domain, each one of the three house looks with
  an accent ("Boutique, in plum"), the first recommended, plus "Use my
  brand" (a site or tokens to read); nothing is read for this. The
  looks: the house look (Reboot's own: cream paper, navy ink, Space
  Grotesk over DM Sans, soft corners: the default for any domain),
  Ledger
  (grey, Space Grotesk headings and figures over Inter, sharp corners,
  compact rows: operations tools watched all day, a dispatch desk, a
  warehouse, a support queue), Boutique (warm paper, a serif for headings, round corners:
  hospitality, retail, food, wellness, culture); the accents teal,
  navy (the house accent), teal, cyan, blue, indigo, violet, purple,
  plum and rose, and no other. An
  option's description says what it is like and why it suits the
  domain, in a few words.
How it is built is not asked here: the user chose the guided build
(the `app` skill's first question), and the go-ahead offers step by
step or all at once. The choice isn't for keeps: at any handoff "build
the rest all at once", "step by step from here" or "prompt by prompt
from here" switches, and the first handoff says so in one line.

**A free answer that refuses the design or the questions** ("just
build it", "no design") ends this skill's part: load the [`build`
skill](../build/SKILL.md) with the Skill tool (`/reboot:build`), its
argument the prompt as typed followed by any answers given (the
features chosen, who signs in, the look), and stop. No design, no
closing line: the build skill says nothing but its steps and the
links.

The front door is never asked (the `app` skill's Routing): the one the
prompt names, otherwise the web app, with the backend ready for an MCP
UI, offered at handoff. The answers are the design's scope: the
features chosen, in build order, and nothing else; what else a real
app in the domain needs goes under **Not in this build**, never built
unless the user asks. A free answer is taken as written. Nothing else
is asked before the design. Everything else is decided as the front
door would, taking its recommended answer:

- **Everything else** (what the app keeps track of, counts, layouts,
  hours): the simplest option, assumed and listed. Roles wait for Who
  may do what unless the round chose them.
- **The app's name,** when the prompt names none: one that suits the
  domain, a working name in the design.
- Times are in the user's time zone.

**Task list:** right after the answers, one item, "Propose the design
for <app>"; a list that exists when this skill loads is replaced with
that item first, in a response of its own. It is done when the design
is shown. The `guided` skill's path list follows the go-ahead.

## 3. The research, then the design

Before the design, read only what it needs: the domain model's shape
rules (`python/references/state-collections.md`, `api-methods.md`)
and [`design-messages.md`](../app/references/design-messages.md)'s
"The proposed design". Nothing else: the build's references are read
by the build, after the answer.

First, in thought, walk every workflow: each person who uses the app,
the jobs they come to do (user stories: "as the front desk, I move a
guest to another room when theirs isn't ready"), and each job's every
step from start to end, not the first click. Each thing the app keeps
track of has a whole lifecycle, which the feature that adds it
covers: created, seen in a list and on its own, found (a filter, a
search), changed (every field a person could get wrong has an edit),
corrected (a mistake undone, a cancel), and ended (done, cancelled,
archived or deleted, as the domain says). "Edit" is the part builds
miss most. A part left for later is named under **Not in this
build**, never silently absent.

Then the proposed design, **once, in the chat**, in the shape of
`design-messages.md`, "The proposed design": the whole design but its
methods, about 500 words, one line before it only when research ran
long (what it found that the design uses). Never a minute without a
line: the opening, the round, then the design itself; reading the
references gets no line of its own.

`design/design.md` is written in one write, in the shape of
[`design-document.md`](../app/references/design-document.md): the same
design plus the first feature's methods. Loaded by the `guided` skill,
it is written after the go-ahead's answer, before any code (on "Not yet",
before the reply that links it); on its own and on the prompt-by-prompt
path, right after the design, before the closing line. Writing it
twice, in parts then for the chat, made the user wait (crm-15 showed
its design at 1 m 58 s; hotel-7, writing it once in the chat, at 47 s).

What the design holds while nothing is built, in chat and file:

- **Status:** "proposed on <date>; nothing is built yet. Names become
  links to the developer dashboard once it shows them."
- **Four or five features** under **Proposed features, in build
  order**: the first marked, with why; each a job for a named person,
  walked start to finish (user story in one line, then what it lets
  them do, with the lifecycle of what it adds), its rules in plain
  words. The first is one page for one side; a customer feature, when
  the prompt implies customers who use the app, comes second. Then
  **Not in this build**: what else a real app in the domain needs,
  one line each, built only when asked. **Who may do what** is listed
  there, before any deploy; until it is built, **Sign-in** says in one
  line "Everyone signed in can do everything for now; roles come with
  Who may do what.", and the first feature has no roles, roster or
  role rules.
- **A `User` object in every design,** by that name: one per person
  who signs in, keyed by their sign-in ID, where both front doors sign
  in and the per-user data hangs; the people the app is about (guests,
  clients, teammates) are their own objects when they hold more than a
  name. **A list that grows without limit** (a history, a feed,
  events) is never a field of another object: its own object or an
  `OrderedMap` (`state-collections.md`), said in the design.
- **No links yet.** Packages, domain objects, methods, features and
  rules are named in code style (`Room`, `Room.check_in`), never as
  dashboard links: a link to nothing reads as broken. Links come once
  the dashboard shows them (`design-first.md`, section 4);
  `scripts/design_links.py` checks them from then on.
- **No review table** and **no Decisions** section yet: both come at
  the first acceptance.
- **Assumed**, after **Sign-in**: every answer taken in the round, one
  line each, question then answer, so the user sees what to change,
  and the build that picks the design up reads how to build there
  ("How: step by step", from the go-ahead's answer; on its own, "How:
  not chosen yet").

The user signs off on what they see, so the assumptions say what the
build picked:

> Assumed, all easy to change: the name Groom Room, opening hours
> 9:00 to 17:00, and an hour per appointment.

At most five, the ones that shape the app most (its name, counts,
hours), in the user's nouns.

## 4. Then

**Loaded by the `one-shot` skill:** write `design/design.md` right
after the design, with no closing line and no dialog; the one-shot
skill goes straight on to the build in the same turn.

**Loaded by the `guided` skill:** no closing line. The go-ahead dialog
follows the design in the same response (`design-first.md`, section
3), and the guided skill takes it from there.

**On its own:** write `design/design.md`, then one line, the path a
Markdown link to the file in the user's project:

> The design is in design/design.md. Say "build it" to build it step
> by step, "build it all at once", or what to change.

Then stop: no dialog, no code. On "build it" (or "build it all at
once", "prompt by prompt"), load the [`guided`
skill](../guided/SKILL.md) with the Skill tool (`/reboot:guided`),
never by reading its file: it takes the proposed
design as its own and starts at **What to expect**; the words were the
go-ahead. A change ("add a waiting list", "two confirmed gigs a night
is fine") updates the design and the file, shows what changed (the
changed lines, not the whole design again), and ends with the same
line. A question about the design is answered in the chat, from the
design, with no new facts added to it.

## Never

- Reading a reference or listing the folder before the opening that
  says what will be built; a name before the design.
- Any question before the design other than the round; a second
  round; a question on the prompt-by-prompt path or when loaded by
  the `one-shot` skill.
- An answer taken in the round without its line under **Assumed**.
- The design drafted only in thinking, or shown only as a pointer to
  `design/design.md`: the user judges what they see in the chat.
- Dashboard links, a review table or a Decisions section in a
  proposed design.
- Code, `rbt generate`, a project scaffold or a dependency installed:
  the design is the whole of this skill.
