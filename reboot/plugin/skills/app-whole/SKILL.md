---
name: app-whole
description: Build a complete Reboot application in one go, asking nothing (or, with ", basic" after the prompt, one feature of it the same way). Designs every feature a real product in the domain needs, not only those the prompt names, builds the whole app with every rule and scenario without stopping, reviews its domain model and its look and fixes what the reviews find, and hands it over once, at the end. Use only when the user asks for it by name ("/reboot:app-whole", "one-shot", "one shot"); otherwise the app skill asks how to build and routes to the guided, one-shot or build skill.
argument-hint: [<app-description>]
allowed-tools: Bash, Read, Write, Glob, Grep, Edit, Agent, Skill
---

# one-shot: a Complete Reboot Application, Asking Nothing

From the prompt to a finished app, the proper way, with no question
until the end: the design, every feature with its rules proven by
scenarios, every page tested in a browser, a domain review and a look
review with what they find fixed, and one handoff. Nothing stops the
build but the end. The `app-guided` skill is not loaded: its round of
questions and its go-ahead are what this skill leaves out.

> **The user sees only message text.** Every line this skill says
> (the opening, the design, What to expect, each feature finished,
> each review, the handoff) goes out as the response's own text,
> before that response's tool calls. Drafting it in thinking is not
> saying it.

## 1. The design, by the `app-design` skill

The response's first act is to load the [`app-design`
skill](../app-design/SKILL.md) with the Skill tool (`/reboot:app-design <the
prompt>`), never by reading its file. Loaded by this skill it asks
nothing. Right after it loads, its opening goes out as text (the two
Skill loads are the response's only tool calls before it; hotel-200
said nothing for 69 seconds and its first text was the design), its
third sentence "No questions: the whole app is designed, then built,
tested and handed over when it is done." word for word. Then it reads
what the design needs, shows the whole proposed design in the chat
with the scope of section 2, and writes `design/design.md` right
after it.

Then, in the same turn, **What to expect**, a list of four lines:

> What to expect:
> - The domain model and every rule first, with the Reboot
>   dashboard's link once it is written: the app's domain model and
>   rules, updated as they're built.
> - Then every feature, its rules proven by scenarios, and every page
>   tested in a browser, without stopping: about <10 minutes a
>   feature, more for a hard domain>.
> - Then a review of the domain model and of the look, and the fixes
>   they call for, about 15 minutes.
> - Nothing to answer until it's done; then you say what's next.

**The task list** has the whole-app items
([`app/references/task-list.md`](../app/references/task-list.md),
"The whole app at once", or "The first feature only" for ", basic")
with no go-ahead, its last item "Review the domain model and the
look, and fix what they find". No item is called "Your turn": the
handoff's **Your turn** section ends the build, and isn't a step of
it.

## 2. Ambitious scope, the round answered

Design the app a team in this domain would run its work on end to
end, not the smallest app that fits the prompt:

- **Every feature the prompt names,** and every feature a real product
  for these users needs to do their whole job: for a hotel, the rooms
  and housekeeping, reservations and the front desk, staff roles,
  guest profiles, amenity bookings, concierge requests, and the
  folio and billing. Aim for six to ten features, each with the rules
  that make it trustworthy, in build order; **Not in this build**
  holds only what a real product could still go without.
- **Every role** that does that work, with what each may do, from the
  first build: **Who may do what** is one of the features, not left
  for later.
- **Pages** for each role's daily work, each with its primary view,
  what it leads with, which states carry colour and where the accent
  goes.

The round's other answers, taken without asking: the palette
the app-design skill would recommend for the domain (or the brand the
prompt names); "How should it be built? One-shot". Each answer and each
feature added beyond the prompt goes under **Assumed**, the feature
with one line on why a real product needs it.

### Basic: one feature

