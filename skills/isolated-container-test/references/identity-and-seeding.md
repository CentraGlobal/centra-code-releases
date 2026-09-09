# Identity, external services, and seed data

Read this reference when the runtime needs authentication, callbacks, migrations, or populated data.

## Choose the identity boundary

Prefer, in order:

1. a disposable identity-provider container already defined by the project;
2. an existing local development identity provider;
3. read-only use of an explicitly intended shared development realm;
4. an application-supported test authentication mode.

Do not weaken product authentication, mint unverifiable tokens, or patch authorization solely to make the environment convenient.

When linking an existing external user to the disposable database:

- resolve the subject with a read-only query or trusted existing local fixture;
- verify that the identifier and requested email match exactly;
- seed only local user mirrors, roles, and memberships;
- never display passwords, client secrets, access tokens, refresh tokens, cookies, or full authorization headers;
- do not update external user attributes unless the user explicitly authorizes that exact mutation.

Treat cached or generated credentials as potentially stale. Validate a client with a non-mutating request that distinguishes client configuration failure from invalid test-user credentials, and report only the classification.

## Apply schema safely

- Confirm the database hostname and container/network ownership before migrations.
- Use the project's normal development bootstrap or migration chain.
- Never point migration commands at a host or URL merely because it already exists in an environment file.
- Verify important enum/status additions and migration history when the requested behavior depends on them.
- On a disposable fresh database, resetting the exact project volume is acceptable after confirming ownership; it is not acceptable for an ambiguous or shared database.

## Seed in layers

1. Run documented base seeders for organizations, permissions, roles, and core catalogs.
2. Verify base counts and relationships before scenario-specific data.
3. Run documented scenario seeders when they match the requested workflow.
4. Add narrowly scoped synthetic fixtures only when existing seeds are absent or fail for an unrelated reason.

Focused fixtures must use unmistakable IDs or metadata, remain inside the disposable database, and model every state the user needs to inspect. Verify them with queries or APIs after insertion.

If a broad seeder partially fails:

- identify which transaction or phase committed;
- do not rerun blindly when it could duplicate data;
- reset the exact disposable database or continue with idempotent focused fixtures;
- disclose the failed seed phase and what replaced it.

## External callbacks and integrations

Use an in-project or in-stack deterministic stub server for outgoing email, payment, webhook, or PMS callbacks. Do not send synthetic payloads to production, a teammate's endpoint, or an arbitrary public request collector.

Seed both successful and failed/retryable responses when the UX covers failure handling. Keep failures deterministic and prevent background retry loops from running indefinitely during interactive handoff.

## Seed verification

Check the invariants the UI or E2E flow relies on, such as:

- identity subject to local membership mapping;
- active roles and required permissions;
- organization/hotel or tenant ownership;
- integration configuration modes;
- snapshot/delivery state combinations;
- grouped activity and retry relationships;
- absence of calls to disabled external delivery targets.

Report synthetic identities by email or label only when useful, and never report their credentials unless the user supplied a disposable password specifically for this local environment.
