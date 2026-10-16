---
title: React Scaffolding — the frontend/ shell, copied from this skill's assets
impact: CRITICAL
impactDescription: The shell files for the `frontend/` tree come from `assets/frontend/`, copied whole. `vite.config.ts` is load-bearing — flattening the HTML output breaks MCP UI artifact discovery (the server resolves `frontend/dist/mcp/<name>/index.html`, the **nested** Vite default). `npm run build` runs `build.mjs`, which discovers and builds every UI.
tags: web, react, vite, tsconfig, package-json, css, build, hmr, scaffolding, build-mjs
---

## React Scaffolding — the `frontend/` shell

Everything here is MCP-UI-specific; the `frontend/` tree is this
skill's, and `python` knows nothing about it. The shell is copied,
never retyped and never read:

```sh
cp -R <this skill>/assets/frontend/. frontend/
mv frontend/mcp/_ui frontend/mcp/<ui-name>
```

Then edit the three marked places and nothing else:
`"<project-name>-web"` in `package.json`, `<UI Title>` in
`mcp/<ui-name>/index.html`, and the component `main.tsx` imports from
`./App` (`ClickerApp` in the copy; the name `App.tsx` exports, from
[`react-app-tsx.md`](react-app-tsx.md)).

What the copy holds:

- `package.json`: `npm run build` type-checks (`tsc -b`) then runs
  `build.mjs`, which discovers every `mcp/<name>/index.html` (and the
  `web/` SPA) and builds each one. Adding or removing a UI changes no
  script: never hand-maintain `build:<name>` scripts. The two Reboot
  packages are pinned to the backend's `reboot` version.
- `vite.config.ts`: one config, three jobs. The dev server gives HMR
  to every `mcp/<name>` UI and the `web/` SPA under `/__/frontend/`,
  which Envoy proxies; two builds are chosen by `RBT_BUILD_TARGET`,
  set per UI by `build.mjs`: `mcp:<name>` writes one self-contained
  `dist/mcp/<name>/index.html` (the path the MCP server resolves) and
  `web` writes the SPA into `dist/web/`. **Never edit it.**
  `Web artifact 'frontend/dist/mcp/<name>/index.html' is missing` means
  `cd frontend && npm run build`, not a change to this file.
- `build.mjs`: the discover-and-loop around that config.
- `tsconfig.json`, `tsconfig.app.json` (the `mcp` and `web` sources,
  `vite-env.d.ts`, the `@api/*` alias) and `tsconfig.node.json` (the
  config itself).
- `vite-env.d.ts`: Vite's ambient types (`*.module.css`,
  `import.meta.env`), at the `frontend/` root beside `mcp/` and `web/`.
- `mcp/_ui/`: one UI's `index.html` (`<div id="root">` and
  `./main.tsx`), `main.tsx` (`RebootClientProvider` around the
  component, `index.css` imported) and `index.css` (the colour tokens,
  dark and light).
