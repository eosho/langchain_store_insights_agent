---
description: Python coding conventions, async patterns, and anti-slop rules for backend development
applyTo: "**/*.{py,ipynb}"
---

# Backend (Python)

**Read [Backend Coding Standard](../../docs/standards/backend.md)** — Complete reference for patterns, anti-slop rules, project structure, and examples.

## Quality Gate

```bash
uv run poe check  # MUST pass before committing or marking tasks as Done
```

## Non-Negotiables

1. **Follow the [project structure](../../docs/standards/backend.md#project-structure)** exactly as it applies:
   - `backend/src/` for source code
   - `schemas.py` for Pydantic models (NOT `models.py` at root)
   - `models/` folder for database/domain models
   - `api/v1/` for versioned routes (REQUIRED)
   - `services/` for business logic (no HTTP imports)
   - `config.py` with pydantic-settings

2. **basedpyright strict mode** — Full type hints, no `Any`:
   ```python
   def process(data: dict[str, Any]) -> str:  # ✅
   ```

3. **Async only when awaiting** — Use `async def` only for functions that actually `await` something (I/O calls, `asyncio.sleep`, async iterators). Plain helpers, callbacks, and stubs that perform no async work must be regular `def` (RUF029). Use `httpx`/`aiohttp` for HTTP, never `time.sleep()` or `requests`.

4. **Pydantic at boundaries** — Validate when data enters the system

5. **Layered architecture** — Routes → Services → Repositories (no database calls from routes)

## Skills (Load on Demand)

- **pydantic-py**: Multi-model patterns, validators, discriminated unions
- **fastapi-py**: Routing, auth, dependency injection, database integration

## Commands

| Task | Command |
|------|---------|
| All checks | `uv run poe check` |
| Tests | `uv run poe test` |
| Format | `uv run poe format` |
| Run script | `uv run python ...` |
