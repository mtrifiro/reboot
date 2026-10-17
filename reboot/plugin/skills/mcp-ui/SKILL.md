---
name: mcp-ui
description: Build complete Reboot MCP UIs for ChatGPT, Claude, VSCode, Goose, and other MCP hosts. Layers on top of the python skill for backend mechanics; covers what's specific to MCP UIs — the User-type front door, MCP tool exposure, the UI() method type, and the full React/Vite scaffolding. The backend stays ready for a web app.
argument-hint: [<app-description>]
allowed-tools: Bash, Read, Write, Glob, Grep, Edit
---

# mcp-ui — Build Reboot MCP UIs

> **Version notices** from `rbt` (a mismatch, a newer Reboot): the [upgrade skill](../upgrade/SKILL.md).
>
> **Errors:** grep a fragment of the string in `python/references/errors.md` (never read whole); known defects and workarounds: [`KNOWN-ISSUES.md`](../../KNOWN-ISSUES.md).

Build complete Reboot MCP UIs from a user description.

> **Reads from `python`.** This skill is the MCP-App + React
> layer on top of the Reboot Python framework. Anything about
> Servicers, Reboot contexts, refs, scheduling primitives,
> backend LLM / agent calls, error types, the testing harness,
> the `.rbtrc` shape, or pydantic API defaults belongs in
> `python` — load those references for those concerns. This
> skill covers what's _specific_ to MCP Chat
> Apps: the `User`-type front door, MCP tool exposure, the `UI()`
> method type, the React/Vite scaffolding, and the cross-cutting
> rules unique to that layer.

> **Dual-frontend apps are supported.** A single app can serve both
> an MCP front door _and_ a standalone browser SPA from the same
> backend; they share `oauth=...`, the same `User` per upstream
> identity, and the same servicer code. For the standalone SPA
> piece, also load the
> [web-app skill](../web-app/SKILL.md). A user who signs in on
> one frontend is signed in on both (cross-frontend SSO): the OAuth
> server's `/authorize` short-circuits when the browser already
> carries a session cookie, and `/callback` sets that cookie
> on every flow.

## When to Use

- Building a new Reboot MCP UI from a description
- Adding features, state, or UI to an existing Reboot MCP UI
- Modifying state model, methods, or React UI in a Reboot MCP UI
- Running an existing Reboot MCP UI — e.g. at the start of a
  new session. This needs no design or build phase: load the
  [`run` skill](../run/SKILL.md), which detects the app type,
  starts the backend and frontend, and opens the setup wizard (from
  which the user can launch MCPJam on demand).

## Which References to Read, and When

The backend mechanics live in the `python` skill's references; the
MCP-UI-specific shape on top of them lives in this skill's own
`references/`. Neither set is restated inline below.

Everything you read stays in the conversation and is re-sent on
every later turn, so **read each reference at the step that needs
it** — not all of them up front — and read each one **once**. The
groups below are in build order, and each reference appears in
exactly one of them — the step that needs it. Never a whole generated
or installed file (`*_rbt.py`, `*_rbt_react.ts`, `site-packages/`,
`node_modules/`), and any search bounded hard:
[`front-door-common.md`](../app/references/front-door-common.md),
"Never Read Generated or Installed Source in the Main Thread".

> **Never read `web-app/references/*` for an MCP UI** (the standalone SPA's shell, `VITE_REBOOT_URL`, `<RebootClientProvider>` and sign-in buttons don't apply to the `frontend/mcp/<name>/` bundles an MCP host loads; the MCP UI equivalents are [`references/react-scaffolding.md`](references/react-scaffolding.md) and [`references/react-app-tsx.md`](references/react-app-tsx.md)), except `web-app/references/ui-design.md`, whose primary views and accent apply to `UI()` views too.

**Before the project shell** (`.python-version`, `pyproject.toml`,
`.rbtrc`, `.mypy.ini`, `main.py`):

- [`references/project-shell.md`](references/project-shell.md) —
  `.rbtrc` deltas, `pyproject.toml` extras, `main.py`,
  `example_prompts.py`.
- `python/references/lifecycle-{project-setup,rbtrc,application-entry}.md`
  — the layout, the CLI flags, `Application(...)`.

**Before the API definition:**

- `python/references/patterns-common-gotchas.md` — recurring trips.
- `python/references/api-pydantic.md` — pydantic API rules.
- `python/references/api-methods.md` — factory → context type mapping.
- `python/references/api-errors.md` — typed errors, when the API
  declares any.
