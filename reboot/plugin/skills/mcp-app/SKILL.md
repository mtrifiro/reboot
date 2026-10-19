---
name: mcp-app
description: Build complete Reboot MCP Apps for ChatGPT, Claude, VSCode, Goose, and other MCP hosts. Layers on top of the python skill for backend mechanics; covers what's specific to MCP Apps — the User-type front door, MCP tool exposure, the UI() method type, and the full React/Vite scaffolding. The backend stays ready for a web app.
argument-hint: [<app-description>]
allowed-tools: Bash, Read, Write, Glob, Grep, Edit
---

# mcp-app — Build Reboot MCP Apps

> **Version notices** from `rbt` (a mismatch, a newer Reboot): the [upgrade skill](../upgrade/SKILL.md).
>
> **Errors:** grep a fragment of the string in `python/references/errors.md` (never read whole); known defects and workarounds: [`KNOWN-ISSUES.md`](../../KNOWN-ISSUES.md).

Build complete Reboot MCP Apps from a user description.

> **Reads from `python`.** Servicers, contexts, refs, scheduling,
> backend LLM / agent calls, error types, the testing harness, the
> `.rbtrc` shape and pydantic API defaults belong to `python`; load
> its references for those. Here: what is _specific_ to MCP Chat
> Apps — the `User`-type front door, MCP tool exposure, the `UI()`
> method type, the React/Vite scaffolding, and that layer's
> cross-cutting rules.

> **Dual-frontend apps are supported.** One backend can serve an MCP
> front door _and_ a browser SPA, sharing `oauth=...`, one `User` per
> upstream identity, and the servicer code; for the SPA, also load the
> [web-app skill](../web-app/SKILL.md). Signing in on one frontend
> signs in on both: the OAuth server's `/authorize` short-circuits when
> the browser already carries a session cookie, and `/callback` sets
> that cookie on every flow.

## When to Use

- Building a new Reboot MCP App from a description
- Adding features, state, or UI to an existing one
- Modifying its state model, methods, or React UI
- Running an existing one, e.g. at the start of a session: no design
  or build phase; load the [`run` skill](../run/SKILL.md), which
  detects the app type, starts backend and frontend, and opens the
  setup wizard (MCPJam launches from it on demand).

## Which References to Read, and When

Neither the `python` references nor this skill's own are restated
below.

Everything read stays in the conversation and is re-sent every turn,
so **read each reference at the step that needs it** — not all of
them up front — and read each one **once**. The groups below are in
build order, each reference in exactly one, the step that needs it.
Never a whole generated or installed file (`*_rbt.py`,
`*_rbt_react.ts`, `site-packages/`, `node_modules/`), and any search
bounded hard:
[`front-door-common.md`](../app/references/front-door-common.md),
"Never Read Generated or Installed Source in the Main Thread".

> **Never read `web-app/references/*` for an MCP App** (the standalone SPA's shell, `VITE_REBOOT_URL`, `<RebootClientProvider>` and sign-in buttons don't apply to the `frontend/mcp/<name>/` bundles an MCP host loads; the MCP App equivalents are [`references/react-scaffolding.md`](references/react-scaffolding.md) and [`references/react-app-tsx.md`](references/react-app-tsx.md)), except `web-app/references/ui-design.md`, whose primary views and accent apply to `UI()` views too.

**Before the project shell** (`.python-version`, `pyproject.toml`,
`.rbtrc`, `.mypy.ini`, `main.py`):

- [`references/project-shell.md`](references/project-shell.md) —
  `.rbtrc` deltas (the `portless`, `ports` and `dist` configs),
  `pyproject.toml` extras, `main.py`, `example_prompts.py`.
- `python/references/lifecycle-{project-setup,rbtrc,application-entry}.md`
  — the layout, the CLI flags, `Application(...)`.

**Before the API definition:**

- `python/references/patterns-common-gotchas.md` — recurring trips.
- `python/references/api-pydantic.md` — pydantic API rules.
- `python/references/api-methods.md` — factory → context type mapping.
- `python/references/api-errors.md` — typed errors, when the API
  declares any.
- `python/references/state-collections.md` — **always read when the
  app has any "list of X" concept**, synced or scraped ones included.
- `python/references/state-nested-models.md` — only when a state
  nests a non-state `Model`.
