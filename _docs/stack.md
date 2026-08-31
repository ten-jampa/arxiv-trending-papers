# Stack Decision

## Decision

Use a small Python CLI with file-based artifacts for v0.

## Chosen Stack

- Language: Python 3.11+
- CLI: standard library `argparse` first; consider Typer only if the command surface grows.
- HTTP: standard library `urllib` or `httpx` if dependency management is added.
- Parsing: arXiv Atom XML with Python stdlib or a tiny parser dependency.
- Storage: JSON artifacts in `artifacts/<run_id>/` for v0.
- Tests: pytest.
- Delivery: Markdown file/stdout.
- CI: GitHub Actions later, after code exists.

## Why Not SQLite Yet

SQLite is useful for repeated/batch runs, dedupe, and researcher history. v0 is one-paper analysis. File artifacts are simpler and make debugging easier.

Add SQLite only when batch discovery exists.

## Alternatives Rejected For v0

### Full Daily Digest Pipeline

Rejected. It avoids the hard question: whether one paper can produce a trustworthy founder-sourcing brief.

### Web App / Dashboard

Rejected. A UI would add surface area before the brief quality is proven.

### People Search Product

Rejected. Author identity resolution is valuable but dangerous; v0 should only resolve profiles when evidence is strong.

### Heavy LLM Summarization First

Rejected. The system should first prove its evidence contract. LLM-written briefs can come after artifacts are reliable.

## Migration Path

If v0 works:

1. Add `discover` sources for HF/DAIR/arXiv candidate lists.
2. Add SQLite for repeated runs and identity cache.
3. Add GitHub/Semantic Scholar enrichment.
4. Add scheduled briefs.
5. Add lab-founder historical graph as a separate artifact-gated stage.
