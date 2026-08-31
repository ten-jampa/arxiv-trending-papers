# arXiv Trending Papers

A research-intelligence pipeline for tracking trending and personally relevant AI papers, with an initial focus on reinforcement learning and agents.

## Current Status

This repo is at the problem/solution shaping stage.

The current artifacts define:

- the product spec
- the RL/agents watchlists
- the proposed architecture
- the CLI/data contracts
- source smoke-test evidence
- the initial stack decision
- the first manual test scenario
- agent instructions for future implementation work

## Key Docs

- `_docs/spec.md` — product behavior and investment/sourcing boundary
- `_docs/solution-shape.md` — architecture and milestones
- `_docs/cli-contract.md` — command surface and no-hallucination behavior
- `_docs/data-contract.md` — internal objects, signals, and suggested SQLite tables
- `_docs/source-smoketests.md` — verified source availability and parser caveats
- `_docs/stack.md` — stack decision
- `_docs/manual-test.md` — future manual/E2E test seed
- `config/watchlists.yaml` — initial categories and topic keywords
- `AGENTS.md` — durable agent instructions

## Recommended First Build Slice

Build a small Python CLI that:

1. Reads `config/watchlists.yaml`.
2. Fetches recent arXiv papers from configured categories.
3. Scores keyword/category matches.
4. Writes a deterministic Markdown brief.
5. Stores seen arXiv IDs in SQLite.

Do not start with a web app or deployment. That would be busywork wearing a nice hat.
