# CLI Contract

The CLI exists to support a vertical founder-sourcing workflow. It should not become a generic paper dashboard.

## v0 Command: `founder-radar founder-brief`

Purpose: generate a founder-sourcing brief from one arXiv paper.

```bash
founder-radar founder-brief <arxiv-id-or-url> \
  --output artifacts/<run_id>/founder_brief.md
```

Accepted input forms:

```text
2608.28447
2608.28447v1
https://arxiv.org/abs/2608.28447
https://arxiv.org/pdf/2608.28447
```

Options (implemented):

- `--output PATH`: write final Markdown brief to a path. Defaults to `<artifacts-dir>/founder_brief.md`.
- `--artifacts-dir PATH`: directory for intermediate artifacts. Defaults to `artifacts/<arxiv-id>/`.
- `--llm-contact-parser`: optional. After deterministic PDF contact-block extraction, send the bounded contact block to an OpenAI model (via `OPENAI_API_KEY` in the environment or a local `.env` file) to clean up affiliation lines and email attribution. Deterministic extraction remains the default and is not replaced; see `_docs/discovery-ranking.md` and `_docs/arxiv-rate-limits.md` for related design notes. Not documented anywhere else, so noted here explicitly.

Options documented in earlier drafts of this contract but not yet implemented:

- `--no-semantic-scholar`: no-op today, because Semantic Scholar enrichment has not been implemented at all (nothing to skip). Add this flag only alongside real Semantic Scholar integration, not before.
- `--raw-only`: not implemented. The CLI currently always generates the founder brief; there is no artifacts-only mode yet.

Required artifacts:

```text
candidate_paper.json
paper_text_evidence.json
resolved_authors.json
founder_signals.json
founder_brief.md
```

Exit codes (implemented):

- `0`: success.
- `1`: invalid arXiv ID or URL.
- `2`: arXiv unavailable, rate-limited past retry budget, or paper not found.

Exit codes documented in earlier drafts but not yet implemented as distinct paths:

- `3`: was intended for "enrichment source failed but arXiv succeeded and strict mode required it." There is no strict/enrichment-failure mode yet; all current enrichment (contact parsing, author resolution) fails soft into `unresolved`/`not found` rather than raising.
- `4`: was intended for artifact write failure. A write failure today raises an unhandled exception rather than a clean exit code.

## Later Command: `founder-radar smoke-sources`

Purpose: verify which sources can currently be fetched and parsed.

```bash
founder-radar smoke-sources
```

Checks:

- arXiv API availability.
- Semantic Scholar paper lookup availability.
- Hugging Face Papers Trending page shape, once parser exists.
- DAIR.AI raw Markdown shape, once parser exists.

## Later Command: `founder-radar discover`

Purpose: produce candidate paper artifacts from trending/curated sources. Not v0.

```bash
founder-radar discover --source arxiv --source hf --source dair --max 20
```

This command must not generate founder conclusions. It only outputs candidate papers.

## Hallucination Boundary

The CLI must not emit metrics or profiles that were not fetched.

Examples:

- If no affiliation is available, write `Affiliation: not found`.
- If the PDF cannot be downloaded or parsed, write `PDF evidence: not checked` or `PDF evidence: unavailable` with the error.
- If Semantic Scholar is skipped or fails, write `Semantic Scholar: not checked`.
- If LinkedIn lookup cannot be corroborated beyond name, write `LinkedIn: unresolved`.
- If GitHub is not directly linked or strongly corroborated, write `GitHub profile: not resolved`; still store paper-provided GitHub repo URLs as repo links.
- If a paper has a project link in arXiv comments, label it as `project link from arXiv comment`, not `official code` unless code is verified.

## Output Brief Shape

```markdown
# Founder-Sourcing Brief: <Paper Title>

## Verdict
- Recommendation: `skip` / `watch` / `manual diligence needed` (`reach out` is a documented future value; current deterministic recommendation logic never produces it, since it requires stronger identity/outreach evidence than the pipeline currently resolves)
- Confidence: high / medium / low
- One-line reason:

## Paper
- arXiv:
- Authors:
- Published:
- Categories:
- Core idea:

## Why This Could Matter Commercially
- Technical wedge:
- Buyer/workflow hypothesis:
- Why now:

## Authors To Watch
### <Name>
- Identity confidence:
- Affiliation:
- Profiles:
- Founder-relevant evidence:
- Suggested outreach angle:

## Unknowns / Do Not Overclaim

## Evidence Ledger
```
