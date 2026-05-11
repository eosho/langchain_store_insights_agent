# Playwright MCP Tools Reference

Complete schema reference for all 22 browser automation tools.

## Navigation

### browser_navigate

Navigate to a URL.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | ✓ | The URL to navigate to |

### browser_navigate_back

Go back to the previous page in history. No parameters.

## Page Inspection

### browser_snapshot

Capture accessibility snapshot of the current page. Returns element refs for interaction.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filename` | string | | Save snapshot to markdown file instead of returning |

### browser_take_screenshot

Take a screenshot of the current page.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | `"png"` \| `"jpeg"` | ✓ | Image format (default: png) |
| `fullPage` | boolean | | Screenshot full scrollable page |
| `element` | string | | Human-readable element description (requires ref) |
| `ref` | string | | Element reference (requires element) |
| `filename` | string | | File name to save screenshot |

## Element Interaction

### browser_click

Perform click on a web page element.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ref` | string | ✓ | Element reference from snapshot |
| `element` | string | | Human-readable element description |
| `button` | `"left"` \| `"right"` \| `"middle"` | | Button to click (default: left) |
| `doubleClick` | boolean | | Perform double click |
| `modifiers` | array | | Modifier keys: `Alt`, `Control`, `ControlOrMeta`, `Meta`, `Shift` |

### browser_type

Type text into editable element.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ref` | string | ✓ | Element reference from snapshot |
| `text` | string | ✓ | Text to type |
| `element` | string | | Human-readable element description |
| `submit` | boolean | | Press Enter after typing |
| `slowly` | boolean | | Type one character at a time |

### browser_fill_form

Fill multiple form fields at once.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `fields` | array | ✓ | Array of field objects |

**Field object:**

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | string | ✓ | Human-readable field name |
| `type` | `"textbox"` \| `"checkbox"` \| `"radio"` \| `"combobox"` \| `"slider"` | ✓ | Field type |
| `ref` | string | ✓ | Element reference from snapshot |
| `value` | string | ✓ | Value to fill (checkbox: `"true"`/`"false"`) |

### browser_select_option

Select an option in a dropdown.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ref` | string | ✓ | Element reference from snapshot |
| `values` | array | ✓ | Values to select (can be multiple) |
| `element` | string | | Human-readable element description |

### browser_hover

Hover over element on page.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ref` | string | ✓ | Element reference from snapshot |
| `element` | string | | Human-readable element description |

### browser_drag

Perform drag and drop between two elements.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `startElement` | string | ✓ | Human-readable source element description |
| `startRef` | string | ✓ | Source element reference |
| `endElement` | string | ✓ | Human-readable target element description |
| `endRef` | string | ✓ | Target element reference |

### browser_press_key

Press a key on the keyboard.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `key` | string | ✓ | Key name (`ArrowLeft`, `Enter`, `a`, etc.) |

### browser_file_upload

Upload one or multiple files.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `paths` | array | | Absolute paths to files. Omit to cancel file chooser. |

### browser_handle_dialog

Handle a dialog (alert, confirm, prompt).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `accept` | boolean | ✓ | Whether to accept the dialog |
| `promptText` | string | | Text for prompt dialog |

## Waiting

### browser_wait_for

Wait for text to appear/disappear or time to pass.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `text` | string | | Text to wait for |
| `textGone` | string | | Text to wait to disappear |
| `time` | number | | Time to wait in seconds |

## JavaScript Execution

### browser_evaluate

Evaluate JavaScript expression on page or element.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `function` | string | ✓ | JS function: `() => { }` or `(element) => { }` |
| `element` | string | | Human-readable element description |
| `ref` | string | | Element reference (when using element param) |

### browser_run_code

Run Playwright code snippet.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `code` | string | ✓ | Async function: `async (page) => { ... }` |

**Example:**
```javascript
async (page) => {
  await page.getByRole('button', { name: 'Submit' }).click();
  return await page.title();
}
```

## Tab Management

### browser_tabs

List, create, close, or select browser tabs.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | `"list"` \| `"new"` \| `"close"` \| `"select"` | ✓ | Operation to perform |
| `index` | number | | Tab index for close/select |

## Window

### browser_resize

Resize the browser window.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `width` | number | ✓ | Width in pixels |
| `height` | number | ✓ | Height in pixels |

## Debugging

### browser_console_messages

Returns all console messages.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `level` | `"error"` \| `"warning"` \| `"info"` \| `"debug"` | ✓ | Minimum level (default: info) |
| `filename` | string | | Filename to save messages |

### browser_network_requests

Returns all network requests since page load.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `includeStatic` | boolean | ✓ | Include images, fonts, scripts (default: false) |
| `filename` | string | | Filename to save requests |

## Setup

### browser_install

Install the browser. Call if you get browser not installed error. No parameters.

### browser_close

Close the page. No parameters.
