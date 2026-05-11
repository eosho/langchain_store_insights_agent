---
description: "Scaffold a new project from the local repo using aig init --local"
argument-hint: "project type: backend, frontend, or fullstack"
---

# Initialize Project from Local Source

Scaffold a new AI-native project by copying template files from this repository using `aig init --local`.

## What This Does

Runs `aig init` with `--local` pointing at the current workspace, which:

1. Copies git-tracked files filtered through `EXCLUDE_PATTERNS` in `constants.py`
2. Applies a type-specific template overlay (`backend`, `frontend`, or `fullstack`)
3. Replaces `{{project_name}}` and `{{description}}` placeholders in template files
4. Writes an `.aig-initialized` marker file (includes `type:` field)
5. Produces a clean project scaffold matching what `uv run poe release-zip` generates

## Usage

```bash
# Initialize a fullstack project (default)
aig init <target-path> --local . --no-open

# Backend-only (Python)
aig init <target-path> --local . --type backend --no-open

# Frontend-only (TypeScript)
aig init <target-path> --local . --type frontend --no-open

# With a custom project name
aig init <target-path> --local . --name my-project --no-open

# Force reinitialize (overwrite existing)
aig init <target-path> --local . --force --no-open
```

### Flags

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--type` | `-t` | `fullstack` | Project type: `backend`, `frontend`, or `fullstack` |
| `--name` | `-n` | directory name | Project name for placeholder replacement |
| `--force` | `-f` | `false` | Overwrite existing files |
| `--open/--no-open` | `-o` | `--open` | Open in VS Code after init |
| `--local` | `-l` | — | Local source path (directory or ZIP) |

## Prompt

Ask the user:

1. **What type** of project? (`backend`, `frontend`, or `fullstack` — default: `fullstack`)
2. **What name** for the project? (optional — defaults to `local_<type>`)

Scaffold into the user's **home directory** — never `/tmp/`:

```bash
aig init ~/local_{{type}} --local /workspaces/ai-garage-copilot --type {{type}} --name {{project-name}} --no-open
```

> **WARNING**: Never open the scaffolded folder in this VS Code window. It will replace the dev container workspace and crash the container. Use `--no-open` (already the default) and tell the user to open it in a **new VS Code window** if they want to explore it.

After success, show the file count and suggest next steps:
- Open the project: `code {{target-path}}`
- Reopen in Dev Container
- Run `aig tracking-init` to scaffold agent workspaces
