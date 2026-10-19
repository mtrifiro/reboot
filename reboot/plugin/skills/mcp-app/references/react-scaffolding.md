---
title: React Scaffolding — the frontend/ shell, copied from this skill's assets
impact: CRITICAL
impactDescription: The shell files for the `frontend/` tree come from `assets/frontend/`, copied whole. `vite.config.ts` is the stock Vite file plus `reboot()` from `@reboot-dev/reboot-react/vite`, which builds each MCP App into the **nested** `frontend/dist/mcp/<name>/index.html` the server resolves. `npm run build` runs `build.mjs`, which calls the package's `build()` for every UI the plugin declares.
tags: web, react, vite, tsconfig, package-json, css, build, hmr, portless, scaffolding, build-mjs
---

## React Scaffolding — the `frontend/` shell

Everything here is MCP App-specific; the `frontend/` tree is this
skill's, and `python` knows nothing about it. The shell is copied,
never retyped and never read:

```sh
cp -R <this skill>/assets/frontend/. frontend/
mv frontend/mcp/_ui frontend/mcp/<ui-name>
```

Then edit the marked places and nothing else: `<project-name>` in
`package.json` (the name and the `dev:portless` script; it is the
`.rbtrc`'s `--application-name`), `<UI Title>` in
`mcp/<ui-name>/index.html`, and the component `main.tsx` imports from
`./App` (`ClickerApp` in the copy; the name `App.tsx` exports, from
[`react-app-tsx.md`](react-app-tsx.md)). `<ui-name>` is the `UI()`'s
`path=`.

What the copy holds:

- `package.json`: `npm run build` type-checks (`tsc -b`) then runs
  `build.mjs`. The `dev` scripts mirror the `.rbtrc`'s configs:
  `npm run dev` is `dev:portless` (`portless frontend.<project-name>
  vite`, at `https://frontend.<project-name>.localhost`) and
  `dev:ports` is plain `vite` on 5173; the [`run`
  skill](../../run/SKILL.md) picks one. `portless`, `vite` and
  `vite-plugin-singlefile` are dev dependencies; the two Reboot
  packages are pinned to the backend's `reboot` version.
- `vite.config.ts`: `plugins: [react(), reboot({ mcpAppPath: "mcp",
  webAppPath: "web", apiPath: "api" })]`. `reboot()` drives the dev
  server (HMR for every MCP App and the web app under
  `/__/frontend/`, each MCP App at `/__/frontend/mcp/<path>/`, which
  Envoy proxies with `--mcp-app`) and the builds selected by
  `RBT_BUILD_TARGET`: `mcp:<path>` writes one self-contained
  `dist/mcp/<path>/index.html` (what `--mcp-app-dist-path=frontend/dist/mcp`
  reads), `web` writes the SPA into `dist/web/`. It also sets the
  `@api` alias, dedupes `react`, `react-dom` and `zod`, and reads
  `.env*` from `web/`. Other Vite config (another plugin,
  `build.sourcemap`) is added to the literal as usual; setting a value
  the plugin owns (`root`, `base`, `envDir`, `publicDir`,
  `build.outDir`, `build.emptyOutDir`, `allowedHosts`, the `@api`
  alias) is an error naming it, and a path the config adds is written
  `path.resolve(__dirname, ...)`. **Never replace it with a
  hand-written config.** `The '<ui>' MCP App's build '.../index.html'
  is missing` means `cd frontend && npm run build`, not a change to
  this file.
- `build.mjs`: `await build()` from `@reboot-dev/reboot-react/vite`,
  which asks `reboot()` for the UIs (every `mcp/<name>/index.html`,
  then `web/`) and runs one `vite build` per UI. Adding or removing a
  UI changes no script: never hand-maintain `build:<name>` scripts.
- `tsconfig.json`, `tsconfig.app.json` (the `mcp` and `web` sources,
  `vite-env.d.ts`, the `@api/*` alias) and `tsconfig.node.json` (the
  config itself).
- `vite-env.d.ts`: Vite's ambient types (`*.module.css`,
  `import.meta.env`), at the `frontend/` root beside `mcp/` and `web/`.
- `mcp/_ui/`: one UI's `index.html` (`<div id="root">` and
  `./main.tsx`), `main.tsx` (`RebootClientProvider` around the
  component, `index.css` imported) and `index.css` (the colour tokens,
  dark and light).