When the argument ends with ", basic" or ", basic, verbose" (the
[`app-basic` skill](../app-basic/SKILL.md), the app skill's "First
feature only"), the build is this skill with one feature in place of
six to ten, and nothing else changes: no questions, the reviews, one
handoff. With ", verbose", the exegesis is on
([`app/references/exegesis.md`](../app/references/exegesis.md)): the
handoff's report ends with the one feature's, and the same text is in
`design/exegesis.md`.

- **A mockup first,** for a web app: right after `design/design.md`,
  the comp as [`web-app/references/comp.md`](../web-app/references/comp.md)
  says for this path, its line said and no stop. The page (and the
  frontend sub-agent, which reads it) builds from it; its server is
  stopped when the app starts.

- **The one feature** is the heart of the prompt: the work the app is
  for, the one its users would open it to do (for a hotel, the rooms
  and the front desk), with the rules that make it trustworthy, its
  page, and who may do what folded into its rules. Sign-in comes with
  the starter and is not a feature.
- **Not in this build** lists the features section 2 would have
  added, in build order, each a line, so "Change something" at the
  handoff ("a feature to add") has a list to start from.
- The opening's third sentence is "No questions: one feature is
  designed, then built, tested and handed over when it is done." word
  for word, and **What to expect** says "Then that feature, its rules
  proven by scenarios, and its page tested in a browser, without
  stopping: about <10 minutes>." in place of its second line.
- The ", basic" is not part of the app's name or its Brief.

## 3. No questions

Ask nothing, from start to finish: no round, no go-ahead on the
design, no acceptance between features, no dialog from a review.
Where a skill this one loads would ask, take the answer it marks as
recommended, or decide the same way: the simplest choice that fits
the scope, listed under **Assumed** in `design/design.md` and named at
the handoff. Times are in the user's own time zone.

## 4. The build, without stopping

**The front door** is the one the prompt names, by the `app` skill's
Routing triggers: MCP, an AI host named as where it runs, or "a tool
for an agent" is an MCP App (`/reboot:mcp-app`); a URL, a route,
"website", "web app", "SPA" or "in the browser" is a web app
(`/reboot:web-app`); "an API", "a backend", "headless" or "for my
mobile app" is a backend only
([`app/references/backend-only.md`](../app/references/backend-only.md));
nothing named is a web app. Load the door with the Skill tool, never
by reading its file, and build by its whole-app flow: for a web app,
[`web-app/references/full-build.md`](../web-app/references/full-build.md);
for an MCP App, its Step-by-Step Build Flow for every feature. The
door's Design Phase, scope round and dialogs are skipped: the design
is done. Read [`app/references/conversation.md`](../app/references/conversation.md)
once, for what the build says at each step.

Build the prototype first, then every feature in the design's order,
each with its rules and scenarios. Between features, say in one line
which is finished and go on; never wait for an answer.

- **The frontend by a sub-agent** (the Agent tool, where the host has
  it) builds the pages beside the backend. It loads no skill, so its
  prompt carries the rules it would never see, word for word: read
  each plugin file with the Read tool, one call per file, never `cat`
  or `sed`; change a file that exists with the Edit tool, never a
  script or `sed -i`; the references to read, by path,
  `web-app/references/react-client.md`,
  `web-app/references/ui-design.md`,
  `python/references/react-generated-client.md` and
  `python/references/testing-web-app.md`; and the house rules it
  keeps: the accent from `styles.css` and no raw color outside it,
  every control and heading labelled for the browser scenarios, each
  page's primary view, what it leads with, which states carry colour
  and where the accent goes as the design's page line says
  (`ui-design.md`, "What the Eye Lands On"), and `design/comp/mockup.html`
  as the main page's target when it exists (the app-guided skill's
  all-at-once path drew it before the go-ahead). (hotel-200's
  sub-agent read four references by `cat` and edited by `sed -i`.)
- **Read this plugin with the Read tool,** one call per file, several
  in one response, never `cat`, `awk` or a loop in a shell (the
  `python` skill's rule: a long shell result comes back as a preview
  and the rest goes unread). A file that exists is changed with the
  Edit tool, never rewritten.
- **A failure:** fix it and go on. A scenario that can't pass after a
  real attempt is tagged `@blocked` with its reason, and the build
  goes on to the next feature; it is named at the handoff.
- **Something the design got wrong:** change the design document and
  the feature, note it for the handoff, and go on.
- **The prototype's "try it" message** is said in one line with the
  URL; the build doesn't wait for it.

