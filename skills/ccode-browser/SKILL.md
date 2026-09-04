---
name: ccode-browser
description: Control CCode's built-in browser tabs and inspect or annotate locally recorded agent browser sessions through the preinstalled ccode-browser MCP tools or the ccode browser CLI. Use for visible browser navigation, semantic page interaction, collaboration cursors, parallel tab actions, and browser recording timelines. Do not use for an unrelated external browser or generic web research when CCode browser state is not required.
metadata:
  author: "CentraGlobal"
  version: "1.1.0"
  repository: "https://github.com/CentraGlobal/centra-code-releases"
  ccode-requirement: "CCode 1.19.0 or later running with either its preinstalled ccode-browser MCP server or the ccode CLI on PATH."
---

# Control the CCode browser

Operate CCode's built-in browser so the user can watch the agent through its collaboration cursor. Keep actions scoped to the user's requested tabs and sites.

## Choose the control surface

1. Prefer MCP when tools ending in `browser_list_tabs`, `browser_open_tab`, and `browser_snapshot` are available. Host prefixes vary. MCP owns the cursor session automatically and is the most reliable interface for agent-driven work. Read [references/mcp.md](references/mcp.md) before using it.
2. Use the CCode browser CLI when the MCP tools are unavailable but a local terminal can reach the running CCode desktop process and `ccode` is on `PATH`. Read [references/cli.md](references/cli.md) before using it.
3. Do not invoke the hidden `browser-mcp` command directly and do not configure a second MCP server. CCode injects and scopes that server for supported external-agent sessions.
4. If neither interface is available, explain that a supported CCode desktop build must be running. Do not silently substitute Chrome, Playwright, or another browser because they do not share CCode's tabs, sessions, or collaboration cursor.

## Follow the interaction loop

1. List tabs and retain their stable tab IDs. Reuse a tab only when the user chose it or the task clearly targets it; otherwise open a new tab rather than navigating away from unrelated user state.
2. Snapshot the target tab before choosing a locator and after navigation or any action that materially changes the page.
3. Choose a semantic locator in this order: role with accessible name, label, test ID, visible text, then CSS. Require a unique match by default.
4. Use `scope` to limit a locator to a known container. Use zero-based `nth` only when the snapshot establishes which repeated match is intended.
5. Perform the smallest action that advances the task. A click that submits, sends, purchases, deletes, or otherwise changes external state still requires the user's authorization for that outcome.
6. Check the structured result or CLI exit status. Verify important state changes with a new snapshot; cursor movement alone is not proof of success.

## Manage the visible cursor

- MCP starts the cursor session on the first browser command, keeps it across calls, and removes it when the MCP process exits. Do not add manual CLI session commands around MCP work.
- Use `presentation: "auto"` normally. Use `"realtime"` when the user is actively watching or asks to see the cursor move. Use `"fast"` for large unattended batches. Use `"off"` only when the user asks to hide action animation.
- The user can dismiss a cursor from its label. Dismissal hides the cursor without changing action results; respect it and continue only as required by the task.
- CLI workflows need one explicit session ID for the whole run, periodic heartbeats during long work, and an end command on completion. The lease removes abandoned cursors after an agent crash.

## Use browser recordings

- Recording is a user-controlled, privacy-sensitive setting. When enabled, it starts automatically with the automation session; do not claim a session is recorded without a recording reference or a successful status check.
- Recorded action results include the recording ID, exact event ID, sequence, and millisecond offset. When an active recording captures an error, unexpected behavior, or another moment that materially helps later review, add one concise comment anchored to that exact event. Do not annotate routine actions.
- A comment can also target a prior event, sequence, or millisecond offset. Comments require the active automation session; completed recordings are read-only.
- When thread context contains an attached recording ID, retrieve its events newest first and follow pagination until `truncated` is false. Use event kind and tab filters when the task does not require the full timeline.
- Read [references/recordings.md](references/recordings.md) whenever recording status, comments, attached recordings, privacy, or captured console/network data matters. Use the exact MCP calls in [references/mcp.md](references/mcp.md) or CLI commands in [references/cli.md](references/cli.md).

## Handle multiple tabs

- Use `browser_batch` or `ccode browser ... batch` when two or more prepared tabs have independent actions. CCode runs different tabs concurrently and preserves listed operation order within each tab.
- Keep dependent actions for one tab in their intended order. Use unique operation IDs and inspect every per-operation result.
- Open, navigate, activate, and close tabs outside a batch. Batch supports snapshots and element interactions, not tab lifecycle commands.
- Do not parallelize actions whose locators depend on state produced by another tab or action.

## Work within supported primitives

CCode supports semantic snapshots, click, hover, fill, check or uncheck, select, keyboard input, file-input upload, locator-to-locator drag and drop, and parallel batches. It intentionally is not a full Playwright runtime. Read [references/capabilities.md](references/capabilities.md) for dropdown, scrolling, upload, drag, URL, and unsupported-operation guidance.

When an action fails, use its error code rather than guessing:

- Re-snapshot for `locator_not_found`, `strict_mode_violation`, `stale_document`, visibility, editability, or obscured-target failures, then refine the locator from current page state.
- Choose the correct control for `not_selectable`, `not_checkable`, or `not_file_input`; blind retries cannot change the element type.
- For `browser_unavailable`, confirm CCode is running and start a fresh external-agent session so CCode can inject its built-in MCP. The built-in server is session-scoped and may not appear in the user-configured MCP list.
- Stop and report persistent or unsupported failures with the exact returned status, code, and message.
