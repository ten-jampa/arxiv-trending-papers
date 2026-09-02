# Solution Shape

## Current Stage

Stage 1: specification and artifact contracts.

Per the agentic-shipping workflow, this repo should not proceed to implementation until the vertical-slice artifacts are explicit enough to constrain the next coding task.

## Product Boundary

This is a founder-sourcing radar built from research-paper evidence.

It should answer one narrow question first:

> Given this AI paper, which authors are worth founder-sourcing attention, and what evidence supports that?

It should not start as a daily digest, dashboard, lab genealogy, or generic paper recommender.

## v0 Architecture

```text
arXiv ID / URL
  -> paper fetcher
  -> CandidatePaper artifact
  -> author resolver
  -> ResolvedAuthor artifact
  -> founder-signal extractor
  -> FounderSignal artifact
  -> Markdown founder brief
```

Each stage writes an inspectable artifact before the next stage runs.

## Stage Responsibilities

### Paper Fetcher

- Fetch one arXiv record.
- Normalize metadata.
- Extract links from arXiv metadata/comment/abstract.
- Write `candidate_paper.json`.

### Author Resolver

- Preserve raw author names.
- Attach paper-native author evidence from PDF text: emails, domains, affiliation lines, affiliation scope, ambiguous emails, and paper-evidence confidence.
- Attempt Semantic Scholar author lookup only when implemented/available.
- Use direct links from source metadata/project pages when available.
- Keep `identity_confidence` unresolved unless external public identity evidence is corroborated.
- Preserve multi-author affiliation blocks as paper-level evidence instead of dropping them.
- Write `resolved_authors.json`.

### Founder-Signal Extractor

- Identify evidence-backed builder/commercialization signals.
- Separate paper-level and author-level signals.
- Do not infer founder intent from prestige alone.
- Write `founder_signals.json`.

### Brief Generator

- Produce a concise sourcing brief.
- Include recommendation and confidence.
- Include outreach angle only when justified.
- Include unknowns/do-not-overclaim section.
- Write `founder_brief.md`.

## First Implementation Slice

Build exactly this:

```bash
founder-radar founder-brief <arxiv-id-or-url>
```

Acceptance criteria live in `_docs/vertical-slice-v0.md`.

Suggested code skeleton:

```text
src/founder_radar/
  __init__.py
  arxiv.py
  models.py
  links.py
  semantic_scholar.py
  author_resolution.py
  founder_signals.py
  brief.py
  cli.py
tests/
  test_arxiv_id_parsing.py
  test_arxiv_normalization.py
  test_author_resolution.py
  test_brief_rendering.py
```

## Later Expansion Gates

Only after v0 is useful:

1. Add paper discovery from Hugging Face Trending and DAIR.AI.
2. Add batch processing.
3. Add persistent researcher profiles.
4. Add lab watchlists and historical founder graph.
5. Add cron/Telegram delivery.

## Design Biases

- Sparse and true beats rich and fake.
- Identity resolution is the hard part; treat it as the primary risk.
- Evidence artifacts matter more than scoring formulas.
- Source adapters should not contain founder judgment.
- Brief generation can use judgment, but facts must come from artifacts.


## Later Discover -> Rank -> Founder-Brief Shape

Once v0 is useful, the next architecture should be:

```text
discover -> rank -> founder-brief
```

Where:

- `discover` finds candidate papers
- `rank` prioritizes them with explicit signal rules
- `founder-brief` does the deeper evidence-backed analysis

Prefer boolean or categorical signals for ranking rules. Avoid uncalibrated numeric founder scores.
