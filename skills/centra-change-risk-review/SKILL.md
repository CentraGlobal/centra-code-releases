---
name: centra-change-risk-review
description: Review Centra pull requests for sync-contract compatibility, small and coherent scope, existing-data and migration safety, sufficient tests, and scale or downtime risk. Use before approving, pushing, or merging changes that may affect integrations, persistence, runtime behavior, or new functionality; withhold approval until every applicable gate has evidence.
metadata:
  author: "CentraGlobal"
  version: "1.0.0"
  repository: "https://github.com/CentraGlobal/centra-code-releases"
---

# Centra Change Risk Review

Act as a release-safety gate, not only a diff commentator. Inspect the full execution paths affected by a change and decide whether it is safe to approve, push, or merge.

## Authorization

- Treat repository inspection, local tests, and a written verdict as read-only review work.
- Post a GitHub review or comment only when the user asks. Approve, push, or merge only when separately authorized and every required gate passes.
- Keep production read-only unless the user explicitly authorizes a specific production action.
- Do not repair the PR as part of review unless the user also requests implementation.

## Non-Negotiable Decision Rule

Return **DO NOT APPROVE** when any applicable gate lacks evidence or fails. A gate may be **N/A** only with a concrete reason grounded in the changed paths and traced call graph. Green CI, author assurances, or successful happy-path unit tests do not replace missing compatibility, migration, or scale evidence.

Use these five required gates:

1. Sync and external contract compatibility.
2. Small, coherent PR scope.
3. Existing-data and database-change safety.
4. Tests for new and changed behavior.
5. Scale and downtime safety.

Approve only when all five are **PASS** or evidence-backed **N/A**.

## Establish the Review Baseline

Resolve the repository and PR from the supplied URL or current branch. For GitHub reads, use an explicit `--repo OWNER/REPO`. Collect:

1. PR title, body, base and head SHAs, commits, changed paths, diff statistics, checks, and review state.
2. Repository and nearest component instructions, ownership, deployment notes, schemas, migrations, and test commands.
3. The merge-base implementation of every changed public boundary. Compare behavior with the released base, not merely with the author's intended design.
4. Callers, consumers, serializers, mapping builders, queues, retry handlers, database queries, and deployment order outside the edited hunks.
5. Existing fixtures, captured payloads, contract tests, and operational limits relevant to the affected flow.

Useful commands include:

```bash
gh pr view PR --repo OWNER/REPO --json number,title,body,url,baseRefName,baseRefOid,headRefName,headRefOid,commits,files,statusCheckRollup,reviews
gh pr diff PR --repo OWNER/REPO --name-only
gh pr diff PR --repo OWNER/REPO
git diff --stat MERGE_BASE...HEAD
```

Do not limit the review to the visible diff. Trace each changed value from its source to every persistence and external-output sink.

## Gate 1: Sync and External Contract Compatibility

Treat the currently released outbound behavior as frozen unless a separately approved requirement explicitly changes that external contract. Internal model growth does not authorize outbound growth.

Verify every affected inbound and outbound path for External PMSs, channel managers, OTAs, webhooks, queues, and internal consumers:

- HTTP method, destination, path, query, headers, authentication placement, content type, and encoding;
- exact body fields, nesting, types, nullability, omission rules, names, identifier formats, currency and date semantics;
- request count, target selection, ordering, batching, idempotency keys, acknowledgement, retry, and deduplication behavior;
- provider capability flags and directionality: a field accepted inbound or used internally must not automatically be serialized outbound;
- mapping cardinality and context. Never collapse a composite identity such as `(room type, rate plan)` into a room-agnostic map when either side can repeat across rooms;
- shared mutable objects. Provider-specific normalization must operate on a clone or provider-owned DTO so one target cannot mutate another target's payload.

An added outbound field is a contract change even if it is optional or ignored by one mock. For example, if channel data is introduced internally but External PMS outbound must remain unchanged, fail the review if `channels` or any derived channel value appears in that PMS request, changes target fan-out, or alters serialization.

Require the provider compatibility suite in [references/integration-compatibility-tests.md](references/integration-compatibility-tests.md) whenever integration mappings, reservation/inventory/rate/restriction events, DTOs, serializers, delivery logic, or provider routing can change. If an external contract is intentionally changed, require explicit product/provider approval, versioning or a compatible rollout, consumer readiness, rollback strategy, and tests for both old and new forms.

## Gate 2: Small and Coherent PR Scope

A PR passes only when one reviewer can reason about one cohesive behavior and its required tests and migrations together.