- `python/references/state-actor-decomposition.md` — when one state
  `Type` has accreted unrelated concerns; the `User` front door most
  of all.
- [`references/api-method-types.md`](references/api-method-types.md)
  — the MCP App's API file: `User`, `mcp=`, `UI()`, `factory=True`.
- [`references/api-state-shapes.md`](references/api-state-shapes.md)
  — two recurring state shapes; composing actors by ID.
- [`references/gotchas.md`](references/gotchas.md) — the MCP App trip
  list.

**Before the servicer:**

- `python/references/servicer-{reader,writer,transaction,constructor}.md` — one per declared context type.
- `python/references/rpc-calls.md` — kwargs, not Request wrappers;
  `Service.create(context, id)`.
- `python/references/servicer-workflow.md` — only when a `Workflow`
  is declared, then top to bottom.
- [`references/servicer-patterns.md`](references/servicer-patterns.md)
  — the MCP App servicer shapes.

**Before the authorizers:**

- `python/references/servicer-authorizer.md`,
  `python/references/auth-rules.md` — the predicate machinery.
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
  — **acting on the user's behalf** when the API is your sign-in
  provider's (`store_tokens=True`); any other service, or an external
  API called inside a `Workflow`:
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
  when `IdempotencyUncertainError` appears, or a seed stalls or errors.
- `python/references/testing-harness.md` and
  `testing-external-context.md` — for custom steps.
- `python/references/testing-custom-steps.md` — for custom steps.
- `testing-failure-recovery.md` — whenever the app has a spawned
  task, a `Workflow`, or `schedule()`d work.
- [`feature/SKILL.md`](../feature/SKILL.md) — the order of work
  around the feature files.

**The two parts.** Every group above this line is the backend part.
The groups from here on are the frontend part: read them only when the
frontend part starts, once the feature's backend passes its scenarios
(on the whole-app paths, every feature's), never before, and not at
all when the user stops after the backend.

**Before the frontend:**

- `web-app/references/ui-design.md` — the primary view for each
  `UI()` view and the accent; the rest is the web app's.
- [`references/react-scaffolding.md`](references/react-scaffolding.md)
  — the `frontend/` shell, copied: `vite.config.ts` (the stock Vite
  file plus `reboot()`) and `build.mjs` (`build()`, every UI).
- [`references/react-app-tsx.md`](references/react-app-tsx.md) —
  `App.tsx`, with the Counter example.
- `python/references/react-generated-client.md` — what
  `rbt generate --react=` emits.
- [`references/pop-out-to-web-app.md`](references/pop-out-to-web-app.md)
  — only when a widget needs a "pop out into the web app" button.

**Before running the app:** the [`run` skill](../run/SKILL.md) and its
[`run/references/mcp-app-processes.md`](../run/references/mcp-app-processes.md) (the
tunnel, the setup wizard, MCPJam).

## Workflow: Propose the Design, Then Build

**Always work out the design before writing code.** The design is a
proposal until the user accepts it, and the Reboot Flywheel's first
stage:
[`front-door-common.md`](../app/references/front-door-common.md),
"The Design Is a Proposal".

### Design Phase

1. Analyze the description with the State Model Assessment below.
2. The scope round, as
   [`front-door-common.md`](../app/references/front-door-common.md)
   ("The Scope Round") says. The first question's options: "One
   feature at a time, so you understand each part as it's built"
   (recommended), "The whole app first, then reviewed as a whole", or
   "Prompt by prompt: I say what to build at each step; ask me nothing".
3. Read the API references, then show the proposed design, word for
   word in the shape of
   [`app/references/design-messages.md`](../app/references/design-messages.md)
   (its Pages section names the `UI()` views), answers included,
   before writing the API. It decides the brief (who uses the app, on
   what screen, the task, the one question its main page answers, the
   palette), the features in a sentence each, and:
   - `User` type and its methods (the front door that creates and
     locates application-type instances).
   - Application types: state shape (fields, types, tags).
   - Method map: each operation's type
     (Reader/Writer/Transaction/Workflow), which get `UI()`, and each
     `UI()` view's primary view (the domain's own shape, a board say;
     a filtered list for lookup).
   - Tool surface: the tools the AI sees.
   - Ready for a web app: the same `User` and `oauth=...` serve a
     later browser SPA, and people-only methods stay in the API with
     `mcp=None`, so its pages need no API change.
   - Example prompts: ~3 named chat scenarios for the root-page
     wizard, most ending on a turn that renders a `UI()` component
     ("Example Prompts" below).
