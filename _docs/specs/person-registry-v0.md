# Person Registry v0 Spec

## Purpose

Track researchers as durable people records. Papers are evidence; the people list is the asset.

This spec is downstream of author resolution. Do not build or populate person records by reparsing papers directly when `resolved_authors.json` already contains the upstream artifact contract.

## Upstream Input

Primary input:

```text
artifacts/<run_id>/resolved_authors.json
```

Each author record should include:

```yaml
author_key: string
name: string
paper_author_string: string
affiliation: string|null
identity_confidence: high|medium|low|unresolved
paper_author_evidence:
  raw_author_name: string
  emails: list[string]
  email_domains: list[string]
  affiliation_lines: list[string]
  affiliation_scope: per_author|paper_level|none
  ambiguous_emails: list[string]
  paper_evidence_confidence: high|medium|ambiguous|none
  source: paper_contact_block|paper_text_evidence
  source_url: string
  notes: list[string]
profiles: map[string,string|null]
evidence: list[EvidenceClaim]
ambiguities: list[string]
```

Key boundary:

```text
paper_author_evidence != resolved external identity
```

Paper evidence can be high confidence while `identity_confidence` remains `unresolved`.

## Storage

Use JSON files for now. Keep the schema portable for a later database migration when deployment/scaling requires it.

Suggested files:

```text
data/people/people.json
data/people/author_observations.jsonl
data/people/identity_clusters.json
data/people/review_feedback.jsonl
```

## Records

### PersonRecord

```json
{
  "person_id": "person_<stable_slug_or_hash>",
  "display_name": "Minghui Xu",
  "status": "watch",
  "identity_confidence": "unresolved",
  "current_best_affiliation": {
    "value": "Stanford University",
    "confidence": "paper_affiliation_block",
    "source": "arxiv:2608.28447v1"
  },
  "emails": [
    {
      "value": "minghuix@stanford.edu",
      "source": "paper_contact_block",
      "paper_id": "arxiv:2608.28447v1",
      "confidence": "high"
    }
  ],
  "domains": ["stanford.edu"],
  "profiles": {
    "linkedin_candidates": [],
    "linkedin_verified": null,
    "semantic_scholar": null,
    "homepage": null,
    "github": null
  },
  "papers_seen": ["arxiv:2608.28447v1"],
  "strongest_founder_signals": [],
  "last_reviewed_at": null,
  "evidence": []
}
```

### PaperAuthorObservation

One paper-specific observation of a raw author string.

```json
{
  "observation_id": "obs_<hash>",
  "paper_id": "arxiv:2608.28447v1",
  "raw_author_name": "Minghui Xu",
  "normalized_name": "minghui xu",
  "paper_author_evidence": {
    "emails": ["minghuix@stanford.edu"],
    "affiliation_lines": ["Department of Energy Science and Engineering", "Stanford University"],
    "domains": ["stanford.edu"],
    "affiliation_scope": "paper_level",
    "paper_evidence_confidence": "high"
  },
  "linked_person_id": "person_minghui_xu_<hash>",
  "link_reason": "exact_email_match_or_new_person"
}
```

### IdentityCluster

Candidate grouping for soft matches that should not auto-merge.

```json
{
  "cluster_id": "cluster_<hash>",
  "candidate_person_ids": ["person_a", "person_b"],
  "reason": "same normalized name and overlapping affiliation",
  "merge_status": "needs_review"
}
```

### ReviewFeedback

```json
{
  "created_at": "2026-09-02T00:00:00Z",
  "paper_id": "arxiv:2608.28447v1",
  "person_id": "person_minghui_xu_<hash>",
  "target": "person",
  "verdict": "watch",
  "note": "Author resolution missed Stanford affiliation.",
  "source": "review_ui"
}
```

## Merge Rules

Auto-merge only on hard identifiers:

- exact email match
- verified external profile URL
- Semantic Scholar author ID tied to the paper

Never auto-merge on name alone. Name + affiliation similarity creates an `IdentityCluster` with `needs_review`.

## LinkedIn Policy

LinkedIn search may produce `candidate_profile` entries. A LinkedIn URL becomes a resolved profile only with corroboration from paper email/domain, affiliation, homepage/lab page, Semantic Scholar record, or project evidence.

No private scraping.

## Review UI Requirements

The review surface must capture paper and person feedback, persist edits, and make feedback agent-readable. These signals are future evaluation/training data for ranking, extraction quality, and prioritization.

Primary verdicts:

- `source`
- `watch`
- `skip`
- `needs_evidence`
