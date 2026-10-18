---
title: The Proposed Design and the Handoff, Word for Word
impact: HIGH
impactDescription: Without a fixed shape each build presents its design differently, and the user has to learn a new layout before judging the app
tags: flywheel, design, proposed design, handoff, template, review
---

## The Proposed Design and the Handoff

Two messages carry the Reboot Flywheel's Design stage
([`flywheel.md`](flywheel.md)): the proposed design, before any code,
and the handoff, when a part is running. Write each in exactly this
shape: the same headings, in this order, with nothing before the
heading. Fill the `<…>` from the design, in the user's nouns. A
heading with nothing to say is left out, never filled.

### The proposed design

The whole design but its methods, about 500 words: this is what the
user signs off on with the question after it, so it shows the design
itself, not a pointer to `design/design.md`. The methods stay in the
file only: they are the build's detail, not what the user decides. Writing it takes about a minute, and the
go-ahead is worth it. The example is a hotel; keep the shape, not the
nouns.

```markdown
## Reboot Design · <App name>, the proposed design

**Brief.** <Who uses <app name> (working name) and on what screen: the
name's first mention, "(working name)" right after it when the build
picked it.> <Their main job, as a
cycle or flow when there is one: *occupied → dirty → cleaned →
inspected → occupied*.> The main page answers one question: **<the
question>** The name is **<name>** and the accent is **<accent: one of navy, teal, cyan, blue, indigo, violet, purple, plum or rose, by that plain name, never a theme such as "newsprint">**
(<why it suits the domain>).<When the build picked them: " Both were
picked for you; either is easy to change.">

**<What the build assumed> (picked for you, easy to change).** <The
counts, layouts and names the brief left open, in one paragraph:
floors 2–8 with 8 rooms each, numbered 201–808, …>

**Proposed features, in build order**
Four or five, in the order they would be built; yours to change.
1. **<First feature> (first).** <Who it is for and the job it gets
   done, start to finish: what they create, see, find, change, correct
   and end.> <Why it comes first: the central object and a rule the
   user can see it keep.> Rules:
   - <A rule, one line, the key words in bold.>
   - …
2. **<Feature>.** <For whom, the job start to finish.> Rules: …
3. …

**Not in this build:** <what else a real app in the domain needs, one
line each, Who may do what among them>. Built only when you ask.

**Domain model (proposed)**
- **<Object>:** one per <what>, keyed by <id>. It holds <fields, in
  plain words>. It is its own object because <why: what changes on
  its own, what runs one at a time, what that prevents>.
- **<Object>:** …
- **`User`:** one per person who signs in, keyed by their sign-in ID.
  It holds <what hangs off a signed-in person>. (In every design.)
- *Later features add* <objects, comma-separated>.

**Pages**
- `<route>`: <the page's primary view in the domain's own shape (a
  floor plan, a board, a calendar), worked on directly: what a tap
  does, what a drag moves where when something moves, what a click
  opens>; <what it leads with, which states carry colour and where the
  accent goes, the normal state plain and the accent on one action:
  "leads with rooms ready and arrivals waiting; dirty, out of order and
  leaving today in colour, ready rooms plain; the accent on Check in">.
  <The one reader that feeds it.>

**Sign-in.** <Who signs in, how in development and at deploy, and
what an anonymous visitor sees.> <In development, the picker's five
accounts and the role each plays: "Alice is the founder, Ben the CTO,
…".>

**What Reboot does for you here.** <Three or four bullets, each one of
these said for this design, in its nouns, naming what the developer
doesn't write: each <Object> is a durable object holding its own state
(no database, tables or migrations); <the rule that spans objects> is
one transaction, all or nothing (no rollback code); <the page> updates
live when anyone changes it (no polling or websocket code); each rule's
scenarios are the tests (no separate test harness); the same backend
serves an MCP UI for Claude or ChatGPT (no second API).>

The whole design, with its methods, is in
[design/design.md](design/design.md).
```

Then the go-ahead's dialog (`design-first.md`, section 3);
nothing between them.

### The handoff

About 500 words. The first handoff shows everything built; a later one
shows only what that part adds, under the same headings.

```markdown
**Reboot Design · ready for your review**

<One sentence: what is running, in the user's nouns.>

**Open it:** <URL>. <How to sign in, and who each test account is:
Alice is the manager, Ben is front desk, …> <Any browser caveat.>

<A screenshot of the page.>

**What it keeps track of**
- [<Object>](<dashboard link>): one per <what>. It holds <fields>. It's
  its own object because <why>.
- …

**What it does.** All <n> scenarios pass, including <n> that drive the
real page in a browser, and mypy is clean. The <main page> shows its
first record <n> ms after it opens.
- **<Action>** (<who may do it>). [Rule: <the rule's words>](<link to
  the rule on the Features page>). Its scenarios cover <the cases>.
- [Rule: <a rule with no action of its own>](<link>).
- The browser scenarios' videos and screenshots are on the [Features
  page](<link>).

**What Reboot did for you.** <Two or three lines, for what was just
built, naming what isn't in the code because Reboot does it: "There is
no database schema, migration, API layer or websocket code in this
app: <Object>'s state is kept by Reboot, <the action> is one
transaction, and <the page> is live through its reader."> Said once,
at the first handoff; later handoffs name only what is new.

**How to check it:** <sign in as whom, open what, try what>. The rule
refuses it. <A second thing to try, when there is one.>

**Not built yet**
<n>. <Feature>
…

**Notes**
- <What the build added beyond the brief, and why.>
- <A workaround, one line: what it is and what undoes it.>
- <What waits for deploy: the sign-in provider, who may sign in.>

---

## Your turn

**Try it:** [open the app](<URL>) and sign in as <who>. <The one thing
to try first, in a sentence: the action and the rule that holds.>

**Look closer:** dashboard [Models](<URL>/#/models) ·
[Features](<URL>/#/features) · [Changelog](<URL>/#/changelog) ·
[the design](design/design.md)

**Build next, when you're ready:**
1. **<The recommended part>:** <what it adds, and why it comes next>.
   About 15 to 20 minutes.
2. **<Another part>:** <what it adds, in one line>.
3. **<Another part>:** <what it adds, in one line>.

Or ask for a change to what's here. <When the other front door isn't
built: "Want it in Claude and ChatGPT too? The backend is ready for an
MCP UI beside the web app.">
```

**Your turn** is always last, set apart by the rule and its heading:
the message is long, and it is what the user acts on, after **Open
it** has scrolled away. Then one dialog, **What should I build
next?** ([`accept-design.md`](accept-design.md)), its options the
parts listed under **Build next**, so the user picks one with a click
instead of typing its number. Nothing follows it but the link line
(`guided` skill, step 4) when the turn has one to give, and no other line
repeats what it says.
The full review table goes to `design/design.md`, not into this
message.

The development sign-in's five accounts are built into Reboot and
always the same: Alice, Ben, Carlos, Dani and Esi
(`python/references/auth-claims.md`). The design gives each a role
from the app's own; it never names accounts the picker doesn't show.

## Never

- Anything before the heading: no "Quick status", no "Here's the
  proposed design", no list of what was read.
- A heading renamed, reordered or added. What doesn't fit goes under
  **Notes**.
- Code names where the user's nouns exist: `check_in` belongs in the
  methods table and the links, not in the sentences.