Require a split when the PR contains independently shippable concerns, unrelated cleanup, multiple product behaviors, broad formatting or generated churn, or cross-component changes that do not need atomic deployment. Also require a split when size or coupling prevents reliable contract, data, or scale analysis.

Do not use line count alone. Apply the independence test: if part A can be deployed or reverted safely without part B, they should normally be separate PRs. Accept a larger atomic PR only when the author documents why splitting would create an invalid intermediate state, organizes the diff into reviewable commits, and provides per-boundary validation.

Generated artifacts and lockfiles do not excuse an otherwise mixed change. If the PR must be split, mark this gate **FAIL** and name the proposed slices and their safe merge order.

## Gate 3: Existing-Data and Database Safety

Inspect migrations and changes to schemas, indexes, constraints, defaults, enums, queries, ORM models, serialization, and data interpretation. Determine effects on both fresh databases and existing production-shaped rows.

Require evidence for:

- backward and forward compatibility during rolling deployment;
- nullable/default transitions and old rows missing newly expected values;
- table rewrites, full scans, lock duration, index construction, and transaction size;
- uniqueness or foreign-key changes against duplicate, orphaned, malformed, and high-volume existing data;
- backfill batching, resumability, idempotency, observability, and partial-failure recovery;
- read/write behavior while old and new application versions overlap;
- rollback or roll-forward recovery without silent data loss or reinterpretation.

Destructive drops, lossy type conversions, enum removals, unbounded updates, and constraints added before cleanup fail unless a staged, measured migration proves safety. Require migration tests on both an empty database and a representative pre-change database, with explicit before/after invariants. Never assume a migration is safe because it succeeds on an empty database.

## Gate 4: Tests for New and Changed Behavior

Every new behavior needs tests at the lowest useful level plus the real boundary it changes. Every bug fix needs a regression test that fails on the base or unfixed implementation for the reported reason.

Require, as applicable:

- unit tests for branching, validation, and mapping logic;
- integration tests for databases, queues, caches, and service boundaries;
- strict contract tests for all affected external providers;
- end-to-end coverage for critical business flows;
- negative, retry, timeout, idempotency, concurrency, and partial-failure cases;
- proof that new tests execute in required CI rather than only locally.

Mocks must assert what Centra sends, not merely return a success response. Avoid subset-only JSON assertions at external boundaries: unexpected fields, extra targets, and changed types must fail. Do not call live providers from CI.

If meaningful behavior is untested, mark this gate **FAIL** and specify the exact missing cases and layer.

## Gate 5: Scale and Downtime Safety

Trace the worst credible production path, not only the single-record happy path. Inspect for:

- N+1 queries, unbounded scans or pagination, large in-memory collections, and repeated serialization;
- synchronous fan-out, provider amplification, retry storms, poison-message loops, and missing backpressure;
- hot locks, long transactions, blocking index changes, pool exhaustion, goroutine/task leaks, and unbounded concurrency;
- absent timeouts, cancellation, rate limits, circuit breaking, dead-letter handling, and graceful shutdown;
- incompatible rolling deploys, startup migration coupling, cache stampedes, and schema/app ordering hazards;
- cardinality-sensitive metrics or logs and payloads that expose secrets or create excessive cost.

Require a bounded complexity argument, query plan, benchmark, load test, or failure-injection result proportional to the risk. A request path, consumer, scheduler, or migration that can exhaust shared resources or require downtime without an approved maintenance plan fails this gate.

## Report the Verdict

Lead with findings ordered by severity and include file/line evidence. Distinguish confirmed defects from risks that still need proof.

Use this compact structure:

```text
Verdict: APPROVE | DO NOT APPROVE

Blocking findings
- [Critical/High/Medium] Finding — consequence, trigger, evidence, required fix/test

Required gates
- Sync compatibility: PASS | FAIL | N/A — evidence
- PR scope: PASS | FAIL | N/A — evidence
- Existing data/database: PASS | FAIL | N/A — evidence
- Test coverage: PASS | FAIL | N/A — evidence
- Scale/downtime: PASS | FAIL | N/A — evidence

Compatibility statement
- Exact external behaviors compared and whether outbound/inbound structures remain unchanged.

Validation
- Tests/checks run, results, and anything not run.
```

Use **Critical** for likely widespread data loss, corruption, security exposure, or outage; **High** for wrong external data, broken compatibility, unsafe migration, or serious availability risk; and **Medium** for a required test or scope gap that prevents confidence. Do not bury a required-gate failure among optional suggestions.
