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

Options:

- `--output PATH`: write final Markdown brief to a path. If omitted, print to stdout and still write intermediate artifacts unless `--no-artifacts` exists later.
- `--artifacts-dir PATH`: default `artifacts/<timestamp>-<arxiv-id>/`.
- `--no-semantic-scholar`: skip Semantic Scholar author/paper enrichment.
- `--raw-only`: fetch and write artifacts without generating judgment-heavy founder hypotheses.

Required artifacts:

```text
candidate_paper.json
paper_text_evidence.json
resolved_authors.json
founder_signals.json
founder_brief.md
```

Exit codes:

- `0`: success.
- `1`: invalid input/config.
- `2`: arXiv unavailable or paper not found.
- `3`: enrichment source failed but arXiv succeeded and strict mode required it.
- `4`: artifact write failure.

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
- Recommendation: reach out / watch / skip / manual diligence needed
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
