# Centra Workspace PR Labeling

Use this reference only for `CentraGlobal/centra-workspace`. Always fetch the live label catalog first; this file defines selection conventions, not a permanently complete catalog.

## Repository Scope

Canonical component paths and preferred label candidates are:

| Path | Preferred scope label |
| --- | --- |
| `services/payment/` | `payments` |
| `services/backend-api/` | `backend-api` |
| `services/bridge-api/` | `bridge-api` |
| `services/workers/` | `workers` |
| `services/pos-backend/` | `pos-backend` |
| `apps/admin-panel/` | `admin-panel` |
| `apps/frontend/` | `frontend` |
| `apps/obe/` | `obe` |
| `apps/pos/` | `pos` |
| `apps/pos-admin/` | `pos-admin` |

These are candidates, not permission to create all component labels. Reuse them when present. Create a missing component label only when label creation was authorized and the label will be useful beyond the current PR.

For cross-component payment work, `payments` is the primary domain label even when backend API, OBE, or admin files support the same payment feature. Add component labels only when maintainers benefit from distinguishing ownership or review scope.

## Established Semantics

- `payments`: material payment-service, tokenization, transaction, gateway, reconciliation, refund, payout, or payment automation behavior.
- `turnstay`: material TurnStay-specific integration behavior or configuration.
- `staging`: deliberately limited to staging/test mode or awaiting production enablement; not merely tested in staging.
- `needs-manual-testing`: automated validation is complete or substantial, but credentials, hardware, a third party, browser flow, or another external dependency still requires manual validation.
- `enhancement`: a new user-facing or platform capability.
- `bug`: a correction to incorrect behavior.
- `documentation`: a documentation-only PR.
- `hermes-review`: opt-in automation trigger. Never add it unless the user explicitly asks for a Hermes advisory review.

Generic issue-management labels such as `good first issue`, `help wanted`, `question`, `invalid`, `duplicate`, and `wontfix` rarely describe implementation PRs. Do not apply them merely because they exist.

## New Label Style

When authorized to extend the Centra taxonomy, use lowercase kebab-case with a concise operational description. Prefer:

- component/scope: blue `1D76DB`;
- provider/integration: purple `6F42C1`;
- staging/lifecycle: yellow `FBCA04`;
- manual validation: orange `D93F0B`.

Do not change existing colors to enforce this palette.

## Selection Example

A staging-only TurnStay card-tokenization and scheduled-payment PR that still needs real vendor credentials is well described by:

- `payments`
- `turnstay`
- `staging`
- `needs-manual-testing`

Add `enhancement` only when the repository consistently pairs a change-kind label with domain labels or the user requests that dimension. Do not add `hermes-review` without an explicit review request.
