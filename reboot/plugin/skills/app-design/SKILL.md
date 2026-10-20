---
name: app-design
description: "Design a Reboot application from a description, without building it: on its own, one round of questions about what to build (the first features, who signs in, the palette); loaded by the app-guided or app-whole skill, none (the recommended answers, under Assumed); then the whole proposed design written once to design/design.md and drawn as a page beside the chat, its summary in the chat, where the guided and build skills pick it up; loaded by the app-whole skill, a whole-app scope. Use when the user asks for a design, a proposal or a plan for an app and not yet the app, or asks for it by name (/reboot:app-design); a prompt that asks to build an app goes to the app skill, which runs this skill through the app-guided skill."
argument-hint: [<app-description>]
allowed-tools: Read, Write, Edit, Glob, Grep
---

# app-design — The Design, Before Any Code

The Reboot Flywheel's Design stage on its own: the opening, one round
of questions (on its own only), the research, and the proposed design, written once to
`design/design.md` and drawn as a page beside the chat. Nothing is built here: no
code, no `rbt generate`, no project scaffold, no dependency installed.

> **The user sees only message text.** Thinking is shown at most as a
> paraphrase that drops and rewords what you wrote. The opening, what
> the research found and the design itself go out as the response's
> own text, in these words, before that response's tool calls.
> Drafting them in thinking is not saying them.

## How this skill runs

- **On its own** (`/reboot:app-design <description>`, or a prompt that
  asks for a design, a proposal or a plan and not yet the app):
  everything below, ending with the closing line in section 4.
- **Loaded by the [`app-guided` skill](../app-guided/SKILL.md)** (the guided
  build): everything below but the round and the closing line. Nothing
  is asked before the design: each of the round's questions takes its
  recommended answer (section 2), listed under **Assumed**, and the
  go-ahead is where the user changes any. The opening goes out as text
  right after this skill loads (the Skill loads are the only tool calls
  before it), and the design follows in the same response. The app-guided skill's go-ahead, **Ready to build this design?**, follows the design in
  the same response
  ([`app/references/design-first.md`](../app/references/design-first.md),
  section 3); on the prompt-by-prompt path, that section's closing line.
- **Loaded by the [`app-whole` skill](../app-whole/SKILL.md)** (it
  loaded first): no round and no question, ever. Its section 1 gives
  the scope (every feature a real product in the domain needs, every
  role) and the answers the round would have asked, and overrides
  "Four or five features" and "No roles first" below; everything
  else below holds. The opening goes out as text right after this
  skill loads: the Skill loads are the response's only tool calls
  before it, and the first read comes after it. Its third sentence is
  "No questions: the whole app is designed, then built, tested and
  handed over when it is done." word for word (for ", basic", "No
  questions: one feature is designed, then built, tested and handed
  over when it is done."), and the design follows
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
3. On its own: "First, a few questions about what to build; then I'll
   design it, starting from its rules." Loaded by the `app-guided`
   skill, two sentences: "Next I'll write the design: what the app
   keeps track of, the rules each feature must keep, and its pages,
   opened beside the chat with a mockup of the main page. Nothing is
   built until you approve it, and you can change any feature." Word
   for word.

Loaded by the `app-guided` skill, one line after the paragraph, word
for word: "To build the whole app without stopping instead, use
/reboot:app-whole." On this path nothing is asked before the design,
so no dialog forces the opening out: it is the response's text, sent
before the task list's update and before the first read (hotel-301
drafted it in thinking, then updated the list and read; the user saw
only the app's paraphrase of that thinking, one compressed sentence
ending "confirm before I proceed"). (the hands-off paths are asked for, never offered
by a dialog: the `app` skill).

Example: "An app for a 56-room boutique hotel, used by its front desk
and housekeeping. I'd start with the room status floor plan: every
room from occupied to dirty to cleaned to inspected, and no guest put
in a room that isn't inspected. First, a few questions about what to
build; then I'll design it, starting from its rules."

Rules for that response:

- Written as the response's text right after this skill loads (the
  Skill loads are the only tool calls before it) and before any other
  tool call, and the same three sentences wherever it is drafted:
  never a longer or different version in thinking, since that is what
  the user may see instead.
