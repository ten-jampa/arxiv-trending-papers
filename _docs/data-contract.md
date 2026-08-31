# Data Contract

This contract defines the internal objects for the local research-intelligence pipeline.

## `Paper`

Canonical paper metadata.

```yaml
paper_id: string          # canonical ID, e.g. arxiv:2608.28578v1
arxiv_id: string|null     # e.g. 2608.28578v1
source_ids: list[string]  # e.g. arxiv URL, HF paper URL, DAIR row anchor
source: string            # first source where discovered
url: string
pdf_url: string|null
title: string
abstract: string|null
authors: list[string]
published_at: datetime|null
updated_at: datetime|null
primary_category: string|null
categories: list[string]
comment: string|null
journal_ref: string|null
doi: string|null
links: list[Link]
first_seen_at: datetime
last_seen_at: datetime
```

## `Link`

```yaml
url: string
label: string|null        # paper, pdf, project, tweet, code, dataset, benchmark
source: string            # arxiv_comment, arxiv_link, dair, hf, parsed_abstract, manual
confidence: high|medium|low
```

## `WatchlistMatch`

```yaml
paper_id: string
watchlist: string         # rl, agents, capability, interpretability, etc.
matched_categories: list[string]
matched_keywords: list[string]
negative_matches: list[string]
match_text_fields: list[string] # title, abstract, comment, categories
relevance_score: float
explanation: string
```

## `ExternalSignal`

Only store signals that were actually fetched or parsed.

```yaml
paper_id: string
signal_type: string       # hf_trending_presence, hf_upvotes, dair_pick, semantic_scholar_citations, github_repo_stars, x_link_present
value: string|number|bool
source_url: string
observed_at: datetime
raw_location: string|null # JSON path, markdown section, HTML selector, etc.
confidence: high|medium|low
notes: string|null
```

Examples:

- `dair_pick=true`, confidence `high`, raw location `years/2026.md section heading + table row`.
- `hf_trending_presence=true`, confidence `medium`, raw location `HTML /papers/<id> link`.
- `hf_upvotes` should not be stored until the parser reliably extracts the count.

## `ScoreBreakdown`

```yaml
paper_id: string
computed_at: datetime
combined_score: float
relevance_score: float
trend_score: float
investment_signal_score: float
source_quality_bonus: float
implementation_signal_bonus: float
hype_penalty: float
age_adjustment: float
reasons: list[string]
missing_signals: list[string]
```

## `BriefItem`

```yaml
paper_id: string
rank: integer
title: string
links: list[Link]
recommendation: read|skim|save|watch|ignore
core_idea: string
why_it_matters: string
investment_sourcing_relevance: string
score_breakdown: ScoreBreakdown
caveats: list[string]
```

## Suggested SQLite Tables

```sql
papers(
  paper_id text primary key,
  arxiv_id text,
  source text not null,
  url text not null,
  pdf_url text,
  title text not null,
  abstract text,
  authors_json text not null,
  published_at text,
  updated_at text,
  primary_category text,
  categories_json text not null,
  comment text,
  journal_ref text,
  doi text,
  first_seen_at text not null,
  last_seen_at text not null
);

links(
  id integer primary key,
  paper_id text not null,
  url text not null,
  label text,
  source text not null,
  confidence text not null
);

watchlist_matches(
  id integer primary key,
  paper_id text not null,
  watchlist text not null,
  matched_categories_json text not null,
  matched_keywords_json text not null,
  negative_matches_json text not null,
  relevance_score real not null,
  explanation text not null
);

external_signals(
  id integer primary key,
  paper_id text not null,
  signal_type text not null,
  value_text text not null,
  source_url text not null,
  observed_at text not null,
  raw_location text,
  confidence text not null,
  notes text
);

score_breakdowns(
  id integer primary key,
  paper_id text not null,
  computed_at text not null,
  combined_score real not null,
  relevance_score real not null,
  trend_score real not null,
  investment_signal_score real not null,
  source_quality_bonus real not null,
  implementation_signal_bonus real not null,
  hype_penalty real not null,
  age_adjustment real not null,
  reasons_json text not null,
  missing_signals_json text not null
);
```

## Investment/Sourcing Interpretation

The system should treat papers as alternative signals for:

- emerging technical wedges
- startup formation themes
- open-source momentum
- lab/researcher clusters
- infrastructure bottlenecks
- new benchmark/task ecosystems
- deployability/cost shifts
- enterprise adoption clues

This is not an investment decision engine. It is a sourcing radar. Its job is to surface leads worth human judgment.
