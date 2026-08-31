---
name: ccode-extension-builder
description: Build, validate, live-activate, reload, and debug CCode extensions, including commands, configurable keybindings, panes, panels, docks, status items, and modals. Use for creating or updating a CCode extension; do not use for ordinary application features compiled directly into CCode.
metadata:
  author: "CentraGlobal"
  version: "1.0.0"
  repository: "https://github.com/CentraGlobal/centra-code-releases"
  ccode-requirement: "CCode 1.19.0 or later running with the ccode CLI on PATH."
---

# CCode Extension Builder

Build the extension in the user's project or another user-selected source directory. Do not write directly into CCode's installed-extension directory.

Use the CCode CLI as the development control plane:

1. Inspect any existing `extension.toml`, Rust crate, and extension resources before choosing a scaffold.
2. Keep contribution and command identifiers stable across reloads.
3. Run `ccode extension check <path> --json` and address every reported diagnostic.
4. Run `ccode extension dev <path> --activate --watch --json` to build and activate the extension in the running CCode app.
5. Exercise contributed commands and UI. When a command has a default keybinding, also verify a user override.
6. Iterate using structured diagnostics. A failed generation should leave the last working generation active.

Extension-provided keybindings are defaults. Never edit the user's keymap to force a binding, remove an override, or bypass a conflict. Register extension commands with stable IDs and let users configure their keys through CCode's keymap.

Declare only capabilities the extension actually needs. Do not approve capability changes on the user's behalf.

For the CLI lifecycle and structured events, read [references/live-development.md](references/live-development.md). For commands and native UI contribution syntax, read [references/contributions.md](references/contributions.md).
