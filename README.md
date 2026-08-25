# Centra Code Releases

This public repository hosts Centra Code desktop release artifacts and auto-update metadata.

Source code lives in the private `CentraGlobal/centra-code` repository.

## CCode CLI

CCode 1.18.0 and later installs its command-line interface as `ccode`. On macOS, run `cli: Install CLI Binary` from the command palette to create `/usr/local/bin/ccode`.

CCode does not install a `zed` command. That name remains available to Zed's own builds. Re-running the CCode installer also removes a legacy `/usr/local/bin/zed` link when, and only when, that link points to CCode's bundled CLI.

## Agent skills

### CCode Browser

[`ccode-browser`](skills/ccode-browser/SKILL.md) teaches Agent Skills-compatible coding agents when and how to control CCode's built-in browser through its preinstalled MCP server or browser CLI. It covers the visible collaboration cursor, semantic locators, forms, dropdowns, uploads, drag and drop, and parallel work across tabs.

The skill requires CCode 1.18.0 or later. Its CLI examples use the supported `ccode browser` command.

For Codex, ask the built-in skill installer:

```text
$skill-installer install the ccode-browser skill from https://github.com/CentraGlobal/centra-code-releases/tree/main/skills/ccode-browser
```

For other clients implementing the [open Agent Skills standard](https://agentskills.io/specification), install or copy the entire `skills/ccode-browser` directory into that client's skill directory. Keep the referenced files with `SKILL.md`; copying only the entrypoint produces an incomplete installation.

Use a tagged skill release when a pinned version is required. Use the folder on `main` for the latest published instructions.
