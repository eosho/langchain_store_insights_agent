---
applyTo: "tools/aig_spec_kit/factory/cli/**/*.py"
description: "Use when modifying the `aig factory` Typer CLI surface — register-pattern, signal handling, log configuration, one-file-per-command rule"
---

# AIG Factory CLI

Operator surface for the factory. One file per command + a parent Typer that wires them. The CLI is the topmost layer in the factory layering pyramid; it imports `WorkerBuilder` and the public services facade only.

**Companion instructions:** [factory-module.instructions.md](./factory-module.instructions.md), [factory-runtime.instructions.md](./factory-runtime.instructions.md).

## Architecture

```
tools/aig_spec_kit/factory/cli/
├── __init__.py         # Re-exports `app` only (RUF067)
├── factory_app.py      # Parent Typer + @app.callback() that wires RichHandler
├── connect.py          # `aig factory connect`  — OAuth device flow (one-time)
├── init.py             # `aig factory init`     — bootstrap labels + write .aig/factory.yaml (one-time)
├── health.py           # `aig factory health`   — install-token probe
├── inspect.py          # `aig factory inspect`  — locks / history / pr (read-only)
├── token.py            # `aig factory token`    — token diagnostics
└── worker.py           # `aig factory worker`   — single run or --watch loop
```

Each per-command module exports `register(parent: typer.Typer) -> None`; `factory_app.py` calls each `register_*(app)` once.

## Critical Rules

1. **One file per command.** Every command/subgroup gets its own module under `cli/`. New commands are added by (a) creating `cli/<name>.py` with `register()`, then (b) appending one `register_<name>(app)` call in `cli/factory_app.py`.
2. **`# pyright: reportUnusedFunction=false` at the top of every command module.** Typer's `@app.command` decorations make the nested functions look unused.
3. **`cli/__init__.py` only re-exports `app`** from `factory_app` — no logic.
4. **CLI never wires services.** Always go through `WorkerBuilder().build(settings)` and consume the resulting `Worker`. Never instantiate `Reconciler`/`Planner`/`Dispatcher`/etc. directly in CLI code.
5. **Log handler lives in `factory_app.py`.** The library only attaches `NullHandler` (per stdlib convention); `factory_app._configure` is the single `@app.callback()` that installs the `RichHandler` and wires `--verbose` / `--quiet`. Do not add per-command log configuration.
6. **Signal handling lives in `cli/worker.py`** (only the `--watch` path needs it). The `Watcher` service stays signal-free; the CLI installs SIGINT/SIGTERM handlers, flips a shutdown flag, and passes the flag's getter into `Watcher(should_stop=...)`. Always restore previous handlers in a `finally` block.
7. **Settings load is per-command.** Each command does `FactorySettings.load()` at the top of its handler and surfaces `ValidationError` as `typer.Exit(code=1)`. Never cache settings across commands.
8. **All output uses `Console(stderr=True)`.** Stdout is reserved for machine-readable output (e.g. future `--json` flags); errors and human summaries go through the module-level `_console = Console(stderr=True)`.
9. **Test patches use the full submodule path.** `@patch("aig_spec_kit.factory.cli.worker.WorkerBuilder")` — patching `cli.WorkerBuilder` will not work because the import lives inside the per-command module.

## Command Catalogue

| Command | When to run | Token surface | Network calls |
|---------|-------------|---------------|---------------|
| `aig factory connect` | Once per machine | OAuth client | OAuth device flow + `/user` |
| `aig factory init [--force]` | Once per target repo | install token | bootstrap workflow/trigger/priority labels + 1 contents listing |
| `aig factory token status` | Anytime | reads OAuth store + App config | none |
| `aig factory health` | Anytime | install token | `/installation/repositories` |
| `aig factory inspect locks` | Anytime | none | none (local cache only) |
| `aig factory inspect history` | Anytime | none | none (local cache only) |
| `aig factory inspect pr <issue>` | Anytime | install token | one GraphQL `PR_SIGNALS` round-trip |
| `aig factory worker [--watch] [--interval N]` | Repeated | install token + per-user OAuth | full `RunOrchestrator.execute()` per iteration |

**Onboarding flow** (do these once per target repo, in order):

1. `aig factory connect` — mint the operator's OAuth refresh token.
2. `aig factory init` — bootstrap workflow, trigger, and priority labels + snapshot `.github/agents/*.agent.md` slugs into `.aig/factory.yaml`. After this, `WorkerBuilder.build()` is pure assembly; the runtime hot path makes no GitHub mutations of its own.
3. `aig factory worker --watch` — leave running.

**`init` is the single onboarding seam.** Do not re-introduce label bootstrap or agent discovery into `WorkerBuilder.build()` — those calls cost ~10 GitHub round-trips per CLI invocation and conflate setup with runtime. If a workflow label is missing at runtime, the `LifecycleService` transition raises a typed error that the orchestrator records as a `phase_failed` history event — operators see it via `aig factory inspect history` and re-run `init`.

The proposal's full "Composable flags on `worker`" matrix (`--execute`, `--local`, `--agent`, `--max-concurrent`, `--pr-detect`, `--cancel-stale`, `--limit`, `--repo`) is **deferred** — values come from `.aig/factory.yaml` until a real consumer needs the override. Do not speculatively add flags, and do not reintroduce local-executor flags.

## Quality Gate

```bash
cd /workspaces/ai-garage-copilot && uv run poe check && uv run poe test
uv run aig factory --help        # smoke
uv run aig factory worker --help # smoke
```
