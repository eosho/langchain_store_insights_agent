---
applyTo: "**/test_*.py"
description: Backend test patterns, fixtures, and pytest conventions for unit and integration testing
---

# Backend Testing Guidelines

## Structure

```
tests/
  unit/           # Fast, isolated tests (no I/O, no network)
  integration/    # Tests that cross module or service boundaries
```

Run tests with `uv run poe test` (includes coverage)

## Non-Negotiable Rules

1. **No `@pytest.mark.asyncio`** — `asyncio_mode = "auto"` is set globally; just use `async def test_*()`
2. **Copyright header** on every test file: `# Copyright (c) Microsoft. All rights reserved.`
3. **`AsyncMock` for async callables**, `MagicMock` for sync
4. **All warnings are errors** — do not suppress warnings unless you explicitly know why
5. **Type hints on all test helpers and fixtures** — same as production code

## File & Naming Conventions

- Files: `test_<module>.py` (e.g., `test_cli.py`, `test_init_cmd.py`)
- Classes: `Test<Subject>` (e.g., `TestVersionCommand`, `TestCheckCanInitialize`)
- Functions: `test_<behaviour>` — describe the expected outcome, not the implementation
  - Good: `test_returns_error_when_already_initialized`
  - Bad: `test_check_can_initialize_1`

## Pytest Markers

Use markers to classify tests. Declare them in `pyproject.toml` under `[tool.pytest.ini_options]`.

```python
@pytest.mark.slow          # Long-running (deselect with -m "not slow")
@pytest.mark.integration   # Crosses module/service boundary
@pytest.mark.unit          # Pure unit test (default assumption)
```

Use `@pytest.mark.parametrize` for data-driven variants instead of copy-paste test bodies:

```python
@pytest.mark.parametrize("bad_input,expected_error", [
    ("", ValueError),
    (None, TypeError),
])
def test_raises_on_invalid_input(bad_input: str | None, expected_error: type[Exception]) -> None:
    with pytest.raises(expected_error):
        parse(bad_input)
```

## Fixtures

- Define shared fixtures in `conftest.py` at the appropriate scope (`tests/` or `tests/unit/`)
- Prefer function-scoped fixtures (`scope="function"`) unless sharing is explicitly needed
- Use `tmp_path` (built-in) for temporary directories — never hardcode paths

```python
@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    """Create a minimal project directory for testing."""
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
    return tmp_path
```

## Async Tests

```python
# CORRECT — no decorator needed
async def test_fetches_data(mock_client: AsyncMock) -> None:
    result = await fetch_data(mock_client)
    assert result is not None

# WRONG — do not add this decorator
@pytest.mark.asyncio
async def test_fetches_data() -> None: ...
```

### Async Fakes and Side-Effects

Only use `async def` when the function body actually `await`s. Test fakes that just set
attributes or return values must be regular `def` — Ruff `RUF029` enforces this.

```python
# ✅ CORRECT: No await needed → regular def
def _fake_refresh(record: object) -> None:
    record.id = 1  # type: ignore[attr-defined]

mock_db.refresh = MagicMock(side_effect=_fake_refresh)

# ❌ WRONG: async without await triggers RUF029
async def _fake_refresh(record: object) -> None:
    record.id = 1  # type: ignore[attr-defined]
```

When a fake genuinely needs to `await`, use `async def` and `AsyncMock`:

```python
# ✅ CORRECT: Fake that actually awaits
async def _fake_fetch(url: str) -> bytes:
    await asyncio.sleep(0)  # yields to event loop
    return b"data"
```

## Mocking

```python
from unittest.mock import AsyncMock, MagicMock, patch

# Patch at the point of use, not the point of definition
with patch("aig_spec_kit.init_cmd.shutil.copytree") as mock_copy:
    mock_copy.return_value = None
    ...

# Async mock
mock_client = AsyncMock()
mock_client.get_auth_status.return_value = MagicMock(isAuthenticated=True)
```

**Stacked `@patch` decorators** — arguments are passed bottom-up (bottom decorator -> first argument):

```python
@patch("module.second_thing")   # -> second argument
@patch("module.first_thing")    # -> first argument
def test_something(mock_first: MagicMock, mock_second: MagicMock) -> None: ...
```

**Assertion tightness** — prefer `assert_called_once_with(expected_arg)` over `assert_called_once()` when you know the arguments; it catches silent regressions where the call signature changes.

## Assertions

Prefer pytest-style assertions — they produce clearer failure output and require less boilerplate.

| Instead of | Use |
| --- | --- |
| `self.assertTrue(a == b)` | `assert a == b` (pytest rewrites asserts for detailed diffs) |
| `self.assertTrue(x)` | `assert x` |
| `self.assertTrue(isinstance(x, Foo))` | `assert isinstance(x, Foo)` |
| `self.assertEqual(a, b)` | `assert a == b` (pytest shows rich comparison output automatically) |

Check exception **messages** with `pytest.raises(match=...)`:

```python
with pytest.raises(ValueError, match="already initialized"):
    init_project(existing_dir)
```

## Skipping Tests

Skip conditionally rather than commenting out:

```python
@pytest.mark.skip(reason="upstream bug, tracked in bd-42")
def test_something() -> None: ...

@pytest.mark.skipif(sys.platform == "win32", reason="POSIX only")
def test_symlink_creation() -> None: ...
```

## Test Independence

Each test must be **fully self-contained**, meaning it must pass when run in isolation or in any arbitrary order. Never share mutable state between tests via module-level variables or class attributes. Use fixtures for shared setup.

## What to Test

| Layer | Test focus |
| --- | --- |
| `src/` public API | Behaviour (inputs -> outputs), error paths, edge cases |
| CLI commands | Exit codes, stdout content, side effects via mocks |
| Utilities / helpers | Pure logic, no I/O — test exhaustively |
| Integration | Real filesystem (`tmp_path`), real subprocess calls — mark `@pytest.mark.integration` |

## What NOT to Test

- Private implementation details (functions prefixed `_`) — test through the public API instead
  - Exception: when a private helper has complex logic worth isolating
- Third-party library internals
- Log output (unless it is part of the public contract)
