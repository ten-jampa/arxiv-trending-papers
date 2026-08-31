# Manual Test Scenario

This is a future test seed, not a claim that the full system exists yet.

## Scenario: Generate A Useful RL/Agents Paper Brief

### Preconditions

- A config file defines arXiv categories and watchlist keywords.
- The local store is empty or reset.
- The collector can fetch or load recent arXiv-like paper records.

### Steps

1. Run the CLI for the last 7 days of papers.
2. Confirm papers from `cs.LG`, `cs.AI`, `cs.CL`, `cs.MA`, and `cs.SE` are considered.
3. Confirm RL and agents keywords cause matching papers to appear in the candidate set.
4. Generate the Markdown brief.
5. Inspect the top-ranked items.
6. Run the same command again with the same state.

### Expected Results

- The brief includes ranked paper items with links and recommendations.
- Each ranked item shows why it matched.
- RL/agents matches are visible and not buried under generic ML papers.
- Duplicate already-seen papers are either omitted or clearly marked, depending on the selected mode.
- No credentials are required for the basic arXiv-only path.

### Cleanup

- Delete or reset the local SQLite database.
- Remove generated brief files if they are test artifacts.
