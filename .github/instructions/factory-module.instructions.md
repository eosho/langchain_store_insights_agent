---
applyTo: "tools/aig_spec_kit/factory/**/*.py, tools/tests/test_layering.py, tools/tests/factory/**/*.py"
description: "Use when modifying the AIG Software Factory v2 package — layering rules, module placement, error hierarchy, and the import-direction guard"
---

# AIG Factory (v2)

Strict layered Python package that mediates an operator, GitHub, and the Copilot Coding Agent. The whole package lives at `tools/aig_spec_kit/factory/` and is enforced by the AST guard at `tools/tests/test_layering.py`.

**Reference:**
- Design: [.copilot-tracking/agents/planner/plans/20260510-aig-factory-design.md](../../.copilot-tracking/agents/planner/plans/20260510-aig-factory-design.md)
- ADR-001 layering: [.copilot-tracking/agents/planner/adrs/20260510-001-layered-modular-architecture.md](../../.copilot-tracking/agents/planner/adrs/20260510-001-layered-modular-architecture.md)
- Source proposal: [docs/proposals/aig-software-factory-v2.md](../../docs/proposals/aig-software-factory-v2.md)
- CLI surface: see [factory-cli.instructions.md](./factory-cli.instructions.md)
- Runtime loop: see [factory-runtime.instructions.md](./factory-runtime.instructions.md)

## Layering (enforced by `tools/tests/test_layering.py`)

```
foundation → models → transport → tokens → github → services → worker → cli
```

A module in layer *N* may only import from layers *0..N*. The guard parses every file in `factory/` via `ast.parse` and fails CI on any backward import. It also enforces:

- Every module with public symbols declares `__all__` (PEP 8).
- Cross-module imports only reference names listed in the target's `__all__`.

**Note:** `cli` is the topmost layer (it imports `WorkerBuilder`); `worker.py` is the assembly point that wires every layer below it.

## Critical Rules

1. **Constants vs config.** Workflow labels, lock-ref namespace, defaults, and the logger root live in `constants.py`. Env-var names live in `config.py` — nothing outside `config.py` references them; callers read settings.
2. **`__init__.py` is re-exports only** (RUF067). `factory/__init__.py` is the public facade; subpackage `__init__.py` files exist only to mark namespaces.
3. **`__all__` is mandatory and alphabetised** (ruff RUF022). Section grouping goes in module docstrings, not in the `__all__` list.
4. **No relative imports** anywhere in `factory/` — always `from aig_spec_kit.factory...`. The layering guard fails on relative imports outright.
5. **Errors are flat under `TransientError` / `PermanentError`.** Every raise picks one of the typed leaf subclasses in `errors.py`. Services never inspect HTTP status codes; transport raises the typed subclass. Do NOT add synthetic intermediate parents (e.g. `ConfigError`) — those were removed when they had only one consumer.
6. **`SecretStr` for every credential.** App PEM path is a `Path` (not the bytes); OAuth client secret + tokens are `SecretStr`. Tokens never appear in logs or string-format output.
7. **Dispatch tokens come only from the OAuth store** — written by `aig factory connect` (device flow). There is no env-var path and no PAT path; the OAuth store is the only source per ADR-003.
8. **Cloud-only dispatch.** There is no local executor mode, no `ExecutorKind`, and no `services/execution/` package. "Local" in this package means disk cache/history/leases only.
9. **GitHub boundary.** `transport.GhClient` is raw `gh api` subprocess transport. `github.GitHubClient` is the install-token repo facade. Do NOT add `DispatchClient`; Copilot assignment uses `operations.assign_copilot()` directly with a per-user OAuth `GhClient` because install tokens get HTTP 403.
10. **Concrete token providers.** `InstallTokenProvider` and `OAuthTokenProvider` have different call contracts. Do NOT add a shared `TokenProvider` Protocol unless a production consumer truly needs provider-agnostic dispatch.
11. **`WorkerBuilder` is the only assembly point.** CLI and tests both consume the resulting `Worker`. Nothing else wires services.
12. **`get_logger(name)` is the only logger factory** — never `logging.getLogger(__name__)` outside `factory/logging.py`. The library attaches a `NullHandler`; the CLI attaches a `RichHandler`. Each service does `self._log = get_logger(f"services.{type(self).__name__.lower()}")`.
13. **`HistoryRecorder` is the only writer to `.copilot-tracking/factory/runs/history.jsonl`.** Services emit events via `self._history.record(...)`; the file is the single source of truth for the per-issue audit trail. Do NOT introduce parallel markdown logs (`planning.md`/`execution.md` were removed for this reason).
14. **Keep single-owner helpers in the owner module.** `PlanStore` lives in `services/planning.py`, `PRDetector` lives in `services/pr_signals.py`, and `CloudExecutor` lives in `services/dispatching.py`. Do not recreate one-class wrapper modules such as `services/plans.py`, `services/pr_detection.py`, or `services/execution/cloud.py`.

