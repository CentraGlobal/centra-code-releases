# Integration Compatibility Tests

Read this reference when a PR can alter integration mappings, external DTOs, serializers, event handlers, provider routing, request delivery, acknowledgements, retries, or reservation/inventory/rate/restriction sync.

The purpose is to prove that an internal change does not unintentionally change the data or delivery behavior observed by External PMSs or channels.

## Test Environment

Run the affected Centra services against disposable provider mocks in an isolated Docker or Compose network. Use one strict mock per external role rather than a generic always-successful server.

At minimum, when those paths are affected, model:

- a **Pluriel External PMS** endpoint that captures Centra's outbound requests and can return success, timeout, retryable error, permanent error, and duplicate acknowledgement scenarios;
- a **HotelRunner channel** endpoint that captures outbound availability, rate, and restriction requests and can inject inbound reservations with HotelRunner room and rate codes;
- the database, queue, and worker versions used by the changed path, with deterministic fixtures and no production credentials.

CI must not contact live providers. Keep mock behavior and expected contracts versioned with the code.

## Establish Base-versus-Head Evidence

For identical seed data and inputs:

1. Run the relevant flow from the PR's merge base and capture the complete provider-observed transcript.
2. Run the same flow from the PR head.
3. Compare request destination, method, path, headers, body, request count, ordering, idempotency keys, retry timing class, and acknowledgement handling.
4. Canonicalize only genuinely dynamic values such as trace IDs or timestamps. Do not remove new fields, reorder semantically ordered arrays, or weaken type comparisons to make a snapshot pass.
5. Fail on any difference unless the PR contains an explicitly approved external-contract change and the test documents that exception.

Use exact or schema-plus-golden assertions. Subset assertions such as “contains these keys” are insufficient because they allow accidental outbound fields.

## Mandatory External PMS Cases

When External PMS outbound is in scope, prove:

- the complete request remains equal to the base behavior for the same reservation or update;
- internal/channel-only metadata is absent from the wire payload;
- adding `channels` or another internal field does not add a JSON/XML key, change null/omission behavior, select more targets, or mutate another provider's request;
- provider-specific transformation cannot modify a DTO later reused for another target;
- transient failures retry according to the existing policy without duplicate business effects;
- permanent failures do not retry forever, block unrelated properties, or acknowledge work prematurely.

For the Pluriel mock, configure unknown-field rejection in at least one test. Include an explicit assertion that the outbound payload contains no `channels` field or derived channel structure when the released contract does not contain it.

## Mandatory HotelRunner Cases

HotelRunner room/rate identities can be contextual. Build fixtures in which the same logical rate-plan ID occurs in multiple rooms while HotelRunner exposes different room-specific external codes.

For example:

```text
Internal rate plan 3219 + Double room -> 288398:HR:288391
Internal rate plan 3219 + Junior suite -> 288399:HR:288392
Internal rate plan 3219 + Senior suite -> 288400:HR:288393
```

Prove that:

- outbound rates and restrictions select the external rate code by the full room/rate context;
- iteration or database row order cannot change which code is selected;
- an inbound reservation resolves the HotelRunner room/rate pair to exactly one internal room/rate pair;
- duplicate identifiers across rooms neither overwrite each other nor become “last row wins” maps;
- master, derived, refundable, and non-refundable variants retain the existing HotelRunner code semantics;
- unknown or unmatched pairs follow the established rejection/manual-mapping path rather than silently choosing another room or rate.

Run the collision case repeatedly with shuffled mapping insertion order. The provider-observed result must be identical on every run.

## Cross-Provider Isolation

Emit one event that is eligible for multiple integrations and capture every request. Assert independently that:

- only intended providers are contacted;
- each provider receives a separately constructed or safely cloned payload;
- provider A's normalization cannot add, delete, or rewrite fields in provider B's request;
- failure or slowness in one provider does not corrupt, suppress, or duplicate another provider's request;
- logging and dead-letter records identify the correct property, integration, room, rate, and event without leaking secrets.

This test is required when common event models, shared payload maps, generic serializers, fan-out loops, or integration target selection change.

## Database and Upgrade Compatibility

Run the compatibility suite twice:

1. against a database created from the new schema; and
2. against representative pre-change data upgraded through the real migrations.

Include duplicate IDs across contextual mapping dimensions, null or legacy values, disabled integrations, and enough rows to exercise batching. During rollout-sensitive changes, test old producer/new consumer and new producer/old consumer combinations or document the deployment barrier that makes a combination impossible.

## Required Evidence in the PR

The PR should link or attach:

- the Compose/test harness and deterministic fixtures;
- base and head SHAs used for comparison;
- strict captured-request assertions or golden files;
- results for happy path, collision, retry, duplicate delivery, timeout, and unknown-field cases;
- a statement of any intentional difference, its approval, rollout, and rollback plan;
- the CI job that runs the suite on every relevant PR.

A local screenshot, successful `200` response, or mock that accepts arbitrary payloads does not prove compatibility.