- Nothing more in it: what the app keeps track of, the front door and
  the rest are in the design, minutes later. Then the dialog, the
  response's next tool call.
- Nothing about how it will be built beyond the dialog's own options:
  **What to expect** is the `app-guided` skill's, after the go-ahead.
- **No name before the design.** The design proposes one, with the
  palette, under what the build assumed. Its first mention in the
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

Only when this skill runs on its own. Loaded by the `app-guided` or
`app-whole` skill nothing is asked: each question below takes its
recommended answer (the recommended features; anyone signed in, roles
later; the palette as below), each a line under **Assumed**, and the user changes any at the
go-ahead, with the design and the mockup in front of them (hotel-270:
three of four questions answered with the recommendation).

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
- **"Which palette?"**, only when the prompt names no brand: two or
  three that suit the domain, the first recommended, and no "Use my
  brand" option: a brand typed in the dialog's own free answer (a
  site, a colour, a name) is taken as a brand named in the prompt
  would be. Nothing is read for this question. A palette is the page,
  text, lines and accent together, a gray and an accent; the type and
  corners are always the house look's (Space Grotesk over DM Sans).
  The palettes are house (Reboot's own: cream paper, navy ink and accent), sand-bronze, sand-brown, sand-orange, sand-gold, olive-grass, sage-teal, slate-blue, slate-iris, mauve-plum and mauve-crimson, and no other; an option's label is its
  name and two colours ("Lagoon: sage and teal", as
  `python3 '<the web-app skill>/assets/palette.py'` lists them), its
  description why it suits the domain, in a few words.
- **The palette, unasked** (loaded by the `app-guided` or `app-whole`
  skill): a brand colour in the prompt is `palette.py --from
  '<#rrggbb>'`, which names the nearest palette and how far off;
  otherwise name the two or three that suit the domain and take the
  one `python3 '<the web-app skill>/assets/palette.py' pick <them>`
  prints from the project root. It picks by the project folder's
  name, so two builds of one prompt differ (hotel-260 to -301, five
  hotel builds, all took sand-bronze).
How it is built is not asked here: the interactive build is the
default (the `app` skill), and the go-ahead, **Ready to
build this design?**, asks only for the yes; "build it all at once",
typed as its free answer, is still honoured. The choice can change: at any handoff "build
the rest all at once", "step by step from here" or "prompt by prompt
from here" switches, and the first handoff says so in one line.

**A free answer that refuses the design or the questions** ("just
build it", "no design") ends this skill's part: load the [`app-just`
skill](../app-just/SKILL.md) with the Skill tool (`/reboot:app-just`), its
argument the prompt as typed followed by any answers given (the
features chosen, who signs in, the palette), and stop. No design, no
closing line: the app-just skill says nothing but its steps and the
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
- **The app's name,** when the prompt names none: thirty candidates
  that suit the domain, spread across five kinds (a place, a plant or
  a material, a term of the trade, an object of the domain, a plain
  description such as "Room Board"), about six each and more of the
  kinds the domain has the most good names for, never a person's name,
  each one the build would be glad to see picked (no filler), then the
  one `python3 '<this skill>/assets/pick.py' name <the thirty>` prints
  from the project root: it picks by the project folder's name, so two
  builds of one prompt rarely share one (about one in thirty). A
  working name in the design (hotel builds named themselves Larkspur
  nine times, Linden six, Halcyon four).
- Times are in the user's time zone.

**Task list:** right after the answers (loaded by the `app-guided` or
`app-whole` skill, right after the opening's text), one item, "Propose
the design for <app>"; a list that exists when this skill loads is replaced with
that item first, in a response of its own. It is done when the design
is shown. The `app-guided` skill's path list follows the go-ahead.

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

Then the domain model's shape, before it is written down:

- **The hub keeps only its own job** (the hotel's name and settings),
  never every list: each list a page reads is an index object of its
  area (`FrontDeskBoard`, `ConciergeQueue`), so no object is called by
  more than four others and no two objects call each other.
- **The roster is its own object** (`Team`,
  `python/references/auth-roles.md`), never the hub: every authorized
  call reads it.
- **More than six objects: packages by area** (rooms, stays, guest
  services, staff), in `design-document.md`'s **Architecture**,
  layered so none imports another in a circle.

(hotel-271: one `Hotel` with 33 methods held the roster and every
index; three objects and it called each other.)

Then the proposed design, **written once, as a page**, one line
before it only when research ran long (what it found that the design
uses). Never a minute without a line: the opening, the round, then the
design; reading the references gets no line of its own.

1. `design/design.md`, in one write, in the shape of
   [`design-document.md`](../app/references/design-document.md), all
   of it but **Methods**, which go in after the go-ahead, before any
   code: the user decides on the rest.
2. The page, with no model output: `python3 '<this
   skill>/assets/design_page.py'` from the project root writes
   `design/design.html`, in the developer dashboard's look, and
   `design/index.html`, which opens it.
3. Serve `design/` in the background, its pid in `design/.design.pid`,
   the mode by `portless doctor` as the
   [`run` skill](../run/SKILL.md) says, never asked. Under portless,
   `<project>` the project folder's name:

   ```sh
   portless design.<project> sh -c 'exec python3 -m http.server "$PORT" --bind 127.0.0.1 --directory design' &
   echo $! > design/.design.pid
   ```

   at `https://design.<project>.localhost/`; on plain ports,
   `python3 -m http.server <port> --directory design`, the first free
   port from 9860, at `http://localhost:<port>/`. The root opens the
   page (`design/index.html`). In the Claude app, open it in the
   Browser pane: a `launch.json` configuration named `design` whose
   `url` is that address alone, with no path (the app refuses one with
   a path, hotel-256); elsewhere, the link. The pane keeps one tab per
   address, so nothing else is ever opened at this one: the mockup has
   its own server and address (`web-app/references/comp.md`).
4. In the chat, the design's summary, in the shape of
   `design-messages.md`, "The proposed design", its link to the page.

Where commands can't run (a planning-only session), the whole design
goes in the chat instead, in `design.md`'s shape without its methods.
Writing the design twice, in parts then for the chat, made the user
wait (crm-15 showed its design at 1 m 58 s; hotel-7, writing it once,
at 47 s).

What the design holds while nothing is built:

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
  in, which holds the per-user data; the people the app is about (guests,
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

**Loaded by the `app-whole` skill:** the design and its page as
section 3 says, with no closing line and no dialog; the one-shot
skill goes straight on to the build in the same turn.

**Loaded by the `app-guided` skill:** no closing line. The go-ahead dialog
follows the design in the same response (`design-first.md`, section
3), and the app-guided skill takes it from there.

**On its own:** the design and its page (section 3), then one line,
the path a Markdown link to the file in the user's project:

> The design is open beside the chat and in design/design.md. Say
> "build it" to build it step by step, "build it all at once", or what
> to change.

Then stop: no dialog, no code. On "build it" (or "build it all at
once", "prompt by prompt"), load the [`app-guided`
skill](../app-guided/SKILL.md) with the Skill tool (`/reboot:app-guided`),
never by reading its file: it takes the proposed
design as its own and starts at **What to expect**; the words were the
go-ahead. A change ("add a waiting list", "two confirmed gigs a night
is fine") updates the design and the file, shows what changed (the
changed lines, not the whole design again), and ends with the same
line; `design_page.py` draws the page again after every change. A
question about the design is answered in the chat, from the
design, with no new facts added to it.

## Never

- Reading a reference or listing the folder before the opening that
  says what will be built; a name before the design.
- Any question before the design other than the round; a second
  round; a question on the prompt-by-prompt path or when loaded by
  the `app-guided` or `app-whole` skill.
- An answer taken in the round without its line under **Assumed**.
- The design drafted only in thinking, or written but not drawn and
  opened (section 3): the user judges the page beside the chat.
- Dashboard links, a review table or a Decisions section in a
  proposed design.
- Code, `rbt generate`, a project scaffold or a dependency installed:
  the design is the whole of this skill.
