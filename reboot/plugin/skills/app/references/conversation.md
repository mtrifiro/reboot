---
title: Talking to the User While the App Is Built
impact: HIGH
impactDescription: What the build says, links, opens and asks at each stage after the opening, so the user always knows where the build is, what Reboot is doing, and what is theirs to do. Read once, right after the user answers how to build.
tags: conversation, links, browser pane, narration, questions, research, handoff
---

# Talking to the User While the App Is Built

**Every line below is message text, in these words, before the
response's tool calls: never only in thinking, which the user never
gets as a message** (`app` skill, top).

Read once, after the go-ahead (on the power-user path, after the
design) and the build has said what to expect (`app` skill, step 1). It covers the
rest of the build: links, the Browser pane, what is said after each
answer and at each stage, research, the questions inside the build,
and keeping a feature.

**Explain, don't just report.** Each message says what happened, what
it means for the user's app, and what comes next, in the user's nouns,
so someone who glanced away can pick it up. "The dashboard is up" is a
report; "The domain model is on the dashboard: Room holds its own
bookings, so no night is booked twice ([Room](<link>)). Next, the
booking actions." explains. Name the thing, link it when it can be
opened, and say why it matters. A dialog is explained the same way:
its title names what it asks about, each option says what happens if
chosen, and the text just above it gives the context to choose; a
question that only makes sense after scrolling up is not ready to ask.

**Say what Reboot does here, for this app.** A stage's line pairs what
the build is doing with what Reboot takes off the developer's hands at
that step, in the app's own nouns: "Moving an account from engaged to
opportunity is one transaction: the account and the book change
together or not at all, with no rollback code to write", never "a
transaction changes several objects all or nothing". Name the object,
the rule or the page, and what the developer didn't have to write (a
database, migrations, an API layer, websocket or polling code, retry
logic, a test harness). The build's own reading is not news: never
"reading how this plugin designs an app", "the shape the design
document takes" or "Reboot's references for the API"; a reading step
gets no line of its own, or, when it is long, the next step's Reboot
line said before it.

**Links at every major turn.** Once the app has started, every
major turn ends with one line linking both, on the ports they started
on, so the user never scrolls back for them:

> App: http://localhost:5173/ · Dashboard: http://127.0.0.1:9871/

Once a feature file exists, the dashboard part names its three pages
(`dashboard` skill, "Links to an Object or a Rule"):

> App: http://localhost:5173/ · Dashboard: [Models](http://127.0.0.1:9871/#/models) · [Features](http://127.0.0.1:9871/#/features) · [Changelog](http://127.0.0.1:9871/#/changelog)

The major turns: the dashboard's first start, the app's first start
(the `run` skill), each handoff (in its **Your turn**), each feature
finished, each change made, and the build's last message. Before the
app runs, the line has the dashboard alone.

**The dashboard's first start** gets its line as soon as it answers,
whatever comes next, never only "it's live on port <port>": the
objects already written, each a link to itself on the models page,
then the three pages:

