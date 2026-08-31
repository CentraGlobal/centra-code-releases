# Centra Code Releases

This public repository hosts Centra Code desktop release artifacts and auto-update metadata.

Source code lives in the private `CentraGlobal/centra-code` repository.

## CCode CLI

CCode 1.18.0 and later installs its command-line interface as `ccode`. On macOS, run `cli: Install CLI Binary` from the command palette to create `/usr/local/bin/ccode`.

CCode does not install a `zed` command. That name remains available to Zed's own builds. Re-running the CCode installer also removes a legacy `/usr/local/bin/zed` link when, and only when, that link points to CCode's bundled CLI.

## Agent skills

### CCode Extension Builder

[`ccode-extension-builder`](skills/ccode-extension-builder/SKILL.md) teaches Agent Skills-compatible coding agents to validate, build, live-activate, watch, reload, and debug CCode extensions through the `ccode extension` CLI. It documents configurable extension commands and keybindings plus native panes, panels, docks, status items, and modals.

The skill requires CCode 1.19.0 or later. That release bundles the skill and provisions managed copies for supported local coding agents; this repository remains the public, independently installable source.

For Codex, ask the built-in skill installer:

```text
$skill-installer install the ccode-extension-builder skill from https://github.com/CentraGlobal/centra-code-releases/tree/main/skills/ccode-extension-builder
```

For other Agent Skills-compatible clients, install or copy the complete `skills/ccode-extension-builder` directory. Keep both reference files with `SKILL.md` so agents have the live-development protocol and contribution schema.

### CCode Browser

[`ccode-browser`](skills/ccode-browser/SKILL.md) teaches Agent Skills-compatible coding agents when and how to control CCode's built-in browser through its preinstalled MCP server or browser CLI. It covers the visible collaboration cursor, semantic locators, forms, dropdowns, uploads, drag and drop, and parallel work across tabs.

The skill requires CCode 1.18.0 or later. Its CLI examples use the supported `ccode browser` command.

For Codex, ask the built-in skill installer:

```text
$skill-installer install the ccode-browser skill from https://github.com/CentraGlobal/centra-code-releases/tree/main/skills/ccode-browser
```

For other clients implementing the [open Agent Skills standard](https://agentskills.io/specification), install or copy the entire `skills/ccode-browser` directory into that client's skill directory. Keep the referenced files with `SKILL.md`; copying only the entrypoint produces an incomplete installation.

Use a tagged skill release when a pinned version is required. Use the folder on `main` for the latest published instructions.

### PR Labeling

[`pr-labeling`](skills/pr-labeling/SKILL.md) teaches agents to inspect a pull request, reuse the repository's existing labels, and apply a small evidence-backed label set. It creates missing labels only when authorized, avoids duplicate taxonomy, and keeps review or workflow-trigger labels opt-in.

The bundled Centra Workspace reference maps canonical component paths and documents the established payment, provider, staging, and manual-testing label semantics. The skill expects an authenticated GitHub CLI with permission to read or update labels in the target repository.

For Codex, ask the built-in skill installer:

```text
$skill-installer install the pr-labeling skill from https://github.com/CentraGlobal/centra-code-releases/tree/main/skills/pr-labeling
```

For other Agent Skills-compatible clients, install or copy the complete `skills/pr-labeling` directory so its Centra-specific reference remains available.

### Dev Container Setup

[`devcontainer-setup`](skills/devcontainer-setup/SKILL.md) teaches agents to inspect a project's actual runtimes, dependencies, services, commands, ports, and environment variables before creating a minimal `.devcontainer` setup. It includes CCode-compatible `environments.json` declarations, safety boundaries for secrets and host access, proportional validation, and a project-specific checklist for the developer to finish.

For Codex, ask the built-in skill installer:

```text
$skill-installer install the devcontainer-setup skill from https://github.com/CentraGlobal/centra-code-releases/tree/main/skills/devcontainer-setup
```

For other Agent Skills-compatible clients, install or copy the complete `skills/devcontainer-setup` directory so its CCode environment reference remains available.
