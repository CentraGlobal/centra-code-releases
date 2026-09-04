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

## Recording boundary

- Browser recording is off by default and controlled by the user in CCode's privacy settings. Automation begins and ends the recording with its session when the setting is enabled.
- Depending on that policy, the local recording can contain real viewport frames, automation and cursor events, redacted console messages, and network metadata, redacted headers, or bounded redacted bodies. Treat the recording as sensitive even after best-effort redaction.
- Excluded origins suppress page content from the recording. Capture can also degrade or stop at its configured storage limit; inspect recording status and degraded reasons instead of assuming completeness.
- MCP and CLI event queries return structured event metadata and details, not frame image bytes. The native Recording Player renders captured frames; a single event attached from that player can include its nearest frame.
- A whole-recording thread attachment contains its recording ID and retrieval instructions. Paginate every event only when the user's task requires the complete timeline.

## Not provided by this interface

- Arbitrary page JavaScript evaluation
- Browser context, cookie, local-storage, or permission manipulation
- Network interception or request mocking. Recording may retain configured network data, but cannot alter traffic.
- Ad hoc pixel screenshots or coordinate-level mouse control. Recording frames are available through the native player rather than event-query image payloads.
- Playwright selectors or Playwright test execution
- Download lifecycle management

Use another explicitly authorized interface only when the task truly requires one of these capabilities. Do not represent another browser's state as CCode browser state.
