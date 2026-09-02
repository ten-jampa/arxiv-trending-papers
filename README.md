# Founder-Sourcing Paper Radar

A vertical research-to-founder sourcing tool.

Given one high-signal AI paper, the system should produce a truthful founder-sourcing brief about its authors: who might be worth contacting, why, and what evidence supports that hypothesis.

## Current Status

This repo is at **Stage 1: artifact contracts** under the agentic-shipping workflow.

The current goal is not to build a daily digest. The current goal is to constrain the first useful vertical slice:

```text
one arXiv paper -> PDF evidence -> resolved authors -> founder signals -> Markdown sourcing brief
```

## Key Docs

- `_docs/spec.md` — product behavior and boundaries
- `_docs/system-design.md` — stage architecture and artifact flow
- `_docs/vertical-slice-v0.md` — first implementation slice and acceptance criteria
- `_docs/cli-contract.md` — command surface
- `_docs/data-contract.md` — artifact schemas and evidence rules
- `_docs/specs/person-registry-v0.md` — downstream JSON-backed people list / identity dedupe contract
- `_docs/source-smoketests.md` — verified public-source behavior
- `_docs/stack.md` — v0 stack decision
- `_docs/manual-test.md` — first manual test scenario
- `_docs/discovery-ranking.md` — later `discover -> rank -> founder-brief` shape and signal design bias
- `AGENTS.md` — durable agent instructions

## v0 Command Target

```bash
founder-radar founder-brief <arxiv-id-or-url>
```

The command should write:

```text
artifacts/<run_id>/candidate_paper.json
artifacts/<run_id>/paper_text_evidence.json
artifacts/<run_id>/resolved_authors.json
artifacts/<run_id>/founder_signals.json
artifacts/<run_id>/founder_brief.md
```

## Non-Goals Right Now

- no daily crawling
- no dashboard
- no cron
- no automated outreach
- no LinkedIn scraping
- no guessed founder scores
- no lab genealogy graph yet

Sparse and true beats rich and fake. That is the whole game here.