- `python/references/state-collections.md` — **always read when the
  app has any "list of X" concept**, a synced or scraped one included.
- `python/references/state-nested-models.md` — only when a state
  nests a non-state `Model`.
- `python/references/state-actor-decomposition.md` — when one state
  `Type` has accreted multiple unrelated concerns; the `User` front
  door most of all.
- [`references/api-method-types.md`](references/api-method-types.md)
  — the MCP UI's API file: `User`, `mcp=`, `UI()`, `factory=True`.
- [`references/api-state-shapes.md`](references/api-state-shapes.md)
  — two recurring state shapes; composing actors by ID.
- [`references/gotchas.md`](references/gotchas.md) — the numbered
  MCP-UI trip list.

**Before the servicer:**

- `python/references/servicer-{reader,writer,transaction,constructor}.md` — one per context type you actually declared.
- `python/references/rpc-refs.md` — `self.ref().state_id`;
  `self.ref().schedule(...)`.
- `python/references/rpc-calls.md` — kwargs, not Request wrappers;
  `Service.create(context, id)`.
- `python/references/servicer-workflow.md` — only when you declared
  a `Workflow`, and then top to bottom.
- [`references/servicer-patterns.md`](references/servicer-patterns.md)
  — the MCP UI servicer shapes.

**Before the authorizers** (write rules from day one — see "Auth"
under Key Framework Concepts):

- `python/references/servicer-authorizer.md`,
  `python/references/auth-allow-if.md`,
  `python/references/auth-built-in-predicates.md` — the predicate
  machinery; `oauth=` makes real rules viable immediately.
- `python/references/auth-custom-predicates.md` — only when the
  built-in predicates don't cover a rule.
- `python/references/auth-allow-deny.md` — only when the design has
  a public, unauthenticated endpoint.
- [`references/auth-oauth-providers.md`](references/auth-oauth-providers.md)
  — when you pick a real provider, at deploy.
- [`references/auth-custom-oauth-provider.md`](references/auth-custom-oauth-provider.md)
  — **writing your own OAuth provider** when none of the shipped
  ones fits.
- [`references/auth-store-tokens.md`](references/auth-store-tokens.md)
  — **acting on the user's behalf** when the API belongs to your
  sign-in provider (`store_tokens=True`); any other service, and
  calling an external API inside a `Workflow`:
  [`python/references/auth-external-api-calls.md`](../python/references/auth-external-api-calls.md).

**Before `main.py`:**

- `python/references/lifecycle-seeding.md` — demo data from
  `initialize`, under `rbt dev run` only, idempotent on restart;
  always.

**Before the tests:**

- `python/references/testing-project-setup.md` — always.
- `python/references/testing-features.md` — the built-in steps'
  spelling; always.
- `python/references/lifecycle-seeding-troubleshooting.md` — only
  when `IdempotencyUncertainError` appears, or a seed stalls, hangs or
  errors.
- `python/references/testing-harness.md` and
  `testing-external-context.md` — for custom steps.
- `python/references/testing-custom-steps.md` — for custom steps.
- `testing-failure-recovery.md` — whenever the app has a spawned
  task, a `Workflow`, or `schedule()`d work.
- [`feature/SKILL.md`](../feature/SKILL.md) — the order of work
  around the feature files.

