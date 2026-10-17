---
type: llm
weight: 1
---

PASS if the final answer presents the proposed design itself (its features with their rules, and the things the app keeps track of), and then stops at the design: it says the design goes in design/design.md and that the user can say "build it" or ask for changes, and it does not start, describe starting, or plan the build steps (no scaffold, no API file, no tests, no page) as its own next action. A statement that nothing could be written in this session does not fail it. FAIL if the answer ends by asking the user a question, if it proceeds to or announces the build of the first feature, or if it shows only a pointer to the design file without the design. Quote what you relied on.
