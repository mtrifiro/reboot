# What Reboot Does for an App

For verbose mode's third part ([`verbose.md`](verbose.md)): one entry
per capability. Each says what Reboot does, the work it takes off the
developer, and where it shows in the dashboard. Use an entry only when
the app's code uses it, said in the app's nouns. Each rests on the
reference named, which has the detail.

**Durable state on each actor.** A state type's fields are its
storage: Reboot persists every committed write, and the state is there
after a restart or a crash. No database to run, no schema, no ORM, no
migrations for a new app. *Models page: each state type's properties.*
(`python/references/state-actor-decomposition.md`)

**Writers.** One method changes one actor's state, and calls to the
same actor are serialized for you. No locks, no read-modify-write
races. *A writer's pane: what it takes and raises.*
(`python/references/servicer-writer.md`)

**Transactions.** One method changes several actors all together or
not at all; an abort rolls every change back. No two-phase commit, no
compensating code, no half-done state to clean up. *A transaction's
pane and the graph: every actor it calls.* (`python/references/servicer-transaction.md`)

**Readers, live in the browser.** A page that reads with a reader hook
re-renders whenever the state changes, from any session. No REST
endpoints, no fetch client, no polling, no websocket server, no cache
to invalidate. *Readers on the graph.*
(`frontend/references/react-generated-client.md`, "Live Updates Are Free")

**Generated clients.** `rbt generate` writes the typed Python and React
calls from the API file. No request and response types kept in step by
hand. *The API file beside each state type.* (`python/references/api-pydantic.md`)

**Workflows.** A long-running method that calls the outside world
(email, payments, an LLM) resumes where it left off after a crash, and
its memoized steps do not run twice. No job queue, no worker process,
no retry bookkeeping. *Workflows on the graph.* (`python/references/servicer-workflow.md`)

**Scheduling.** `schedule(when=...)` runs a method later, and a method
that reschedules itself is a recurring job that survives restarts. No
cron daemon, no scheduler service. *Dashed "schedules" lines on the
graph.* (`python/references/scheduling-basic.md`, `python/references/scheduling-recurring.md`)

**Idempotent calls.** `at_least_once` / `at_most_once` and the
`.per_workflow` / `.per_iteration` aliases make a step happen once
across replays. No idempotency keys or dedupe tables of your own.
(`python/references/servicer-workflow.md`, `python/references/patterns-idempotency.md`)

**Authorizers.** Each servicer states who may call each method, checked
before the method runs; a method without a rule is denied in
production. No permission middleware. *A scenario that expects
`PermissionDenied`.* (`python/references/servicer-authorizer.md`)

**Sign-in.** `oauth=` on the `Application` gives one User per person
for the web app and the AI client both, sessions included. No auth
server, no session store. (`python/references/auth-oauth-providers.md`, `python/references/auth-web-apps.md`)

**AI tools from the API.** A method marked `mcp=Tool()` is a tool
Claude or ChatGPT can call, with the same authorizer. No MCP server
code. (`python/references/mcp-app-concepts.md`)

**The durable agent.** An LLM agent inside a workflow whose model
calls are memoized: a replay after a crash does not call the model
again or bill twice. No caching of model calls of your own.
*Agents and their tools on the graph.* (`python/references/agent-pydantic-ai.md`)

**Collections.** `OrderedMap` and the other library types hold large,
sorted or queued data across many actors. No sharding of your own.
(`python/references/stdlib-ordered-map.md`, `python/references/stdlib-queue.md`)

**Scenarios on the dashboard.** The `.feature` files are the tests and
the spec at once: the dashboard shows each rule with the scenarios
proving it, and a browser scenario's video. No separate spec document
to keep in step. *Features page.* (`python/references/testing-features.md`)
