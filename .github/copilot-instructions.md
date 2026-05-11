# Copilot Instructions

Trust these instructions first; only search if information is incomplete or incorrect.

## Agents

See [AGENTS.md](../AGENTS.md) for agent definitions, skills, and workspaces.

## Project Rules

1. **Type-safe**: Type hints (Python) or strict TypeScript — no `any`
2. **Schema validation**: Pydantic (Python) or Zod (TypeScript) for I/O boundaries
3. **Async-first**: Use `async def` / `async function` for I/O operations
4. **Quality gates**: Must pass before commit (`uv run poe check` / `pnpm check`)
5. **Conventional Commits**: `type(scope): description`

## Project Layouts

### Package (CLI/Library)

```
src/
├── models/          # Data models
├── services/        # Business logic
├── cli/             # CLI entry points
└── lib/             # Shared utilities
tests/
├── unit/
├── integration/
└── contract/        # API contract tests
```

### Full-Stack (Monorepo)

```
backend/
├── src/
│   ├── api/         # Routes/endpoints
│   ├── models/      # Data models
│   └── services/    # Business logic
└── tests/
frontend/
├── src/
│   ├── features/    # Feature modules
│   ├── shared/      # Shared components
│   └── app/         # App shell/routing
└── tests/
docs/                # Documentation
```

See [Coding Standards](../docs/standards/) for detailed internal structure.

## Path-Specific Instructions

Auto-applied based on file patterns:

| File Pattern | Instructions | Purpose |
|-------------|--------------|---------|
| `**/*.py` | [backend-dev.instructions.md](instructions/backend-dev.instructions.md) | Python conventions, async patterns, anti-slop rules |
| `**/test_*.py` | [tests-backend.instructions.md](instructions/tests-backend.instructions.md) | Pytest patterns, fixtures, mocking conventions |
| `{docs,backlog,templates}/**/*.md`, `*.md` | [markdown.instructions.md](instructions/markdown.instructions.md) | Documentation standards, formatting rules |
| `**/*.{ts,tsx,js,jsx}` | [frontend-dev.instructions.md](instructions/frontend-dev.instructions.md) | TypeScript/React conventions, component patterns |
| `**/*.test.{ts,tsx}` | [tests-frontend.instructions.md](instructions/tests-frontend.instructions.md) | Vitest patterns, React Testing Library conventions |
| `tools/aig_spec_kit/**/*.py` | [aig-cli-module.instructions.md](instructions/aig-cli-module.instructions.md) | Outer `aig` CLI scaffolding/init/update commands |
| `tools/aig_spec_kit/factory/**/*.py` | [factory-module.instructions.md](instructions/factory-module.instructions.md) | AIG Factory v2 layering, module placement, errors |
| `tools/aig_spec_kit/factory/cli/**/*.py` | [factory-cli.instructions.md](instructions/factory-cli.instructions.md) | `aig factory` Typer surface — register pattern, signal handling, log config |
| Factory runtime services (orchestrator/watcher/history/...) | [factory-runtime.instructions.md](instructions/factory-runtime.instructions.md) | RunOrchestrator phases, run_id propagation, watcher loop, history-as-source-of-truth |
| `tools/harness/**/*.py` | [harness.instructions.md](instructions/harness.instructions.md) | Test harness for evaluating agents/skills |

## Context-Triggered Instructions

| Topic | Instructions | Purpose |
|-------|--------------|---------|
| Backlog tracking | [backlog.instructions.md](instructions/backlog.instructions.md) | Task management via Backlog.md CLI |
| Git conventions | [git.instructions.md](instructions/git.instructions.md) | Conventional commits, branching, PR guidelines |

## Key References

| Document | Purpose |
|----------|---------|
| [Coding Standards](../docs/standards/) | Code style, anti-slop rules |
| [Dev Setup](../docs/getting-started/dev-setup.md) | Commands, environment setup |
| [AGENTS.md](../AGENTS.md) | Agent quick reference |

## Task Tracking

This project uses **Backlog.md** for git-native issue tracking. See [AGENTS.md](../AGENTS.md) for commands.
