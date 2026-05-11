---
name: test-driven-development
description: Test-Driven Development (TDD) workflow for AI agents. Use when writing tests before implementation, following Red-Green-Refactor cycle, or when task depends on a design document. Triggers on TDD mode, failing tests, test scenarios, red-green-refactor, or "write tests first" requests.
argument-hint: 'Name the feature or module to test-drive'
---

# Test-Driven Development (TDD)

TDD inverts the traditional workflow: **tests are written BEFORE implementation**.

## When to Use TDD

| Use TDD When                       | Use Traditional When                    |
| ---------------------------------- | --------------------------------------- |
| New features with clear design     | Bug fixes (reproduce first)             |
| Task depends on design document    | Spikes/prototypes (exploring)           |
| Test Scenarios exist in design doc | Unclear requirements                    |
| Fresh implementation needed        | Legacy code without design              |

## Workflow

```
Planner (Design + Test Scenarios)
    ↓
Builder (Write FAILING tests → Make tests PASS → Refactor)
    ↓
Reviewer (Code review + security)
```

## Mode Detection

### Detecting TDD Mode

```bash
backlog task view <task-id>  # Check deps field
```

| Dependency Task Starts With        | Mode        | Expected Test State |
| ---------------------------------- | ----------- | ------------------- |
| `"Design:"` or `"Plan:"`            | **TDD**     | Tests MUST FAIL     |
| `"Implement:"` or `"Create:"`       | Traditional | Tests MUST PASS     |

### Check Existing Test State

```bash
uv run poe test  # Run tests first
```

| Test Result          | Mode        | Your Goal            |
| -------------------- | ----------- | -------------------- |
| Tests exist and FAIL | **TDD**     | Make tests pass      |
| No relevant tests    | Traditional | Implement → Write tests |

## Builder TDD Process

### Phase 1: Write Failing Tests (RED)

1. **Claim Task** - `backlog task edit <id> -s "In Progress"`
2. **Read Design** - Find **Test Scenarios** section in design doc
3. **Map Scenarios** - Each scenario → one test function
4. **Write Tests** - Follow existing patterns (implementation doesn't exist yet)
5. **Verify Failure** - `uv run poe test` — tests MUST FAIL with meaningful errors

**Required:** Tests must fail with clear error messages explaining expected behavior.

### Phase 2: Make Tests Pass (GREEN)

1. **Run Tests** - `uv run poe test` to see failures
2. **Read Assertions** - Understand expected behavior from test code
3. **Implement** - Write minimal code to make tests pass
4. **Verify Green** - `uv run poe test` — ALL tests MUST PASS
5. **Quality Checks** - `uv run poe check`
6. **Complete** - `backlog task edit <id> -s "Done"`

**Goal:** Make the red tests green. Nothing more.

## Design Document Test Scenarios

Planner creates design docs with this section:

```markdown
## Test Scenarios

| ID | Scenario | Input | Expected Output | Type |
|----|----------|-------|-----------------|------|
| T1 | Happy path | valid_input | success | Unit |
| T2 | Edge case | empty_string | ValidationError | Unit |
| T3 | Error handling | None | raises ValueError | Unit |
| T4 | Integration | realistic_data | full_workflow | Integration |
```

Test function names should match scenario IDs:

```python
def test_t1_happy_path(self) -> None: ...
def test_t2_empty_string_edge_case(self) -> None: ...
def test_t3_none_raises_value_error(self) -> None: ...
```

## Task Dependencies (Backlog.md)

### TDD Workflow

```bash
# Design task (Planner)
backlog task create "Design: auth module" -a @planner

# Test task depends on DESIGN (not implementation)
backlog task create "Tests: auth module" -a @builder \
  --dep <design-task-id>

# Implementation depends on TESTS
backlog task create "Implement: auth module" -a @builder \
  --dep <test-task-id>
```

### Traditional Workflow

```bash
# Implementation depends on design
backlog task create "Implement: bug fix" -a @builder \
  --dep <design-task-id>

# Tests depend on IMPLEMENTATION
backlog task create "Tests: bug fix" -a @builder \
  --dep <impl-task-id>
```

## Red-Green-Refactor Cycle

1. **RED** — Write a failing test
2. **GREEN** — Write minimal code to pass the test
3. **REFACTOR** — Clean up while keeping tests green

```python
# RED: Write failing test
def test_password_requires_digit(self) -> None:
    assert validate_password("abcdefghij") is False

# GREEN: Minimal implementation
def validate_password(password: str) -> bool:
    return any(c.isdigit() for c in password) and len(password) >= 8

# REFACTOR: Clean up if needed (tests still pass)
```

## Quality Gates

### Builder (TDD Mode — RED Phase)

- [ ] All Test Scenarios from design doc covered
- [ ] Tests FAIL with meaningful error messages
- [ ] Test names match scenario IDs
- [ ] Tests are independent (no shared state)

### Builder (TDD Mode — GREEN Phase)

- [ ] All tests pass (`uv run poe test`)
- [ ] No tests skipped or disabled
- [ ] Quality checks pass (`uv run poe check`)
- [ ] Implementation matches design doc

## Reference Documents

- [Acceptance criteria](references/acceptance-criteria.md) — Required patterns, forbidden patterns, quality gates, and checklist
