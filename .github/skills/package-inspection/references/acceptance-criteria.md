# Acceptance Criteria: package-inspection

| Field       | Value                                                                            |
|-------------|----------------------------------------------------------------------------------|
| Skill Type  | Research / API Discovery                                                         |
| Target      | Python packages in `.venv` or Node.js/TypeScript packages in `node_modules`      |
| Output      | Structured markdown API summary                                                  |

## 1. Package Discovery Patterns

### 1.1 Correct Package Location

#### Python

##### ✅ CORRECT: Using `find` to locate the package

```bash
find .venv/lib -path "*/<package_name>/*.py" -type f | head -20
```

##### ✅ CORRECT: Using Python to resolve package path

```bash
PKG_DIR=$(python -c "import <package_name>; import pathlib; print(pathlib.Path(<package_name>.__file__).parent)")
echo "$PKG_DIR"
```

#### Node.js / TypeScript

##### ✅ CORRECT: Check package.json for entry points

```bash
PKG_DIR="node_modules/<package_name>"
cat "$PKG_DIR/package.json" | grep -E '"main"|"types"|"exports"'
```

##### ✅ CORRECT: Find type declarations first

```bash
find "$PKG_DIR" -name "*.d.ts" | sort
```

### 1.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Guessing or hardcoding paths

```bash
# WRONG - Don't assume Python version or site-packages structure
cat .venv/lib/python3.12/site-packages/package/module.py

# WRONG - Don't use system packages
find /usr/lib/python3 -name "*.py"

# WRONG - Don't read .js when .d.ts files exist (Node)
cat node_modules/<package>/dist/index.js  # use index.d.ts instead
```

## 2. Search Patterns

### 2.1 Correct Search Strategy

#### Python

##### ✅ CORRECT: Resolve path dynamically, then grep

```bash
PKG_DIR=$(python -c "import <package>; import pathlib; print(pathlib.Path(<package>.__file__).parent)")

grep -rn "class.*Enum" "$PKG_DIR"/
grep -rn "@dataclass" "$PKG_DIR"/
grep -rn "def " "$PKG_DIR"/
```

##### ✅ CORRECT: Map module structure first

```bash
find "$PKG_DIR" -name "*.py" | sort
```

#### Node.js / TypeScript

##### ✅ CORRECT: Search type declarations first

```bash
PKG_DIR="node_modules/<package>"

grep -rn "export interface\|export type\|export enum" "$PKG_DIR"/ --include="*.d.ts"
grep -rn "export function\|export class" "$PKG_DIR"/ --include="*.d.ts"
```

##### ✅ CORRECT: Map declaration files first

```bash
find "$PKG_DIR" -name "*.d.ts" | sort
```

### 2.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Reading whole files instead of targeted line ranges

```python
# WRONG — use line ranges from grep results
read_file(path, start_line=1, end_line=500)
```

#### ❌ INCORRECT: Searching without purpose

```bash
# WRONG - Be specific about what you're looking for
grep -r ".*" .venv/lib/
```

#### ❌ INCORRECT: Hardcoding the Python version

```bash
# WRONG - Never hardcode python3.12 or any version in paths
grep -rn "class" .venv/lib/python3.12/site-packages/<package>/
```

#### ❌ INCORRECT: Reading compiled files

```bash
# WRONG - Python: skip __pycache__ and .pyc files
cat __pycache__/module.cpython-312.pyc

# WRONG - Node: skip .map files when .d.ts exists
cat node_modules/<package>/dist/index.js.map
```

## 3. Output Format Patterns

### 3.1 Correct Summary Structure

#### ✅ CORRECT: Structured markdown with types, signatures, and examples

````markdown
## <Package> API Surface: <Topic>

### Types/Interfaces Found

- `TypeName` (file:L42) — brief description
  - Fields: `field1: type`, `field2: type`

### Enum Values

- `EnumName.VALUE_A` = "string_value"
- `EnumName.VALUE_B` = "string_value"

### Functions/Methods

- `functionName(param: Type) => ReturnType` — what it does

### Usage Pattern

```typescript
// or python — minimal working example
```
````

#### ✅ CORRECT: Every finding includes file location

