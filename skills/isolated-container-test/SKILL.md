---
name: isolated-container-test
description: Create and operate disposable Docker or Compose test environments for the current repository or worktree, reusing existing devcontainer, Compose, Dockerfile, migration, seed, and test configuration when available or synthesizing a minimal runner outside the repository when none exists. Use when asked to spin up temporary containers, isolate integration or E2E tests, populate disposable test data, hand off local test URLs, resume an owned test runtime, or clean it up. Do not use for production deployments or ordinary host-only test runs.
metadata:
  author: "CentraGlobal"
  version: "1.0.0"
  repository: "https://github.com/CentraGlobal/centra-code-releases"
---

# Isolated Container Testing

Build a disposable runtime that reflects the project closely enough to test the requested behavior without colliding with other worktrees or mutating shared infrastructure.

## Establish the boundary

1. Read applicable repository instructions and preserve the user's current worktree changes.
2. Determine the requested scope: services, tests, seed data, authentication, and whether the user wants an interactive handoff.
3. Treat Docker access as permission to operate only the temporary environment. It does not authorize production, shared database, external identity, or cloud mutations.
4. Use **validation mode** by default: test, capture evidence, and clean up. Use **interactive mode** only when the user asks to access or test the running environment; leave it running and provide an exact cleanup command.

## Discover before composing

Run `python3 scripts/discover.py --root <project-or-worktree>` from this skill directory and inspect the returned candidates. The helper reads configuration metadata, not environment values.

Honor an explicitly requested configuration first. Otherwise prefer, in order:

1. documented development or test Compose configuration;
2. `.devcontainer` Compose configuration;
3. repository Compose configuration;
4. existing Dockerfiles;
5. a temporary manifest-derived runner outside the repository.

Read [references/runtime-strategies.md](references/runtime-strategies.md) when choosing or adapting a runtime strategy. Ask only when multiple viable choices would materially change fidelity, cost, or external dependencies.

## Give the runtime a unique identity

Run `python3 scripts/project_name.py --root <worktree> --purpose <short-purpose> --json`. Use its project name with `docker compose -p` and apply its labels to generated services and resources where possible.

- Never trust a fixed `name:` in a Compose file to provide worktree isolation; `-p` must override it.
- Check for existing resources with the proposed project name. Generate another suffix instead of adopting or deleting an ambiguous runtime.
- Keep generated overlays and harnesses in a `mktemp -d` directory outside the repository.
- Bind published ports to `127.0.0.1` by default. Prefer dynamically assigned host ports unless redirects, callbacks, or user-facing configuration require a stable port.
- Snapshot `git status --short` before and after the run. Report any generated worktree artifact; do not silently remove user files.

## Execute phase gates

Advance only after the current phase is healthy:

1. **Preflight** — confirm Docker/Compose availability, render configuration, inspect variable names without printing values, check ports and disk/resource constraints, and select the smallest service dependency closure.
2. **Build** — build unique local images or pull pinned base images. Do not pass unrelated host credentials or mount the Docker socket into project containers.
3. **Infrastructure** — start dependencies, then applications. Use health/readiness conditions with bounded timeouts instead of fixed sleeps.
4. **Schema** — run the project's normal disposable-database migration or schema bootstrap and verify its exit status.
5. **Data** — run documented idempotent seeds, then add only the focused synthetic fixtures needed by the request.
6. **Tests** — run focused checks first, followed by the broadest relevant integration/E2E checks. Verify observable behavior, not just process health.
7. **Disposition** — hand off a healthy interactive runtime or capture logs and remove the exact owned runtime.

Stop after a failed gate unless diagnosis or an in-scope correction can make the same gate pass. Never describe a partially failed seed or unavailable browser check as successful.

## Protect credentials and external systems

- Do not load production `.env` files, import production data, echo secrets, embed secrets in command text that will be reported, or persist credentials in generated overlays.
- Existing local runtime credentials may be injected in memory only when they are clearly intended for the same development environment. Validate stale credentials with a non-mutating probe and reveal only the result.
- Prefer a local identity provider. A shared development identity provider is read-only by default; resolving an existing subject does not authorize changing that user.
- Populate memberships and fixtures only in the disposable database unless the user explicitly authorizes another exact target.

Read [references/identity-and-seeding.md](references/identity-and-seeding.md) whenever authentication, external callbacks, migrations, or seed data are involved.

## Clean up safely

Before deletion, resolve the exact Compose project and confirm it belongs to this run through its name, labels, configuration path, and worktree fingerprint. Then use the same `-p` and configuration stack with `docker compose down --volumes --remove-orphans`; remove uniquely built local images only when they are not shared.

Never use `docker system prune`, global image/volume pruning, broad name globs, or cleanup based on an unresolved variable. Run `python3 scripts/verify_cleanup.py --project <project>` afterward. A nonzero result means cleanup is incomplete.

For interactive mode, read [references/interactive-handoff.md](references/interactive-handoff.md), keep the healthy runtime running, and do not schedule an invisible self-destruct operation.

## Completion report

Report:

- runtime state: running, cleaned, or blocked;
- project name, source commit, dirty-state result, and selected configuration;
- service health and loopback URLs;
- authentication identity without passwords or tokens;
- seeded scenarios and verification counts;
- exact commands/checks run and any gaps;
- exact cleanup command for a running handoff, or cleanup verification for a completed run.
