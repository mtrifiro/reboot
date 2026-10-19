---
title: Running an MCP App — the Tunnel, the Setup Wizard, MCPJam
impact: HIGH
impactDescription: The process and the one page only an MCP App needs around the backend and frontend, and the client it launches on demand; a Web App skips all of it
tags: run, mcp-app, tunnel, cloudflared, portless, tunnel-url, setup-wizard, mcpjam
---

## Running an MCP App — the Tunnel, the Setup Wizard, MCPJam

Read from the `run` skill's Step 5, for an MCP App only. The backend
and frontend steps, and whether portless is in use, are the skill's;
these go around them. Below, `<app>` is the `.rbtrc`'s
`--application-name`.

### Tunnel — before the backend

An MCP App's backend needs a Cloudflare quick tunnel so external MCP
clients (e.g. ChatGPT) can reach it. A **Web App** gets none: it has
no MCP clients, and a tunnel would publish a dev server where the
`Development()` picker lets anyone sign in as anyone.

**One tunnel per app, for the whole session.** A quick tunnel's
`*.trycloudflare.com` URL is new every time one starts, and the
user's MCP client holds the old one. So first look for one already
up, from earlier in this session or from another:

```sh
pgrep -af cloudflared
```

A `cloudflared tunnel` line whose target is this app is the tunnel to
use: under portless, `--http-host-header <app>.localhost`; otherwise
`--url http://localhost:<BACKEND_PORT>`. Its
`--metrics localhost:<METRICS_PORT>` says where
`http://localhost:<METRICS_PORT>/quicktunnel` returns the URL. Leave
every other line alone; those are other apps' tunnels.

If there is none, run the bundled `cloudflared` shim in its own
background shell, with `--metrics localhost:<METRICS_PORT>` a free
local port (`4040`, unless another app's tunnel holds it). Under
portless the tunnel reaches the backend by name through the portless
proxy, so it needs no port, can start before the backend, and
outlives every `rbt dev run` after it:

```sh
cloudflared tunnel \
    --metrics localhost:4040 \
    --url https://127.0.0.1:443 \
    --http-host-header <app>.localhost \
    --origin-server-name <app>.localhost \
    --origin-ca-pool ~/.portless/ca.pem
```

(`443` is `PORTLESS_PORT` if the user set it.) cloudflared passes the
public hostname on as `X-Forwarded-Host`, which the backend uses for
the URLs it hands the MCP client. On plain ports, point the tunnel at
the backend's port instead, `9991` unless `rbt dev run` is given
`--port` (`python/references/lifecycle-rbtrc.md`, the
`application_port` knob):

```sh
cloudflared tunnel \
    --metrics localhost:4040 \
    --url http://localhost:9991
```

Either way, read the tunnel's URL, `https://<hostname>` from
`http://localhost:<METRICS_PORT>/quicktunnel` (it can take a few
seconds to appear), and pass it to the skill's `rbt dev run` as
`--tunnel-url=<URL>`: the setup wizard then shows and verifies this
app's tunnel at once, rather than looking for one through the
providers' local APIs, which with several apps up can find another
app's.

### Setup wizard — after the backend

An MCP App's backend serves an interactive **setup wizard** at its
root URL (`https://<app>.localhost` under portless, else
`http://localhost:9991`): a browser page that walks the user through
connecting the app to an MCP client (picking a client, copying the
`/mcp` endpoint, completing the OAuth handshake). It is the natural
starting point, and the place the user launches MCPJam from, so open
it.

Once the backend logs show it is serving traffic, do two things:

1. **Tell the user the wizard exists and what it's for** — e.g.
   "Setup wizard (connect an MCP client) at https://<app>.localhost".
2. **Open it once**: in the Claude app (or any host with a Browser
   pane), in the pane, with the pane's tool (`preview_start` with its
   URL), never in the external browser. Elsewhere, in the browser,
   best-effort:

   ```sh
   URL=https://<app>.localhost   # or http://localhost:9991 on plain ports
   "$BROWSER" "$URL" || xdg-open "$URL" || python3 -m webbrowser "$URL"
   ```

Open the wizard **exactly once, at first startup — never on
reloads.** The backend runs under `--watch` and reprints its
"serving traffic" banner on every hot reload; re-opening a tab each
time would be hostile. Opening it as a one-shot startup step (not
from a loop that watches for the backend coming back) satisfies
this; just don't add a reload-driven re-open.

**Skip this only for a Web App**, which serves no wizard and has
nothing to connect. Every other app here is an MCP App, so open it
even for a **tools-only app** with no `UI()` methods: connecting
MCPJam or Claude through the wizard is how the user tries those
tools.

### MCPJam inspector — on demand, never during startup

Do **not** start the MCPJam inspector as part of bringing the app up.
It is one of the MCP clients the setup wizard offers (alongside
Claude and ChatGPT), relevant only once the user picks **MCPJam**
there. The wizard's MCPJam step then shows the exact launch command,
pointed at the app's `/mcp` endpoint with OAuth, for the user to run
in their own terminal:

```sh
npx @mcpjam/inspector@2.23.3 --url http://localhost:9991/mcp --oauth
```

Leave the launch to the wizard. Only run it yourself if the user
explicitly asks, and then with the plugin's `mcpjam-inspector` shim
(it pins the version and passes `--no-open`, so you surface the URL
instead of a browser tab popping), at the app's `/mcp`
(`https://<app>.localhost/mcp` under portless):

```sh
mcpjam-inspector --url http://localhost:9991/mcp --oauth
```

Either way the inspector binds the fixed port 6274.

### At the hand-off

Give the user the setup-wizard URL (`https://<app>.localhost` or
`http://localhost:9991`, already opened for them, for connecting an
MCP client) and a first prompt to try (e.g. "Create a new todo list
and show it to me"). Don't hand over an MCPJam URL: MCPJam isn't
running, and only starts if the user picks it in the wizard.
