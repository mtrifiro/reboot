---
title: Configure `.rbtrc` Correctly
impact: CRITICAL
impactDescription: `rbt generate` and `rbt dev run` won't find files without correct config; the file is copied with the project shell
tags: rbtrc, config, generate, dev, expunge, application-name
---

## Configure `.rbtrc` Correctly

> **Critical:** `.rbtrc` is line-based, each line `<subcommand> <flag>`
> (or `<subcommand>:<config> <flag>` for a named config), comments
> with `#`. On `reboot>=1.0.4`, `dev run --application-name=<app>` is
> the canonical persistence flag; `--name=<app>` still works as a
> deprecated alias that warns on every run. A fresh `.rbtrc` uses
> `--application-name`, whatever older examples and tutorials show.

**Incorrect (older Reboot, which models remember best):**

```sh
# DON'T — APIs are pydantic files found by `generate`, not .proto
# files compiled by `protoc`; `--name` is deprecated.
protoc --include=api/
protoc --python=backend/api
dev run --name=chat-room
```

**Correct:** the `.rbtrc` copied with the project shell
(`lifecycle-project-setup.md`; the same shape as the
[`reboot-bank-pydantic`](https://github.com/reboot-dev/reboot-bank-pydantic)
example's), with `<project-name>` replaced. It holds the `generate`
lines (`api/` as the definition root, `--python=backend/api/`,
`--react=frontend/api`), the `dev run` lines (`--watch` on the backend
sources, `--python`, `--application-name`, `--env-file=.env`,
`--application=backend/src/main.py`), the matching `dev expunge`, and
the `serve run` block.

## `--application-name` Persists State Across Restarts

The value keys the state that survives between `rbt dev run`
restarts; `dev expunge --application-name=<name>` takes the same value
so one command resets it.

## `--env-file` Loads Secrets Into `rbt dev run`

`dev run --env-file=.env` reads `KEY=VALUE` lines (standard `.env`
syntax: comments, blank lines, `export` prefixes, quoted values) and
sets each as an environment variable before launching the app, which
reads them with `os.environ`. A missing file is a warning, not an
error, so the line stays in an app with no secrets yet; editing the
file while `rbt dev run` runs restarts the app, as editing a
`--watch`ed source does. `--env-file` is **dev-only**, and
`--env=KEY=VALUE` overrides it; `.env` stays out of git. Full secrets
guidance, including Reboot Cloud, is `lifecycle-secrets.md`.

## `serve run` Lines: Production Config

The same file holds the flags for `rbt serve run`, the command the
Cloud image's `CMD ["rbt", "serve", "run"]` and any on-prem deploy
invoke: `--python`, `--application`, the **same** `--application-name`
(it keys state in production too) and `--tls=external`. When
`--tls=external` is right, and the full production block, is
[`lifecycle-dockerfile.md`](lifecycle-dockerfile.md); the deploy
workflow is [`lifecycle-reboot-cloud.md`](lifecycle-reboot-cloud.md);
production secrets come from `rbt cloud secret set`
([`lifecycle-secrets.md`](lifecycle-secrets.md)) or the environment of
a self-hosted `rbt serve`.

## Named Configs

A `<subcommand>:<config>` line applies only with `--config=<config>`
on the command line, and `dev run --default-config=hmr` picks one
when none is given. The MCP UI shell uses this for its `:hmr`
(`--frontend-host=http://localhost:4444`) and `:dist`
(`--frontend-dist-path=frontend/dist`) modes.
