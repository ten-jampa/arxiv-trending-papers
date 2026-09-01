# System Design

## Design Principle

Cut vertically. Every stage produces an inspectable artifact. The final founder brief must be traceable back to source evidence.

```text
Paper Discovery -> PDF Evidence Extraction -> Author Resolution -> Founder-Signal Extraction -> Founder Brief
```

v0 executes this pipeline for **one paper**. Batch discovery comes later.

## Stage 1: Paper Discovery

Purpose: produce one `CandidatePaper` artifact.

v0 source:

- arXiv API by ID or URL.

Later candidate sources:

- Hugging Face Papers Trending.
- DAIR.AI AI Papers of the Week.
- OpenReview.
- lab blogs.

Artifact:

```text
artifacts/<run_id>/candidate_paper.json
```

Responsibilities:

- Fetch paper metadata.
- Normalize title, abstract, authors, categories, dates, and links.
- Extract URLs from arXiv comments/abstract when present.
- Record source URL and fetched timestamp.

Non-responsibilities:

- Founder judgment.
- Author identity merging.
- Trend scoring.

## Stage 2: PDF Evidence Extraction

Purpose: extract paper-native author/contact evidence before broad profile lookup.

Artifact:

```text
artifacts/<run_id>/paper_text_evidence.json
```

Responsibilities:

- Download the arXiv PDF.
- Extract text with `pdftotext` or equivalent.
- Parse the first-page contact block when possible.
- Extract emails, email domains, affiliation-ish lines, and URLs.
- Store GitHub URLs found in the PDF as high-priority builder-signal candidates with source location.

Non-responsibilities:

- Claiming permanent employment from an email domain.
- Treating every extracted URL as official code.
- Inferring founder intent.

## Stage 3: Author Resolution

Purpose: turn raw author strings into evidence-backed public-person candidates.

Artifact:

```text
artifacts/<run_id>/resolved_authors.json
```

Resolution sources, in preferred order:

1. PDF contact block: emails, domains, affiliation lines.
2. Author links from the paper/project page.
3. Semantic Scholar author records tied to the paper.
4. LinkedIn public profile lookup, mainly for identity/contact enrichment, requiring corroborating evidence beyond name.
5. Homepage/lab page found through source-linked pages.
6. GitHub only if directly linked or strongly corroborated; paper-provided GitHub repo URLs are stored even if author ownership is not resolved.
7. X only if directly linked or strongly corroborated.

Identity rules:

- Do not merge people by name alone.
- Require at least two corroborating features for medium/high confidence when using web search: paper title, coauthors, affiliation, domain, project link, email, or profile bio.
- If ambiguous, emit multiple candidates or mark unresolved.
- It is acceptable for most authors to remain unresolved in v0.

## Stage 4: Founder-Signal Extraction

Purpose: extract evidence-backed signals relevant to founder sourcing.

Artifact:

```text
artifacts/<run_id>/founder_signals.json
```

Initial signal families:

- technical wedge: the paper attacks a commercially painful bottleneck.
- builder signal: code, demo, project page, package, benchmark, dataset.
- category signal: the work defines a new task/benchmark/workflow.
- repeated obsession: same author has prior papers on the same wedge, if fetched.
- commercialization adjacency: industry/startup collaboration, if sourced.
- deployability signal: cost, latency, local deployment, reliability, or integration improvement.

Signal rules:

- Every signal must include an evidence URL and confidence.
- Missing signal is not a negative signal; write `not found`.
- Do not infer founder intent from prestige alone.
- Do not label someone founder-ready without builder/commercial evidence.

## Stage 5: Founder Brief Generation

Purpose: produce the human-facing sourcing artifact.

Artifact:

```text
artifacts/<run_id>/founder_brief.md
```

Brief sections:

```markdown
# Founder-Sourcing Brief: <paper title>

## Verdict

## Paper

## Why This Could Matter Commercially

## Authors To Watch

## Founder-Signal Evidence

## Suggested Outreach

## Unknowns / Do Not Overclaim

## Evidence Ledger
```

The brief should be concise enough to read before a partner meeting.

## v0 Command Flow

```bash
founder-radar founder-brief 2608.28447 --output artifacts/manual-test/founder_brief.md
```

Expected side effects:

```text
artifacts/<run_id>/candidate_paper.json
artifacts/<run_id>/paper_text_evidence.json
artifacts/<run_id>/resolved_authors.json
artifacts/<run_id>/founder_signals.json
artifacts/<run_id>/founder_brief.md
```

`artifacts/` is local output and ignored by git.

## Why Not Batch First

Batch discovery is easy to build and easy to make useless. The hard part is whether one paper can produce a trustworthy founder-sourcing brief. v0 tests that core risk before adding scale.

## Future Expansion

Only after v0 produces a useful single-paper brief:

1. Add `discover` for HF/DAIR/arXiv candidate papers.
2. Add batch author resolution with cache and review queue.
3. Add researcher profile history.
4. Add lab watchlist.
5. Add scheduled delivery.

Do not advance to a later stage until the current artifact gate passes.


## Later Discovery And Ranking Layers

After the single-paper v0 gate passes, the broader system should separate:

```text
discover -> rank -> founder-brief
```

Rules:

- Discovery produces candidate papers only.
- Ranking prioritizes candidates but does not create founder facts.
- Founder briefs remain evidence-first and paper-specific.
- Prefer boolean or categorical signal inputs over fake-precise numeric founder scores.
