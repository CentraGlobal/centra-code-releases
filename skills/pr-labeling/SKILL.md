---
name: pr-labeling
description: Inspect GitHub pull requests and apply a small, consistent label set from repository evidence. Use when suggesting, applying, creating, or reconciling PR labels; prefer existing labels and avoid review-trigger or workflow labels unless explicitly requested.
metadata:
  author: "CentraGlobal"
  version: "1.0.0"
  repository: "https://github.com/CentraGlobal/centra-code-releases"
---

# PR Labeling

Label a pull request from its actual change scope, repository conventions, and remaining rollout state. Use the `gh` CLI for GitHub reads and mutations.

## Authorization

- Treat inspection and label suggestions as read-only.
- Apply labels only when the user asks to label, classify, or reconcile the PR.
- Create repository labels only when the user authorizes label creation. If creation is not authorized, report the missing taxonomy and propose names, descriptions, and colors.
- Do not comment, review, assign, close, merge, or edit the PR body as part of labeling unless separately requested.
- Do not remove existing labels unless the user asks for reconciliation/removal. Report contradictory labels instead.

## Inspect Before Selecting

Resolve the repository and PR from the supplied URL/number or the current branch. Use an explicit `--repo owner/repo` for every GitHub command.

Collect at least:

1. PR title, body, base/head branches, current labels, state, and changed-file count.
2. Changed paths and, when paths are insufficient, the relevant diff hunks.
3. The complete live label catalog, including descriptions and colors.
4. Repository guidance such as `AGENTS.md`, `CONTRIBUTING.md`, and affected component instructions when available.
5. Recent merged PR labels only when the current catalog does not reveal the naming convention.

Useful commands:

```bash
gh pr view PR --repo OWNER/REPO --json number,title,body,state,baseRefName,headRefName,labels,files
gh pr diff PR --repo OWNER/REPO --name-only
gh label list --repo OWNER/REPO --limit 200 --json name,description,color
gh pr list --repo OWNER/REPO --state merged --limit 30 --json number,title,labels
```

Before using a label that can trigger automation, inspect its description and relevant workflow configuration. Labels containing concepts such as review, deploy, release, security escalation, priority, or merge blocking require explicit user intent or a documented repository rule.

If the repository is `CentraGlobal/centra-workspace`, read [references/centra-workspace.md](references/centra-workspace.md) before choosing labels.

## Choose a Minimal Label Set

Prefer two to five high-confidence labels, but use fewer when the evidence supports fewer. Classify along distinct dimensions:

- **Change kind:** bug, enhancement, documentation, dependency, refactor, or another established type.
- **Material scope:** the component or domain whose behavior actually changed.
- **Integration:** a provider or external system when the PR contains meaningful provider-specific behavior.
- **Lifecycle:** staging-only, needs manual testing, blocked, or another established rollout state.

Apply a dimension only when it adds useful information. Avoid label spam and do not label incidental files such as lockfiles, generated artifacts, provenance metadata, or docs accompanying a larger implementation as separate scopes.

Evidence rules:

- Use `documentation` for documentation-only changes, not every PR that updates docs.
- Use `bug` only when the PR corrects broken behavior; use `enhancement` for a new capability.
- Use component labels when that component has material logic, contract, configuration, or deployment changes.
- Use provider labels only for provider-specific work, not generic abstractions that could support the provider later.
- Use lifecycle labels only when the PR body, code guard, test gap, or rollout plan proves the state.
- Do not infer priority, security severity, production readiness, or approval state from the title alone.

## Reuse Existing Labels First

Match candidates against the live catalog in this order:

1. Exact name, case-insensitively.
2. Same normalized spelling after treating spaces, underscores, and hyphens as equivalent.
3. A semantic equivalent confirmed by its description and repository usage.

Prefer the repository's established singular/plural form and namespace. Never create near-duplicates such as `payment`, `payments`, and `area: payments`. If two existing labels are semantic duplicates, use the one established on recent merged PRs and report the taxonomy issue without rewriting repository labels.

## Create Missing Labels Carefully

When creation is authorized and no semantic equivalent exists:

- Create only labels that are reusable across future PRs; do not create labels for a branch, ticket, person, or one-off implementation detail.
- Follow the repository's existing naming pattern. If none exists, prefer lowercase kebab-case and short names.
- Write a description that states when the label applies.
- Use the repository's palette when established. Otherwise, keep related categories visually consistent: blue for components, purple for providers/domains, yellow or orange for lifecycle/manual-validation states, and red for defects or risk.
- Do not use `--force`; label creation must not silently overwrite an existing label's description or color.
- Refetch the catalog after creation or an already-exists race, then apply the resolved label.

Example:

```bash
gh label create LABEL --repo OWNER/REPO --description "WHEN THIS APPLIES" --color RRGGBB
```

## Apply and Verify

Apply the chosen labels in one PR edit where possible:

```bash
gh pr edit PR --repo OWNER/REPO --add-label LABEL_A --add-label LABEL_B
```

Then refetch the PR and verify the final label names. Report:

- labels applied;
- which labels were reused versus created;
- any requested label not applied and why;
- any existing contradictory label left untouched;
- the PR URL.

One agent should own mutations for a given PR to avoid races. Multiple agents may inspect or label different PRs independently.