**The two parts.** Every group above this line is the backend part.
The groups from here on are the frontend part: read them only when the
frontend part starts, once the user says to build the frontend (or, on
the automatic paths, once every feature's backend passes), never
before, and not at all when the user stops after the backend.

**Before the frontend:**

- `web-app/references/ui-design.md` — the primary view for each
  `UI()` view and the accent; the rest is the web app's.
- [`references/react-scaffolding.md`](references/react-scaffolding.md)
  — the `frontend/` shell; `vite.config.ts` copied exactly.
- [`references/react-app-tsx.md`](references/react-app-tsx.md) —
  `App.tsx`, with the Counter example.
- `python/references/react-generated-client.md` — what
  `rbt generate --react=` emits.
- [`references/pop-out-to-web-app.md`](references/pop-out-to-web-app.md)
  — only when a widget needs a "pop out into the web app" button.

**Before running the app:** the [`run` skill](../run/SKILL.md) and its
[`run/references/mcp-ui-processes.md`](../run/references/mcp-ui-processes.md) (the
tunnel, the setup wizard, MCPJam).

## Workflow: Propose the Design, Then Build

**Always work out the design before writing code.** The design is a
proposal until the user accepts it, and the first stage of the Reboot
Flywheel:
[`front-door-common.md`](../app/references/front-door-common.md),
"The Design Is a Proposal".

### Design Phase

1. Analyze the user's description using the State Model Assessment
   below.
2. The scope round, as
   [`front-door-common.md`](../app/references/front-door-common.md)
   ("The Scope Round") says. The first question's options: "One
   feature at a time, so you understand each part as it's built"
   (recommended) or "The whole app first, then reviewed as a whole".
3. Read the references for the API, then show the proposed design,
   word for word in the shape of
   [`app/references/design-messages.md`](../app/references/design-messages.md)
   (its Pages section names the `UI()` views instead),
   with the answers in it, before writing the API. What it decides: the brief (who
   uses the app and on what screen, the task, the one question its
   main page answers, the accent), the features in a sentence each,
   and:
   - `User` type and its methods (the MCP front door for creating new
     application-type instances and locating existing ones).
   - Application types: state shape (fields, types, tags).
   - Method map: which operations, which method type
     (Reader/Writer/Transaction/Workflow), which get `UI()`, and
     each `UI()` view's primary view (the domain's own shape, such as
     a board or a calendar; a filtered list for lookup).
   - Tool surface: what the AI will see as callable tools.
   - Ready for a web app: the same `User` and `oauth=...` serve a
     browser SPA added later, and methods for people only stay in the
     API with `mcp=None`, so its pages need no API change.
   - Example prompts: the ~3 named chat scenarios the root-page
     wizard will offer, each a sequence of messages exercising a
     main user story — and most of them ending on a turn that
     renders a `UI()` component, not just a tool call (see
     "Example Prompts" under Key Framework Concepts).
4. Then build it the way the user chose. The whole app: the
   Step-by-Step Build Flow below, for every feature. One feature at a
   time: the same flow for the first feature only, its types, methods,
   `UI()` views, example prompts and scenarios, handed off at step 14
   with what it keeps track of, what it does and the rules it keeps,
   and the question dialog as in the `web-app` skill's step 11: accept
   this feature (its `@wip` comes off) or change something first, and
   what to build next, the recommended feature first. Each next
   feature then goes through the Update Flow, its feature file first
   ([`feature` skill](../feature/SKILL.md)), and ends with the same
   dialog.

For updates to existing apps, still work the design first: read
current state, state the changes, then modify. Write the design for a
person who hasn't read these skills:
[`front-door-common.md`](../app/references/front-door-common.md),
"Writing the Design for a Human Reader".

## State Model Assessment

Before writing code, analyze the user's request:

1. **Application types** — decompose per
   `python/references/state-collections.md` Step 1: every entity the
   user adds, edits, lists or finds is its own `Type`, never a
   `list[Person]` on `User`; a collection synced or scraped from an
   external system is an entity collection too.
2. **Container shape for each collection** — shape per
   `python/references/state-collections.md` Step 2: the parent stores
   references, not objects. Boundedness is a domain fact, not a size
   cap, and an externally synced collection is always an `OrderedMap`
   (its boundedness guard).
3. **User methods**: How does the AI create instances of application
   types? Each gets a `Transaction` on `User` that calls
   `<Type>.create(context)`, then registers the new ID in the
   appropriate container (Shape B or C of
   `python/references/state-collections.md`).
4. **State shape (per type)**: Fields, types — lists, nested
   objects, primitives. Each gets `Field(tag=N)`. **Nested `Model`
   sub-objects** owned 1:1 by a parent state must be
   `Optional[X] = Field(tag=N, default=None)` and hydrated in the
   parent's factory `create` Writer (Gotcha #13); non-Optional
   `Model`-typed fields reject `default=` / `default_factory=`.
   Full rules + examples in
   [`references/api-state-shapes.md`](references/api-state-shapes.md).
5. **Operations**: Map to the right method type:
   - `Reader` — read-only queries.
   - `Writer` — single-state mutations.
   - `Transaction` — multi-state atomic operations (e.g. transfer
     between two accounts, or User creating an application-type
     instance).
   - `Workflow` — long-running control flows with loops, scheduling,
     and idempotency helpers.
