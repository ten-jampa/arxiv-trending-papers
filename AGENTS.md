# Agent Instructions

## Project Stage

This repository is in **Stage 1: artifact contracts**.

The first product slice is intentionally vertical and narrow:

```text
one arXiv paper -> resolved authors -> founder signals -> Markdown founder-sourcing brief
```

Do not expand into batch ingestion, cron, dashboards, lab graphs, or generic paper digests until the v0 gate in `_docs/vertical-slice-v0.md` passes.

## Source Of Truth

Before code changes, read these in order:

1. `_docs/spec.md`
2. `_docs/system-design.md`
3. `_docs/vertical-slice-v0.md`
4. `_docs/cli-contract.md`
5. `_docs/data-contract.md`
6. `_docs/source-smoketests.md`

## Agent skills

### Issue tracker

Issues and specs are tracked in GitHub Issues for `ten-jampa/arxiv-trending-papers`. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the default Matt Pocock triage labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context repo: use root `CONTEXT.md` and root `docs/adr/` when they exist. See `docs/agents/domain.md`.

## Change Discipline

- Keep changes small and artifact-gated.
- Every pipeline stage must write an inspectable artifact.
- Facts in final briefs must trace to source URLs in artifacts.
- Sparse and true beats rich and fake.
- Unknown fields must be `not found`, `not checked`, or `unresolved`.
- Do not merge author identities by name alone.
- Do not add external paid services or secrets.
- Do not add deployment/cron until the single-paper founder brief is useful.

## Verification Expectations

For documentation-only changes:

- Check required files exist.
- Check docs mention the v0 vertical slice.
- Review git diff before committing.

For code changes:

- Run unit tests.
- Run a CLI smoke test against one real arXiv ID if network is available.
- Verify generated artifacts exist.
- Include exact command output in the handoff.

## Allowed Side Effects Without Extra Approval

- Local files in this repository.
- Local tests and static checks.
- Public unauthenticated GET requests for research APIs.
- Git commits.
- Git pushes when the user explicitly asks to push.

## Ask Before

- Creating cron jobs.
- Writing to Obsidian.
- Posting/sending scheduled messages.
- Adding paid APIs or credentials.
- Deploying anything.
- Automated outreach.
- Broad people-search scraping.
