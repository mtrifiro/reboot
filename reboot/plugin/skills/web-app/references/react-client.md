---
title: Wire the Web SPA to the Reboot Backend
impact: HIGH
impactDescription: The browser shell, the backend URL, the generated hooks, and how a typed backend error reaches the user
tags: web-app, react, vite, hooks, errors, RebootClientProvider
---

## Wire the Web SPA to the Reboot Backend

Everything the standalone browser frontend needs. This is the
web-app equivalent of the `mcp-app` skill's scaffolding references —
**do not read those**. The `frontend/` shell is the same one (the
stock Vite file plus Reboot's `reboot()` plugin), and this file
has the web app's version of it;
the rest of those references is about `mcp/<name>/` entries and
one-file MCP App bundles, which a web app has no use for.

## The `frontend/` Shell

Rendered by the `python` skill's `render.py --web` (the web-app
skill's step 1), never scaffolded with `create-vite` and never
retyped: a Vite React-TS project with the SPA's `index.html`, `src/`
and `public/` under `web/`, so that the generated client at
`frontend/api/` and, should the app ever add MCP Apps, `frontend/mcp/`
sit beside it:

```
frontend/
├── package.json         # React, Vite, TypeScript; the Reboot packages at the backend's pin; the house typefaces; zod
├── tsconfig.json
├── tsconfig.app.json    # `include: ["web/src"]`, the `@api/*` path
├── tsconfig.node.json   # Node's types, for the config
├── vite.config.ts       # The stock Vite file plus `reboot()`, below
├── api/                 # `rbt generate --react=frontend/api`
└── web/
    ├── .env.development # No `VITE_REBOOT_URL` in development; below
    ├── .env.production  # Written at deploy time (the `deploy` skill)
    ├── index.html       # `<div id="root">` + `<script type="module" src="./src/main.tsx">`
    ├── public/          # Static files, copied into the build as they are; `favicon.svg`.
    │                    # An image a page shows is imported from src/ instead: in
    │                    # development Vite serves under /__/frontend/, so /band.jpg 404s
    │                    # (crm-30's header photo)
    └── src/
        ├── main.tsx     # The provider, below
        ├── App.tsx      # The starter page: sign-in, one reader, a form, a table; edited into the design's pages
        ├── styles.css, theme.tsx, backend-check.tsx, reload-prompt.tsx  # The house look (`ui-design.md`)
        ├── errors.ts    # `friendlyError`; its cases filled in per typed error
        └── vite-env.d.ts
```

`vite.config.ts` is the stock Vite file plus Reboot's plugin,
`reboot({ webAppPath: "web", apiPath: "api" })` from
`@reboot-dev/reboot-react/vite`, the same config the `mcp-app` skill
uses, so adding MCP Apps later is one more option (`mcpAppPath`), not
another file. The plugin serves the SPA in `web/` at `/` (and at any
path, so the app's routes survive a reload), builds it to
`frontend/dist/web/` at `base: "/"`, aliases `@api` to the generated
client, dedupes `react`, `react-dom` and `zod` (two copies, one from
the app and one pulled through the Reboot packages, break hooks and
schema identity checks at runtime), reads `.env*` from `web/`, and
listens on every interface: Vite's default `localhost` resolves to IPv6
`[::1]` only, and a forwarded port (Codespaces, VS Code remote, a dev
VM, a tunnel) would get connection refused while the server is up. It
owns `root`, `base`, `envDir`, `publicDir`, `build.outDir`,
`server.allowedHosts` and the alias: a config that sets one too is an
error naming it. Anything else (another plugin, `build.sourcemap`)
goes in the config as in any Vite project. `web/index.html` loads its
entry relatively, `./src/main.tsx`, so the dev server can serve it at
`/`; with `/src/main.tsx` the script is a 404 and the page is blank.

`package.json` mirrors the `.rbtrc`'s configs as scripts: `dev` runs
`dev:portless` (`portless frontend-<app> vite`, under the name the
backend's `--frontend-url` gives), `dev:ports` is plain `vite` on
5173, and `build` is `tsc -b && vite build`, which builds the web app
into `dist/web/`. It pins `react`, `react-dom`, Vite, its React plugin
and TypeScript at versions made to work together, the two Reboot
packages and an `overrides` entry for `@reboot-dev/reboot-web` at the
backend's `reboot` pin (two copies of it break the client), `zod`, the
three house typefaces, and `portless` and `vite-plugin-singlefile` as
dev dependencies (the plugin imports the second from the project).
`tsconfig.node.json` has Node's types; `tsconfig.app.json` includes
`web/src` and maps `@api/*` to `./api/*`.

Which script runs follows the run skill's choice (portless when it is
ready, plain ports otherwise): under portless the dev server is
`https://frontend-<app>.localhost` and the app `https://<app>.localhost/`;
on plain ports Vite is `http://localhost:5173/` and the app
`http://localhost:9991/`.

## The Backend URL — The Page's Own in Dev, Set for a Deploy

`<RebootClientProvider>` with no `url` detects the backend:
`window.REBOOT_URL`, then a `?rebootUrl=` query parameter, else
`window.location.origin`. The origin is right whenever the backend
serves the SPA, which it does in development (`--web-app`, Envoy
sending `/` to the Vite dev server) and once built
(`--web-app-dist-path`). So development has no `VITE_REBOOT_URL`
(the copied `web/.env.development` says so), and the page is opened
at the backend's URL, `https://<app>.localhost/` or
`http://localhost:9991/`, never at Vite's own, where the origin would
be Vite's and every call would go to the wrong place.

In production the backend serves the built SPA from its image (the
`deploy` skill), same origin, so there is nothing to set either. Only
a SPA on a static host of its own is on another origin, and says where
the backend is in `web/.env.production`
(`VITE_REBOOT_URL=https://<backend>`). The starter's `web/src/main.tsx`
takes it: `REBOOT_URL` is
`import.meta.env.VITE_REBOOT_URL ?? window.location.origin`, passed to
`<BackendCheck url>` and `<RebootClientProvider url>` around `<App />`
and `<ReloadPrompt>`; the copied `web/src/vite-env.d.ts` gives
`import.meta.env` its types (without it `npm run build` fails with
`Property 'env' does not exist on type 'ImportMeta'`). The browser
scenarios open the app at the backend's origin too (the harness routes
the backend's Envoy to the Vite dev server), so they need nothing
from this file.

The `?? window.location.origin` keeps the production build working
when the backend serves the built assets from one origin.

`BackendCheck` (`import { BackendCheck } from "./backend-check"`,
rendered with the starter, beside the stylesheet) says so while
`REBOOT_URL` doesn't answer, instead of a blank page or a failed call
per hook, and checks every few seconds; one failed check is ignored;
two in a row mean the backend is down. In development it replaces the app with a page
(the backend restarting after a change, or not started and how to
start it). In production it never takes the app down: the app renders
at once, and a banner over it says "<name> is updating, or can't
reach its server right now. Reconnecting…" until the backend answers
(a backend deploy is the usual reason), so nothing a person was in the
middle of is lost.

`ReloadPrompt` (`import { ReloadPrompt } from "./reload-prompt"`,
rendered with it) tells an open tab, in production, that a newer version
of the frontend has been published: a card in the bottom corner,
"<name> has been updated. Reload to get the new version.", with Reload
and Later. It never reloads by itself, so nothing half done is lost.
It compares the script the tab loaded with the one the site serves
now, so it needs no build id; it checks when the tab comes back into
view and every five minutes. Pass the app's name as `name`. A
web app scenario starts the backend first, so it never sees either.

A handle costs a connection too: `use<Type>({ id })` opens one when it
mounts, even with no reader called on it, so a list doesn't call it per
item. Mount one for the record being acted on: the open drawer, the
card being dragged, the row being edited.

## The Generated Client

The hook, mutator, and error declarations `rbt generate --react=`
emits are identical for every frontend, so they live in one place:
[`python/references/react-generated-client.md`](../../python/references/react-generated-client.md).
Read it before writing components — it has the `useFoo` overloads,
`UseFooApi`, the three-field reader return, `ResponseOrAborted`, the
`<Type><Method>Aborted` error classes, the snake→camel naming rules,
and why a hook id must be real on every render. Do **not** open
`frontend/api/**/*_rbt_react.ts` to rediscover them.

What is web-app-specific: the client is created by the
`<RebootClientProvider url={...}>` above, and the signed-in user's
handle comes from the no-argument `useUser()` (see "Sign-in and
Sign-out" below).

**One reader per page, not per record.** A page that shows many
records (rooms on a floor plan, cards on a board, rows in a list)
subscribes once, to a reader on their parent that returns them all.
One subscription per tile, card or row paints the page one record at a
time, and its totals change until the last arrives
([`patterns-cross-actor-reads.md`](../../python/references/patterns-cross-actor-reads.md)).

## Surfacing a Typed Error to the User

`aborted.error` is a discriminated union — the errors the method
declared plus the framework's (`PermissionDenied`, `Unknown`, …) —
tagged by `error.type`, which is the Python error class's name. The
copied `web/src/errors.ts` is the single translator, `friendlyError`,
a `switch` on `error.type` with `PermissionDenied` and a default on
`aborted.message`: add one case per error the API declares, its text
from the error model's fields (camelCased), and route every story with
a "shows a visible error" requirement through it. The frontend only
_reports_; the backend already refused the operation.

## Accessible Markup, So Scenarios Can Drive the Page

The web app scenarios (`python/references/testing-web-app.md`)
find elements the way a person, or a screen reader, does: a button
by what it says, a field by its label, a table by its heading. They
never take a selector, so the page has to expose an accessibility
tree. Build every page this way from the start, not when the first
scenario fails to find something:

```tsx
// A field's label is paired with it: `htmlFor` names the input's
// `id`. `fills "Amount ($)" in the web app with `250`` finds it
// through that pairing; a placeholder does not count.
<label htmlFor="amount">Amount ($)</label>
<input id="amount" type="number" value={amount} onChange={...} />

// A select is a `<select>` with a paired label, its options saying
// what a person would pick (here the account id).
<label htmlFor="from-account">From Account</label>
<select id="from-account" value={from} onChange={...}>
  {accounts.map((a) => <option key={a.id} value={a.id}>{a.id}</option>)}
</select>

// A button says what it does. `clicks the "Open Account" button`
// matches that text exactly; an icon-only button gets `aria-label`.
<button onClick={open}>Open Account</button>
<button aria-label="Delete" onClick={remove}><TrashIcon /></button>

// A table a scenario names has a labelled heading (or a
// `<caption>`). `sees "$1000" in the "Your Accounts" table` looks
// only inside it.
<h2 id="your-accounts">Your Accounts</h2>
<table aria-labelledby="your-accounts">...</table>

// A value a scenario reads back (an id the backend made up)
// carries `data-testid`, on the element whose text is exactly the
// value. This is the only place a test id belongs.
<td data-testid="account-id">{account.id}</td>
```

The roles a scenario may name are `button`, `link`, `tab`,
`checkbox`, `radio`, `menuitem`, `option`, `row`, and `table`; use
the native element for each (`<button>`, `<a href>`, `<input type="checkbox">`) rather than a `<div onClick>`, which has no role.
Text that changes on a backend event (a balance, a status) is
rendered as text, so `eventually sees "$1000"` can wait for it.

## Sign-in and Sign-out

`useSignIn()` / `useSignOut()` from `@reboot-dev/reboot-react` drive
the built-in OAuth server mounted at `/__/oauth/*`; call the
returned function from a button. Session state lives in the
HttpOnly `rbt_session` cookie, so there is no token to store, and
`useUser()` reports the result (`user === undefined` when signed
out).

The starter's `App.tsx` is the whole shape: `App` takes `useUser()`,
`useSignIn()` and `useSignOut()`, shows a skeleton while `isLoading`
covers the `/__/oauth/whoami` session probe, a Sign in button when
`user === undefined`, and otherwise Sign out and the signed-in
subtree; `SignedIn` is mounted only once `user` exists, so
`user.state_id` is real and every hook below it is called with a
genuine id.
