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
heading but a horizontal rule (`---`) on its own line, and a rule after
the last line, so each reads as a document set apart from the step
lines and dialogs around it. No other message is framed. Fill the `<…>` from the design, in the user's nouns. A
heading with nothing to say is left out, never filled.

### The proposed design

The design itself is `design/design.md` (the `app-design` skill,
section 3), linked from the summary; no page is drawn for it. The chat carries its summary, about 120 words. The example is a
hotel; keep the shape, not the nouns.

```markdown
---
## Reboot Design · <App name>, the proposed design

**[The whole design](design/design.md)** is in design/design.md: the
brief, the features and their rules, the domain model, the pages and
sign-in, and what Reboot does for you here.

**Brief.** <Who uses <app name> ("(working name)" after it unless the
user named the app), and the one question
the main page answers.> The palette is **<palette, in words, with its
band and paper>**.

**Features, in build order:** 1. **<First feature> (first)**, <why it
comes first, in a clause>; 2. <feature>; 3. …

**Assumed, all easy to change:** <the name, counts, hours: the few
that shape the app most>.

---
```

Where commands can't run, the whole design goes here instead, in
`design.md`'s shape without its methods, between the same two rules.

Sent the moment the page opens. Then the build, with no go-ahead
(`design-first.md`, section 3); nothing between them but, in a guided
web app build, the mockup, made while the user reads, and its one line
(`web-app/references/comp.md`).

### The handoff

About 500 words. The first handoff shows everything built; a later one
shows only what that part adds, under the same headings.

```markdown
---
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
real page in a browser, and mypy is clean. <Or, the suite still
running: "The feature's <n> scenarios pass; the whole suite is running."> The <main page> shows its
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

**In Claude or ChatGPT**
<At the first handoff of a build that started the developer dashboard:
the `dashboard` skill's step 6, required, as it says there: installing
`cloudflared`, the tunnel command `rbt dashboard` printed, verbatim,
adding the address with `/mcp` as a connector in Claude and in ChatGPT,
and its two reminders.>

---

### Exegesis · <the part>
<only in a verbose build (`exegesis.md`): what this part's code means
and why it is shaped so, 250 to 450 words with the decisive lines
quoted; the same text appended to design/exegesis.md. Its rule above
sets it apart; the rule before **Your turn** closes it.>

---

## Your turn

**Try it:** [open the app](<URL>) and sign in as <who>. <The one thing
to try first, in a sentence: the action and the rule that holds.>

**Look closer:** dashboard [Models](<URL>/#/models) ·
[Features](<URL>/#/features) · [Changelog](<URL>/#/changelog) ·
[the design](design/design.md)<in a verbose build: " ·
[the exegesis](design/exegesis.md)">

**Build next, when you're ready:**
1. **<The recommended part>:** <what it adds, and why it comes next>.
   About 15 to 20 minutes.
2. **<Another part>:** <what it adds, in one line>.
3. **<Another part>:** <what it adds, in one line>.

Or ask for a change to what's here. <When the other front door isn't
built: "The backend can also serve an MCP App for Claude and ChatGPT;
ask to add it.">

---
```

**Your turn** is always last, set apart by the rule and its heading:
the message is long, and it is what the user acts on, after **Open
it** has scrolled away. Then one dialog, **What should I build
next?** ([`accept-design.md`](accept-design.md)), its options the
parts listed under **Build next**, so the user picks one with a click
instead of typing its number. Nothing follows it but the link line
(`app-guided` skill, step 4) when the turn has one to give, and no other line
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
