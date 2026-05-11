---
applyTo: "{docs,backlog,templates}/**/*.md, *.md, !site/**"
description: Documentation standards for markdown files (README, guides, proposals)
---

# Documentation Guidelines

Standards for project documentation.

## File Types

| Location | Purpose |
|----------|---------|
| `README.md` | Project overview, quick start |
| `AGENTS.md` | AI agent instructions |
| `docs/` | MkDocs-powered documentation site |
| `docs/getting-started/` | Setup and contributing guides |
| `docs/standards/` | Coding standards (backend, frontend) |
| `docs/guides/` | How-to guides and tutorials |
| `docs/reference/` | Reference docs (glossary, templates) |
| `docs/proposals/` | Design proposals and RFCs |
| `backlog/` | Task tracking (Backlog.md) |

## Structure

1. **Title** — Single `#` heading matching the file purpose
2. **Overview** — 1-2 sentence summary (no heading needed)
3. **Sections** — Use `##` for major sections, `###` for subsections
4. **Code blocks** — Always specify language (```python, ```bash, etc.)

## Writing Style

- **Concise** — Prefer bullet points over paragraphs
- **Actionable** — Lead with verbs ("Run", "Create", "Add")
- **Examples** — Show, don't just tell
- **Tables** — Use for structured data (commands, options, mappings)

## Links

- Use relative paths from file location: `[Dev Setup](getting-started/dev-setup.md)`
- Link to source files: `[cli.py](tools/aig_spec_kit/cli.py)`
- Anchor to headings: `[Quality Gate](#quality-gate)`
- Cross-folder links: `[Contributing](../getting-started/contributing.md)`

## Code Examples

Always include:
- Language identifier
- Realistic, copy-pasteable commands
- Comments for non-obvious steps

```bash
# Install dependencies
uv sync --all-extras --all-groups

# Run quality checks
uv run poe check
```

## Tables

Align columns for readability:

```markdown
| Command     | Purpose              |
|-------------|----------------------|
| `poe check` | Run all quality gates |
| `poe test`  | Run tests with coverage |
```
