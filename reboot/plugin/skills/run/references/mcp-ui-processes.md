---
title: Running an MCP UI — the Tunnel, the Setup Wizard, MCPJam
impact: HIGH
impactDescription: The two processes and the one page only an MCP UI needs around the backend and frontend; a Web App skips all of it
tags: run, mcp-ui, tunnel, cloudflared, setup-wizard, mcpjam
---

## Running an MCP UI — the Tunnel, the Setup Wizard, MCPJam

Read from the `run` skill's Step 5, for an MCP UI only. The backend
and frontend steps are the skill's; these go around them.

### Tunnel — before the backend

Before starting an MCP UI's backend, kick off a Cloudflare quick
tunnel pointed at the dev server's port so external MCP clients
(e.g. ChatGPT) can reach it. Run the bundled `cloudflared` shim in
its own background shell with two flags you choose:

- `--url http://localhost:<BACKEND_PORT>` — the dev server's HTTP
  port (the default is `9991`; pick a different free port if `9991`
  is taken and configure `rbt dev run` to match below).
- `--metrics localhost:<METRICS_PORT>` — a free local port for
  cloudflared's metrics endpoint (the default is `4040`; pick a
  different free port if `4040` is taken). Once the tunnel is up,
  `http://localhost:<METRICS_PORT>/quicktunnel` returns the
  allocated `*.trycloudflare.com` URL.

```sh
cloudflared tunnel \
    --metrics localhost:4040 \
    --url http://localhost:9991
```

Pass the **same** `<BACKEND_PORT>` to `rbt dev run` so the dev
server and the tunnel agree on the port — Reboot's default is
`9991`, so no extra flag is needed if you stuck with the default;
otherwise see `python/references/lifecycle-rbtrc.md` for the
`application_port` knob.

### Setup wizard — after the backend

An MCP UI's backend serves an interactive **setup wizard** at
its root URL (`http://localhost:9991`) — a browser page that walks
the user through connecting the app to an MCP client (such as
MCPJam: picking a client, copying the `/mcp` endpoint, completing
the OAuth handshake). It is the natural starting point — and the
place the user launches MCPJam from, if they pick it — so open it.

Once the backend logs show it is serving traffic, do two things:

1. **Tell the user the wizard exists and what it's for** — e.g.
   "Setup wizard (connect an MCP client) at http://localhost:9991".
2. **Open it once**: in the Claude app (or any host with a Browser
   pane), in the pane, with the pane's tool (`preview_start` with its
   URL), never in the external browser. Elsewhere, in the browser,
   best-effort:

   ```sh
   "$BROWSER" http://localhost:9991 || xdg-open http://localhost:9991 || \
     python3 -m webbrowser http://localhost:9991
   ```

Open the wizard **exactly once, at first startup — never on
reloads.** The backend runs under `--watch` and reprints its
"serving traffic" banner every time it hot-reloads on a code change;
re-opening a browser tab on each reload would be hostile. Because
you open it as a one-shot step during initial startup (not from a
loop that watches for the backend coming back up), this is naturally
satisfied — just don't add any reload-driven re-open.

**Skip this only for a Web App.** A **Web App** has no MCP frontend,
so no wizard is served and there's nothing to connect — don't
announce or open it. Every other app here is an MCP app, and the
wizard is how you point a client at it, so open it even for a
**tools-only app** with no `UI()` methods: connecting MCPJam or
Claude through the wizard is exactly how the user tries those MCP
tools out.

### MCPJam inspector — on demand, never during startup

Do **not** start the MCPJam inspector as part of bringing the app
up. MCPJam is just one of the MCP clients the setup wizard offers
(alongside Claude and ChatGPT), so starting it is only relevant
once the user picks **MCPJam** in the wizard. When they do, the
wizard's MCPJam step shows the exact launch command — pointed at
the app's `/mcp` endpoint with OAuth — for the user to run from
their own terminal:

```sh
npx @mcpjam/inspector@2.23.3 --url http://localhost:9991/mcp --oauth
```

Leave the launch to the wizard. Only run it yourself if the user
explicitly asks you to, and then use the plugin's
`mcpjam-inspector` shim (it pins the version and passes `--no-open`
so it does not pop a browser tab — you surface the URL instead):

```sh
mcpjam-inspector --url http://localhost:9991/mcp --oauth
```

Either way the inspector binds the fixed port 6274.

### At the hand-off

Give the user the setup-wizard URL (`http://localhost:9991`, already
opened for them, for connecting an MCP client) and a first prompt to
try (e.g. "Create a new todo list and show it to me"). Don't hand
over an MCPJam URL — MCPJam isn't running, and only starts if the
user picks it in the wizard.
