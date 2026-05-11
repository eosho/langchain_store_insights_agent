---
applyTo: "tools/aig_spec_kit/factory/services/run_orchestrator.py, tools/aig_spec_kit/factory/services/watcher.py, tools/aig_spec_kit/factory/services/history.py, tools/aig_spec_kit/factory/services/reconciliation.py, tools/aig_spec_kit/factory/services/planning.py, tools/aig_spec_kit/factory/services/dispatching.py, tools/tests/factory/test_run_orchestrator.py, tools/tests/factory/test_run_soak.py, tools/tests/factory/test_services_watcher.py"
description: "Use when modifying the factory runtime loop — `RunOrchestrator`, `Watcher`, history events, per-phase orchestration, run_id propagation"
---

# AIG Factory Runtime Loop

The factory's runtime is a single idempotent **run** (`RunOrchestrator.execute()` → `RunReport`). A long-running operator wraps that with the **watcher** loop (`Watcher.watch()`) which re-invokes `Worker.run()` every `--interval` seconds until SIGINT/SIGTERM.

**Companion instructions:** [factory-module.instructions.md](./factory-module.instructions.md), [factory-cli.instructions.md](./factory-cli.instructions.md).

## The Six Phases

`RunOrchestrator.execute()` runs `RunPhase` in fixed order:

1. **HEALTH** — install-token validity probe via `GET /installation/repositories`.
2. **RECONCILE** — for every issue carrying a `factory:running` / `factory:pr-open` / `factory:queued` label, snapshot → decide → apply.
3. **PLAN** — every `factory:run` issue gets a `Plan` (saved to `.copilot-tracking/factory/runs/issue-N/plan.json`), a planning comment posted, and the label flipped to `factory:queued`.
4. **DISPATCH** — slot-fill: pick `factory:queued` issues that fit the dispatch cap, acquire the atomic git-ref lock, transition to `factory:running`, then `CloudExecutor` calls `operations.assign_copilot()` with a per-user OAuth `GhClient`.
5. **HOUSEKEEP** — `LockManager.evict_orphans()` drops cached leases that no longer have a matching ref.
6. **LOG** — append the aggregate `RunReport` row.

Each phase delegates to a private `_run_<phase>_phase` method so `execute()` reads top-to-bottom as the spec.

## Critical Rules

1. **Fresh `run_id` per `execute()`.** The first line of `execute()` is `self._history.run_id = new_run_id()`. This is load-bearing for the watcher: a single `Worker` instance is reused across every iteration, so without this every event would carry the same ULID. Tests assert `report1.run_id != report2.run_id` for back-to-back calls.
2. **Phase failures never abort the run.** `_safe_phase` / `_safe_phase_with_counters` catch `FactoryError`, log a `phase_failed` history event, and return. Subsequent phases still execute. Watcher relies on this to survive transient GitHub blips.
3. **REST `?labels=A,B,C` is AND.** `_run_reconcile_phase` scans each workflow label separately and dedupes by issue number. Do not collapse the loop back into one call — silently misses issues that carry only one of the labels.
4. **`HistoryRecorder` is the single writer to `.copilot-tracking/factory/runs/history.jsonl`.** Every state mutation, every dispatch attempt, every reconcile decision (including no-ops) records one event. Operators read via `aig factory inspect history`. There is no parallel markdown log; the JSONL is the source of truth.
5. **Reconciler records noops too.** `Reconciler.reconcile()` writes a `reconciled` event with `payload={workflow_state, action: "noop"|"transition", reason}` for every scanned issue. This makes `inspect history | grep #N` a complete per-issue replay even when the issue is in steady state.
6. **`LifecycleService` is the only mutator of `factory:*` workflow labels.** Reconciler and planner never call `gh.add_label` directly — they go through `lifecycle.transition()` so the history event + handoff comment + sticky-terminal guard all fire in one place.
7. **`Plan.summary` keeps the issue body verbatim** because the cloud dispatch prompt should preserve the issue request. The GitHub planning comment is a compact 4-line header rendered inline in `Planner.plan()` — do not echo `plan.summary` into the comment.
8. **`PlanStore` writes `plan.json` only.** `planning.md` and `execution.md` were removed (zero readers; the JSONL had the same data). Do not reintroduce per-issue markdown files.
9. **No dispatch facade.** `DispatchClient` was removed as a one-method wrapper. Keep Copilot assignment in `github/operations.py` and call it from `CloudExecutor` with a user-token `GhClient`.

## Watcher Semantics

- **Pure loop driver.** `services/watcher.py::Watcher` takes a `run_once: Callable[[], RunReport]`, a `should_stop: Callable[[], bool]`, an `interval_seconds: int`, and an injectable `sleep`. Zero signal coupling — that lives in `cli/worker.py`.
- **`WorkerBuilder.build()` runs once per CLI invocation.** The assembled `Worker` is reused across every watcher iteration, so install-token cache + service graph live for the lifetime of the process. Do not rebuild per iteration.
- **`FactoryError` inside one run is logged but does NOT stop the loop.** Anything else (KeyboardInterrupt / SystemExit / unhandled bug) propagates. The watcher counts `runs_completed` vs `runs_failed` in its returned `WatcherSummary`.
- **`--interval` is floored at `DEFAULT_POLL_INTERVAL_MIN_SECONDS` (10s)** in `Watcher.__init__`. This is a real safety belt, not a bug — operators have hit GitHub rate limits with `--interval 1`.
- **SIGINT/SIGTERM is graceful**: the current run finishes, then exit. A second SIGINT reverts the handler to `SIG_DFL` so a stuck run can still be killed forcibly.

## Test Conventions

- **Orchestrator tests** mock the `GitHubClient` + `Reconciler` + `Planner` + `Dispatcher` + `LockManager` seams; the real services aren't exercised here. Use the `_Fixtures` bundle dataclass to keep parameter lists short (PLR0913).
- **Reconcile-scan side effects need 5 entries** (3 reconcile labels + plan + dispatch). When a test sets `gh.list_issues_by_label.side_effect = [...]`, count carefully — `StopIteration` is the failure mode.
- **Soak tests live in `test_run_soak.py`**, marked `@pytest.mark.slow`. They run 100 consecutive `execute()` calls in <2s using mocked seams; assert (a) every run completes, (b) every event carries the correct run_id, (c) the JSONL grows monotonically.
- **Watcher tests use injected `sleep` + `should_stop`** to make the loop deterministic. Never let a test actually sleep or rely on wall-clock time.

## Quality Gate

```bash
cd /workspaces/ai-garage-copilot && uv run poe check && uv run poe test
```

Both must pass before marking any runtime-loop change as Done.
