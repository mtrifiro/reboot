---
name: deploy
description: Deploy a finished Reboot app to production — the backend on Reboot Cloud, and the web frontend (if the app has one) published to a static host (Cloudflare Pages) under the user's own custom domain, talking to the backend cross-origin. Covers the production frontend build (backend URL, SPA fallback, asset paths), publishing with wrangler, attaching the domain, and the Application(allowed_origins=...) configuration that lets the browser reach the backend.
argument-hint: [<project-directory>]
allowed-tools: Bash, Read, Write, Glob, Grep, Edit, AskUserQuestion
---

# deploy — Put a Reboot App in Production

> **Version notices** from `rbt` (a mismatch, a newer Reboot): the [upgrade skill](../upgrade/SKILL.md).

Backend on **Reboot Cloud**, web frontend (a React SPA) on Cloudflare
Pages under the user's **own domain**, talking cross-origin: the SPA
calls `https://<application-id>.<cell>.rbt.cloud:9991` directly, and
the backend allows that origin via `OAuth(allowed_origins=[...])`.
An MCP UI with **no** web frontend: only the backend deploy applies —
do Step 2, then Step 6's release record, and stop. MCP UIs ship inside
the backend image and the backend serves them; nothing is hosted
externally.

> This skill **deploys**; it changes nothing beyond production
> configuration. Building: the [`mcp-ui` skill](../mcp-ui/SKILL.md)
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

1. **The frontend's domain** — e.g. `app.example.com` — and whether
   its DNS is managed on Cloudflare. Custom domains are the static
   host's feature, so the hostname must be attachable there.
2. **Cloudflare credentials** for headless publishing:
   `CLOUDFLARE_ACCOUNT_ID` and a `CLOUDFLARE_API_TOKEN` with
   permissions Cloudflare Pages: Edit, Zone: Read, and DNS: Edit
   (DNS only when the zone is on Cloudflare).
3. **Reboot Cloud access**: `REBOOT_CLOUD_API_KEY`, the
   organization, and an application name — see
   `python/references/lifecycle-reboot-cloud.md`.

Export the secrets as environment variables; never pass them as
command-line flags (visible in the process listing).

**Before the first deploy, who may do what.** An app built without
its **Who may do what** feature (`design/design.md`'s Sign-in says
"Everyone signed in can do everything for now") lets anyone who signs
in do everything — with a real provider, anyone with a Google account.
Say so in one line and ask in a question dialog (`AskUserQuestion`
where available): "Build Who may do what first" (recommended) or
"Deploy anyway". Never deploy such an app without that answer.

## Step 2 — Deploy the backend to Reboot Cloud

Follow `python/references/lifecycle-reboot-cloud.md` (with
`python/references/lifecycle-dockerfile.md` for the image and
`python/references/lifecycle-secrets.md` for secrets). Checks that
bite here:

- **A real OAuth provider.** `Development()` is dev-only; the `prod=`
  provider must be set, and the backend's `/__/oauth/callback`
  redirect URI registered with the IdP
  (`mcp-ui/references/auth-oauth-providers.md`, per provider).
- **Authorizers everywhere.** Every externally reachable method
  needs an authorizer; calls without one are denied in production
  (`python/references/servicer-authorizer.md`).
- **Dual-frontend apps:** the Docker image must still run the MCP UI
  builds so `dist/mcp/<name>/` is in the image (the backend serves
  those); the **web** SPA goes to the static host and need not be.

Record the API URL `rbt cloud up` prints,
`https://<application-id>.<cell>.rbt.cloud:9991`; Step 4 bakes it in.

## Step 3 — Allow the frontend's origin on the backend

The browser only reaches the backend cross-origin when the frontend's
origin is in the app's allow-list:

```python
application = Application(
    ...,
    oauth=OAuth(
        provider=...,
        allowed_origins=["https://app.example.com"],
    ),
)
```

Rules:

- Entries are exact origins — `scheme://host[:port]`, no trailing
  slash, no path. List **every** origin the frontend is served from:
  `https://example.com` and `https://www.example.com` if both
  resolve, `https://<project>.pages.dev` if the user wants it to work
  too.
- This one list is both the CORS policy on Reboot Cloud's proxy
  **and** the OAuth browser flow's redirect validation
  (`/__/oauth/start?return_to=...` only accepts origins on it); no
  separate OAuth configuration exists.
- In production, an app with `oauth=` set **must** set
  `allowed_origins` (the empty list is accepted for apps with no
  browser frontend); startup fails otherwise.

After adding it, redeploy: `rbt cloud up`.

## Step 4 — Build the frontend for production

