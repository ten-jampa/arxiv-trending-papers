# Context

This file is the project glossary. It defines domain language only; implementation details belong in `_docs/` or ADRs.

## Terms

### Prospective Founder Radar

The product category for this repo: a system that uses research-paper evidence to surface researchers who may become startup founders before the market notices.

Preferred over: `paper tracker`, `research digest`, `literature monitor`.

### Candidate Paper

A paper selected for founder-radar analysis. In v0, the user supplies exactly one arXiv paper, so candidate selection is manual.

A candidate paper is not itself an investment opportunity; it is evidence that may point to a researcher, wedge, or market timing shift.

### Resolved Author

A paper author string mapped to an evidence-backed public person record.

An author is not resolved by name alone. Resolution requires corroborating evidence such as paper linkage, email/domain, affiliation block, Semantic Scholar record tied to the paper, LinkedIn profile evidence, project page, or linked GitHub profile.

### Unresolved Author

A paper author for whom the system cannot safely identify a public person record.

Unresolved is an acceptable v0 outcome. The system should preserve the raw author string and explain what was not found or not checked.

### Founder Signal

Evidence that a researcher may be relevant for founder sourcing.

Examples include code release, project page, benchmark/dataset creation, infrastructure/tooling orientation, commercially legible problem choice, repeated work on a wedge, or industry/startup collaboration.

Prestige alone is not a founder signal.

### Evidence Claim

A factual claim with a source URL, observed timestamp, confidence label, and note about where the claim came from.

Every non-obvious factual claim in a founder brief should trace to an evidence claim.

### Identity Confidence

The confidence that a resolved author record refers to the same person as the paper author.

Allowed values:

- `high`: strong direct evidence, such as author homepage/project page linking the paper, paper PDF email/domain plus matching profile, or Semantic Scholar record tied to the paper plus corroborating affiliation/profile evidence.
- `medium`: multiple corroborating weak signals but no single decisive link.
- `low`: plausible candidate, but risky enough that the brief must not rely on it for outreach.
- `unresolved`: no safe identity match.

### Contact Block

The first-page paper region containing author names, affiliations, emails, and sometimes contribution notes.

In v0, the contact block is extracted from arXiv PDF text when possible.

### Affiliation Block

The subset of the contact block that names institutions, departments, labs, or companies.

Affiliation blocks are evidence from the paper, not proof of current employment.

### LinkedIn Candidate

A LinkedIn profile that may correspond to a paper author.

LinkedIn is allowed in v0 mainly as an identity/contact enrichment target, but the system must not scrape private data or treat a name-only match as resolved.

### GitHub URL

A GitHub repository or profile URL found in arXiv metadata, PDF text, paper comments, abstract, or linked project pages.

GitHub URLs are important builder signals and should be stored with source and confidence. A repo URL is not automatically an author profile unless ownership is evidenced.

### Commercial Wedge

A concise hypothesis about what company-shaped opportunity the paper may imply.

This is interpretation, not a fact. It should be grounded in evidence and labelled with confidence.

### Founder Brief

The human-facing Markdown artifact that summarizes the paper, authors to watch, founder signals, commercial wedge, outreach angle, unknowns, and evidence ledger.

### Sparse And True

The quality bar for this project: prefer a brief with fewer claims and stronger evidence over a rich-looking brief filled with guessed profiles, affiliations, or founder intent.

### Unknown / Not Found / Not Checked

Explicit absence markers.

- `unknown`: the system cannot determine the value from available evidence.
- `not found`: the system checked an allowed source and did not find the value.
- `not checked`: the source or enrichment step was not run.

These are preferred over plausible guesses.


### Ranking Signal

A boolean or categorical founder-radar input used to prioritize candidate papers later.

Examples: `code_repo_present`, `project_page_present`, `identity_confidence`, `benchmark_or_dataset_created`.

A ranking signal is not itself a verdict and should not pretend to be a calibrated score unless real review data later supports calibration.