6. **Tool surface**: Which operations need explicit tool exposure
   (`mcp=Tool()`)? Default Servicer methods to `mcp=Tool()` if the
   AI should call them, `mcp=None` otherwise.
7. **UI placement** — for each UI in the app: **is the AI passing
   in an entity ID for this UI to operate on, or is the UI about
   the user as a whole?** Per-entity UIs (`show_person`,
   `edit_task`, `view_document`) go on the entity's own `Type`
   with `request=None` — the AI's tool-call target becomes the
   actor ID automatically, and the generated `use<Type>()` hook
   resolves it with no arguments. User-scoped UIs (a dashboard,
   a global browser) go on `User`. Putting a per-entity UI on
   `User` with the entity ID inside a `request=<Model>` field is
   an antipattern; see "UI Placement" in
   [`references/api-method-types.md`](references/api-method-types.md).
8. **Identity**: Single default instance vs. multiple instances?
9. **Cross-state coordination**: Does any operation touch multiple
   state instances? If yes, use `Transaction`.
10. **Names** — for what each type holds and is for, never for its
    key: [`front-door-common.md`](../app/references/front-door-common.md),
    "Names".

## When Correct Decomposition Fights the UI

The React references in this skill show **one `use<Type>()`
subscription per UI**, which quietly pressures you to flatten an
entity collection into `list[Item]` on a single actor so the
dashboard can read it in one subscription. **Resolve the tension the
other way: the data model wins.** A collection that is its own entity
type (Assessment step 1) or unbounded (step 2) stays decomposed, one
actor per item with an `OrderedMap` index on the parent; do **not**
collapse the model to fit the single-subscription pattern. The UI
still gets its single subscription from a **composing reader** on the
front-door type, which ranges the `OrderedMap` for one page of IDs,
reads each item actor and returns hydrated objects plus a
`next_cursor`: "Reading Across Many Actors — the Composing Reader" in
[`references/react-app-tsx.md`](references/react-app-tsx.md).

## Key Framework Concepts (MCP UI–specific)

### `User` and Application Types

Every MCP UI has a `User` type and one or more application types:

- **`User`** is the AI's front door for **creating and locating**
  application-type instances. **"Front door" means entry point +
  delegation, not container for all application state.** `User`
  holds identity (e.g. display name) and **IDs of the concern-
  specific actors it owns**; per-concern state (auth/session,
  background-engine config, persona config, transient caches) lives
  on its own `Type` and is referenced by ID from `User`. Typical
  `User` methods are `Transaction`s that create application-type
  instances, or `Reader`s that locate existing instances' IDs —
  either directly or via indexes whose IDs are stored on `User`.
  `User`-scoped UIs (a dashboard spanning the whole user, a global
  browser) also live here.
- **Application types** (e.g. `Counter`, `Person`, `Task`) hold
  most of the actual entity state. They typically need a `create`
  Writer with `factory=True` for construction. **Once an entity exists,
  anything specific to that entity — Readers, Writers, UIs —
  lives on that entity's `Type`**, never on `User`. The actor
  ID is then implicit in every call: the AI passes the entity
  ID to the tool, and the generated `use<Type>()` React hook
  auto-resolves the same ID with no arguments.

The most common scaffolding mistake is putting a per-entity UI
(e.g. `show_person`) on `User` with the entity ID stuffed into a
`request=<Model>` field. Don't — see "UI Placement" in
[`references/api-method-types.md`](references/api-method-types.md).

A second, equally common mistake is letting `User`'s state accrete
unrelated concerns — auth/session fields alongside persona config
alongside a background engine's configuration alongside a UI cache.
That turns the front door into a God actor and, because writers on
the same actor serialize, makes a login step contend with a persona
edit and a background workflow's state writes. Split each concern
into its own `Type` and have `User` reference it by ID. The signals
that warn you are accreting concerns, and the split pattern, are in
`python/references/state-actor-decomposition.md`.

Full pydantic shape in
[`references/api-method-types.md`](references/api-method-types.md);
the `UserServicer` + `<X>.create(context)` pattern in
[`references/servicer-patterns.md`](references/servicer-patterns.md).

### Tool Exposure Control

Every method must explicitly declare its MCP exposure:

- **`mcp=Tool()`** — expose the method as an AI-callable tool.
  Required on every method (including `User` methods) the AI should
  be able to call.
