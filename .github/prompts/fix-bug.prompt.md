---
agent: Builder
description: "Diagnose and fix a bug — provide error message, file path, or description of the problem"
argument-hint: "error message, file path, or bug description"
---

# Bug Fix

Diagnose and fix the reported bug using a systematic approach.

## Input

Use the argument provided to identify the bug. It may be:

- **Error message or stack trace**: Search the codebase for the origin
- **File path**: Read the file and look for the reported problem
- **Description**: Reproduce or locate the issue from the description

## Process

1. **Reproduce** — Confirm the bug exists. Run the relevant code or tests to see the failure.
2. **Isolate** — Trace to the root cause. Use `@Explore` if the code path is unfamiliar.
3. **Write failing test** — Capture the bug as a test case before fixing.
4. **Fix** — Make the minimal change that resolves the root cause, not just symptoms.
5. **Verify** — Run the failing test (should pass now) and the full test suite.
6. **Quality gate** — Run `uv run poe check` (backend) or `pnpm check` (frontend).

## Constraints

- **Minimal diff**: Fix the bug, don't refactor surrounding code
- **Test first**: Always write or update a test that fails without the fix
- **Root cause**: Address the underlying problem, not just the error message

## Output Artifacts

- Bug fix with regression test
- Root cause explanation
- Commit: `fix(scope): description`
