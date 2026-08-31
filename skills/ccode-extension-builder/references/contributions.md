# Commands and native UI contributions

Declare commands first, then reference those stable command IDs from keybindings and surfaces. CCode registers each command as the configurable `extension::InvokeExtension` action and removes its default binding when the extension is deactivated.

```toml
id = "example-tools"
name = "Example Tools"
version = "0.1.0"
schema_version = 1

[commands.open-dashboard]
title = "Open Dashboard"
description = "Open the extension dashboard"

[commands.show-details]
title = "Show Details"

[[keybindings]]
key = "ctrl-alt-e"
command = "open-dashboard"
context = "Workspace"

[panes.dashboard]
title = "Example Dashboard"
command = "open-dashboard"

[panels.tools]
title = "Example Tools"
command = "open-dashboard"
dock = "right"

[docks.activity]
title = "Example Activity"
command = "open-dashboard"
position = "bottom"

[status_items.example]
label = "Example"
command = "show-details"
alignment = "right"

[modals.details]
title = "Example Details"
command = "show-details"
```

Supported dock positions are `left`, `right`, and `bottom`. Supported status item alignments are `left` and `right`. Identifiers may contain letters, numbers, `.`, `_`, and `-`.

Default keybindings use GPUI key syntax and may include an optional key context. Users can override them without editing the extension:

```json
[
  {
    "context": "Workspace",
    "bindings": {
      "ctrl-shift-e": [
        "extension::InvokeExtension",
        {
          "extension_id": "example-tools",
          "command_id": "open-dashboard"
        }
      ]
    }
  }
]
```

Use one command for multiple surfaces only when they intentionally open the same extension experience. Keep command IDs stable across live reloads so user overrides remain valid.
