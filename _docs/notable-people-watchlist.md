# Notable People Watchlist

## Why This Exists

`founder_signals.json` includes a `notable_coauthor_name_match` signal type.
It flags when a paper's raw author list contains a name that matches an
entry in a small, manually curated watchlist of people already known to
have founded or co-founded a company.

This came directly from a real example: Atindra Jha (arXiv `2606.12688`,
first author) co-authored a paper with Jure Leskovec (Stanford CS
professor, co-founder of Kumo AI). Jha was independently reported to be
getting courted by VCs around the same period. Two more real, verified
examples (Frank Hutter and Noah Hollmann, TabPFN -> Prior Labs) were found
and confirmed via primary sources during the same session that built this
feature. See `artifacts/ground-truth-*` for the real briefs generated
against these three cases.

## What This Signal Is NOT

This is a name-only match, never an identity resolution. Per this repo's
identity rules (`CONTEXT.md`), a name match alone must never be treated as
a confirmed identity, and this signal must never write to a
`ResolvedAuthor`'s `identity_confidence` or `profiles` fields. It stays
entirely within `founder_signals.json` as a low-confidence hint that a
human should verify, exactly like any other founder signal here.

The wording of the evidence note always says "name match only (not a
verified identity resolution)" for this reason -- do not remove that
phrasing when adding entries or touching `founder_signals.py`.

## Verification Policy For Adding An Entry

Every entry in `src/founder_radar/data/notable_people.json` must be:

1. Individually verified against a primary source (the company's own site,
   the person's own institutional bio page) or at least two independent
   credible secondary sources (e.g. Wikipedia plus a reputable press
   article) before being added.
2. Cited with a real, working `evidence_url` (and ideally a
   `corroborating_url`) -- not a search-result redirect link, not a guess.
3. Dated with `verified_at` so stale entries can be periodically re-checked.
4. Added one at a time, from a real, checkable claim -- not bulk-scraped,
   not inferred from a list of "notable AI people," not guessed from
   memory/training data without independent verification in the current
   session.

Do not add an entry you have not personally verified in the current
session, even if it seems obviously true. This repo's whole design
philosophy is "sparse and true beats rich and fake" -- a wrong entry here
would put a fabricated, high-stakes claim about a specific real person
directly into a founder-sourcing brief.

## Known Limitations

- Exact, case-insensitive name matching only. A name formatted differently
  on a given paper (middle initials, transliteration, maiden name, etc.)
  will not match. This is a deliberate simplicity choice: fuzzy matching
  raises the risk of merging two different people by name alone, which is
  explicitly forbidden by this repo's identity rules.
- The watchlist is small and grows manually. It will miss the vast
  majority of real founder-relevant coauthors. Absence of a match is not
  evidence of anything; it just means nobody has verified and added that
  person yet.
- This does not replace deeper identity resolution (homepage, GitHub,
  Semantic Scholar, LinkedIn) described elsewhere in `_docs/spec.md`; it is
  a cheap, deterministic, low-confidence early hint layered on top.