4. Then build as the user chose. The whole app: the Step-by-Step
   Build Flow below, for every feature. One feature at a time: the
   same flow for the first feature only (its types, methods, `UI()`
   views, example prompts and scenarios), handed off at step 14 with
   what it keeps track of, what it does and the rules it keeps, and
   the `web-app` skill's step-11 dialog: accept this feature (its
   `@wip` comes off) or change something first, and what to build
   next, the recommended feature first. Each next feature goes
   through the Update Flow, feature file first
   ([`feature` skill](../feature/SKILL.md)), ending with the same
   dialog.

Updates to existing apps still design first: read the current state,
state the changes, then modify. Write the design for a person who
hasn't read these skills:
[`front-door-common.md`](../app/references/front-door-common.md),
"Writing the Design for a Human Reader".

## State Model Assessment

Before writing code, analyze the request:

1. **Application types** — decompose per
   `python/references/state-collections.md` Step 1: every entity the
   user adds, edits, lists or finds is its own `Type`, never a
   `list[Person]` on `User`; a synced or scraped collection too.
2. **Container shape for each collection** — per
   `python/references/state-collections.md` Step 2: the parent stores
   references, not objects. Boundedness is a domain fact, not a size
   cap; an externally synced collection is always an `OrderedMap`.
3. **User methods**: how the AI creates instances — a `Transaction`
   on `User` per type that calls `<Type>.create(context)`, then
   registers the new ID in its container (Shape B or C of
   `python/references/state-collections.md`).
4. **State shape (per type)**: fields and types, each with
   `Field(tag=N)`. **Nested `Model` sub-objects** owned 1:1 by a
   parent state must be `Optional[X] = Field(tag=N, default=None)`
   and hydrated in the parent's factory `create` Writer (Gotcha #13);
   non-Optional `Model`-typed fields reject `default=` /
   `default_factory=`. Rules and examples:
   [`references/api-state-shapes.md`](references/api-state-shapes.md).
5. **Operations**: the method type for each:
   - `Reader` — read-only queries.
   - `Writer` — single-state mutations.
   - `Transaction` — multi-state atomic operations (e.g. `User`
     creating an application-type instance).
   - `Workflow` — long-running control flows with loops, scheduling
     and idempotency helpers.
6. **Tool surface**: `mcp=Tool()` on every method the AI should call,
   `mcp=None` otherwise.
7. **UI placement** — for each UI: **is the AI passing in an entity
   ID for this UI to operate on, or is the UI about the user as a
   whole?** Per-entity UIs (`show_person`, `edit_task`) go on the
   entity's own `Type` with `request=None`; user-scoped UIs (a
   dashboard, a global browser) on `User`. The antipattern and why:
   "UI Placement" in
   [`references/api-method-types.md`](references/api-method-types.md).
8. **Identity**: one default instance, or many?
9. **Cross-state coordination**: an operation that touches several
   state instances is a `Transaction`.
10. **Names** — for what each type holds and is for, never for its
    key: [`front-door-common.md`](../app/references/front-door-common.md),
    "Names".

## When Correct Decomposition Fights the UI

This skill's React references show **one `use<Type>()` subscription
per UI**, which pressures the model to flatten an entity collection
into `list[Item]` on one actor. **Resolve the tension the other way:
the data model wins.** A collection that is its own entity type
(Assessment step 1) or unbounded (step 2) stays decomposed, one actor
per item with an `OrderedMap` index on the parent; never collapse it
to fit the pattern. The UI still gets one subscription, from
a **composing reader** on the front-door type that pages the
`OrderedMap`, reads each item actor and returns
hydrated objects plus a `next_cursor`: "Reading Across Many Actors —
the Composing Reader" in
[`references/react-app-tsx.md`](references/react-app-tsx.md).

## Key Framework Concepts (MCP App–specific)

### `User` and Application Types

Every MCP App has a `User` type and one or more application types:

