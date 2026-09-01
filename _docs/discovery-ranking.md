# Discovery And Ranking Shape

## Why This Exists

The repo should keep three concerns separate:

```text
discover -> rank -> founder-brief
```

These stages answer different questions.

- **Discover**: which papers should enter the candidate set?
- **Rank**: which candidate papers deserve founder-radar attention first?
- **Founder brief**: for one selected paper, what evidence-backed founder view can we produce?

Do not collapse these into one hidden score.

## Stage Boundaries

### Discover

Purpose: produce candidate paper artifacts from public sources.

Inputs later may include:

- arXiv search
- Hugging Face Papers Trending
- DAIR.AI AI Papers of the Week

Output:

- candidate paper artifacts only

Discover does **not** produce founder conclusions.

### Rank

Purpose: prioritize candidate papers for manual review or founder-brief generation.

Ranking should prefer transparent rule composition over one fake-precise scalar.

Good ranking inputs:

- `code_repo_present`
- `project_page_present`
- `infra_or_tooling_orientation`
- `agent_or_rl_systems_focus`
- `benchmark_or_dataset_created`
- identity still `unresolved` or not

Good ranking outputs:

- priority bucket: `high`, `medium`, `low`
- explicit reasons
- unresolved fields preserved

Avoid:

- opaque founder scores like `7.3/10`
- numeric weighting that looks precise but is not calibrated

### Founder Brief

Purpose: perform deeper analysis on one paper and produce the human-facing sourcing artifact.

This stage can use the evidence artifacts and an optional ranking hint, but the brief must still stand on its own evidence ledger.


## Ranking Signal Families

The best ranking signals should feel intuitive to a human reviewer.

A good question is:

> if this signal is `true`, does it change whether I would want to read the brief now instead of later?

Prefer a small set of deep signal families over a long bag of shallow tags.

### 1. Builder Signal

Question:

> did the authors ship something beyond the paper?

Examples:

- `code_repo_present`
- `project_page_present`
- demo or package link later, if sourced

Why it matters:

Builder behavior is more founder-relevant than prestige alone.

### 2. Wedge Signal

Question:

> does the paper attack a painful, legible problem that could become a company wedge?

Examples:

- reliability
- verification
- workflow bottlenecks
- infrastructure friction
- deployment constraints
- operational cost or latency

Preferred output shape:

- `commercially_legible_problem = true|false|unresolved`
- short reason, not a numeric score

Why it matters:

A founder-radar paper should point to a problem, not just an elegant idea.

### 3. Systems Signal

Question:

> is this work about real systems, tools, or workflows instead of only benchmark accuracy?

Examples:

- `infra_or_tooling_orientation`
- `agent_or_rl_systems_focus`

Why it matters:

Systems-oriented researchers are often closer to productizable behavior than purely abstract work.

### 4. Artifact Signal

Question:

> did the paper create a reusable asset other people may build on?

Examples:

- `benchmark_or_dataset_created`
- benchmark, corpus, or evaluation suite language in title/abstract

Why it matters:

Reusable artifacts can indicate category-shaping behavior, not just paper-writing.

### 5. Identity Confidence Signal

Question:

> can we safely tell who these people are?

Examples:

- `identity_confidence = unresolved|low|medium|high`
- public profiles resolved or not

Why it matters:

A strong paper with weak identity resolution may still be worth ranking, but should route to diligence instead of outreach.

### 6. Source Quality Signal

Question:

> how direct is the evidence?

Examples:

- from arXiv metadata/comment
- from PDF contact block
- from cited GitHub URL in the paper
- from later web enrichment, if corroborated

Why it matters:

Direct paper-native evidence should outrank weak or indirect web guesses.

## Ranking Pattern

A good ranking system can stay simple if the signals are deep enough.

Example reasoning shape:

- `high`: builder signal + systems or wedge signal + at least moderate evidence quality
- `medium`: one strong signal family or several weak-but-consistent ones
- `low`: interesting paper, but founder relevance is thin or identity remains unclear
- `skip`: no meaningful founder-radar signals

