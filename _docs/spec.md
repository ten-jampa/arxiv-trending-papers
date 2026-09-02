# Founder-Sourcing Paper Radar — Product Spec

## Purpose

Identify AI researchers who may become prospective founders early enough to reach them before the market notices.

The system uses research-paper signals as an alternative sourcing layer for VC/investment work. It is a prospective founder radar, not a generic paper digest and not a literature-review bot.

## Target User

Tenzin: AI/VC-oriented operator who wants a short, evidence-backed list of researchers worth contacting, watching, or mapping into a thesis.

## Primary Job To Be Done

Given one high-signal AI paper, resolve its authors as real public people where possible, extract founder-relevant evidence, and produce a concise founder-sourcing brief.

## Vertical Slice v0

Input:

```text
one arXiv ID or arXiv URL
```

Output:

```text
one Markdown founder-sourcing brief
```

Pipeline:

```text
arXiv paper fetch
  -> candidate paper artifact
  -> author identity resolution artifact
  -> founder-signal extraction artifact
  -> founder brief artifact
```

The first implementation should support one paper only. Batch discovery and monitoring come later.

## Core Workflow

1. Fetch one paper from arXiv.
2. Normalize paper metadata into `candidate_paper.json`.
3. Enumerate author strings from the paper.
4. Resolve public author profiles only when evidence supports the match; separately attach paper-native author evidence even when identity remains unresolved.
5. Extract founder-relevant signals from verified paper metadata, PDF text, and resolved profiles.
6. Generate a Markdown founder-sourcing brief.
7. Mark unknowns explicitly instead of filling gaps with plausible nonsense.

## Core Objects

### CandidatePaper

- `paper_id`: canonical internal ID, e.g. `arxiv:2608.28447v1`.
- `arxiv_id`
- `title`
- `abstract`
- `authors`: raw author strings from arXiv.
- `categories`
- `published_at`
- `updated_at`
- `url`
- `pdf_url`
- `comment`
- `links`: paper/project/code/social links only if extracted from a verified source.
- `source_hits`: where this paper was discovered or validated.
- `candidate_reason`: why this paper is worth founder-radar analysis.

### ResolvedAuthor

- `name`: normalized author name.
- `paper_author_string`: original string from the paper.
- `affiliation`: best paper-native affiliation display when sourced; not proof of current employment.
- `paper_author_evidence`: paper-native emails, domains, affiliation lines, affiliation scope, ambiguous emails, confidence, and source URL.
- `profiles`: Semantic Scholar, homepage, lab page, GitHub, Google Scholar, DBLP, X, LinkedIn when verified.
- `identity_confidence`: `high`, `medium`, `low`, or `unresolved`.
- `evidence`: source URL plus claim.
- `ambiguities`: possible mistaken identities, unmapped emails, paper-level affiliations, or unresolved conflicts.

### FounderSignal

- `author_name`
- `signal_type`
- `value`
- `confidence`
- `evidence_url`
- `evidence_note`

Allowed initial signal types:

- `commercially_legible_problem`
- `project_page_present`
- `code_repo_present`
- `benchmark_or_dataset_created`
- `infra_or_tooling_orientation`
- `agent_or_rl_systems_focus`
- `repeat_theme`, only if prior papers are actually fetched.
- `industry_or_startup_collaboration`, only if affiliation/source proves it.

### FounderBrief

- paper summary
- authors to watch
- founder-relevance hypotheses
- commercialization angles
- suggested outreach actions
- evidence ledger
- gaps and unknowns

## Source Policy

Allowed in v0:

- arXiv API.
- arXiv PDF download and text extraction.
- Semantic Scholar public API, if available.
- URLs present in arXiv metadata, comments, or abstract.
- Public GitHub pages/repos only when linked directly or strongly matched with evidence.
- LinkedIn profile lookup for authors, but only as public identity/contact enrichment and never by name alone.

Optional but not required in v0:

- Hugging Face Papers Trending as a candidate-paper source after parser smoke tests pass.
- DAIR.AI AI Papers of the Week as a candidate-paper source after parser smoke tests pass.

Out of scope for v0:

- Broad LinkedIn scraping or private-profile scraping.
- Company-registration scraping.
- X/Twitter monitoring beyond links already present in source metadata.
- Lab-founder historical graph.
- Daily cron/Telegram automation.
- Full text PDF analysis.
- Web UI.

## Happy Path

1. User runs `founder-radar founder-brief 2608.28447`.
2. The CLI fetches the arXiv record.
3. The CLI downloads the PDF, extracts text, and parses the first-page contact/affiliation block when possible.
4. The CLI writes normalized intermediate artifacts.
5. The CLI resolves whatever author profiles can be resolved with evidence, including LinkedIn candidates when sufficiently corroborated.
6. The CLI stores any GitHub URLs found in paper metadata/PDF/project pages as important builder-signal evidence.
7. The CLI emits a Markdown brief with high-confidence claims and explicit unknowns.

## Success State

A useful v0 brief lets a VC operator decide:

- whether any author is worth reaching out to now,
- what specific commercial wedge to ask about,
- what evidence supports the hypothesis,
- what is still unknown and requires manual diligence.

## Non-Goals

- Ranking all AI papers.
- A daily digest.
- A generic research assistant.
- A full people-search product.
- A lab genealogy system.
- Automated outreach.
- Unverified founder scoring.

## Open Questions

1. Should the CLI package keep the repo name `arxiv-trending-papers` or expose the command as `founder-radar`?
2. Should v0 require Semantic Scholar, or gracefully run arXiv-only?
3. Should LLM summarization be included in v0, or should v0 generate a template brief with extracted evidence only?
4. What confidence threshold is required before surfacing GitHub/X/LinkedIn profiles?


## Later System Shape

After the single-paper founder brief is useful, the broader product should separate:

```text
discover -> rank -> founder-brief
```

And should prefer boolean or categorical signal inputs over fake-precise founder scores.
