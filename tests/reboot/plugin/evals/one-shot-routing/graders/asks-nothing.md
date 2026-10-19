---
type: llm
weight: 1
---

PASS if the transcript asks the user nothing before the design or after it: no AskUserQuestion call, no round of questions about features, sign-in, palette or how to build, no go-ahead such as "Build on this design?", and the final answer does not end by asking the user a question or waiting for an answer. Stating assumptions and going on is fine; saying that a question comes only at the very end, after the app is built, is fine. FAIL on any question put to the user before the app would be built, or a final answer that waits for a reply before building. Quote what you relied on.
