# Vertical Slice v0

## Objective

Prove the core thesis with the smallest useful artifact:

> Given one arXiv paper, can we produce a truthful prospective-founder sourcing brief about its authors?

## Input

One of:

```text
2608.28447
2608.28447v1
https://arxiv.org/abs/2608.28447
```

## Output

A Markdown brief:

```text
artifacts/<run_id>/founder_brief.md
```

plus inspectable intermediate JSON artifacts:

```text
artifacts/<run_id>/candidate_paper.json
artifacts/<run_id>/paper_text_evidence.json
artifacts/<run_id>/resolved_authors.json
artifacts/<run_id>/founder_signals.json
```

## CLI Contract

```bash
founder-radar founder-brief <arxiv-id-or-url> [--output PATH] [--no-semantic-scholar]
```

Required behavior:

- Fetch arXiv metadata for exactly one paper.
- Download the arXiv PDF and extract text when available.
- Parse emails, domains, affiliation-ish lines, and URLs from the paper text.
- Extract raw authors exactly as returned by arXiv.
- Attempt author resolution using only allowed public sources.
- Attempt LinkedIn lookup mainly for author identity/contact enrichment, but require corroborating evidence before marking a profile resolved.
- Store GitHub URLs found in paper metadata, PDF text, or project pages as important builder-signal candidates.
- Generate a brief even when author resolution is incomplete.
- Mark unresolved fields as `not found` or `unresolved`.
- Include evidence URLs for all factual claims.

## Allowed v0 Sources

- arXiv API.
- Semantic Scholar public API, if reachable.
- URLs linked from arXiv metadata/comment/abstract.
- Directly linked project/code pages.

## Forbidden v0 Behavior

- No daily crawling.
- No broad internet people search unless explicitly marked as candidate evidence.
- No broad LinkedIn/private-profile scraping.
- No fabricated affiliations.
- No guessed GitHub/X profiles.
- No founder score without evidence.
- No automated outreach.

## Acceptance Criteria

- [x] One CLI command creates all required artifacts.
- [x] `candidate_paper.json` contains arXiv title, abstract, authors, categories, dates, and links.
- [x] `paper_text_evidence.json` contains PDF fetch status, extraction status, emails, domains, affiliation-ish lines, and URLs when found.
- [x] `resolved_authors.json` preserves raw author strings and marks unresolved authors honestly.
- [x] `founder_signals.json` contains only evidence-backed signals.
- [x] `founder_brief.md` includes verdict, paper summary, authors to watch, suggested outreach, unknowns, and evidence ledger.
- [x] All factual claims in the brief point to evidence.
- [x] Running with a known arXiv ID succeeds without credentials.
- [x] Tests cover ID parsing, arXiv fixture normalization, unresolved-author behavior, and brief rendering.

Audited 2026-09-02 against a real run of `founder-radar founder-brief 2608.31142v1`
(see git history for the exact commit). All nine criteria verified directly against
generated artifact contents, not just code inspection. One known gap found and fixed
during this audit: the per-author "Suggested outreach angle" line was previously a
static string identical for every author regardless of evidence; it now reflects each
author's actual `identity_confidence` and resolved profiles.

Known doc/implementation mismatch, not yet resolved: the CLI contract above documents
a `--no-semantic-scholar` flag, but Semantic Scholar enrichment was never implemented
(the pipeline is deterministic-only, plus an optional `--llm-contact-parser` flag not
mentioned in this doc). No flag was added to fake compliance; either implement
Semantic Scholar enrichment and the flag together, or update this doc to drop the flag
and document `--llm-contact-parser` instead.

## Manual Test Seed

Use an agents/RL paper with at least one link in comments or abstract if available. The test should verify that links are labelled by source and confidence, not magically promoted to official code.

## Stage Gate

Do not build batch ingestion until this vertical slice produces a brief that is useful enough for manual founder-sourcing review.
