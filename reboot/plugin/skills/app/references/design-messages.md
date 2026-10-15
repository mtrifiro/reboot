---
title: The Proposed Design and the Handoff, Word for Word
impact: HIGH
impactDescription: Without a fixed shape each build presents its design differently, and the user has to learn a new layout before judging the app
tags: design, proposed design, handoff, template, review
---

## The Proposed Design and the Handoff

Two messages carry the design to the user: the proposed design,
before any code, and the handoff, when a part is running. Write each in exactly this
shape: the same headings, in this order, with nothing before the
heading. Fill the `<…>` from the design, in the user's nouns. A
heading with nothing to say is left out, never filled.

### The proposed design

About 600 words. The example is a hotel; keep the shape, not the
nouns.

```markdown
## <App name>: the proposed design

**Brief.** <Who uses <app name> and on what screen.> <Their main job, as a
cycle or flow when there is one: *occupied → dirty → cleaned →
inspected → occupied*.> The main page answers one question: **<the
question>** The name is **<name>** and the accent is **<accent>**
(<why it suits the domain>).<When the build picked them: " Both were
picked for you; either is easy to change.">

**<What the build assumed> (picked for you, easy to change).** <The
counts, layouts and names the brief left open, in one paragraph:
floors 2–8 with 8 rooms each, numbered 201–808, …>

**Domain model (proposed)**
- **<Object>:** one per <what>, keyed by <id>. It holds <fields, in
  plain words>. It is its own object because <why: what changes on
  its own, what runs one at a time, what that prevents>.
- **<Object>:** …
- *Later features add* <objects, comma-separated>.

**Proposed features, in build order**
Only the first is built next; the rest, and their order, are yours to
change at any point.
1. **<First feature> (first).** <Why it comes first: the central
   object and a rule the user can see it keep.> Rules:
   - <A rule, one line, the key words in bold.>
   - …
2. <Feature>
3. …

**<First feature>: methods.** <One line on who calls them.>

| Object | Method | Kind | Role for an AI caller |
|---|---|---|---|
| <Object> | `<method>` (<what it does, when not obvious>) | <Reader, Writer, Transaction or Workflow; constructor> | <tool, `UI()` view, app only, or people only> |

**Pages**
- `<route>`: <the page's primary view, worked on directly>, <what a
  click opens>. <The one reader that feeds it.>

**Sign-in.** <Who signs in, how in development and at deploy, and
what an anonymous visitor sees.> <In development, the picker's five
accounts and the role each plays: "Alice is the founder, Ben the CTO,
…".>

Building <first feature> now.
```

With a full prototype chosen, the methods table covers every feature,
and the last line is "Building the whole prototype now."

### The handoff

About 500 words. The first handoff shows everything built; a later one
shows only what that part adds, under the same headings.

```markdown
**Ready for your review**

<One sentence: what is running, in the user's nouns.>

**Open it:** <URL>. <How to sign in, and who each test account is:
Alice is the manager, Ben is front desk, …> <Any browser caveat.>

<A screenshot of the page.>

**What it keeps track of**
- [<Object>](<dashboard link>): one per <what>. It holds <fields>. It's
  its own object because <why>.
- …

**What it does.** All <n> scenarios pass, including <n> that drive the
real page in a browser, and mypy is clean.
- **<Action>** (<who may do it>). [Rule: <the rule's words>](<link to
  the rule on the Features page>). Its scenarios cover <the cases>.
- [Rule: <a rule with no action of its own>](<link>).
- The browser scenarios' videos and screenshots are on the [Features
  page](<link>).

**How to check it:** <sign in as whom, open what, try what>. The rule
refuses it. <A second thing to try, when there is one.>

**Not built yet**
<n>. <Feature>
…

**Notes**
- <What the build added beyond the brief, and why.>
- <A workaround, one line: what it is and what undoes it.>
- <What waits for deploy: the sign-in provider, who may sign in.>

**In short:** <one or two sentences: what now runs and what the
question below decides>. [Open the app](<URL>) ·
[the dashboard](<dashboard URL>) · [the design](design/design.md)
```

**In short** is always last, right above the question: the message is
long, and the user reads its end while answering, after **Open it**
has scrolled away. Its links are the same as above.

Then the one question, as [`accept-design.md`](accept-design.md) says:
accept this and build the next part (named, with why), another, or
change something first.
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