`frontend/vite.config.ts` builds the SPA, `frontend/web/`, into
`frontend/dist/web/` at `base: "/"`: a plain build served at any
host's root.

1. **Bake in the backend URL.** Next to
   `frontend/web/.env.development` (which sets `VITE_REBOOT_URL` for
   dev), write `frontend/web/.env.production`:

   ```sh
   VITE_REBOOT_URL=https://<application-id>.<cell>.rbt.cloud:9991
   ```

   Vite's production build reads it; the dev one stays.

2. **Build.** `cd frontend && npm run build`. The publish directory is
   `frontend/dist/web/`, where `index.html` lands. Without a top-level
   `404.html`, Pages serves `index.html` for any path it has no file
   for: URL-path routes need no routing file.

   A dual-frontend app builds with the `mcp-ui` skill's
   `vite.config.ts`, whose web build carries the `/__/frontend/web/`
   prefix the backend serves it under. For it, a `_redirects` file in
   `frontend/web/public/` (Vite copies it into the build) maps the
   prefix back onto the published files, and any URL-path router's
   basename stays `"/"` — never `basename={import.meta.env.BASE_URL}`,
   which bakes the prefix into route matching in the browser:

   ```
   /__/frontend/web/* /:splat 200
   /* /index.html 200
   ```

## Step 5 — Publish to Cloudflare Pages and attach the domain

With `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` exported,
`wrangler` runs headless (no `wrangler login`):

```sh
npx --yes wrangler@4 pages project create <project-name> \
    --production-branch=main
npx --yes wrangler@4 pages deploy <publish-directory> \
    --project-name=<project-name> --branch=main
```

The deploy prints `https://<project-name>.pages.dev`, already live.
Attach the custom domain via the Cloudflare API (wrangler has no
subcommand for it):

```sh
curl -sS -X POST \
    "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/pages/projects/<project-name>/domains" \
    -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
    -H "Content-Type: application/json" \
    --data '{"name": "app.example.com"}'
```

Then DNS. On a Cloudflare zone, create the record via the API (zone
id: `GET /zones?name=example.com`):

```sh
curl -sS -X POST \
    "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records" \
    -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
    -H "Content-Type: application/json" \
    --data '{"type": "CNAME", "name": "app.example.com", "content": "<project-name>.pages.dev", "proxied": true}'
```

When the zone is **not** on Cloudflare, tell the user to add
`CNAME app.example.com → <project-name>.pages.dev` at their DNS
provider; the attachment validates once it resolves, and Cloudflare
then provisions TLS.

Redeploys are `wrangler pages deploy` again — the project and domain
stay put.

## Step 6 — Verify

1. **Static serving:** `curl -sSI https://app.example.com/` returns
   200 with `content-type: text/html`; a deep route
   (`curl -sSI https://app.example.com/some/route`) also returns 200
   (the SPA fallback).
2. **CORS:**

   ```sh
   curl -sSI "https://<application-id>.<cell>.rbt.cloud:9991/__/oauth/whoami" \
       -H "Origin: https://app.example.com"
   ```

   must include `access-control-allow-origin: https://app.example.com`
   and `access-control-allow-credentials: true`. If not, the backend
   in the Cloud predates the `allowed_origins` change — redeploy it.

3. **In the browser** (the user, or a browser tool if available):
   open `https://app.example.com`, sign in, and confirm signed-in data
   renders: live data proves the WebSocket path cross-origin too.
4. **The release record:** `python3 scripts/release_record.py
   --revision <N> --api-url <url> --site <url>` from the deploy's
   output appends the release record to `deploy/ledger.jsonl`. Close
   with the **Reboot Observe · live** card
   ([`app/references/flywheel.md`](../app/references/flywheel.md)).

## Troubleshooting

- **Blank page, console full of MIME-type or 404 asset errors:** the
  asset prefix doesn't match the host — on the dual-frontend layout,
  `_redirects` lacks the `/__/frontend/web/*` rewrite line, or it
  isn't first.
- **Routes render nothing on the custom domain but the app loads at
  `/`:** router basename baked from `import.meta.env.BASE_URL`
  (Step 4.3).
- **Browser console shows CORS errors:** the exact origin (watch
  scheme and `www.`) is missing from `allowed_origins`, or the
  backend wasn't redeployed after adding it.
- **Sign-in fails with an invalid-redirect error:** same cause — the
  frontend origin isn't on `allowed_origins`, so `/__/oauth/start`
  refuses the `return_to`.
- **Signed-in session doesn't survive a reload in Safari/Firefox:**
  tracking prevention strips the cross-site session cookie that
  silent restoration relies on. Sign-in still works; the user signs
  in again — a known limit of fully cross-site hosting.