- **`mcp=None`** — hide the method from the AI. Use for human-only
  actions or to reduce context bloat.
- **`Tool(name="...", title="...")`** — override the default tool
  name or add a human-readable title.

### Method Types

The `Reader` / `Writer` / `Transaction` / `Workflow` markers come from
`reboot.api` and behave exactly as `python`'s `api-methods.md`
describes (each fixes the Servicer's context type). The MCP UI
adds one more:

- **`UI()`** — opens a React UI inside the MCP client. Takes
  `request=` (config type or `None`), `path=` (web dir relative to
  project root), `title=`, `description=`. **No servicer
  implementation needed** — the React app _is_ the implementation.
  When `request=` is a `Model`, its fields become props on the React
  component.

`factory=True` on an application type's `create` Writer is the
MCP UI spelling of a constructor (see `python`'s
`servicer-constructor.md` for the underlying mechanic).

### Auth: `oauth=` Provider Selection and Real Authorizers from Day One

MCP UIs wire identity via `Application(oauth=...)`: it decides who
`context.auth.user_id` says the caller is, and in an MCP app that
principal is the user. There's no middle ground: either every user
signs in through this OAuth flow, or the app has no per-user auth at
all. The typical shape is
`oauth=OAuth(provider=OAuthProviderByEnvironment(dev=Development(), prod=Google(...)))`:
under `rbt dev`, `Development()` is a fake account picker that issues
every caller a verified, stable `dev-{hash}` `context.auth.user_id`
with no external IdP; every other environment (`rbt serve`, Reboot
Cloud, anything unrecognized) gets the real provider. Both arms are
required; either may be `None`, and a selected `None` arm makes the
app **fail to start** with a clear message, so you can't silently ship
without sensible auth. Servicer-side code doesn't change between
providers. In unit tests, omit `oauth=` entirely — the test harness
supplies a test OAuth provider.

> **Choose your production provider deliberately, at deploy.** The
> design and every build before deploy keep `prod=None`; the
> [`deploy` skill](../deploy/SKILL.md) sets the provider. Each
> provider issues user IDs in its own namespace, so switching
> providers after launch strands every user-keyed piece of state;
> `Development` is dev-only. Which provider, what each needs, and
> writing your own when none fits:
> [`references/auth-oauth-providers.md`](references/auth-oauth-providers.md)
> and
> [`references/auth-custom-oauth-provider.md`](references/auth-custom-oauth-provider.md).

Consequences for authorizers:

- **Write `authorizer()` on every Servicer from day one.** Don't
  defer it "until prod." Identity is wired the same in dev and prod,
  so production-shaped rules (`allow_if(all=[state_id_is_user_id])`,
  `allow_if(all=[has_verified_token])`, etc.) work immediately.
- **Don't use `allow()` as a default.** It declares "this endpoint
  is public on the internet, no identity required" — not what you
  want for app-state methods.
- **`User`-type Servicers don't need a custom `authorizer()`.** The
  framework's default rule (`state_id_is_user_id` + `is_app_internal`)
  is production-worthy already.
- **Application-type Servicers (`Counter`, `TodoList`, …)** typically
  use `allow_if(all=[state_id_is_user_id])` when the state belongs to
  one user, or compose other predicates (`has_verified_token`,
  custom) when state is shared.

Predicate composition, custom predicates and the function-vs-instance
footgun live in `python/references/auth-*.md` and
`python/references/servicer-authorizer.md`. The MCP UI delta is just
**which mode you're in**: `oauth=` + real rules from day one.

**Acting on the user's behalf at the provider** (extra OAuth
`scopes=[...]`, `store_tokens=True`, the provider's own tokens read
back and called **inside a `Workflow`**):
[`references/auth-store-tokens.md`](references/auth-store-tokens.md),
then
[`python/references/auth-external-api-calls.md`](../python/references/auth-external-api-calls.md).

### Declarative, Not Decorator

All MCP surface is defined in the API file. `main.py` is minimal. No
`@mcp.tool()` decorators.

### State Is Durable

State survives restarts. `dev run --application-name=<name>` in
`.rbtrc` (see [`references/project-shell.md`](references/project-shell.md))
is what makes that work.

### Example Prompts (Root-Page Wizard)

Every MCP UI ships **example prompts** — short, named chat
scenarios the root-page wizard shows users so they can try the app
the moment it boots, without having to invent a first message. They
are not optional polish: a fresh user landing on the wizard with no
suggested prompts has nothing to click, so always author a set.

