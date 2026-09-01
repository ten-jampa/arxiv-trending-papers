# Manual Test Scenario

## Scenario: Generate A Founder-Sourcing Brief For One Paper

This is the seed for the first manual and automated test. It does not assume batch ingestion exists.

### Preconditions

- The CLI can accept one arXiv ID or URL.
- Public arXiv API is reachable.
- Artifact output directory is empty or disposable.

### Steps

1. Run:

```bash
founder-radar founder-brief 2608.28447 --output artifacts/manual-test/founder_brief.md
```

2. Inspect generated artifacts:

```text
artifacts/manual-test/candidate_paper.json
artifacts/manual-test/paper_text_evidence.json
artifacts/manual-test/resolved_authors.json
artifacts/manual-test/founder_signals.json
artifacts/manual-test/founder_brief.md
```

3. Confirm the paper metadata matches arXiv.
4. Confirm `paper_text_evidence.json` records PDF download/extraction status.
5. Confirm emails, domains, affiliation-ish lines, and GitHub URLs are extracted when present.
6. Confirm all raw authors appear in `resolved_authors.json`.
7. Confirm unresolved authors are marked `unresolved`, not guessed.
8. Confirm LinkedIn candidates are not accepted without corroboration beyond name.
9. Confirm every founder-relevant claim has an evidence URL.
10. Confirm the brief includes unknowns/do-not-overclaim.

### Expected Results

- The command succeeds without credentials.
- The final brief is readable Markdown.
- The brief contains a recommendation: `reach out`, `watch`, `skip`, or `manual diligence needed`.
- Any project/code/profile links are labelled with source and confidence.
- Missing GitHub/X/LinkedIn/affiliation data is explicit.

### Cleanup

Delete the local artifact directory if it was only a test run.
