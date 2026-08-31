# Solution Shape

## Current Stage

Stage 1: specification and architecture shaping.

We are intentionally not building the full end-to-end system yet. The immediate goal is to constrain the problem, pick the first useful surface area, and define the artifacts future implementation agents should follow.

## System Boundary

The system is a research-intelligence pipeline, not a general paper database.

It should answer:

- What new AI/RL/agent papers appeared recently?
- Which ones are getting external attention?
- Which ones match Tenzin's interests even if they are not loud yet?
- What should Tenzin read, skim, save, or ignore?

It should not try to answer everything about the literature.

## v1 Architecture

```text
Sources
  -> collectors
  -> normalizer
  -> local store
  -> enrichment workers
  -> scorer
  -> brief generator
  -> delivery surface
```

### Sources

v1 starts with arXiv because it is stable, public, and canonical for fresh AI papers.

Likely first sources:

- arXiv API for canonical paper discovery and metadata.
- DAIR.AI AI Papers of the Week raw Markdown for curated weekly signal.
- Hugging Face Papers Trending for practitioner/curation signal, behind a parser that must pass smoke tests.

Likely enrichment sources after v1:

- Semantic Scholar API for citation/reference metadata.
- GitHub API/search for code/repo signal.

Later sources:

- OpenReview for conference cycles.
- Papers with Code for benchmark/code mapping.
- Lab blogs/RSS for major release context.
- X/Twitter only as links found in curated sources until a reliable access path exists.

### Collectors

Collectors fetch raw source data and write normalized records.

They should be boring and source-specific:

- `collect_arxiv_recent`
- `collect_semantic_scholar_metadata`
- `collect_github_signal`
- `collect_hf_papers_signal`

Collectors should not decide final ranking.

### Normalizer

The normalizer converts each source into internal objects:

- paper IDs
- title
- abstract
- authors
- categories
- dates
- URLs
- source metadata

arXiv ID should be the canonical key for v1.

### Local Store

Use SQLite for v1.

Reasons:

- Easy cron-friendly local persistence.
- Good enough for seen-paper dedupe.
- No service dependency.
- Easy migration to Postgres if this becomes multi-user or hosted.

### Enrichment

Enrichment workers attach evidence, not vibes.

Examples:

- GitHub repo exists and has stars.
- Semantic Scholar citation count or influential citation count.
- HF Papers likes/upvotes if obtainable.
- Recognized lab or author signal.
- Matched watchlist terms.

Each enrichment should include source and timestamp.

### Scoring

Scoring should be transparent.

Use separate dimensions:

- topical relevance
- external trend
- implementation signal
- source/lab quality
- novelty/age adjustment
- hype penalty

The generated brief should expose the top reasons for a score.

### Brief Generator

The generator turns scored papers into Markdown.

Default sections:

- Top papers to read
- Worth skimming
- Quiet but potentially important
- Probably overhyped
- Watchlist misses or anomalies

Each item should include:

- title and link
- authors/lab if available
- one-sentence core idea
- why it is trending or why it matters
- read/skim/save/ignore recommendation

### Delivery Surface

v1 delivery should be simple:

- CLI command writes Markdown to stdout or file.
- Hermes cron can later call the CLI and deliver the brief to Telegram.

Do not build a web UI until the scoring and brief are useful.

## Suggested Milestones

### Milestone 1: Useful Local Brief

Build a CLI that:

1. Fetches recent arXiv papers from configured categories.
2. Filters by RL/agents watchlists.
3. Stores seen IDs in SQLite.
4. Produces a Markdown brief.

No external trend enrichment required yet beyond arXiv metadata and keyword scoring.

### Milestone 2: Real Trend Signals

Add enrichment:

1. Semantic Scholar metadata.
2. GitHub repo/code search signal.
3. Hugging Face Papers signal if stable.

### Milestone 3: Personalization

Add:

1. Topic weights.
2. Saved/ignored paper feedback.
3. Weekly rollup.
4. Obsidian export for selected papers.

### Milestone 4: Automation

Add:

1. Hermes cron job.
2. Telegram delivery.
3. Failure reporting.
4. Last-run state and dedupe.

## Design Biases

- Prefer stable public APIs over brittle scraping.
- Prefer a useful top 5 over an exhaustive dump.
- Prefer explainable scoring over fancy ranking.
- Prefer local files and SQLite until the workflow proves useful.
- Keep source collection, scoring, and summarization separate.
- Treat “trending” as evidence-weighted attention, not truth.

## First Implementation Slice

The first coding slice should be deliberately small:

```text
config/watchlists.yaml
src/arxiv_trending/
  arxiv.py
  models.py
  scoring.py
  brief.py
  cli.py
tests/
  test_scoring.py
  test_brief.py
```

Acceptance criteria:

- Can run one CLI command with mocked or recorded arXiv data.
- Produces deterministic Markdown.
- Clearly shows why each paper matched.
- Does not require credentials.
- Does not attempt full automation/deployment.