- **`User`** is the AI's front door for **creating and locating**
  application-type instances. **"Front door" means entry point +
  delegation, not container for all application state.** `User`
  holds identity (e.g. display name) and **IDs of the concern-
  specific actors it owns**; per-concern state (auth/session, engine
  config, persona config, caches) lives on its own `Type`, referenced
  by ID. Typical `User` methods are `Transaction`s that create
  instances, or `Reader`s that locate existing ones' IDs, directly or
  via indexes `User` holds the IDs of. `User`-scoped UIs (a
  dashboard, a global browser) also live here.
- **Application types** (`Counter`, `Person`, `Task`) hold most of
  the entity state and typically need a `create` Writer with
  `factory=True`. **Once an entity exists, anything specific to that
  entity — Readers, Writers, UIs — lives on that entity's `Type`**,
  never on `User`. The actor ID is then implicit in every call: the
  AI passes the entity ID to the tool, and the generated `use<Type>()`
  React hook auto-resolves the same ID with no arguments.

The most common scaffolding mistake is a per-entity UI
(`show_person`) on `User` with the entity ID in a `request=<Model>`
field. Don't: "UI Placement" in
[`references/api-method-types.md`](references/api-method-types.md).

The second is letting `User` accrete unrelated concerns. That makes
the front door a God actor and, because writers on the same actor
serialize, a login step contends with a persona edit and a background
workflow's writes. Split each concern into its own `Type`, referenced
by ID from `User`; the warning signals and the split pattern:
`python/references/state-actor-decomposition.md`.

Full pydantic shape in
[`references/api-method-types.md`](references/api-method-types.md);
the `UserServicer` + `<X>.create(context)` pattern in
[`references/servicer-patterns.md`](references/servicer-patterns.md).

### Tool Exposure Control

Every method must explicitly declare its MCP exposure:

- **`mcp=Tool()`** — an AI-callable tool. Required on every method
  (`User` methods included) the AI should call.
- **`mcp=None`** — hidden from the AI: human-only actions, or less
  context.
- **`Tool(name="...", title="...")`** — a custom tool name or a
  human-readable title.

### Method Types

The `Reader` / `Writer` / `Transaction` / `Workflow` markers come from
`reboot.api` and behave as `python`'s `api-methods.md` describes
(each fixes the Servicer's context type). The MCP App adds one:

- **`UI()`** — opens a React UI inside the MCP client. Takes
  `request=` (config type or `None`), `path=` (the UI's URL path
  under `/__/frontend/mcp/`, like `"clicker"` or `"shop/cart"`; its
  source is `frontend/mcp/<path>/`, its build
  `frontend/dist/mcp/<path>/index.html`), `title=`, `description=`.
  **No servicer implementation needed** — the React app _is_ the
  implementation.
  When `request=` is a `Model`, its fields become props on the React
  component.

`factory=True` on an application type's `create` Writer is the MCP App
spelling of a constructor (the mechanic: `python`'s
`servicer-constructor.md`).

### Auth: `oauth=` Provider Selection and Real Authorizers from Day One

MCP Apps wire identity via `Application(oauth=...)`: it decides who
`context.auth.user_id` says the caller is, and in an MCP App that
principal is the user. No middle ground: every user signs in through
this OAuth flow, or the app has no per-user auth. The typical shape is
`oauth=OAuth(provider=OAuthProviderByEnvironment(dev=Development(), prod=Google(...)))`:
under `rbt dev`, `Development()` is a fake account picker that issues
every caller a verified, stable `dev-{hash}` `context.auth.user_id`
with no external IdP; every other environment (`rbt serve`, Reboot
Cloud, anything else) gets the real provider. Both arms are required;
either may be `None`, and a selected `None` arm makes the app **fail
to start** with a clear message. Servicer-side code doesn't change between
providers. In unit tests, omit `oauth=` — the test harness supplies a
test OAuth provider.

> **Choose your production provider deliberately, at deploy.** The
> design and every build before deploy keep `prod=None`; the
> [`deploy` skill](../deploy/SKILL.md) sets the provider. Each
> provider issues user IDs in its own namespace, so switching
> providers after launch strands all user-keyed state; `Development`
> is dev-only. Which provider, what each needs, and
> writing your own when none fits:
> [`references/auth-oauth-providers.md`](references/auth-oauth-providers.md)
> and
> [`references/auth-custom-oauth-provider.md`](references/auth-custom-oauth-provider.md).

Consequences for authorizers:

- **Write `authorizer()` on every Servicer from day one.** Don't
  defer it "until prod": identity is wired the same in dev and prod,
  so production-shaped rules (`allow_if(all=[state_id_is_user_id])`,
  `allow_if(all=[has_verified_token])`) work at once.
- **Don't use `allow()` as a default.** It declares the endpoint
  public on the internet, no identity required — wrong for app-state
  methods.
- **`User`-type Servicers don't need a custom `authorizer()`.** The
  framework's default rule (`state_id_is_user_id` + `is_app_internal`)
  is production-worthy already.
- **Application-type Servicers (`Counter`, `TodoList`, …)** use
  `allow_if(all=[state_id_is_user_id])` when the state belongs to one
  user, or compose other predicates (`has_verified_token`, custom)
  when it is shared.

Predicate composition, custom predicates and the function-vs-instance
footgun: `python/references/auth-*.md` and
`python/references/servicer-authorizer.md`.

**Acting on the user's behalf at the provider** (extra OAuth
`scopes=[...]`, `store_tokens=True`, the provider's tokens read back
and called **inside a `Workflow`**):
[`references/auth-store-tokens.md`](references/auth-store-tokens.md),
then
[`python/references/auth-external-api-calls.md`](../python/references/auth-external-api-calls.md).

