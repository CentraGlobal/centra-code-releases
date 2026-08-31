# Live extension development

Use `--json` for agent-driven work. Each output line is a JSON event and the final event reports success or failure.

## Validate without activation

```sh
ccode extension check ./path/to/extension --json
```

Validation covers the manifest, declared contributions, keybindings, capabilities, and the Wasm build when the extension has a Rust library.

## Activate and watch

```sh
ccode extension dev ./path/to/extension --activate --watch --json
```

The running CCode app owns activation. The CLI sends the canonical source path to the app and exits after the watcher is registered. CCode keeps the watcher alive and rebuilds changed sources transactionally.

The newline-delimited event names are `progress`, `checked`, `activated`, `watching`, `reloaded`, `deactivated`, `status`, `log`, `completed`, and `failed`. A failed watched rebuild leaves the last working generation active; inspect it with `logs`.

## Explicit operations

```sh
ccode extension reload <extension-id> --json
ccode extension deactivate <extension-id> --json
ccode extension status [<extension-id>] --json
ccode extension logs <extension-id> --follow --json
```

`reload`, `deactivate`, `status`, and `logs` require a running CCode app. Do not silently launch a new UI process unless the user requested it.

## Install from an origin

```sh
ccode extension install <source> --origin managed --json
ccode extension install <source> --origin personal --json
ccode extension install <extension-id> --origin gallery --json
ccode extension install <path> --origin dev --json
ccode extension install <extension-id> --origin zed-dev --json
ccode extension install <owner/repository> --origin github --json
```

For `managed`, `personal`, and `dev`, `source` is a local extension directory. For `gallery` and `zed-dev`, it is an extension identifier and may be paired with `--version`. For `github`, use `owner/repository` or a GitHub clone URL. Origin metadata is retained by CCode without changing the existing gallery installation flow.

## Completion criteria

The extension is complete only when the active generation is reported by CCode and each requested contribution can be exercised. For a keybinding-triggered contribution, verify both its contributed default and a temporary user override without committing the temporary override.
