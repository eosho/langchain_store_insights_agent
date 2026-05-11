---
description: Bootstrap dev environment in new or existing projects via devsetup.sh
---

# Development Environment Setup

Bootstrap the development environment for the current project using `./devsetup.sh`.

## Prerequisites

The project must be initialized first (`aig init <path> --type backend|frontend|fullstack`).
The script reads `.aig-initialized` to detect project type and adjusts setup accordingly.

## What devsetup.sh Does

1. Validates Python version (3.12, 3.13, 3.14) — backend/fullstack only
2. Installs Python via `uv python install` — backend/fullstack only
3. Creates `.venv` and syncs dependencies (`uv sync --all-extras --all-groups`) — backend/fullstack only
4. Installs frontend dependencies (`pnpm install`) — frontend/fullstack only
5. Configures git hooks (`.githooks/` → `core.hooksPath`)
6. Sets up prek pre-commit hooks
7. Installs Backlog.md task tracker (via npm)
8. Initializes `backlog/` directory with default DoD

## Execution

```bash
chmod +x devsetup.sh
./devsetup.sh          # Python 3.12 (default)
./devsetup.sh 3.13     # Specific Python version
```

## Verify Setup

After completion, verify based on project type:

- **Backend/fullstack**: `uv run poe check`
- **Frontend/fullstack**: `pnpm check`
- **Git hooks**: `git commit --allow-empty -m "test: verify hooks"` (should trigger pre-commit)

## Common Troubleshooting

If setup fails, diagnose with these checks:

| Problem | Cause | Fix |
|---------|-------|-----|
| "No .aig-initialized found" | Project not scaffolded | Run `aig init . --type <type>` first |
| "Invalid Python version" | Unsupported version | Use 3.12, 3.13, or 3.14 |
| uv.lock conflicts on first setup | Stale lock from template | Script auto-removes if no `.venv` exists |
| prek install fails | Non-critical | Hooks still work via `.githooks/` fallback |
| pnpm not found | Node.js missing or no pnpm | `npm i -g pnpm` or install Node.js 20+ |
| Frontend checks skipped | Project type is `backend` | Expected behavior — set `--type fullstack` if both needed |
| Backlog.md install fails | No Node.js | Install Node.js 20+, then `npm i -g backlog.md` |

For deeper issues, check [Dev Setup docs](../../docs/getting-started/dev-setup.md) and [Troubleshooting guide](../../docs/guides/troubleshooting.md).
