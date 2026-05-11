---
name: browser-automation
description: Browser automation using VS Code Playwright MCP extension. Use when navigating websites, filling forms and clicking buttons, extracting data from web pages, testing web UIs via Swagger/OpenAPI docs, taking screenshots, handling dialogs and file uploads, frontend E2E testing, visual regression testing, debugging frontend applications, or automating any browser interaction. NOT for static content fetching (use curl/wget instead).
argument-hint: 'Describe the page and action to perform'
compatibility: Requires VS Code with ms-playwright.playwright extension and Chromium browser.
metadata:
  author: eosho
  version: "1.0"
---

# Browser Automation with Playwright MCP

Browser automation using the VS Code Playwright extension. Navigate websites, fill forms, click elements, take screenshots, and extract data.

## Prerequisites

The `ms-playwright.playwright` extension is included in devcontainer.

Install browser:

```bash
.github/skills/browser-automation/scripts/install-browser.sh
# Or manually: npx playwright install chromium
```

## Core Pattern

1. **Navigate** → `browser_navigate` to URL
2. **Snapshot** → `browser_snapshot` to get element refs
3. **Interact** → Use refs with `click`, `type`, `fill`
4. **Wait** → `browser_wait_for` conditions
5. **Verify** → `browser_snapshot` or `browser_take_screenshot`

## Basic Usage

```
# Navigate to a page
browser_navigate(url="https://example.com")

# Get element refs (ALWAYS do this before interacting)
browser_snapshot()

# Click an element (use ref from snapshot)
browser_click(element="Submit button", ref="e42")

# Type text
browser_type(element="Search input", ref="e15", text="query", submit=true)

# Fill multiple form fields
browser_fill_form(fields=[
  {"name": "Email", "type": "textbox", "ref": "e10", "value": "email@example.com"},
  {"name": "Password", "type": "textbox", "ref": "e12", "value": "password"}
])

# Take screenshot
browser_take_screenshot(type="png", fullPage=true)
```

## Available Tools

| Tool | Purpose |
|------|---------|
| `browser_navigate` | Go to URL |
| `browser_navigate_back` | Go back in history |
| `browser_snapshot` | Get accessibility tree with element refs |
| `browser_click` | Click element by ref |
| `browser_type` | Type text (optionally submit) |
| `browser_fill_form` | Fill multiple fields at once |
| `browser_select_option` | Select dropdown value |
| `browser_hover` | Hover over element |
| `browser_drag` | Drag element to target |
| `browser_press_key` | Press keyboard key |
| `browser_wait_for` | Wait for text/URL/time |
| `browser_evaluate` | Run JavaScript |
| `browser_run_code` | Execute Playwright code |
| `browser_take_screenshot` | Capture page image |
| `browser_file_upload` | Upload files |
| `browser_handle_dialog` | Accept/dismiss dialogs |
| `browser_tabs` | List open tabs |
| `browser_resize` | Resize viewport |
| `browser_console_messages` | Get console logs |
| `browser_network_requests` | Get network activity |
| `browser_install` | Install browser |
| `browser_close` | Close browser |

## Example: Swagger UI Form Submission

```
1. browser_navigate(url="http://localhost:8001/docs")
2. browser_snapshot()  # Find endpoint ref (e.g., e48)
3. browser_click(element="POST Create Item", ref="e48")
4. browser_click(element="Try it out", ref="e203")
5. browser_type(element="Request body", ref="e283",
     text='{"title": "New Item", "description": "Created via browser"}')
6. browser_click(element="Execute", ref="e284")
7. browser_snapshot()  # Verify 201 response
```

## Example: Login Flow

```
1. browser_navigate(url="https://app.example.com/login")
2. browser_snapshot()  # Get form field refs
3. browser_fill_form(fields=[
     {"name": "Email", "type": "textbox", "ref": "e15", "value": "user@example.com"},
     {"name": "Password", "type": "textbox", "ref": "e18", "value": "password123"}
   ])
4. browser_click(element="Sign in", ref="e22")
5. browser_wait_for(text="Dashboard")
6. browser_snapshot()  # Verify logged in
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Element not found | Run `browser_snapshot` first to get current refs |
| Click fails | Try `browser_hover` first, then click |
| Form not submitting | Use `submit: true` with `browser_type` |
| Page not loading | Use `browser_wait_for` with text or time |
| Refs changed | Re-run `browser_snapshot` after any navigation |
| Tool not available | Run `tool_search_tool_regex` with pattern `mcp_microsoft_pla` |

## Reference Files

| File | Purpose |
|------|--------|
| [references/playwright-tools.md](references/playwright-tools.md) | Full parameter schemas for all 22 tools |
| [scripts/install-browser.sh](scripts/install-browser.sh) | Install Chromium browser |
