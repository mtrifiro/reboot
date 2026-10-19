---
type: llm
weight: 1
---

PASS if the plan builds a backend only for the user's React Native app: no web pages or SPA of its own and no MCP App, with a client generated for React Native (`rbt generate --mobile`, or a React Native client named in other words) for the user's app to call. FAIL if it plans web pages or an MCP App as part of this build, or generates no client for the mobile app. Quote what you relied on.
