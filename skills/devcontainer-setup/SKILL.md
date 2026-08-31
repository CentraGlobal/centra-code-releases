---
name: devcontainer-setup
description: Create or improve a project-specific .devcontainer setup, including CCode environments.json declarations and a developer handoff checklist. Use when an agent should inspect a repository's runtimes, services, commands, ports, and environment dependencies and prepare a safe, reproducible local development container. Do not use for production deployment configuration.
metadata:
  author: "CentraGlobal"
  version: "1.0.0"
  repository: "https://github.com/CentraGlobal/centra-code-releases"
---

# Dev Container Setup

Prepare the smallest development-container configuration that reproduces the project's documented local workflow. Base every choice on repository evidence, preserve existing developer workflows, and leave the developer with an actionable checklist for anything the agent cannot safely complete.

## Authorization and Safety

- Treat a request to set up a dev container as authorization to inspect the repository, edit the project-scoped `.devcontainer` directory, and perform static validation.
- Do not start services, run migrations or seeds, connect to shared infrastructure, import real data, or publish images unless the user separately requests that action.
- Building an image can download and execute third-party content. Build only when the user asks for a tested/runnable container or when build validation is clearly part of the requested task, and inspect the Dockerfile, Features, and lifecycle commands first.
- Never read, copy, print, or commit live secret values. Do not copy a developer's `.env`, credential files, SSH keys, cloud configuration, Docker socket, or host credential stores into the container.
- Avoid `privileged`, host networking, added Linux capabilities, security-profile relaxation, and host bind mounts outside the workspace unless a demonstrated requirement justifies the minimum access and the user approves it.
- Check the worktree before editing. Preserve unrelated changes and adapt an existing dev-container setup rather than replacing it wholesale.

## Inspect the Project First

Read repository instructions and the files that define the real development workflow. Resolve at least:

1. The workspace root and whether the repository is a monorepo or has multiple independently runnable projects.
2. Language runtimes and versions from version files, manifests, lockfiles, CI, build images, and toolchain configuration.
3. The canonical dependency-install, build, run, test, lint, migration, and seed commands from documentation, scripts, task runners, and CI.
4. Required system packages, native libraries, package-manager configuration, private registries, architecture constraints, and generated-code tools.
5. Local supporting services, service health dependencies, ports, volumes, and network names from Compose files and application configuration.
6. Environment variable names and semantics from committed examples, configuration parsing, schemas, and docs. Classify each as a safe committed default, a secret, or unresolved; never infer values from live environment files.
7. Existing Dockerfiles, Compose files, `.devcontainer` files, ignore files, and repository-specific validation commands that should be reused.

Prefer pinned versions already established by the project. If evidence conflicts, follow the repository's documented local workflow and report the conflict. Ask the user only when an unresolved choice would materially change the topology, security boundary, or developer experience; otherwise choose the minimal evidence-backed setup and disclose the assumption.

## Design the Configuration

Use `.devcontainer/devcontainer.json` as the default entrypoint. Use a named `.devcontainer/<name>/devcontainer.json` only when the repository genuinely needs multiple selectable environments.

Choose one approach:

- Use a trusted, versioned development image when the project needs only a runtime and common tools.
- Add `.devcontainer/Dockerfile` when reproducible operating-system packages, native toolchains, users, or filesystem setup are required.
- Add a development-only Compose file when the project needs multiple coordinated local services. Reuse an existing Compose definition only when its defaults are safe for local development; prefer an override or dedicated file over changing production behavior.

Keep the configuration focused:

- Install the runtimes and native dependencies proven by the repository, not a speculative toolbox.
- Use the project's package manager and lockfiles. Do not run an unpinned global installer when an image, Feature, lockfile, or checked-in script already provides the tool.
- Give every configuration an explicit, stable `name`; CCode uses it as the environment container key for image- and Dockerfile-based configurations.
- Run interactive development as a non-root user when supported. Use root only for image construction steps that require it.
- Make the workspace path and Compose service explicit when Compose is used.
- Forward only ports developers need to reach from the host. Do not publish database or administration ports to all interfaces by default.
- Preserve dependency caches with named volumes only when they materially improve the workflow and cannot leak credentials across unrelated projects.
- Put deterministic, idempotent dependency setup in `postCreateCommand`. Keep `postStartCommand` lightweight and never use lifecycle commands to migrate, seed, or mutate shared systems automatically.
- Add editor customizations only when the repository proves that an extension is required for the primary workflow.

