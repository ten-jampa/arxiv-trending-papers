# Source Smoke Tests

This document records what we actually verified from public sources. Do not treat unverified signals as available just because they sound useful.

Smoke test date: 2026-08-31.

## arXiv API

Endpoint tested:

```text
https://export.arxiv.org/api/query
```

Example query tested:

```text
search_query=cat:cs.AI OR cat:cs.LG OR cat:cs.CL OR cat:cs.MA OR cat:cs.SE
start=0
max_results=5
sortBy=submittedDate
sortOrder=descending
```

Result:

```text
HTTP bytes: 12338
entries: 5
```

Fields verified from Atom entries:

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

Observed example papers from the smoke test:

- `2608.28589v1` — `cs.LG`, `math.NA`
- `2608.28578v1` — `cs.RO`, `cs.AI`, `cs.LG`; comment included a project page URL.
- `2608.28576v1` — `stat.ME`, `cs.AI`, `cs.LG`, `stat.ML`

Takeaway: arXiv can reliably provide fresh paper metadata, categories, abstracts, authors, dates, comments, DOI/journal refs when present, and canonical links. It does **not** provide trend/attention metrics.

## arXiv Query Shape Tests

Tested broad and focused queries.

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

Takeaway: arXiv search is enough to build an arXiv-only candidate generator for RL/agents. Keyword search is broad and noisy, so scoring must explain matches and downrank irrelevant collisions.

## Hugging Face Papers Trending

URL tested:

```text
https://huggingface.co/papers/trending
```

Result:

```text
status: 200
content-type: text/html; charset=utf-8
bytes_read: 500000+
```

Verified from returned HTML:

- The page is publicly fetchable.
- It contains many `/papers/<arxiv-id>` links.
- Test page contained at least 253 `/papers/YYYY.NNNNN` matches in the first ~1.2 MB.
- It contains embedded paper metadata-like text including summaries, thumbnails, submitter data, `numComments`, and `upvotes` strings.

Not verified yet:

- A stable public JSON/API contract.
- A documented sort/ranking field.
- Whether upvote counts can be parsed reliably without brittle HTML extraction.
- Whether pagination/history is stable.

Takeaway: Hugging Face Papers Trending is a promising curated/trend source, but v1 should treat it as an optional source behind a parser with smoke tests. Do not claim exact likes/upvotes unless the parser extracts and tests that field.

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

Takeaway: DAIR.AI is not a raw trend metric but is a strong curated weekly signal. It is especially relevant for investment/sourcing because each entry includes a human-written “why it matters” style rationale and often a social link.

## Source Reliability Ranking For v1

Use sources in this order:

1. **arXiv API** — canonical paper discovery and metadata.
2. **DAIR.AI raw Markdown** — curated weekly signal, easy to fetch and parse.
3. **Hugging Face Papers Trending** — promising trend/curation signal, but parser stability must be proven.
4. **Semantic Scholar / GitHub** — useful enrichment, not smoke-tested in this pass.
5. **X/Twitter** — optional and brittle; use only as a link found in curated sources until stable access exists.

## No-Hallucination Rule

A source signal can only appear in generated briefs if it has an attached extraction method and evidence:

- source URL
- fetched timestamp
- raw field or parsed location
- confidence label

If unavailable, say `not checked` or omit the field. Never fill in trend metrics because they “probably exist.”
