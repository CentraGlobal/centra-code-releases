# Runtime strategies

Read this reference after project discovery when deciding how to construct the disposable runtime.

## Selection rules

An explicit user choice wins. Otherwise rank candidates by fidelity to the documented developer workflow, then isolation, startup cost, and maintenance risk. A production-oriented Compose file is not automatically safer or more faithful than a small test harness.

Use only the services needed by the requested behavior and their declared dependency closure. Do not start an entire monorepo merely because one Compose file defines every component.

## Existing Compose configuration

1. Render with `docker compose ... config` before starting anything. Check service names, build contexts, mounts, networks, published ports, profiles, `depends_on`, health checks, and variable names.
2. Do not print the rendered configuration when it may contain secrets. Use targeted queries or redact values.
3. Override the project with `-p <unique-project>`, even when the file has a top-level `name:`.
4. Put temporary overrides outside the repository. Use them to:
   - bind ports to `127.0.0.1`;
   - choose dynamic or collision-free host ports;
   - add ownership labels;
   - replace shared hostnames or volumes with disposable equivalents;
   - inject explicitly authorized development credentials without persisting them.
5. Preserve repository build contexts and entrypoints unless a documented test mode provides a better one.

If Compose reuses explicit external networks, volumes, container names, or databases, replace them with project-scoped resources. Stop rather than attach to an ambiguous shared resource.

## Dev Container configuration

Resolve `dockerComposeFile`, `service`, `workspaceFolder`, mounts, features, and lifecycle commands from `.devcontainer/devcontainer.json`.

- Reuse its Compose files and service graph without requiring an editor attachment.
- Run only lifecycle commands needed for installation, schema setup, seeding, or tests.
- Treat editor conveniences and a complete all-service stack as optional.
- Check whether source mounts point at another checkout. Override them to the current worktree.

## Dockerfile-only projects

Build with a unique image tag derived from the generated project name. Inspect build arguments and stages before use. Prefer an existing development or test target; otherwise use the normal target and override only the command required for tests.

Add databases, caches, browsers, or stub servers only when documentation or test configuration establishes that dependency. A library dependency in a manifest alone is not enough evidence to invent infrastructure.

## Projects without container configuration

Create a harness in a temporary directory, not in the repository.

1. Pin the base image from repository toolchain files such as `.nvmrc`, `go.mod`, `.python-version`, `pyproject.toml`, `rust-toolchain.toml`, or Java toolchain configuration.
2. Respect the repository's lockfile and package manager.
3. Mount the source read-only and copy it into a disposable work volume before dependency installation or compilation when the toolchain writes into the source tree.
4. Use named project-scoped caches only when repeated phases materially benefit. Do not mount a user's global dependency or credential directories by default.
5. Run the repository's own test scripts. Do not synthesize a different test command merely because the language is recognized.

If the language version or required system services cannot be resolved reliably, ask for the missing choice instead of silently selecting `latest`.

## Ports and URLs

- Prefer no published ports for autonomous tests; containers should communicate on the project network.
- For interactive handoff, publish only required ports on `127.0.0.1` and inspect Docker's actual mappings before reporting URLs.
- Use dynamic ports when the app can discover them. Stable OAuth redirects, webhooks, absolute callback URLs, and browser origins may require fixed ports.
- Check fixed ports immediately before startup. If occupied, determine whether the owner is the intended runtime. Do not stop it without authorization.
- When a fixed redirect port is unavailable, ask before changing identity-provider configuration or introducing a proxy.

## Readiness and evidence

Use declared health checks first. Otherwise probe the narrowest meaningful readiness condition: database acceptance, queue ping, HTTP health endpoint, or application port plus a functional API response. Bound every wait and keep the user updated during long builds.

Capture:

- image build exit status;
- schema/migration exit status;
- `docker compose ps` health;
- bounded relevant logs for failures;
- test commands and exit status;
- functional HTTP, queue, database, or browser assertions required by the task.

A listening port is not proof that migrations, authentication, background workers, or requested product behavior work.