Do not edit application code or production deployment files merely to make the container convenient. If the application cannot run safely without such a change, stop and explain the boundary.

## Declare CCode Environments

Create `environments.json` beside every target `devcontainer.json` when it is missing, even when the initial `variables` object is empty. Read [references/ccode-environments.md](references/ccode-environments.md) before writing it.

Populate declarations only from committed evidence:

- Commit ordinary values only when they are intentionally public development defaults.
- Represent credentials and sensitive values with logical `secret` identifiers, never placeholder secret text.
- Omit unresolved non-secret values rather than inventing a value that may make the application behave unsafely; add them to the developer checklist.
- Match each `containers` key to the exact Compose service name. For an image or Dockerfile configuration, use the `name` from `devcontainer.json`.
- Use `dev_container_runtime` unless a value is specifically needed while resolving the container build. Avoid build-time secrets when a runtime value works.

If the repository already uses `.env.example`, keep it as application documentation. Do not replace it with `environments.json`; the two files serve different consumers.

## Implement Without Hiding Decisions

Create only files required by the selected design. Typical output is:

```text
.devcontainer/
|-- devcontainer.json
|-- environments.json
|-- Dockerfile          # only when an image plus Features is insufficient
`-- compose.yaml        # only when local supporting services are required
```

Use comments sparingly and only for non-obvious reasons. Do not leave generic TODOs in executable configuration. Put user-specific setup work in the final checklist with the exact file, variable, command, or external prerequisite involved.

## Validate Proportionally

Always:

1. Parse strict JSON files, including `environments.json`; parse JSON-with-comments files with a JSONC-aware tool.
2. Confirm every referenced Dockerfile, Compose file, workspace path, lifecycle script, and environment file exists at the path expected relative to `devcontainer.json`.
3. If Compose is used, run its configuration renderer such as `docker compose -f FILE config` without starting services.
4. Use the Dev Container CLI's configuration validation when it is already available. Do not install global tooling merely to make the validation report look complete.
5. Review the final diff for plaintext secrets, unsafe mounts or privileges, unpinned project versions, accidental production configuration changes, and commands with external side effects.

When authorized to build, build the selected configuration without injecting real credentials. Do not start the application automatically. If the build requires a secret or private registry, stop at that boundary and make the missing developer action explicit.

Run a representative project command inside the container only when the container can be created without sensitive or destructive setup and the request includes runtime verification. Prefer a version check or non-mutating test/build command over migrations, seeds, or live integrations.

## Handoff

Finish with:

- the detected stack and chosen container design;
- files created or changed;
- validation actually performed and its result;
- assumptions and anything left unverified;
- a **Developer checklist** containing only concrete remaining actions.

Make every checklist item verifiable and project-specific. Include, as applicable:

- installing and starting the required Docker- or Podman-compatible engine;
- authenticating to each proven private image or package registry;
- supplying each required CCode secret through **Containers → Environment Variables…**;
- deciding values for unresolved non-secret variables;
- rebuilding or recreating the container after configuration or environment changes;
- running exact dependency, migration, seed, and application commands that were intentionally not automated;
- confirming each forwarded port or local URL;
- running the project's canonical tests, lint, or health check;
- resolving any host architecture or optional-tool limitation.

Do not claim the environment is ready when validation was skipped or a required checklist item remains. Distinguish an agent-verified result from a developer action.

## Authoritative References

- Dev Container specification: <https://containers.dev/implementors/spec/>
- `devcontainer.json` reference: <https://github.com/devcontainers/spec/blob/main/docs/specs/devcontainerjson-reference.md>
