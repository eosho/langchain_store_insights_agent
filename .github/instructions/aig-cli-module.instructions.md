---
applyTo: "tools/aig_spec_kit/**/*.py, docs/reference/aig-cli.md"
description: "Use when modifying the aig CLI tool — scaffolding, init commands, tracking, or release downloads"
---

# AIG Spec Kit CLI

CLI tool that downloads and scaffolds AI-native projects from GitHub releases or local sources, with selective component-level updates.

## Architecture

```
tools/aig_spec_kit/
├── __init__.py               # Version only (__version__)
├── cli.py                    # Typer CLI entry point (aig command)
├── components.py             # Component group definitions for update command
├── constants.py              # Shared constants, exclusion matching, git helpers
├── init_cmd.py               # Init orchestrator + UI (banner, marker, success)
├── release_zip.py            # Build release ZIP (reuses EXCLUDE_PATTERNS)
├── update_cmd.py             # Update orchestrator + UI (diff, dry-run, apply)
├── tracking.py               # Agent workspace scaffolding, context health, marker I/O
├── py.typed                  # PEP 561 marker
└── sources/
    ├── __init__.py
    ├── github.py             # GitHub API: fetch releases, download/extract ZIPs
    └── local.py              # Local copy: git-aware directory copy, ZIP extract
```

## Module Responsibilities

| Module | Owns | Does NOT own |
|--------|------|--------------|
| `constants.py` | `MARKER_FILE`, `GITHUB_*`, `ASSET_NAME`, `BANNER`, `EXCLUDE_PATTERNS`, `ProjectType`, `TEMPLATE_DIRS`, `is_excluded()`, `git_tracked_files()` | I/O orchestration |
| `components.py` | `COMPONENT_GROUPS`, `META_CONTEXT`, `META_ALL`, `resolve_components()`, `get_prefixes()` | File I/O, UI output |
| `sources/github.py` | GitHub token, release fetch, ZIP download/extract, VS Code open | UI output, orchestration |
| `sources/local.py` | Git-aware copy, directory copy | GitHub API, UI output, matching logic |
| `release_zip.py` | `create_release_zip()`, CLI entry point (`python -m`) | Source-specific logic |
| `init_cmd.py` | `init_project()` orchestrator, banner, template overlay, success panel | Source-specific logic |
| `update_cmd.py` | `update_project()` orchestrator, file comparison (SHA-256), dry-run, apply actions | Component resolution, marker I/O |
| `cli.py` | Typer app, command definitions, argument parsing | Business logic |
| `tracking.py` | Agent workspace scaffolding, context health, `MarkerInfo`, `read_marker()`, `write_marker()`, `update_marker()` | Init/download/update logic |

## Critical Rules

1. **Constants live in `constants.py`** — never duplicate URLs, patterns, or the banner
2. **Exclusion matching lives in `constants.py`** — `is_excluded()` and `_matches()` are the single source of truth; `sources/local.py`, `sources/github.py`, and `release_zip.py` all import from here
3. **Sources are pure logic** — no Rich console output in `sources/`; UI stays in orchestrators
4. **`init_cmd.py` and `update_cmd.py` are thin orchestrators** — delegate to `sources.github` or `sources.local`
5. **Marker I/O lives in `tracking.py`** — `write_marker()` is the single serialisation point; `init_cmd._write_marker()` is a thin wrapper that adds init-specific defaults
6. **Component resolution lives in `components.py`** — CLI flags map to directory prefixes via `COMPONENT_GROUPS`
7. **Git-aware copy by default** — `copy_directory()` uses `git ls-files` when available
8. **`EXCLUDE_PATTERNS`** — single source of truth for release ZIP, `aig init --local`, and `aig update`
9. **`release_zip.py`** — builds the release ZIP using `git_tracked_files()` + `is_excluded()` from `constants.py`; invoked via `uv run poe release-zip` in CI
10. **`# noqa: S310`** — required on `urlopen` calls in `sources/github.py`
11. **`ProjectType` enum** — `backend`, `frontend`, `fullstack` (default)
12. **Template overlay** — copies from `templates/<type>/` after shared files, replacing `{{project_name}}`/`{{description}}`

## Adding Features

1. **New CLI command**: Add `@app.command()` in `cli.py`, orchestrator in a `*_cmd.py` module
2. **New exclusion**: Add pattern to `EXCLUDE_PATTERNS` in `constants.py` (applies everywhere: release ZIP, init, update)
3. **New source type**: Create `sources/<name>.py`, wire into orchestrators
4. **New agent**: Add entry to `AGENT_ARTIFACTS` in `tracking.py`
5. **New component group**: Add entry to `COMPONENT_GROUPS` in `components.py` and `META_ALL`/`META_CONTEXT` as appropriate
6. **Any CLI change**: Update `docs/reference/aig-cli.md`

## Test Conventions

- Tests split across `tools/test_cli.py` (CLI + init), `tools/test_tracking.py` (tracking), `tools/test_update.py` (update + components + marker helpers)
- Patch at import site: `@patch("aig_spec_kit.init_cmd.fetch_release_info")`
- Exception: patch `sources.local.get_git_tracked_files` directly when testing git detection
- Private imports in tests use `# noqa: PLC2701`