An example prompt is an `ExamplePrompt(title=..., prompts=[...])`
(imported from `reboot.application`). The `title` is a short label
(and the identity key — same title replaces an existing entry); the
`prompts` are an **ordered sequence** of chat messages the user sends
one per turn, walking a real end-to-end flow through the app's MCP
tools (create something → act on it → view the result), not one
isolated message. Write ~3 examples that together cover the app's
main user stories, phrased the way a real user would talk to the
chat client.

**Make the prompts show the UI, not just call tools.** The embedded
React UIs (the `UI()` methods) are the whole reason this is an MCP
**App** and not a plain MCP server — a flow that only calls
tool-only methods and never renders a component demos the boring
half. Every example should end on (or pass through) a turn that
triggers a `UI()` method — phrase that turn as a natural "show me
/ open / view ..." request so the AI picks the UI tool. In the counter
example, the "…and show me the counter" / "show me the wins counter"
turns are exactly this: they resolve to the `Counter` UI and render the
live component, not just a text reply. When you write the set, look at
the method map from the design: for each `UI()` method, make sure at
least one example drives the user to it.

They live in `backend/src/example_prompts.py` and are passed to
`Application(example_prompts=...)` in `main.py`. Full file shapes and
a worked set are in
[`references/project-shell.md`](references/project-shell.md); the
`mcp-ui-counter` example is the canonical reference.

## Project Structure

```
<project>/
├── .python-version          # "3.10"
├── .rbtrc                   # rbt config, one flag per line
├── .mypy.ini                # Type-check config (python skill)
├── pyproject.toml           # Python deps (uv)
├── api/
│   └── <pkg>/v1/
│       └── <name>.py        # API definition
├── pytest.ini               # testpaths: tests; pythonpath: backend/src backend/api api
├── backend/
│   └── src/
│       ├── main.py          # Application entrypoint
│       ├── example_prompts.py  # Wizard example prompts
│       └── servicers/
│           └── <name>.py    # Servicer implementation
├── tests/
│   ├── <capability>.feature  # One feature per capability
│   └── <name>_test.py       # `application` fixture + `scenarios(...)`
└── frontend/
    ├── package.json
    ├── build.mjs            # Discovers + builds every UI
    ├── tsconfig.json
    ├── tsconfig.app.json
    ├── tsconfig.node.json
    ├── vite.config.ts
    ├── api/                 # Generated React bindings (rbt generate)
    ├── mcp/
    │   └── <ui-name>/
    │       ├── index.html
    │       ├── index.css        # Theme variables
    │       ├── main.tsx         # RebootClientProvider entry
    │       ├── App.tsx          # React component
    │       └── App.module.css
    └── web/                 # Optional standalone browser SPA
        ├── index.html
        └── src/
            ├── main.tsx
            └── App.tsx
```

## Step-by-Step Build Flow

The build's task list, where the agent keeps one, uses the items in
[`app/references/task-list.md`](../app/references/task-list.md), word
for word: the list for the way the user chose to build.

**All commands run from the application directory.**

1. Create `.python-version`, `pyproject.toml`, `.rbtrc`, and
   `.mypy.ini` — see
   [`references/project-shell.md`](references/project-shell.md);
   the `.mypy.ini` template lives in
   `python/references/lifecycle-project-setup.md`. Then give the
   project its `AGENTS.md` and `CLAUDE.md` with the
   [`agents-md` skill](../agents-md/SKILL.md), naming the API and
   servicer files the design settled on.
2. `uv sync`.
3. Don't start the developer dashboard yet: it starts after step 5,
   once there is an API for it to show.
4. Write API definition (`api/<pkg>/v1/<name>.py`) — see
   [`references/api-method-types.md`](references/api-method-types.md)
   and [`references/api-state-shapes.md`](references/api-state-shapes.md);
   field-level pydantic rules in
   `python/references/api-pydantic.md`.
5. `uv run rbt generate`. Don't read what it wrote: the signature
   your servicer must match is in `python/references/api-methods.md`
   ("The Servicer Signature Each Declaration Obliges"). Then start
   the developer dashboard — load the
   [`dashboard` skill](../dashboard/SKILL.md) and follow it — so the
   user can watch the app come together, and go on without waiting
   for it. If it fails to come up, say so in one sentence and keep
   building; do not stop to debug it. Built from the `app` skill, the
   first feature instead waits for it and asks "Build on this domain model?" (the model check)
   ([`app/references/design-first.md`](../app/references/design-first.md),
   "The domain model, once") before step 6.