This keeps the ranking intuitive without pretending to know more than the artifacts support.

## Signal Design Bias

Prefer boolean or categorical signals over invented numeric scoring.

Examples:

- `code_repo_present = true`
- `project_page_present = false`
- `identity_confidence = unresolved`
- `benchmark_or_dataset_created = true`

This is better than:

- `founder_score = 6.8`
- `commerciality_score = 72`

unless the number is directly observed or later calibrated from real review data.

## Later Extension Rule

If the repo later adds ranking:

1. keep signal extraction inspectable
2. keep ranking rules explicit
3. treat ranking as a prioritization layer, not a truth layer
4. add learned scoring only after enough reviewed examples exist


## Working Ranking Rule From Local Experiments

This rule is not a final model. It is the current explicit heuristic that survived small real-paper checks.

### Priority Buckets

- `high`
  - direct builder evidence is present (`code_repo_present` or `project_page_present`)
  - and at least one more founder-radar signal family is present

- `medium`
  - direct builder evidence is present by itself, or
  - multiple non-builder signal families are present

- `low`
  - exactly one weaker founder-radar signal family is present
  - examples: only `infra_or_tooling_orientation`, only `agent_or_rl_systems_focus`, or only `benchmark_or_dataset_created`

- `skip`
  - no meaningful founder-radar signals are present

### Why This Rule

Observed from local experiments on real papers:

- code links plus systems orientation felt clearly more urgent than other cases
- multiple independent signal families were worth reading even without code
- a single broad systems or benchmark signal felt interesting but weak
- no-signal papers should not consume founder-brief attention first

## What Belongs In Ranking vs Processing

### Ranking Inputs

Ranking should mostly use cheap, inspectable, early-stage features:

- direct builder signal present or not
- number of independent signal families
- signal-source directness
- broad systems orientation
- benchmark or dataset artifact present or not
- optional identity confidence only as a routing hint

### Do Not Let Ranking Depend On These Early

These belong more to the later founder-brief processing layer than to first-pass ranking:

- nuanced commercialization narrative
- outreach wording
- fine-grained identity interpretation
- hand-wavy founder intent claims
- fake-precise scalar founder scores

### Processing Layer Responsibilities

Once a paper is selected for `founder-brief`, the deeper layer can spend more effort on:

- cautious author resolution
- evidence ledger quality
- unknowns and caveats
- optional bounded LLM interpretation
- final watch / diligence / skip wording for the paper-level brief


## Calibration Finding: Broad Keyword Hints Break Ranking

A batch experiment on 16 real, varied arXiv papers found that `infra_or_tooling_orientation`
fired on 9/16 (56%) papers under the original hint list `("tool", "tools", "workflow",
"system", "infrastructure", "verification", "batching", "deploy", "reliability")`.

Root cause: words like `system` and `deploy` (matching "deployment", "deployed") are
near-universal in ML abstracts and carry almost no discriminating signal. This silently
inflated the `high` priority bucket, since any paper with a GitHub link plus this
near-guaranteed hit reached "multiple signal families."

Fix: tightened the hint list to more specific operational-orientation words:
`("infrastructure", "reliability", "batching", "latency", "on-premise", "real-time",
"production-grade", "throughput", "verification")`.

Result on the same 16-paper batch: hit rate dropped from 56% to 25%, and the `high` bucket
dropped from 6/16 to 5/16, with the remaining `high` papers showing genuinely stronger
combined evidence (e.g. code repo + benchmark artifact, or 4 independent signal families).
A previously-approved case (`Auditing Anonymous AI Models`, high via code + verification)
was preserved, and a previously-noisy case (`SUN`, tagged low via a bare "system" match)
correctly dropped to `skip` since it has no real evidence.

Lesson: any keyword-based signal must be spot-checked against a real batch, not just a
handful of hand-picked positive/negative examples, before being trusted in ranking. A
single common word can dominate a signal's behavior across an entire corpus.
