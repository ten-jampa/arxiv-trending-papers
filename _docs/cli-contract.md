# CLI Contract

The first implementation surface is a local CLI. It exists to produce an investment/sourcing research brief, not to be a generic arXiv browser.

## Command: `arxiv-trending smoke-sources`

Purpose: verify what can currently be fetched and parsed from configured public sources.

```bash
arxiv-trending smoke-sources --config config/watchlists.yaml
```

Expected behavior:

- Fetch a small sample from arXiv.
- Optionally fetch Hugging Face Papers Trending.
- Optionally fetch DAIR.AI raw Markdown.
- Print source availability, fields detected, and parser confidence.
- Exit nonzero if arXiv is unavailable.
- Do not write investment conclusions.

## Command: `arxiv-trending brief`

Purpose: produce a Markdown brief of new/high-signal papers.

```bash
arxiv-trending brief \
  --days 7 \
  --max 10 \
  --config config/watchlists.yaml \
  --source arxiv \
  --source dair \
  --output output/brief.md
```

Defaults:

- `--days`: `7`
- `--max`: `10`
- `--config`: `config/watchlists.yaml`
- `--output`: stdout if omitted
- sources: `arxiv` only until optional parsers are implemented and smoke-tested

Expected output sections:

```markdown
# AI Research Alt-Signal Brief — YYYY-MM-DD

## Top Investment/Sourcing Signals

## RL / Agents Watchlist

## Quiet But Potentially Important

## Curated External Picks

## Source Coverage And Gaps
```

Each paper item must include:

- title
- source links
- arXiv ID when available
- authors
- published/updated date
- matched categories
- matched watchlists and keywords
- score breakdown
- recommendation: `read`, `skim`, `save`, `watch`, or `ignore`
- investment/sourcing relevance note
- caveats / missing data

## Command: `arxiv-trending collect`

Purpose: fetch and cache normalized source data without generating a brief.

```bash
arxiv-trending collect --days 7 --source arxiv --source dair
```

Expected behavior:

- Write normalized paper records to local SQLite.
- Write raw-source fetch metadata.
- Do not overwrite manually attached notes.

## Command: `arxiv-trending score`

Purpose: recompute scores from cached papers/signals.

```bash
arxiv-trending score --max 25
```

Expected behavior:

- Recompute score breakdowns deterministically.
- Print top scored items or write them to the database.

## Exit Codes

- `0`: success.
- `1`: invalid arguments or config.
- `2`: required source unavailable.
- `3`: parser failed against fetched source shape.
- `4`: local storage error.

## Generated Files

Suggested local files:

```text
/data/arxiv_trending.sqlite3
/output/brief-YYYY-MM-DD.md
/output/source-smoke-YYYY-MM-DD.json
```

`data/` and `output/` are ignored by git.

## Hallucination Boundary

The CLI must not emit metrics that were not fetched. Examples:

- If Hugging Face upvote extraction fails, write `HF signal: not checked` or omit it.
- If GitHub repo signal is not implemented, write `GitHub signal: not checked`.
- If a paper has a project link in arXiv comments, label it as `project link from arXiv comment`, not `official code` unless code is verified.