### Declarative, Not Decorator

All MCP surface is defined in the API file. `main.py` is minimal. No
`@mcp.tool()` decorators.

### State Is Durable

State survives restarts; `dev run --application-name=<name>` in
`.rbtrc` ([`references/project-shell.md`](references/project-shell.md))
makes that work.

### Example Prompts (Root-Page Wizard)

Every MCP App ships **example prompts**: short, named chat scenarios
the root-page wizard shows so users can try the app the moment it
boots; always author a set.

An example prompt is an `ExamplePrompt(title=..., prompts=[...])`
(imported from `reboot.application`). The `title` is a short label
and the identity key (the same title replaces an existing entry); the
`prompts` are an **ordered sequence** of chat messages, one per turn,
walking an end-to-end flow through the app's MCP tools (create → act
→ view), not one isolated message. Write ~3 that together cover the
app's main user stories, phrased as a real user talks to the chat
client.

**Make the prompts show the UI, not just call tools.** The `UI()`
methods are why this is an MCP **App** and not a plain MCP server.
Every example ends on (or passes through) a turn that triggers a
`UI()` method, phrased as a natural "show me / open / view ..."
request so the AI picks the UI tool. Check the design's method map:
each `UI()` method has at least one example that drives the user to
it.

They live in `backend/src/example_prompts.py` and are passed to
`Application(example_prompts=...)` in `main.py`. File shapes and a
worked set: [`references/project-shell.md`](references/project-shell.md);
the `mcp-app-counter` example is the canonical reference.

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
    ├── tsconfig.json
    ├── tsconfig.app.json
    ├── tsconfig.node.json
    ├── vite.config.ts       # defineConfig({ plugins: [react(), reboot({...})] })
    ├── build.mjs            # await build(): every UI
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

**All commands run from the application directory.** **A file that exists is changed with the Edit tool,** the lines that change and nothing more, never a `sed -i`, a `python3 -` script or a heredoc that rewrites it ([`front-door-common.md`](../app/references/front-door-common.md), "A Change Is an Edit, Never a Rewrite").

1. Create `.python-version`, `pyproject.toml`, `.rbtrc`, and
   `.mypy.ini` per
   [`references/project-shell.md`](references/project-shell.md); the
   `.mypy.ini` template is in
   `python/references/lifecycle-project-setup.md`. Then give the
   project its `AGENTS.md` and `CLAUDE.md` with the
   [`agents-md` skill](../agents-md/SKILL.md), naming the API and
   servicer files the design settled on.
2. `uv sync`.
3. Don't start the developer dashboard yet: it starts after step 5.
4. Write the API definition (`api/<pkg>/v1/<name>.py`) per
   [`references/api-method-types.md`](references/api-method-types.md)
   and [`references/api-state-shapes.md`](references/api-state-shapes.md);
   field-level pydantic rules in `python/references/api-pydantic.md`.