## Adding Layers / Modules

| Adding... | Where it goes | Layer it imports from |
|-----------|---------------|------------------------|
| New constant | `factory/constants.py` (alphabetise `__all__`) | nothing in `factory/` |
| New env-driven setting | `factory/config.py` (extend an existing `*Settings` or add a new one composed into `FactorySettings`) | `errors.py` only |
| New typed error | `factory/errors.py` directly under `TransientError` or `PermanentError` (no synthetic parents) | nothing |
| New Pydantic model | `factory/models/<domain>.py` (4 domains: `auth`, `lifecycle`, `work`, `observability`) | foundation only |
| New `gh` call surface | `factory/transport/gh.py` (or new `transport/<x>.py`) | foundation + models |
| New token flow/provider | `factory/tokens/<name>.py` (only add a shared Protocol after a production consumer needs provider-agnostic dispatch) | foundation + models + transport |
| New GraphQL query | `factory/github/queries.py` as a `Final[str]` constant; never inline in `operations.py` | nothing |
| New GitHub primitive | `factory/github/operations.py` (flat function taking `GhClient`); add a `GitHubClient` method only for install-token repo operations | foundation + models + transport |
| New workflow service | `factory/services/<name>.py`; register the submodule in `services/__init__.py` `__all__` | foundation + models + tokens + github |
| Cloud dispatch behavior | `factory/services/dispatching.py` | foundation + models + tokens + github |
| New CLI command | `factory/cli/<command>.py` with `register(parent: typer.Typer)` + register call in `cli/factory_app.py` | services + worker |

## GitHub API gotchas (verified empirically)

- **`Repository.suggestedActors.loginNames` is `[String!]`, not a substring filter.** Passing a single string returns `{nodes: []}` silently. Omit the arg and filter `node.login.startswith(...)` in Python. See `factory/github/operations.py::get_copilot_actor_id`.
- **REST `GET /repos/.../issues?labels=A,B,C` is AND**, not OR. To scan multiple workflow labels, call once per label and dedupe — see `RunOrchestrator._run_reconcile_phase`.
- **`gh api -F` cannot encode arrays or nested objects.** Always use `body_json=...` on `GhClient.rest()` — internally it pipes JSON via `--input -`. Same constraint applies to GraphQL variables: `GhClient.graphql()` always uses `--input -`.
- **Install tokens get HTTP 403 on `/user` and on `replaceActorsForAssignable`.** Use `/installation/repositories` for health probes. Use a per-user OAuth token for Copilot dispatch.
- **Copilot login string lives in `constants.COPILOT_LOGIN_PREFIX`.** Use that constant for suggested-actor prefix matching and stock-Copilot log/comment text.

## Quality Gate

```bash
cd /workspaces/ai-garage-copilot && uv run poe check && uv run poe test
```

Both must be green before marking any factory task as Done. The layering guard runs in the default test gate.
