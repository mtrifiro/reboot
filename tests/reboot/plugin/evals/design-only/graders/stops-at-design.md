---
type: llm
weight: 1
---

PASS if the final answer presents the proposed design itself (its features with their rules, and the things the app keeps track of), and then stops at the design: it says the design goes in design/design.md and that the user can say "build it" or ask for changes, and it does not start building code (a project scaffold, an API file, servicers, tests, a page) or announce that as its own next action. These do not fail it: a statement that nothing could be written in this session; saying that design/design.md would be or will be written, now or later; listing the design's methods. FAIL if the answer ends by asking the user a question, if it starts or announces building the first feature's code, or if it shows only a pointer to the design file without the design. Quote what you relied on.