5. `uv run rbt generate`. Don't read what it wrote: the signature
   your servicer must match is in `python/references/api-methods.md`
   ("The Servicer Signature Each Declaration Obliges"). Then start
   the developer dashboard — load the
   [`dashboard` skill](../dashboard/SKILL.md) and follow it — and go
   on without waiting for it. If it fails to come up, say so in one
   sentence and keep
   building; don't stop to debug it. Built from the `app-guided` skill, the
   first feature instead waits for it and asks "Build on this domain model?" (the model check;
   not on the prompt-by-prompt path, which asks nothing)
   ([`app/references/design-first.md`](../app/references/design-first.md),
   "The domain model, once") before step 6.
6. Write the servicer (`backend/src/servicers/<name>.py`) per
   [`references/servicer-patterns.md`](references/servicer-patterns.md);
   context-type rules in `python/references/servicer-*.md`.
7. Write `backend/src/example_prompts.py` and `main.py` (which
   imports them and passes `example_prompts=` to `Application`) per
   [`references/project-shell.md`](references/project-shell.md) and
   `python/references/lifecycle-application-entry.md`.
8. `npm create @reboot-dev/ui`.
9. `cd frontend && npm install`.
10. `uv run rbt generate` (React bindings need `node_modules`).
11. Customize the React UIs:
    [`references/react-scaffolding.md`](references/react-scaffolding.md)
    for the `frontend/` shell,
    [`references/react-app-tsx.md`](references/react-app-tsx.md) for
    `App.tsx`.
12. `cd frontend && npm run build`.
13. **Write and run the scenarios of every feature before handing
    the app off.** Each feature file from the design phase (the
    [`feature` skill](../feature/SKILL.md)) gets its scenarios now,
    in the built-in steps of `python/references/testing-features.md`:
    every action the user can _do_ through the MCP tool surface,
    calling the methods the tools call, each step naming who
    calls (`"alice" is an authenticated user`), against the **real**
    servicers — never subclass one to weaken its `authorizer()`. Let
    factories make ids up. Tag what cannot pass yet `@blocked` with
    its reason, and `@wip` as the `feature` skill says. Run
    `uv run pytest` as the [`feature` skill](../feature/SKILL.md)'s step 4 says (the
    feature's own files, in the foreground), with `rbt dev run`
    stopped (`run` skill, "Stopping the App"), then
    `uv run mypy backend/ tests/` from the project root
    (`python/references/lifecycle-project-setup.md`); fix every
    failure and error before the next step. Point the user at the
    dashboard's Features page.
14. Run the app — load the [`run` skill](../run/SKILL.md) and follow
    it with [`run/references/mcp-app-processes.md`](../run/references/mcp-app-processes.md):
    the tunnel, the backend, then the **setup wizard at its root
    (`https://<app>.localhost` under portless, else
    `http://localhost:9991`)**, the handoff for an MCP App, not the
    `/mcp` URL; MCPJam only on demand from the wizard; never a bare
    `rbt dev run` / `npm run dev`. Open
    the wizard once at first startup, run the whole suite once in the
    background while the handoff is written (`feature` skill, "Report
    a full run once, at the end"), and write the handoff in the shape
    of
    [`app/references/design-messages.md`](../app/references/design-messages.md)
    with the wizard's URL under **Open it**, and ask in a question
    dialog (`AskUserQuestion` where available) **What should I build next?**
    (on the prompt-by-prompt path no dialog: **Your turn** ends with the plain
    line "Say what's next."), worded as
    [`app/references/accept-design.md`](../app/references/accept-design.md)
    says, which also records the acceptance. Unless the user asked for
    only an MCP App, end the handoff with the one-line offer of a web
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
   `backend/src/example_prompts.py`.
7. Run `uv run mypy backend/ tests/` from the project root and
   `uv run pytest`, as the [`feature` skill](../feature/SKILL.md)'s step 4 says (the
    feature's own files, in the foreground), with `rbt dev run`
   stopped; fix every error and failure before handing back.
8. Bring the app up with the [`run` skill](../run/SKILL.md) if it
   isn't running; under `rbt dev run`, edits (and `.env`) reload it.
9. If the change moved a file, added a state type or a UI, changed
   a command, or taught a rule, update `AGENTS.md` in the same
   change ([`agents-md` skill](../agents-md/SKILL.md)).
