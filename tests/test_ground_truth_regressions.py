"""Regression tests locking in real, human-verified founder-radar outcomes.

These fixtures are frozen artifacts from three real, independently-verified
paper -> founder examples (see `_docs/notable-people-watchlist.md`):

- 2606.12688 (M*): Atindra Jha (1st author) co-authored with Jure Leskovec
  (Kumo AI co-founder). Reported to be courted by VCs at time of writing.
- 2207.01848 (TabPFN): Frank Hutter and Noah Hollmann, both Prior Labs
  founders, are direct co-authors.
- 2312.04615 (Relational Deep Learning): Jure Leskovec is a co-author;
  this is Kumo's real technical genesis paper.

These tests run entirely from saved fixtures (no live arXiv/network calls),
so they stay fast and hermetic while still guarding against real
regressions: if a future change causes any of these three known-good
papers to stop being flagged as notable/founder-relevant, this test suite
will fail immediately, per the agentic-shipping principle of turning
manual validation into automated tests.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from founder_radar.author_resolution import resolve_authors
from founder_radar.brief import render_founder_brief
from founder_radar.founder_signals import extract_founder_signals
from founder_radar.models import CandidatePaper, EvidenceLink, PaperTextEvidence, SourceHit

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "ground_truth"


def _load_candidate(fixture_dir: Path) -> CandidatePaper:
    raw = json.loads((fixture_dir / "candidate_paper.json").read_text())
    raw["links"] = [EvidenceLink(**link) for link in raw["links"]]
    raw["source_hits"] = [SourceHit(**hit) for hit in raw["source_hits"]]
    return CandidatePaper(**raw)


def _load_paper_text(fixture_dir: Path) -> PaperTextEvidence:
    raw = json.loads((fixture_dir / "paper_text_evidence.json").read_text())
    raw["urls"] = [EvidenceLink(**link) for link in raw["urls"]]
    raw["github_urls"] = [EvidenceLink(**link) for link in raw["github_urls"]]
    return PaperTextEvidence(**raw)


GROUND_TRUTH_CASES = [
    ("atindra-jha", ["Jure Leskovec"]),
    ("tabpfn", ["Frank Hutter", "Noah Hollmann"]),
    ("kumo-rdl", ["Jure Leskovec"]),
]


@pytest.mark.parametrize("case_name,expected_notable_names", GROUND_TRUTH_CASES)
def test_ground_truth_paper_flags_expected_notable_coauthors(case_name: str, expected_notable_names: list[str]) -> None:
    fixture_dir = FIXTURES_DIR / case_name
    candidate = _load_candidate(fixture_dir)
    paper_text = _load_paper_text(fixture_dir)

    signals = extract_founder_signals(candidate, paper_text)
    notable_matches = [s for s in signals if s["signal_type"] == "notable_coauthor_name_match"]
    matched_names = {match["evidence_note"].split("'")[1] for match in notable_matches}

    assert matched_names == set(expected_notable_names)
    assert all(match["confidence"] == "low" for match in notable_matches)
    assert all(match["evidence_url"].startswith("https://") for match in notable_matches)


@pytest.mark.parametrize("case_name,_expected_notable_names", GROUND_TRUTH_CASES)
def test_ground_truth_paper_reaches_manual_diligence_verdict(case_name: str, _expected_notable_names: list[str]) -> None:
    fixture_dir = FIXTURES_DIR / case_name
    candidate = _load_candidate(fixture_dir)
    paper_text = _load_paper_text(fixture_dir)

    authors = resolve_authors(candidate, paper_text)
    signals = extract_founder_signals(candidate, paper_text)
    brief = render_founder_brief(candidate, authors, signals)

    assert "- Recommendation: manual diligence needed" in brief
    assert "Notable network signal" in brief
