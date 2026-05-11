---
applyTo: "tools/harness/**/*.py"
description: Agent/skill test harness using GitHub Copilot SDK — async patterns, tool validation, test structure
---

# Test Harness

Test framework for evaluating custom agents and skills via the GitHub Copilot SDK.

## Architecture

```
tools/harness/
├── harness.py              # AIGSpecKitTestHarness class (core)
├── agents/<name>/main.py   # Agent test scripts
├── skills/<name>/main.py   # Skill test scripts
└── */prompt.md             # Input prompts
```

## Critical Rules

1. **Async context manager required** — Always use `async with AIGSpecKitTestHarness(...) as harness:`
2. **Tools determine pass/fail** — Every `@define_tool` must return `{"success": bool, "output": str}`. If no tools are called, the test fails.
3. **Never use `working_directory` in tests** — Use `custom_agents` with explicit agent definitions to control token usage
4. **`auto_approve_permissions` is test-only** — Never expose this pattern in production code
5. **Import path** — Use `from tools.harness.harness import AIGSpecKitTestHarness`

## Writing a New Test

### Test Script Pattern (`main.py`)

```python
import asyncio, sys
from pathlib import Path
from copilot.tools import define_tool
from pydantic import BaseModel, Field
from tools.harness.harness import AIGSpecKitHarnessConfig, AIGSpecKitTestHarness

HARNESS_DIR = Path(__file__).parent
REPO_ROOT = HARNESS_DIR.parent.parent.parent.parent
PROMPT_FILE = HARNESS_DIR / "prompt.md"

# 1. Define validation tool(s) — must return {"success": bool, "output": str}
@define_tool(description="Verify the output meets requirements")
async def validate_output(params: MyParams) -> dict[str, Any]:
    ...
    return {"success": True, "output": "Passed"}

# 2. Configure and run
async def main() -> int:
    config: AIGSpecKitHarnessConfig = {
        "custom_agents": [{"name": "Builder", "prompt": "..."}],
    }
    async with AIGSpecKitTestHarness(tools=[validate_output], config=config) as harness:
        result = await harness.invoke(PROMPT_FILE.read_text(), agent="Builder")
    print(result.to_json())
    return 0 if result.success else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
```

### Key Classes

| Class | Purpose |
|-------|---------|
| `AIGSpecKitTestHarness` | Async context manager — creates Copilot session, tracks tool calls |
| `AIGSpecKitTestResult` | Result with `success`, `message`, `tool_executions`, `usage` |
| `AIGSpecKitHarnessConfig` | TypedDict for `model`, `timeout`, `custom_agents`, `skill_directories` |
| `AIGSpecKitToolExecution` | Record of one tool call: `name`, `success`, `output` |

### Running Tests

```bash
uv run python tools/harness/agents/infrastructure/main.py
uv run python tools/harness/skills/package-inspection/main.py
```

Requires `copilot login` authentication first.
