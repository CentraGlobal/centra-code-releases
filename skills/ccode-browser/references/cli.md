# CLI reference

Use CCode's installed CLI alias to control the running CCode desktop process. Try `ccode browser --help` first. If the `ccode` executable is not installed, try `zed browser --help`; current macOS packages may retain that alias. Use whichever command exposes the `browser` subcommand consistently for the whole run. The examples below use `ccode`; replace only that executable name with `zed` when discovery selected it.

Commands return one JSON response; browser failures also use a nonzero exit status. CCode 1.18.0 or later is required.

## Cursor session lifecycle

Choose a stable, unique session ID and actor name for one agent run:

```sh
ccode browser --session "agent-run-123" --actor-name "Coding Agent" session start --lease-seconds 120
```

Use the same `--session` on every subsequent command. For work lasting near the lease duration, refresh it before expiry:

```sh
ccode browser --session "agent-run-123" session heartbeat
```

End the session when the browser work finishes, including after handled failures:

```sh
ccode browser --session "agent-run-123" session end
```

Do not leave the session open merely to keep the cursor visible after the agent has finished. If the process exits unexpectedly, the lease removes it.

## Discover and inspect tabs

```sh
ccode browser --session "agent-run-123" tabs
```

```sh
ccode browser --session "agent-run-123" open "https://example.com"
```

```sh
ccode browser --session "agent-run-123" snapshot --tab "TAB_ID"
```

Retain the returned tab ID. Navigation, activation, and close operations use it:

```sh
ccode browser --session "agent-run-123" navigate --tab "TAB_ID" "https://example.com/docs"
ccode browser --session "agent-run-123" activate --tab "TAB_ID"
ccode browser --session "agent-run-123" close --tab "TAB_ID"
```

## Locators and interactions

Each element action accepts exactly one locator strategy:

- `--role ROLE --name NAME [--exact]`
- `--label TEXT [--exact]`
- `--test-id VALUE`
- `--text TEXT [--exact]`
- `--css SELECTOR`

Add `--scope-css SELECTOR` to constrain the search or `--nth INDEX` for a snapshot-confirmed, zero-based repeated match.

Examples:

```sh
ccode browser --session "agent-run-123" click --tab "TAB_ID" --role button --name "Save" --exact --presentation realtime
```

```sh
ccode browser --session "agent-run-123" hover --tab "TAB_ID" --text "Learn more" --exact --presentation realtime
```

```sh
ccode browser --session "agent-run-123" select --tab "TAB_ID" --label "Country" --exact --value "MA" --presentation auto
```

Use `fill --value-stdin` for credentials or other values that should not appear in shell history or process arguments. Supply the value through the agent host's secret-aware stdin mechanism:

```sh
ccode browser --session "agent-run-123" fill --tab "TAB_ID" --label "Password" --exact --value-stdin --presentation auto
```

Regular non-secret values may use `--value`.

Upload targets must be file inputs, including a hidden input behind a visible drop zone:

```sh
ccode browser --session "agent-run-123" upload --tab "TAB_ID" --css "input[type=file]" "/absolute/path/image.png"
```

Drag between located CSS elements. Try the default HTML5 mode first; use `--mode pointer` for pointer-driven sortable interfaces:

```sh
ccode browser --session "agent-run-123" drag-to --tab "TAB_ID" --source-css "[data-card='a']" --target-css "[data-column='done']" --mode html5 --presentation realtime
```

Use `press` for focused-page keyboard interactions and scrolling:

```sh
ccode browser --session "agent-run-123" press --tab "TAB_ID" PageDown --presentation realtime
```

## Parallel batch files

Create a JSON array with unique operation IDs, then pass its path to `batch`:

```json
[
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
    "presentation": "fast"
  }
]
```

```sh
ccode browser --session "agent-run-123" batch --file "/absolute/path/browser-actions.json"
```

The batch accepts `snapshot`, `click`, `hover`, `fill`, `check`, `select`, `press`, `drag_to`, and `upload_files`. Operations for the same tab execute in listed order; different tabs may run concurrently. Relative upload paths inside a CLI batch resolve from the batch file's directory.
