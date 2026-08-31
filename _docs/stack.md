# Stack Decision

## Decision

Use a small Python CLI plus SQLite for v1.

## Chosen Stack

- Language: Python 3.11+
- CLI: standard library `argparse` first; consider Typer only if the CLI grows.
- HTTP: `httpx` or standard library initially; avoid heavy frameworks.
- Parsing: arXiv Atom via `feedparser` or XML stdlib.
- Storage: SQLite.
- Config: YAML watchlist file.
- Tests: pytest.
- Delivery: Markdown output consumed manually or by Hermes cron.
- CI: GitHub Actions later, after the first code slice exists.

## Alternatives Considered

### Full Web App

Rejected for now. A UI is not the bottleneck. The bottleneck is signal quality and ranking.

### Hosted Backend + Database

Rejected for now. Production deployment adds operational drag before the brief is proven useful.

### Notebook Prototype

Useful for exploration but not ideal as the durable interface. A CLI is easier to automate with cron.

### TypeScript App

Reasonable if this becomes a web product, but Python is better for fast research-data plumbing and local automation.

## Why This Fits

- Cron-friendly.
- Works locally without secrets.
- Easy to test.
- Easy to hand to future coding agents.
- Easy to pipe into Telegram or Obsidian workflows later.

## Known Risks

- Hugging Face Papers access may require scraping or unstable endpoints.
- X/Twitter signal may be too brittle to include early.
- Semantic Scholar rate limits may require caching.
- Keyword filters can miss important papers with unusual phrasing.
- arXiv category coverage may include lots of irrelevant noise.

## Migration Path

If the system becomes valuable enough to host:

1. Keep the collector/scoring modules.
2. Swap SQLite for Postgres.
3. Add a small FastAPI service around the same pipeline.
4. Add a frontend only after the daily/weekly brief proves useful.