The build part ends when every feature is built, the whole suite runs
once (browser scenarios included) with every scenario passing or
`@blocked` with its reason, and mypy is clean
(`full-build.md`, step 18, up to the handoff).

## 5. The reviews, and their fixes

Two reviews of what was built, each by its skill's own method, with
no dialog: the build picks what to fix by the rules below. Read each
skill's file with the Read tool for its method; don't load it with
the Skill tool, which would start its conversation.

**The domain model** ([`review-domain`](../review-domain/SKILL.md)):

1. Its sections 1 and 3: `review.py`, then the review, the scale taken
   from the design's own counts (the scale dialog's recommended
   answer, never asked), written to `design/review.md`. Say its verdict in two lines.
2. Fix every finding marked **now** or **before the first deploy**,
   one at a time, by its section 4: measured first when it is about
   load, every rule and scenario unchanged, the suite and mypy green,
   the probe again, one commit "Domain: <what changed>". A finding
   whose fix would change a rule, or what a user sees, is not made:
   it goes to the handoff.

**The look** ([`review-ui`](../review-ui/SKILL.md)), for a web
app:

1. Its section 2: capture every page at desktop and phone width,
   light and dark, measure, judge, and write `design/look-review.md`.
   Say its verdict in two lines.
2. Fix every finding that breaks a rule of
   `web-app/references/ui-design.md` ("What the Eye Lands On"
   included: a page that leads with nothing, a resting state in
   colour, the accent on names or a status, a page a third empty) or
   fails a measurement (contrast, spill, clipped text, touching
   controls, a raw color outside `styles.css`, a page that doesn't
   hold at phone width or in the dark scheme), as its "Beyond the
   Tokens" says, then capture that page again. A change of taste (the
   accent, the page tones, the typefaces, the corners) is never made:
   it goes to the handoff.

After the fixes, the whole suite and mypy once more when anything
changed, the result said once.

## 6. One handoff, at the end

`design/design.md` rewritten as built, its links checked by
`scripts/design_links.py`; then the handoff in the shape of
[`app/references/design-messages.md`](../app/references/design-messages.md),
covering every feature (in a verbose build, asked for in the prompt,
its **Exegesis** covers the whole app in about 400 words and links
`design/exegesis.md`, written feature by feature as the build went:
[`app/references/exegesis.md`](../app/references/exegesis.md)), with
under **Notes**, when the reviews ran:
what each review fixed, in a line each with its numbers, what it found
and left for the user (a rule change, a change of look), and the links
to `design/review.md` and `design/look-review.md`. Every `@blocked`
scenario is named with its reason, and every assumption that shaped
the app is in **Assumed**.

No dialog: **Your turn** ends with the plain line, word for word,
"I built all the features you asked for. Tell me what you want to do
next: change something, add a feature from **Not built yet**, write a
user manual for your staff, explain how the code works, or put it
online." (when a feature is
blocked, "all the features you asked for but <the feature>, under
Notes"). Then stop.

What the user says next decides, as
[`app/references/accept-design.md`](../app/references/accept-design.md)
says: a change or a feature to add is made as the `feature` skill
makes any change, then a handoff for it ending with the same line; a
manual is the [`manual` skill](../manual/SKILL.md)'s and the code's
explanation the [`explain` skill](../explain/SKILL.md)'s, each loaded
with the Skill tool; putting it online is the [`deploy` skill](../deploy/SKILL.md)'s;
asking for anything else, or saying it is good, accepts the app as
built, recorded as `accept-design.md` says, with **Assumed** in the
first decisions entry, and one line saying what that means
(accept-design.md, "What accepting means"). Trying the app, or no
reply, is not acceptance.

## Never

- A question, a dialog or a wait for an answer before the handoff,
  from this skill or any skill it loads or reads.
- The `app-guided` skill loaded: its round and go-ahead are the questions
  this skill leaves out.
- A smaller app than the domain needs because the prompt was short.
- A feature dropped silently: a feature that can't be finished is in
  the handoff, with what blocks it.
- A feature or an answer taken without its line under **Assumed**.
- A rule, a scenario, or the app's look changed by a review fix: those
  are the user's, named at the handoff.
- The handoff before the reviews, or before the suite and mypy are
  green after their fixes.
