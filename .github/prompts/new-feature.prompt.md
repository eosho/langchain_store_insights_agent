---
agent: Builder
description: "Implement a new feature end-to-end — from requirements through tested, quality-gated code"
argument-hint: "feature description or backlog task ID"
---

# New Feature

Implement the requested feature end-to-end.

## Input

Use the argument to determine what to build:

- **Feature description**: Clarify scope, then implement
- **Backlog task ID**: Read the task (`backlog task <id> --plain`) for requirements and acceptance criteria

## Process

1. **Understand** — Identify what the feature does, who it's for, and where it lives (backend/frontend/both). Use `@Explore` to find similar patterns in the codebase.
2. **Plan** — Break down into steps. If a backlog task exists, add the plan (`backlog task edit <id> --plan "..."`). Share the plan and wait for approval.
3. **Implement** — Follow [coding standards](../../docs/standards/) and existing patterns. Scaffold files using project layout conventions.
4. **Test** — Write unit tests (pytest/vitest) covering acceptance criteria and edge cases.
5. **Verify** — Run `uv run poe check` (backend) or `pnpm check` (frontend).
6. **Document** — Update relevant docs if the feature changes user-facing behavior.

## Constraints

- Follow Conventional Commits for all commits
- One feature per PR — don't bundle unrelated changes
- If a backlog task exists, check off acceptance criteria as you complete them