> Dashboard is up: [Hotel](http://127.0.0.1:9871/#/models?type=hotel.v1.Hotel) · [Room](http://127.0.0.1:9871/#/models?type=hotel.v1.Room) · [Stay](http://127.0.0.1:9871/#/models?type=hotel.v1.Stay). [Models](http://127.0.0.1:9871/#/models) · [Features](http://127.0.0.1:9871/#/features) · [Changelog](http://127.0.0.1:9871/#/changelog)

**A feature file, wherever it is named,** is two links: the file in
the project, and its page on the dashboard once the dashboard is up,
so the rules can be read where they live and where they run: the
path, tests/room_booking.feature, as a Markdown link to the file in
the user's project, then "(on the dashboard)" as a link to
http://127.0.0.1:9871/#/features/tests/room_booking.feature.
The same for a rule named on its own: its link is the feature's
dashboard link plus `/rules/<n>` (`dashboard` skill, "Links to an
Object or a Rule").

**Open the dashboard in the app's Browser pane** where the host has
one (the Claude app's `preview_start`), the first time it is up and
whenever the build links into it at a turn the user acts on (the
model check, each review). The dashboard is already running, so
attach to it: a configuration in `.claude/launch.json` named
`dashboard` with only `"url": "http://127.0.0.1:<port>"`, the port it
started on, and no command (the origin only, no path); start it by
name, then navigate to the page the turn is about, as a whole: the
model check opens `#/models` with no object selected (no `?type=`), so
the user sees every object and how they connect and opens one by
clicking it; the backend check opens `#/features`. A single object's
or rule's link is for the chat's own links, never the pane. The link line stays as well, for a host without a
pane and for later. Never start a second dashboard for the pane.

**Two pages side by side.** For the feature that adds a customer
side, the handoff's **How to check it** starts with the two pages side
by side: "Open the booking page as Carlos and the room board as Alice,
side by side. Book a stay as Carlos and watch it land on the board,
with no refresh." In the Claude app, both open in the Browser pane,
one tab each.

**The app, once it is ready to try.** The pane is for the user, not
for the build's own testing: the build tests the app in a headless
browser (the browser scenarios, and the checks in
`web-app/references/ui-design.md`, run with Playwright), never in the
pane, so no card for an app still being tested appears in the chat.
The app opens in the pane once, at the handoff's **Your turn**, ready
to try (a `launch.json` configuration named `app` with only its URL,
e.g. `"url": "http://localhost:5173"`, started by name), and for the
feature that adds a customer side, in two tabs, one per side. In the Claude app
nothing opens in the user's external browser: not the app, not the
dashboard (`dashboard` skill, Step 4, starts it with `BROWSER=true`),
not an MCP UI's setup wizard. Outside the Claude app, the skills'
usual behaviour stands.

**After every answer, say what comes next.** Whenever the user
answers a dialog or asks for something (how to build, the go-ahead,
the model check, the page, the next feature), the first thing after
it, before any tool call, is one or two sentences in plain words: what
will be done now, in the user's nouns, and what they'll see next, with
the time when the opening's estimates give one. Short: no list of
internal steps, no promise of further updates. For the go-ahead on a feature at a
time:

> Building the room status floor plan's domain model and rules now.
> Each room is its own durable object in Reboot, its status kept for
> it, so there is no database to set up. Each rule, such as a room
> can't be checked into until it's clean, is written first as a
> scenario in plain words; the floor plan isn't done until every one
> passes. The Reboot dashboard's link comes once the model is
> written, for you to check it before the rest is built on it.

Never a silent start after an answer, and never only a task list
update.

**Looking things up.** When the prompt asks for research (a real
company, a place, a regulation), say what is being looked up in one
line before the first search ("Looking up Kenmore Air's fleet, bases
and routes."), and after it, one line on what was found that the
design uses. When the research corrects the prompt (a name spelled
differently, a fact the prompt got wrong), say so in one line before
the design, and keep the user's own spelling nowhere it was wrong:
"Kenwood Air appears to be Kenmore Air, the floatplane airline out of
Lake Union; the design uses that name, easy to change."

**Backend and frontend, named apart.** Every message about building
says which half it is about: the backend (the domain model, the
rules, the actions, who may do each, the tests) or the frontend (the
page and the browser tests). The task list shows one part at a time,
and the messages open with "Backend:" or "Frontend:" ("Backend:
running the floor plan's 9 scenarios." "Frontend: building the floor
plan page."), so the user always knows which half is being worked on
and which is done.

**The tests, by their name.** To the user, the tests are "the tests"
or "the test suite", never "the suite" alone ("Backend: running the
full test suite, 14 scenarios.").

**Each question asked once, in the right place.** The Claude app
ends a working turn with a next-step box of its own (`wrap_up`: a
recap, one question, reply buttons), and that box also checks off the
whole task list. So:

- **Questions inside the build** (Build on this design?, after the design; Build on
  this domain model? (the model check), Build the frontend: the <screen>?, What
  should I build next?) are dialogs (`AskUserQuestion`) asked while the
  turn goes on, never the box: the box would tick every item on the
  list before anything is built, and the list would then have to be
  made again.
- **The end of a feature asks one dialog,** What should I build
  next?, its options the next parts, the recommended one first, and
  "Not yet" ([`accept-design.md`](accept-design.md)). A part chosen
  starts it in the same turn, with its new list. On "Not yet", or a
  skipped dialog, the box gets the recap only, with no `ask` and no
  buttons: the feature is running for the user to try.
- **Every question inside the build offers a way to learn more before
  answering:** "Tell me more" on Build on this design? and Build the
  frontend: the <screen>?, "Walk me through it" on the model check
  (`design-first.md` gives each one's answer). It answers in the chat
  and asks the same dialog again. What should I build next? describes
  each part in its option instead, since its options are the parts.
- **On the power-user path none of these is asked** (`design-first.md`,
  section 3): each prompt is built as asked, **Your turn** ends with
  the plain line "Say what's next.", and the box carries the recap
  only.
- A dialog the user skipped is not a reason to ask again in the box.

**A change to the look** (colors, typefaces, a brand, corners, the
layout), asked for at any point after the first handoff, goes to the
[`design-review` skill](../../design-review/SKILL.md): it reviews the look first, then the user picks from previews
and each change can be undone. It isn't a feature, so nothing is
recorded as kept for it.

**A review of the domain model or the architecture** ("will this
scale?", "review the data model") goes to the
[`domain-review` skill](../../domain-review/SKILL.md): it reviews from numbers and
makes the changes the user picks, every rule still passing.

**What to build next, for a roadmap or "what's missing"** goes to the
[`what-next` skill](../../what-next/SKILL.md): it weighs
what's built, the design's gaps and original research, and suggests
four to six features with their evidence.

**Keeping a feature is recorded when the user asks for more.** When
the user asks for the next feature, or says to keep this one, the
build records it as kept ([`accept-design.md`](accept-design.md)) and says
so in a few words, as tidying up, with what it means in parentheses,
then what's next: "Tidying up the chore board first (its rules are
locked in, so later features won't change them without asking you).
Next, recurring chores: their backend first, about 15 to 20 minutes."
Never the mechanics: "kept", "recording", work-in-progress tags, the
accepted design or the decisions log.
Nothing
is recorded while the user only tries the app.

**At every stage, say what is being done and what Reboot brings to
it.** Each task-list item that starts gets two or three sentences
before its work: what the build is doing now, in the user's nouns, and
the part Reboot does that a usual stack leaves to the developer. Plain
and specific, never a sales line, and each point said once in a build,
not repeated at every feature or in a wait note
([`while-you-wait.md`](while-you-wait.md)) later. What to draw on, at the stage it fits:

- **The design:** the app is described as domain objects and the rules
  they keep, before any code, so what's proposed is what gets built
  and checked.
- **The domain model:** each domain object is its own durable actor
  with its state kept by Reboot; there is no database to set up, no
  tables or migrations, and no cache to keep in sync.
- **The rules:** each rule is written as a scenario in plain words
  before the code, and the build isn't done until every scenario
  passes; a rule the code breaks shows up as a failing scenario, not
  a bug report.
- **Who may do what:** every action declares who may call it, checked
  by Reboot on each call, so a page can't reach what its user isn't
  allowed to.
- **Actions across objects:** a transaction changes several objects
  all or nothing, so a check-in can't half happen.
- **The dashboard:** the Reboot dashboard draws the domain model and
  the rules from the code itself, so what the user checks is what
  runs.
- **The page:** the page subscribes to its data and updates on its own
  when anything changes, with no refresh and no polling code.

**Show the first feature's rules, the first time, in plain words.**
Once the first feature file is written, list its rules in the chat,
one line each in the user's nouns, each a link to the rule on the
dashboard's Features page, with how many scenarios test it; then one
or two sentences on what they are: each rule is something the app
must keep true, and each is tested by scenarios, examples of someone
acting and what must hold after, written in plain words in the
feature file; the feature isn't done until every scenario passes.
Never the file's text or a code block of it: the user reads the rules,
and opens the file on the dashboard if they want the scenarios. Once
per build; later features name their rules the same way.

For the hotel:

> Room booking's rules, each tested by its scenarios:
> - [A room can't be booked twice for the same night](<link>) (3 scenarios)
> - [A stay needs at least one night](<link>) (2 scenarios)
> - [Only the front desk can cancel a guest's booking](<link>) (2 scenarios)
>
> Each rule is something the app must keep true. Its scenarios are
> examples in plain words, someone acting and what must hold after,
> and the backend isn't done until every one passes.

**Fixes stay in the user's terms.** A fix while proving a feature is
said as what it changes for the user, in one sentence, or not at all
when it changes nothing they'd see ("A scenario was phrased in a way
the test steps don't accept; reworded, same rule."). Never the
mechanics: step libraries, `Given` restrictions, response paths,
field names.

**While a slow step runs,** a short true fact about Reboot that fits
it goes out first, once per build each:
[`while-you-wait.md`](while-you-wait.md).
