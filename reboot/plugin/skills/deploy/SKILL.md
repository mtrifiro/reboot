---
name: deploy
description: Deploy a finished Reboot app to production on Reboot Cloud with `rbt cloud up` — one container that runs the backend and serves the built MCP Apps and web app from it, same-origin, so there is no second host, no cross-origin configuration and no cross-site cookie problems. Covers the Dockerfile that builds the frontend into the image, the `.rbtrc` `serve run` lines that serve it, the OAuth and `allowed_origins` production checks, and verification; and what hosting the web app on a CDN of your own (Cloudflare Pages, Firebase, Vercel, ...) costs instead.
argument-hint: [<project-directory>]
allowed-tools: Bash, Read, Write, Glob, Grep, Edit, AskUserQuestion
---

# deploy — Put a Reboot App in Production

> **Version notices** from `rbt` (a mismatch, a newer Reboot): the [upgrade skill](../upgrade/SKILL.md).

`rbt cloud up` puts the app in **one container** on **Reboot Cloud**:
the backend, and the built frontend it serves from the image, the MCP
Apps under `/__/frontend/` and the web app (a React SPA) at `/`. The
browser, the backend and sign-in share one origin,
`https://<application-id>.<cell>.rbt.cloud:9991`: no second host, no
backend URL baked into the frontend, no cross-site cookie to lose. A
new revision is the same `rbt cloud up` again (Step 4).

> This skill **deploys**; it changes nothing beyond production
> configuration. Building: the [`mcp-app` skill](../mcp-app/SKILL.md)
> and the [web-app skill](../web-app/SKILL.md); running locally: the
> [run skill](../run/SKILL.md).

A deploy is the Reboot Flywheel's **promote** decision, and it is the
user's ([`app/references/flywheel.md`](../app/references/flywheel.md)).
Before Step 2, run `python3 scripts/release_record.py --dry-run` and
open with its output under the **Reboot Prove · ready to deploy** card
([`app/references/evidence.md`](../app/references/evidence.md)). Say
plainly when the run is not a clean, full, passing run of this commit,
or when the design carries changes nobody accepted. Then ask in a
question dialog (`AskUserQuestion` where available) whether to deploy
now or not yet. On a branch other than `main`, say what isn't merged
yet. Never merge, switch branches or deploy on your own.

## Step 1 — Gather inputs (ask early, in one pass)

Before the first deploy, when `scripts/model_diff.py` lists a package
under _Packages_, say so in one line with the rest of the inputs: the
split is cheap now and a schema change after
(`app/references/accept-design.md`, "Packages").

Ask everything below up front, in one `AskUserQuestion` round or one
message, so no later step stalls:

1. **Reboot Cloud access**: `REBOOT_CLOUD_API_KEY`, and the
   organization (the first deploy only) — see
   `python/references/lifecycle-reboot-cloud.md`. The application
   name is not asked: `rbt cloud up` reads it from `.rbtrc`. Add these
   lines, with the `serve run --application-name`'s name, where they
   are missing:

   ```sh
   cloud up --application-name=<app>
   cloud down --application-name=<app> --expunge
   cloud logs --application-name=<app>
   ```

2. **Production OAuth**, if the app has `oauth=`: which provider, and
   its client id and secret (Cloud secrets,
   `python/references/lifecycle-secrets.md`).

Export the secrets as environment variables; never pass them as
command-line flags (visible in the process listing).

**Before the first deploy, who may do what.** An app built without
its **Who may do what** feature (`design/design.md`'s Sign-in says
"Everyone signed in can do everything for now") lets anyone who signs
in do everything — with a real provider, anyone with a Google account.
Say so in one line and ask in a question dialog (`AskUserQuestion`
where available): "Build Who may do what first" (recommended) or
"Deploy anyway". Never deploy such an app without that answer.

## Step 2 — Production readiness

Follow `python/references/lifecycle-reboot-cloud.md` (with
`python/references/lifecycle-secrets.md` for secrets). Checks that
matter here:

- **A real OAuth provider.** `Development()` is dev-only; the `prod=`
  provider must be set, and the backend's
  `https://<application-id>.<cell>.rbt.cloud:9991/__/oauth/callback`
  redirect URI registered with the IdP once the URL is known
  (`mcp-app/references/auth-oauth-providers.md`, per provider).
- **`allowed_origins=[]`.** In production an app with `oauth=` must
  set `OAuth(allowed_origins=...)`, or startup fails. The backend
  serves the web app, so its only browser origin is the backend's
  own, always trusted: the empty list. Only a web app hosted elsewhere
  (the last section) lists an origin.
- **Authorizers everywhere.** Every externally reachable method
  needs an authorizer; calls without one are denied in production
  (`python/references/servicer-authorizer.md`).
- **No baked-in backend URL.** The React client finds the backend at
  the page's own origin, so `frontend/web/.env.production` must not
  set `VITE_REBOOT_URL` (delete the file if that is all it holds);
  one pointing anywhere else turns every call cross-origin and breaks
  sign-in.

## Step 3 — The container serves the frontend

`rbt cloud up` builds the project's `Dockerfile`; its canonical
layout, with the frontend layers any app with a `frontend/` adds, is
`python/references/lifecycle-dockerfile.md`. Two halves:

1. **The `Dockerfile`** copies `frontend/` in before `rbt generate`,
   then runs `cd frontend && npm ci && npm run build`, so
   `frontend/dist/mcp/<name>/` (the MCP Apps) and `frontend/dist/web/`
   (the web app) are in the image. `.dockerignore` keeps
   `frontend/node_modules/` and `frontend/dist/` out of the context.
2. **`.rbtrc`'s `serve run` lines** point the backend at the builds:
   an MCP App has the first line, a web app the second, a
   dual-frontend app both:

   ```sh
   serve run --mcp-app-dist-path=frontend/dist/mcp
   serve run --web-app-dist-path=frontend/dist/web
   ```

   `--web-app-dist-path` serves the SPA at `/`, its `index.html`
   answering any path with no route or file, so the SPA's routing
   works on reload, as `dev run --web-app` does from the dev server.
   The web build is at `base: "/"`, so any URL-path router's basename
   stays `"/"`. The other production lines are in
   `lifecycle-rbtrc.md`.

If anything above changed, try the builds locally first:
`rbt dev run --config=dist` (after `cd frontend && npm run build`)
serves them the way `rbt serve run` will.

## Step 4 — Deploy

With `REBOOT_CLOUD_API_KEY` exported:

```sh
rbt cloud up --organization=<org>
```

(`--organization` the first time only.) It builds the image, pushes
it, rolls out a revision and prints the app's URL,
`https://<application-id>.<cell>.rbt.cloud:9991`: the web app (`/`),
the MCP endpoint (`/mcp`) and the API at once. Register
`<that URL>/__/oauth/callback` with the IdP now if Step 2 waited on
it; no redeploy is needed. Secrets go in with `rbt cloud secret set`
and roll the app on their own.

## Step 5 — Verify

With `URL=https://<application-id>.<cell>.rbt.cloud:9991`:

1. **The web app:** `curl -sSI "$URL/"` and a deep route
   (`curl -sSI "$URL/some/route"`, the SPA fallback) return 200 with
   `content-type: text/html`. Reboot's own page at `/` means
   `--web-app-dist-path` is missing or names a directory the image
   did not build.
2. **The MCP Apps:** `curl -sSI "$URL/__/frontend/mcp/<name>/index.html"`
   (a `UI(path="<name>")`, built to `frontend/dist/mcp/<name>/`)
   returns 200; a 404 means `--mcp-app-dist-path` is missing or the
   build is not in the image.
3. **In the browser** (the user, or a browser tool if available):
   open `$URL/`, sign in (through `/__/oauth/start` and back to `/`,
   same-origin), and confirm signed-in data renders and updates live.
   An app with MCP Apps: connect an MCP client to `$URL/mcp` and
   render one.
4. **The release record:** `python3 scripts/release_record.py
   --revision <N> --api-url "$URL" --site "$URL"` from the deploy's
   output appends the release record to `deploy/ledger.jsonl`. Close
   with the **Reboot Observe · live** card
   ([`app/references/flywheel.md`](../app/references/flywheel.md)).

## Troubleshooting

- **Blank page, console full of MIME-type or 404 asset errors:** the
  build's `base` doesn't match where it is served; the web build is
  at `base: "/"`.
- **Routes render nothing but the app loads at `/`:** router basename
  baked from `import.meta.env.BASE_URL`; keep it `"/"`.
- **CORS errors, or sign-in fails with an invalid-redirect error:**
  the page calls an origin other than the one it was served from: a
  `VITE_REBOOT_URL` is baked into the build (Step 2); remove it and
  rebuild.
- **Startup fails naming `allowed_origins`:** `oauth=` without an
  explicit list; set `[]` (Step 2).
- **The image builds locally but Cloud rejects it, or `rbt serve run`
  fails on boot:** the Dockerfile departs from the canonical layout
  (base image version, `CMD`, layer order): `lifecycle-dockerfile.md`'s
  pitfalls.

## Hosting the web app somewhere else

The web build is a plain SPA, so it _can_ go on a static host of the
user's choosing (Cloudflare Pages, Firebase Hosting, Vercel, Netlify,
S3) with the backend still on Reboot Cloud. Only when the user asks,
and say what it costs first:

- **It is cross-site.** `app.example.com` and
  `<application-id>.<cell>.rbt.cloud` are different sites, so the
  session cookie is third-party: Chrome keeps it, Safari and Firefox
  strip it, and the user signs in again on every visit there. Same-site
  hosting (`api.example.com` beside `app.example.com`) needs Reboot
  Cloud's upcoming **custom domains**; until then persistent sign-in
  is Chrome-only.
- **Reboot Cloud is going to serve the web bundle from a CDN itself**,
  so edge delivery, the main reason to host elsewhere, is going away
  and this setup becomes something to undo.

If the user still wants it: build with `VITE_REBOOT_URL=<the backend's
URL>` in `frontend/web/.env.production`, list the app's exact origins
(`scheme://host`, no trailing slash) in `OAuth(allowed_origins=[...])`,
drop the `serve run --web-app-dist-path` line, publish
`frontend/dist/web/` with the host's own tooling and point the domain
at it; pass that URL as the release record's `--site`. The MCP Apps
stay in the image; the backend serves them.
