# Capabilities and boundaries

## Supported interaction patterns

### Dropdowns and menus

- Use `select` for native `<select>` controls and supported ARIA select controls. Pass option values, not assumed display labels, unless the tool schema or page state shows they are identical.
- For a custom popover menu, click its trigger, snapshot the open menu, then click the intended option by role or visible text.
- Keyboard-driven controls can use `ArrowDown`, `ArrowUp`, `Enter`, `Escape`, or `Tab` through `press` after the correct element has focus.

### Scrolling

There is no dedicated scroll or wheel command. Use `press` with `PageDown`, `PageUp`, `Home`, or `End` on the focused page. Snapshot after scrolling before selecting a newly visible target.

### Uploads

Upload assigns local files through an `<input type="file">`. A styled drop zone often contains a hidden file input; locate that input with a stable test ID or scoped CSS selector. If the page exposes only a drop target and no file input, upload cannot synthesize a filesystem drag payload.

### Drag and drop

Drag uses source and target locators rather than arbitrary screen coordinates. Use `html5` for native web drag events and `pointer` for pointer-driven sortable interfaces. If one mode fails, re-snapshot the targets before trying the other mode once; report the limitation if neither works.

### Forms and state

- `fill` replaces the current editable value.
- `check` sets an explicit checked state rather than blindly toggling.
- `click`, `hover`, `fill`, `check`, `select`, drag, and upload enforce locator strictness and relevant actionability checks.
- Retryable page-state failures may be retried internally for up to 30 seconds. Do not add an unbounded external retry loop.

## URL policy

Public navigation accepts HTTPS. Plain HTTP is limited to loopback development URLs such as `http://127.0.0.1:3000` or `http://localhost:3000`. Treat a rejected public HTTP URL as unsupported rather than weakening or bypassing the policy.

## Snapshot boundary

A snapshot returns an agent-oriented representation: current URL, title, visible text, and semantic interactive elements. It is not a screenshot, full DOM export, accessibility-tree dump, or guarantee that offscreen and hidden content is included.

## Not provided by this interface

- Arbitrary page JavaScript evaluation
- Browser context, cookie, local-storage, or permission manipulation
- Network interception, request mocking, or response-body capture
- Pixel screenshots or coordinate-level mouse control
- Playwright selectors or Playwright test execution
- Download lifecycle management

Use another explicitly authorized interface only when the task truly requires one of these capabilities. Do not represent another browser's state as CCode browser state.