6. Write servicer (`backend/src/servicers/<name>.py`) — see
   [`references/servicer-patterns.md`](references/servicer-patterns.md);
   context-type rules in `python/references/servicer-*.md`.
7. Write `backend/src/example_prompts.py` (the wizard's example
   prompts) and `main.py` (which imports them and passes
   `example_prompts=` to `Application`) — see
   [`references/project-shell.md`](references/project-shell.md) and
   `python/references/lifecycle-application-entry.md`.
8. `npm create @reboot-dev/ui`.
9. `cd frontend && npm install`.
10. `uv run rbt generate` (React bindings need `node_modules`).
11. Customize React UIs — see
    [`references/react-scaffolding.md`](references/react-scaffolding.md)
    for the `frontend/` shell and
    [`references/react-app-tsx.md`](references/react-app-tsx.md) for
    `App.tsx` patterns.
12. `cd frontend && npm run build`.
13. **Write and run the scenarios of every feature before handing
    the app off.** Each feature file from the design phase (the
    [`feature` skill](../feature/SKILL.md)) gets its scenarios now,
    in the built-in steps of `python/references/testing-features.md`:
    every action the user should be able to _do_ through the MCP tool
    surface, calling the methods the tools call, each step naming who
    calls (`"alice" is an authenticated user`), against the **real**
    servicers — never subclass one to weaken its `authorizer()`. Let
    factories make ids up. Tag what cannot pass yet `@blocked` with
    its reason, and `@wip` as the `feature` skill says. Run
    `uv run pytest` as [`feature/SKILL.md`](../feature/SKILL.md)'s
    "Report a full run once, at the end" says, with `rbt dev run`
    stopped (`run` skill, "Stopping the App"), then
    `uv run mypy backend/ tests/` from the project root
    (`python/references/lifecycle-project-setup.md`); fix every
    failure and error before the next step. Point the user at the
    dashboard's Features page to review the features.
14. Run the app — load the [`run` skill](../run/SKILL.md) and follow
    it with [`run/references/mcp-ui-processes.md`](../run/references/mcp-ui-processes.md):
    the tunnel, the backend, then the **setup wizard at its root
    (`http://localhost:9991`)**, which is the handoff for an MCP UI,
    not the `/mcp` URL; MCPJam only on demand from the wizard; never
    a bare `rbt dev run` / `npm run dev`, which drop the wizard hint.
    Open the wizard once at first startup, write the handoff in the
    shape of
    [`app/references/design-messages.md`](../app/references/design-messages.md)
    with the wizard's URL under **Open it**, and ask in a question
    dialog (`AskUserQuestion` where available) **What should I build next?**,
    worded as
    [`app/references/accept-design.md`](../app/references/accept-design.md)
    says, which also records the acceptance. Unless the user asked for
    only an MCP UI, end the handoff with the one-line offer of a web
    app (`app` skill, "At handoff").

## Update Flow

When modifying an existing app:

1. Read `AGENTS.md`, `.rbtrc`, the API, the servicers, `main.py`;
   route the change as
   [`front-door-common.md`](../app/references/front-door-common.md)
   ("Routing a Change") says.
2. Assess the state model changes; an app with persisted or deployed
   state follows `python/references/api-schema-evolution.md`.
3. Update the API → `uv run rbt generate`.
4. Update the servicers.
5. Update the React components.
6. A new user-facing capability gets an example prompt in
   `backend/src/example_prompts.py`, so the wizard surfaces it.
7. Run `uv run mypy backend/ tests/` from the project root and
   `uv run pytest`, as [`feature/SKILL.md`](../feature/SKILL.md)'s
   "Report a full run once, at the end" says, with `rbt dev run`
   stopped; fix every error and failure before handing back.
8. Bring the app up with the [`run` skill](../run/SKILL.md) if it
   isn't running; under `rbt dev run`, edits (and `.env`) reload it,
   no restart.
9. If the change moved a file, added a state type or a UI, changed
   a command, or taught a rule, update `AGENTS.md` in the same
   change ([`agents-md` skill](../agents-md/SKILL.md)).
