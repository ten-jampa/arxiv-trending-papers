# Source Smoke Tests

This document records what was actually verified from public sources. Do not treat unverified signals as available just because they sound useful.

Smoke test date: 2026-08-31.

## arXiv API

Endpoint tested:

```text
https://export.arxiv.org/api/query
```

Tested one-paper and search-style access through the public Atom API.

Verified fields from Atom entries:

- `id`, e.g. `http://arxiv.org/abs/2608.28589v1`
- `published`
- `updated`
- `title`
- `summary` / abstract text
- `author` names
- `arxiv:primary_category`
- category terms
- `arxiv:comment` when present
- `arxiv:journal_ref` when present
- `arxiv:doi` when present
- HTML link
- PDF link

Observed examples from smoke test:

- `2608.28589v1` — `cs.LG`, `math.NA`
- `2608.28578v1` — `cs.RO`, `cs.AI`, `cs.LG`; comment included a project page URL.
- `2608.28576v1` — `stat.ME`, `cs.AI`, `cs.LG`, `stat.ML`

Takeaway: arXiv is the reliable v0 source for paper metadata and raw author strings. It does **not** provide affiliations, author homepages, founder intent, or trend metrics.

## arXiv Query Shape Tests

These are useful later for candidate discovery, not required for v0.

### Agents query

```text
(cat:cs.AI OR cat:cs.CL OR cat:cs.MA OR cat:cs.SE)
AND
(all:agent OR all:"tool use" OR all:"SWE-bench" OR all:"multi-agent")
```

Observed:

```text
totalResults: 42568
```

Top recent examples returned:

- `2608.28553v1` — `cs.AI`, `cs.MA` — `Logos: An Agent Harness on a Cross-Process Bus`
- `2608.28542v1` — `cs.CR`, `cs.MA` — `Offline-Verifiable Accountability for Cross-Organization Agent Messaging: A Preserved Evidence-Bundle Approach`
- `2608.28497v1` — `cs.SE`, `cs.AI` — `On the Maintenance and Co-evolution of Agent Plugins: An Empirical Study of Claude Code Plugin Marketplaces`

### RL query

```text
(cat:cs.LG OR cat:cs.AI OR cat:cs.MA OR cat:stat.ML OR cat:cs.RO)
AND
(all:"reinforcement learning" OR all:RLHF OR all:GRPO OR all:"policy optimization")
```

Observed:

```text
totalResults: 37644
```

Top recent examples returned:

- `2608.28578v1` — `cs.RO`, `cs.AI`, `cs.LG` — `Aero Hand Open: A Simulation-Ready Tendon-Driven Hand for Dexterous Manipulation Learning`
- `2608.28499v1` — `cs.LG`, `cs.CR` — `REPLICANT: Learning Policies for Evading and Hardening Malware Detectors`
- `2608.28447v1` — `cs.AI` — `Learning to Use Tools: Reinforcement Learning for Tool-Integrated Mathematical Reasoning`

Takeaway: arXiv search can support later paper discovery, but v0 should focus on one supplied paper.

## Hugging Face Papers Trending

URL tested:

```text
https://huggingface.co/papers/trending
```

Result:

```text
status: 200
content-type: text/html; charset=utf-8
```

Verified from returned HTML:

- The page is publicly fetchable.
- It contains many `/papers/<arxiv-id>` links.
- Test page contained at least 253 `/papers/YYYY.NNNNN` matches in the first ~1.2 MB.
- It contains embedded metadata-like text including summaries, thumbnails, submitter data, `numComments`, and `upvotes` strings.

Not verified:

- A stable public JSON/API contract.
- A documented ranking field.
- Reliable upvote-count extraction.
- Stable pagination/history.

Takeaway: HF Trending is a promising later candidate-discovery source, not a v0 dependency.

## DAIR.AI AI Papers of the Week

URLs tested:

```text
https://github.com/dair-ai/AI-Papers-of-the-Week
https://raw.githubusercontent.com/dair-ai/AI-Papers-of-the-Week/main/README.md
https://raw.githubusercontent.com/dair-ai/AI-Papers-of-the-Week/main/years/2026.md
```

Verified:

- GitHub repo page is public.
- Raw README is public and lists weekly issue links.
- `years/2026.md` is public Markdown.
- `years/2026.md` contained `Top AI Papers of the Week` sections.
- `years/2026.md` contained 318 arXiv links in the tested read.
- Rows include curated prose and links such as `[Paper](https://arxiv.org/abs/...)` and `[Tweet](...)`.

Takeaway: DAIR.AI is a strong later curated candidate source, but v0 does not need it.

## No-Hallucination Rule

A source signal can only appear in generated artifacts if it has:

- source URL,
- fetched timestamp,
- raw field or parsed location,
- confidence label.

If unavailable, say `not checked`, `not found`, or `unresolved`. Never fill in trend metrics, author profiles, affiliations, or founder intent because they “probably exist.”
