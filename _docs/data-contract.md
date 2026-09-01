# Data Contract

The data model exists to preserve evidence boundaries between stages. The founder brief is only as trustworthy as these artifacts.

## Artifact Layout

```text
artifacts/<run_id>/
  candidate_paper.json
  paper_text_evidence.json
  resolved_authors.json
  founder_signals.json
  founder_brief.md
```

`artifacts/` is local output and ignored by git.

## CandidatePaper

```yaml
paper_id: string          # canonical ID, e.g. arxiv:2608.28447v1
arxiv_id: string
source: arxiv
url: string
pdf_url: string|null
title: string
abstract: string
authors: list[string]     # raw author names from arXiv
published_at: datetime
updated_at: datetime
primary_category: string|null
categories: list[string]
comment: string|null
journal_ref: string|null
doi: string|null
links: list[EvidenceLink]
source_hits: list[SourceHit]
candidate_reason: list[string]
fetched_at: datetime
```

## EvidenceLink

```yaml
url: string
label: paper|pdf|project|code|dataset|benchmark|social|unknown
source: arxiv_link|arxiv_comment|abstract|semantic_scholar|project_page|manual
confidence: high|medium|low
notes: string|null
```

## SourceHit

```yaml
source: arxiv|huggingface_trending|dair_weekly|semantic_scholar|manual
source_url: string
observed_at: datetime
raw_location: string|null
confidence: high|medium|low
```

## PaperTextEvidence

```yaml
paper_id: string
pdf_url: string
download_status: success|failed|not_checked
text_extraction_status: success|failed|not_checked
text_chars: integer
contact_block: string|null
emails: list[string]
email_domains: list[string]
affiliation_lines: list[string]
urls: list[EvidenceLink]
github_urls: list[EvidenceLink]
observed_at: datetime
errors: list[string]
```

Notes:

- Email/domain evidence comes from the paper PDF, not from a durable profile database.
- Affiliation lines are paper evidence, not proof of current employment.
- GitHub URLs found in paper text should be stored even if author ownership is unresolved.

## ResolvedAuthor

```yaml
author_key: string        # local run-scoped key
name: string
paper_author_string: string
affiliation: string|null
profiles:
  semantic_scholar: string|null
  homepage: string|null
  lab_page: string|null
  github: string|null
  google_scholar: string|null
  dblp: string|null
  x: string|null
  linkedin: string|null
identity_confidence: high|medium|low|unresolved
evidence: list[EvidenceClaim]
ambiguities: list[string]
```

## EvidenceClaim

```yaml
claim: string
source_url: string
observed_at: datetime
confidence: high|medium|low
notes: string|null
```

## FounderSignal

```yaml
author_key: string|null   # null for paper-level signals
paper_id: string
signal_type: string
value: string|number|bool
confidence: high|medium|low
evidence_url: string
evidence_note: string
```

Allowed v0 signal types:

- `commercially_legible_problem`
- `project_page_present`
- `code_repo_present`
- `benchmark_or_dataset_created`
- `infra_or_tooling_orientation`
- `agent_or_rl_systems_focus`
- `repeat_theme`
- `industry_or_startup_collaboration`

## FounderBrief

```yaml
paper_id: string
verdict:
  recommendation: reach_out|watch|skip|manual_diligence_needed
  confidence: high|medium|low
  reason: string
paper_summary: string
commercial_wedge: string|null
authors_to_watch: list[AuthorBrief]
unknowns: list[string]
evidence_ledger: list[EvidenceClaim]
```

## AuthorBrief

```yaml
author_key: string
name: string
identity_confidence: high|medium|low|unresolved
affiliation: string|null
profiles: map[string,string|null]
founder_relevance_hypothesis: string|null
suggested_outreach_angle: string|null
supporting_signals: list[FounderSignal]
caveats: list[string]
```

## Storage

v0 does not require SQLite. File artifacts are enough.

SQLite becomes useful only after batch discovery and repeated runs exist.

## No-Hallucination Rule

Every non-obvious factual claim must be represented as an `EvidenceClaim` or `FounderSignal` with a source URL. If the system cannot produce evidence, the correct value is `null`, `not found`, or `unresolved`.
