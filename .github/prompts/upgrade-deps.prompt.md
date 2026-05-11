---
description: "Check for outdated Python packages and upgrade dependencies via uv"
argument-hint: "package name, or 'all' for everything"
agent: "agent"
---

# Python Dependency Upgrade

Check for outdated dependencies and upgrade them using `uv`.

The user argument specifies what to upgrade:

- `all` — upgrade every dependency
- A package name (e.g. `fastapi`) — upgrade only that package
- Multiple names (e.g. `fastapi pydantic`) — upgrade each listed package

## Workflow

1. **Preview upgrades** (dry-run first, always):

   ```bash
   # All packages
   uv lock --upgrade --dry-run

   # Specific package
   uv lock --upgrade-package <package> --dry-run
   ```

2. **Review the dry-run output:**
   - Flag major version bumps (first digit change) — mention them to the user
   - Note new transitive dependencies being added

3. **Apply the upgrade:**

   ```bash
   # All packages
   uv lock --upgrade

   # Specific packages (repeat flag per package)
   uv lock --upgrade-package fastapi --upgrade-package pydantic
   ```

4. **Sync environment:**

   ```bash
   uv sync --all-extras --all-groups
   ```

5. **Update pyproject.toml lower bounds:**
   - Find all `pyproject.toml` files in the workspace (`find . -name pyproject.toml -not -path '*/site/*' -not -path '*/.venv/*'`)
   - For each file, read the `[dependency-groups]`, `[project.dependencies]`, and `[project.optional-dependencies]` sections
   - For each upgraded package that appears as a direct dependency, bump the `>=` lower bound to match the newly resolved version
   - Do NOT change pinned (`==`) or upper-bounded (`<`) constraints without user approval

6. **Verify:**

   ```bash
   uv run poe check
   ```

## Safety Notes

- **Review major version bumps** — check changelogs for breaking changes
- **Test after upgrade** — `uv run poe check` must pass before finishing
- **Upgrade incrementally** — for large version jumps, upgrade one package at a time
- **Pin if needed** — use exact versions (`==1.2.3`) for stability-critical packages
