# arXiv Trending Papers — Product Spec

## Purpose

Track newly interesting AI research papers, especially reinforcement learning and agents, as an alternative signal for investment sourcing and thesis formation.

The output is a ranked research-intelligence brief that separates genuine signal from hype and clearly labels what was actually verified.

## Target User

Tenzin: AI capability/research/VC-oriented reader who wants a daily or weekly shortlist of papers worth reading, skimming, saving, watching, or ignoring for sourcing and investment insight.

## Primary Job To Be Done

When new AI papers appear across arXiv and adjacent curated channels, identify which ones signal emerging technical wedges, startup formation themes, infrastructure bottlenecks, benchmark ecosystems, or open-source momentum; explain why; and recommend what to do with them.

## Core Workflow

1. Collect recent papers from selected arXiv categories.
2. Filter papers by topic watchlists: RL, agents, AI capability, evaluation, interpretability, inference, and AI infra.
3. Enrich candidate papers with trend signals where available.
4. Score papers using a transparent relevance/trend formula.
5. Generate a terse Markdown brief with the top papers and rationale.
6. Persist seen paper IDs so future briefs avoid duplicate spam.
7. Optionally save selected papers into Obsidian later.

## Core Objects

### Paper

- `paper_id`: canonical ID, usually arXiv ID.
- `source`: `arxiv`, later possibly `openreview`, `semantic_scholar`, `huggingface`, etc.
- `title`
- `abstract`
- `authors`
- `categories`
- `published_at`
- `updated_at`
- `url`
- `pdf_url`
- `primary_category`
- `comment`
- `links`: code, project page, dataset, benchmark, if found.

### Watchlist

- `name`: e.g. `rl`, `agents`, `capability`, `interpretability`.
- `categories`: arXiv category allowlist.
- `keywords`: positive match terms.
- `negative_keywords`: terms to downrank or exclude.
- `weight`: scoring weight.

### Trend Signal

- `paper_id`
- `signal_type`: `hf_likes`, `github_stars`, `citation_velocity`, `x_mentions`, `lab_bonus`, `keyword_relevance`, etc.
- `value`
- `observed_at`
- `source_url`
- `confidence`: `high`, `medium`, `low`.

### Brief Item

- `paper_id`
- `rank`
- `trend_score`
- `relevance_score`
- `recommendation`: `read`, `skim`, `save`, `ignore`.
- `why_trending`
- `core_idea`
- `why_it_matters`
- `caveats`

## Initial arXiv Categories

Primary:

- `cs.LG` — machine learning, RL, post-training, optimization.
- `cs.AI` — planning, reasoning, agents, symbolic/neural AI.
- `cs.CL` — LLM agents, tool use, language-model post-training.
- `cs.MA` — multi-agent systems and multi-agent RL.
- `cs.SE` — coding agents, SWE-bench, software engineering agents.

Secondary:

- `cs.RO` — embodied agents and robot RL.
- `stat.ML` — theoretical RL, bandits, statistical ML.
- `cs.HC` — human-agent interaction.
- `cs.CR` — security/cyber agents and adversarial agent behavior.
- `cs.CY` — agent governance and socio-technical risk.

## Initial Topic Watchlists

### Reinforcement Learning

Keywords:

- reinforcement learning
- RLHF
- RLAIF
- GRPO
- PPO
- DPO
- online RL
- offline RL
- policy optimization
- reward model
- preference optimization
- verifiable reward
- actor-critic
- bandit
- MDP
- Q-learning
- Monte Carlo tree search
- MCTS
- test-time reinforcement

### Agents

Keywords:

- agent
- agents
- LLM agent
- multi-agent
- tool use
- function calling
- planning
- reasoning
- autonomous
- workflow
- environment
- web agent
- browser agent
- computer use
- coding agent
- software engineering agent
- SWE-bench
- embodied agent
- robot agent
- memory
- reflection
- self-improvement

## Scoring Principles

Trend is not the same as importance. The system should show both:

- `trend_score`: how much the paper is being noticed now.
- `relevance_score`: how aligned it is with Tenzin's interests.
- `importance_note`: why it might matter even if not noisy yet.

Initial score shape:

```text
combined_score =
  age_adjusted_trend_score
+ personal_relevance_score
+ source_quality_bonus
+ implementation_signal_bonus
- hype_penalty
```

The score must be explainable in the brief. No black-box ranking without reasons.

## Permissions And Auth

- Public sources first: arXiv API/RSS, Semantic Scholar public API, GitHub public API/search, Hugging Face Papers pages/RSS/API if available.
- No paid APIs required for v1.
- No posting, bookmarking, or Obsidian writes unless explicitly enabled later.
- No secrets committed.

## Important Edge Cases

- arXiv revisions should not be treated as brand-new papers unless the update is meaningful.
- Generic “agent” papers outside AI agents should be filtered or downranked.
- Survey papers can be useful but should not dominate daily trend lists.
- Lab prestige should be a weak signal, not a trump card.
- Very new papers may have no citations/stars yet; avoid burying them solely because metrics lag.
- X/Twitter signal is noisy and brittle; it should be optional, not foundational.

## Non-Goals For Current Stage

- Full production deployment.
- Browser automation for every source.
- Paid data providers.
- Perfect trend detection.
- Full-text PDF summarization.
- Automatic Obsidian publishing.
- E2E UI/app build.

## Open Questions

1. Should the first deliverable be a Telegram cron brief, a CLI-generated Markdown report, or both?
2. Daily, weekly, or both?
3. Should the system optimize for “top 5 must-read” or broader “top 15 radar” coverage?
4. Should X/Twitter be included if access is flaky, or skipped until there is a stable source?
5. Should saved papers create Obsidian notes immediately or only after explicit selection?