```markdown
- `SessionEventType` (session_events.py:L15) — Event type enum
```

#### ✅ CORRECT: Complete enum listings (all values, not a subset)

```markdown
### SessionEventType Values

- `ASSISTANT_MESSAGE_DELTA` = "assistant_message_delta"
- `ASSISTANT_USAGE` = "assistant_usage"
- `SESSION_ERROR` = "session_error"
- ... (ALL values listed)
```

### 3.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Raw source code dumps

```python
# WRONG - Don't paste large blocks of source code
# The agent should summarize, not copy
class SessionEventType(str, Enum):
    ASSISTANT_MESSAGE_DELTA = "assistant_message_delta"
    # ... entire class pasted
```

#### ❌ INCORRECT: Missing type annotations

```markdown
<!-- WRONG - Always include types -->

- `input_tokens` — number of input tokens
```

```markdown
<!-- CORRECT -->

- `input_tokens: float` — number of input tokens consumed
```

#### ❌ INCORRECT: Incomplete enum listings

```markdown
<!-- WRONG - Don't list "some" values -->

### SessionEventType Values (partial)

- `ASSISTANT_USAGE`
- `SESSION_ERROR`
- ... and more
```

#### ❌ INCORRECT: No file/line references

```markdown
<!-- WRONG - Every finding must cite its source -->

- `SessionEventType` — Event type enum
```

## 4. Delegation Patterns

### 4.1 Correct Delegation

#### ✅ CORRECT: Specific subagent prompt with clear deliverables

```python
runSubagent(
    description="Research copilot SDK events",
    prompt="""Research the `copilot` package.

    Ecosystem: Python (.venv)

    Find: all SessionEventType enum values and their associated event data payloads.

    Steps:
    1. Resolve path: python -c "import copilot; import pathlib; print(pathlib.Path(copilot.__file__).parent)"
    2. grep for SessionEventType in that directory
    3. Read only relevant line ranges
    4. Return concise summary with exact names, types, and a usage example.
    Do NOT return raw source code. Do NOT hardcode Python version in paths."""
)
```

### 4.2 Anti-Patterns (ERRORS)

#### ❌ INCORRECT: Main agent reads package files directly

```python
# WRONG - Main agent wastes context tokens on package reading
# The main agent should delegate to a subagent
read_file(".venv/lib/.../copilot/types.py", 1, 500)
read_file(".venv/lib/.../copilot/session.py", 1, 500)
```

## 5. Quality Gates

### 5.1 Output File Validation

```bash
# Output file must exist and be non-empty
test -s output/api-summary.md
```

### 5.2 Required Content Checks

The output summary **MUST** contain:

| Pattern                               | Reason                                     |
| ------------------------------------- | ------------------------------------------ |
| Enum/class names with source location | Traceability to actual package source      |
| Type annotations on all fields        | Consumers need types to write correct code |
| At least one usage example            | Practical demonstration of the API         |
| >= 2 markdown headings                | Structured, scannable output               |

### 5.3 Forbidden Content Checks

The output summary **MUST NOT** contain:

| Pattern                          | Reason                               |
| -------------------------------- | ------------------------------------ |
| Raw source blocks > 20 lines     | Summary, not a copy                  |
| Implementation internals         | Public API surface only              |
| Information from memory/training | Must come from the installed package |

## Summary Checklist

Before returning a package inspection summary, verify:

- [ ] Package was located correctly (Python: `.venv` via dynamic resolution; Node: `node_modules`)
- [ ] `grep` was used before `read_file` (targeted, not exhaustive)
- [ ] Only source files were read (Python: `.py` not `.pyc`; Node: `.d.ts` preferred over `.js`)
- [ ] Line ranges were used (not whole-file reads)
- [ ] All enum values are listed (complete, not partial)
- [ ] Every finding has a file:line citation
- [ ] All fields/params include type annotations
- [ ] At least one runnable usage example is included
- [ ] Output is structured with markdown headings
- [ ] Output is under 200 lines (concise, not verbose)
- [ ] No raw source code blocks > 20 lines
- [ ] Research was delegated to a subagent (when called from a main agent)
