# MCP reference

Use this mode when the host exposes CCode browser tools. The visible tool name may include a host prefix; match the stable suffixes below.

## Tool selection

| Tool suffix | Use |
| --- | --- |
| `browser_recording_status` | Inspect whether this MCP session is being recorded, its capture policy, timeline offset, and degraded reasons. |
| `browser_recording_events` | Query active or saved recording events newest first, with sequence, kind, and tab filters. |
| `browser_recording_comment` | Add a concise comment now or at an exact prior event, sequence, or offset in the active recording. |
| `browser_list_tabs` | Discover stable tab IDs, URLs, titles, loading state, and the active tab. |
| `browser_open_tab` | Open an optional HTTPS or loopback URL and choose whether it is active. |
| `browser_close_tab` | Close one known tab. |
| `browser_activate_tab` | Bring a known tab and its workspace forward. |
| `browser_navigate` | Navigate a known tab to a URL. |
| `browser_snapshot` | Read the current URL, title, visible text, and semantic interactive elements. |
| `browser_click` / `browser_hover` | Interact with a located element or visibly point at it. |
| `browser_fill` | Replace an editable value; protocol debug output redacts the value. |
| `browser_check` | Set a checkbox or radio control using the `checked` boolean. |
| `browser_select` | Select one or more values in a native or supported ARIA select. |
| `browser_press` | Send a `KeyboardEvent.key`, such as `Enter`, `Escape`, `Tab`, `ArrowDown`, or `PageDown`. |
| `browser_drag` | Drag a located source to a located target with `html5` or `pointer` mode. |
| `browser_upload` | Assign one or more local paths to a file input. |
| `browser_batch` | Run supported element actions concurrently across tabs and serially within each tab. |

The tool schemas are authoritative. Do not invent parameters that the active server does not expose.

## Locators

Prefer semantic locators:

```json
{"kind":"role","role":"button","name":"Save","exact":true}
```

```json
{"kind":"label","text":"Email","exact":true}
```

```json
{"kind":"test_id","value":"profile-form"}
```

Use text when semantic information is unavailable:

```json
{"kind":"text","text":"Continue","exact":true}
```

Use CSS as the last choice:

```json
{"kind":"css","selector":"input[type=file]"}
```

Add `scope` to any locator to constrain it beneath one CSS container. Add zero-based `nth` only for repeated matches confirmed by a snapshot.

## Typical flow

1. Call `browser_list_tabs`.
2. Call `browser_open_tab` with `{"url":"https://example.com","active":true}` when a new tab is appropriate.
3. Call `browser_snapshot` using the returned `tab_id`.
4. Call an interaction tool with that same `tab_id`, a locator derived from the snapshot, and `presentation: "auto"` or `"realtime"`.
5. Snapshot again when the result matters.

For a custom dropdown that is not directly selectable, click the trigger, snapshot the opened menu, then click the option by role or text. Native and supported ARIA selects should use `browser_select` with their option values.

## Recording queries and comments

Check recording state before relying on recorded output:

```json
{}
```

Call the empty object above with `browser_recording_status`. Ordinary recorded tool results include a `recording` reference containing `recording_id`, `event_id`, `sequence`, and `offset_ms`.

Use `browser_recording_events` without a recording ID for the active MCP session:

```json
{"kinds":["automation","console","network","comment"],"limit":100}
```

Use an attached ID to inspect an active or completed recording:

```json
{"recording_id":"rec_EXAMPLE","limit":100}
```

Results are newest first. If `truncated` is true, set `before_sequence` to the lowest returned sequence and repeat. `after_sequence` and `before_sequence` are exclusive. The maximum page size is 500.

When a result identifies an important moment, call `browser_recording_comment` with its exact event ID:

```json
{
  "text":"Checkout failed after the API returned 500",
  "anchor":{"type":"event","event_id":"event_EXAMPLE","placement":"at"}
}
```

Use `type: "sequence"` with `sequence` and optional `placement`, or `type: "offset"` with `offset_ms`, when no event ID is available. Omit `anchor` to comment at the current moment. Comments can only be added to the active session recording. Read [recordings.md](recordings.md) for event, attachment, and privacy semantics.

## Parallel batch

Send operations that are independent across tabs in one `browser_batch` call:

```json
{
  "operations": [
    {
      "id": "inspect-a",
      "command": "snapshot",
      "tab_id": "TAB_A"
    },
    {
      "id": "point-b",
      "command": "hover",
      "tab_id": "TAB_B",
      "locator": {
        "kind": "role",
        "role": "link",
        "name": "Details",
        "exact": true
      },
      "presentation": "realtime"
    }
  ]
}
```

Supported batch command values are `snapshot`, `click`, `hover`, `fill`, `check`, `select`, `press`, `drag_to`, and `upload_files`. Operations sharing a tab ID execute in listed order; different tab IDs may execute concurrently. Inspect every result by operation ID because one failed operation makes the overall batch an error while other operations may still have completed.

## Sensitive values and files

- Use user-provided credentials only for the requested task. Do not repeat filled secrets in the final response or diagnostic text.
- MCP fill values are redacted from CCode browser-protocol debug output, but they still pass through the agent host and MCP request.
- Upload paths must be accessible to the MCP process. Relative paths resolve from its working directory; prefer absolute paths when the location is unambiguous.
