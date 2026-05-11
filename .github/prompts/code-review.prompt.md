---
agent: Reviewer
description: "Code review with security audit — run on changed files or a specific PR before merging"
argument-hint: "file path, PR number, or 'all changes'"
---

# Code Review

Review the specified code for quality, security, and architecture compliance in a single pass.

## Scope

Determine what to review from the argument provided:

- **File path(s)**: Review those files only
- **PR number**: Fetch changed files from the PR and review them
- **"all changes"** (or no argument): Use `git diff main...HEAD --name-only` to find all changed files on this branch

## Process

1. **Gather context** — Read design docs, ADRs, and builder change logs from `.copilot-tracking/` if they exist. Use `@Explore` for unfamiliar modules.
2. **Quality review** — Type safety, error handling, naming, patterns. Check against [coding standards](../../docs/standards/).
3. **Security scan** — OWASP Top 10 baseline: injection, auth, secrets, data exposure.
4. **Architecture check** — Verify implementation matches design docs and ADRs if present.
5. **Output** — Save the review document to `.copilot-tracking/agents/reviewer/reviews/` using the [review template](../../templates/outputs/reviewer-review-template.md).

## Output Structure

The review document must contain:

- **Summary**: Approve / Request Changes / Needs Discussion
- **Must Fix**: Blocking issues with file, line, problem, and suggested fix
- **Security Findings**: OWASP category, severity, remediation
- **Nice to Have**: Non-blocking suggestions
- **Positive Highlights**: Good patterns worth calling out
