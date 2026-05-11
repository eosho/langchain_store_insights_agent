---
name: package-inspection
description: "Inspect installed Python or Node.js packages to discover API surfaces, types, events, and methods. Look up latest published versions from PyPI or npm registries. Use when you need to understand an SDK or library before writing code that depends on it, or when you need to pin dependency versions in a design document. Designed for subagent delegation to avoid wasting main-agent context tokens."
argument-hint: "Name the package, its ecosystem (Python or Node), and what API surface to discover"
---

# Package Inspection

Discover API surfaces, types, and methods of installed packages by reading source files from the virtual environment (Python) or node_modules (Node.js/TypeScript). This skill is optimized for **subagent use** — a main agent delegates the research, and the subagent returns a concise summary without bloating the caller's context window.

## When to Use

- You need to understand a package's types, events, classes, or methods
- The official docs are insufficient, outdated, or unavailable
- You're writing code against an SDK and need exact signatures
- You want to discover all enum values, dataclass fields, TypedDict keys, or exported interfaces

## Detect the Ecosystem

Before starting, determine which ecosystem you're inspecting:

| Signal | Ecosystem | Package Location |
|--------|-----------|-----------------|
| `.venv/` exists, `pyproject.toml` | **Python** | `.venv/lib/python3.X/site-packages/<pkg>/` |
| `node_modules/` exists, `package.json` | **Node.js/TypeScript** | `node_modules/<pkg>/` |

---

## Python Workflow

### 1. Locate the Package

```bash
# Resolve path dynamically (NEVER hardcode the Python version)
PKG_DIR=$(python -c "import <package_name>; import pathlib; print(pathlib.Path(<package_name>.__file__).parent)")
echo "$PKG_DIR"

# Or use find if the import name differs from the package name
find .venv/lib -path "*/<package_name>/*.py" -type f | head -20
```

### 2. Map the Module Structure

```bash
# List all Python files in the package (use the discovered path)
find "$PKG_DIR" -name "*.py" | sort
```

### 3. Search for Specific Concepts

Use #tool:search to find relevant code without reading entire files:

```bash
# Find all classes
grep -rn "^class " "$PKG_DIR"/

# Find enums
grep -rn "class.*Enum" "$PKG_DIR"/

# Find dataclasses
grep -rn "@dataclass" "$PKG_DIR"/

# Find specific patterns
grep -rn "token\|usage\|metrics" "$PKG_DIR"/
```

### 4. Read Targeted Line Ranges

```python
# Only read the lines you need — use line numbers from grep
read_file(path, start_line=322, end_line=360)
```

---

## Node.js / TypeScript Workflow

### 1. Locate the Package

```bash
# Find the package entry point
PKG_DIR="node_modules/<package_name>"
cat "$PKG_DIR/package.json" | grep -E '"main"|"types"|"exports"'

# For scoped packages
PKG_DIR="node_modules/@scope/<package_name>"
```

### 2. Map the Module Structure

```bash
# List TypeScript declaration files (best source of API surface)
find "$PKG_DIR" -name "*.d.ts" | sort

# If no .d.ts files, list source files
find "$PKG_DIR" \( -name "*.js" -o -name "*.ts" -o -name "*.mjs" \) | grep -v node_modules | sort
```

### 3. Search for Specific Concepts

```bash
# Exported types and interfaces
grep -rn "export interface\|export type\|export enum" "$PKG_DIR"/ --include="*.d.ts" --include="*.ts"

# Exported functions and classes
grep -rn "export function\|export class\|export default\|export const" "$PKG_DIR"/ --include="*.d.ts" --include="*.ts"

# React hooks
grep -rn "export function use[A-Z]" "$PKG_DIR"/ --include="*.d.ts"

# Specific patterns
grep -rn "token\|config\|options" "$PKG_DIR"/ --include="*.d.ts"
```

### 4. Read Targeted Line Ranges

```python
# Prefer .d.ts files — they contain the public API without implementation noise
read_file(path, start_line=42, end_line=80)
```

---

## Output Format

Structure your findings the same way regardless of ecosystem:

````markdown
## <Package> API Surface: <Topic>

### Types/Interfaces Found

- `TypeName` (file:L42) — brief description
  - Fields: `field1: type`, `field2: type`

### Enum Values

- `EnumName.VALUE_A` = "string_value"

### Functions/Methods

- `functionName(param: Type) => ReturnType` — what it does

### Usage Pattern

```typescript
// or python — minimal working example
```
````

## Delegation Pattern

Main agents should delegate package research to a subagent to save tokens:

```python
runSubagent(
    description="Research <package> API",
    prompt="""Research the <package> package.

    Ecosystem: Python (.venv) | Node.js (node_modules)  # pick one

    Find: <specific question — e.g., "all SessionEventType enum values and their
    associated event data payloads">

    Steps:
    1. Find package location (see above for ecosystem-specific commands)
    2. grep for relevant terms: <term1>, <term2>
    3. Read only the relevant line ranges
    4. Return a concise summary with:
       - Exact type/class/interface names and their fields
       - Method/function signatures with param types and return types
       - A minimal usage example
    Do NOT return raw source code. Return only the API surface summary."""
)
```

### Key Rules for Subagent Efficiency

| Rule | Why |
| --- | --- |
| **grep before read** | Find exact line numbers, don't scan whole files |
| **Read line ranges, not files** | `read_file(path, start=X, end=Y)` not the whole file |
| **Return summaries, not source** | The caller needs signatures, not implementations |
| **Be specific in the prompt** | "Find all enum values" not "tell me about the package" |
| **Resolve paths dynamically** | Python: `python -c "import X; ..."` — never hardcode Python version. Node: check `package.json` exports |
| **Prefer type declarations** | Python: `.py` source. Node: `.d.ts` files over `.js` |

## Anti-Patterns

| Don't | Do Instead |
| --- | --- |
| Read every file in the package | `grep` for your term first |
| Return raw source blocks | Summarize: name, fields, signatures |
| Research in the main agent | Delegate to a subagent |
| Ask vague questions | Be specific: "find the return type of X" |
| Read compiled/cached files | Python: skip `__pycache__`/`.pyc`. Node: skip `.map` files |
| Hardcode Python version in paths | Use `python -c "import X; ..."` to resolve |
| Read `.js` when `.d.ts` exists | `.d.ts` is the API contract without implementation noise |

## Registry Version Lookup

When you need the **latest published version** of a package (not the installed version), fetch from the public registry API:

### Python (PyPI)

Use #tool:web/fetch to fetch `https://pypi.org/pypi/<package>/json` and parse `info.version` from the response.

### Node.js (npm)

Use #tool:web/fetch to fetch `https://registry.npmjs.org/<package>/latest` and parse `version` from the response.

### Output Format

Return version info alongside API surface results:

```markdown
## <Package> — Latest Version

- **Registry**: PyPI | npm | NuGet
- **Latest stable**: `1.2.3`
- **Installed**: `1.2.1` (or "not installed")
- **Recommended pin**: `>=1.2.3,<2.0.0`
```

---

## Reference Documents

- [Acceptance criteria](references/acceptance-criteria.md) — Required patterns, forbidden patterns, quality gates, and checklist
