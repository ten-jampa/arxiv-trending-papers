from founder_radar.brief import render_founder_brief
from founder_radar.models import CandidatePaper, EvidenceClaim, EvidenceLink, FounderSignal, ResolvedAuthor, SourceHit


def make_candidate() -> CandidatePaper:
    return CandidatePaper(
        paper_id="arxiv:2608.31142v1",
        arxiv_id="2608.31142v1",
        source="arxiv",
        url="https://arxiv.org/abs/2608.31142v1",
        pdf_url="https://arxiv.org/pdf/2608.31142v1",
        title="Auditing Anonymous AI Models: A Four-Stage Protocol for Black-Box Identity Verification",
        abstract="We present a protocol for black-box identity verification of anonymous AI models.",
        authors=["Yisen Xi"],
        published_at="2026-08-31T00:00:00Z",
        updated_at="2026-08-31T00:00:00Z",
        primary_category="cs.AI",
        categories=["cs.SE", "cs.AI", "cs.CR"],
        comment=None,
        journal_ref=None,
        doi=None,
        links=[EvidenceLink(url="https://arxiv.org/abs/2608.31142v1", label="paper", source="arxiv_link", confidence="high")],
        source_hits=[SourceHit(source="arxiv", source_url="https://arxiv.org/abs/2608.31142v1", observed_at="2026-09-01T00:00:00+00:00", raw_location=None, confidence="high")],
        candidate_reason=["user-supplied arXiv paper"],
        fetched_at="2026-09-01T00:00:00+00:00",
    )


def test_render_founder_brief_includes_required_sections() -> None:
    candidate = make_candidate()
    authors = [
        ResolvedAuthor(
            author_key="author-1",
            name="Yisen Xi",
            paper_author_string="Yisen Xi",
            affiliation="Independent Researcher, Beijing, China",
            profiles={"semantic_scholar": None, "homepage": None, "lab_page": None, "github": None, "google_scholar": None, "dblp": None, "x": None, "linkedin": None},
            identity_confidence="unresolved",
            evidence=[
                EvidenceClaim(claim="Raw author preserved from arXiv metadata", source_url="https://arxiv.org/abs/2608.31142v1", observed_at="2026-09-01T00:00:00+00:00", confidence="high", notes=None),
                EvidenceClaim(claim="Paper-native affiliation from PDF contact block", source_url="https://arxiv.org/pdf/2608.31142v1", observed_at="2026-09-01T00:00:01+00:00", confidence="medium", notes="Independent Researcher, Beijing, China"),
            ],
            ambiguities=[],
        )
    ]
    signals = [
        FounderSignal(author_key=None, paper_id=candidate.paper_id, signal_type="code_repo_present", value=True, confidence="medium", evidence_url="https://github.com/example/repo", evidence_note="GitHub URL from PDF text"),
        FounderSignal(author_key=None, paper_id=candidate.paper_id, signal_type="infra_or_tooling_orientation", value=True, confidence="medium", evidence_url=candidate.url, evidence_note="Title suggests systems orientation"),
    ]

    brief = render_founder_brief(candidate, authors, signals)

    assert brief.startswith(f"# Founder-Sourcing Brief: {candidate.title}")
    assert "## Verdict" in brief
    assert "## Paper" in brief
    assert "## Why This Could Matter Commercially" in brief
    assert "## Authors To Watch" in brief
    assert "## Founder-Signal Evidence" in brief
    assert "## Unknowns / Do Not Overclaim" in brief
    assert "## Evidence Ledger" in brief
    assert "manual diligence needed" in brief.lower()
    assert "Yisen Xi" in brief
    assert "Independent Researcher, Beijing, China" in brief
    assert "https://github.com/example/repo" in brief


def test_render_founder_brief_skips_when_no_founder_signals_exist() -> None:
    candidate = CandidatePaper(
        paper_id="arxiv:2608.31126v1",
        arxiv_id="2608.31126v1",
        source="arxiv",
        url="https://arxiv.org/abs/2608.31126v1",
        pdf_url="https://arxiv.org/pdf/2608.31126v1",
        title="Bounded gaps between primes",
        abstract="A pure math paper.",
        authors=["Julia Stadlmann"],
        published_at="2026-08-31T00:00:00Z",
        updated_at="2026-08-31T00:00:00Z",
        primary_category="math.NT",
        categories=["math.NT"],
        comment=None,
        journal_ref=None,
        doi=None,
        links=[EvidenceLink(url="https://arxiv.org/abs/2608.31126v1", label="paper", source="arxiv_link", confidence="high")],
        source_hits=[SourceHit(source="arxiv", source_url="https://arxiv.org/abs/2608.31126v1", observed_at="2026-09-01T00:00:00+00:00", raw_location=None, confidence="high")],
        candidate_reason=["user-supplied arXiv paper"],
        fetched_at="2026-09-01T00:00:00+00:00",
    )
    authors = [
        ResolvedAuthor(
            author_key="author-1",
            name="Julia Stadlmann",
            paper_author_string="Julia Stadlmann",
            affiliation=None,
            profiles={"semantic_scholar": None, "homepage": None, "lab_page": None, "github": None, "google_scholar": None, "dblp": None, "x": None, "linkedin": None},
            identity_confidence="unresolved",
            evidence=[EvidenceClaim(claim="Raw author preserved from arXiv metadata", source_url="https://arxiv.org/abs/2608.31126v1", observed_at="2026-09-01T00:00:00+00:00", confidence="high", notes=None)],
            ambiguities=[],
        )
    ]
    brief = render_founder_brief(candidate, authors, [])
    assert "- Recommendation: skip" in brief
    assert "- Confidence: low" in brief


def test_render_founder_brief_watch_confidence_increases_for_multiple_signal_families() -> None:
    candidate = make_candidate()
    authors = []
    signals = [
        FounderSignal(author_key=None, paper_id=candidate.paper_id, signal_type="infra_or_tooling_orientation", value=True, confidence="medium", evidence_url=candidate.url, evidence_note="Tooling"),
        FounderSignal(author_key=None, paper_id=candidate.paper_id, signal_type="benchmark_or_dataset_created", value=True, confidence="low", evidence_url=candidate.url, evidence_note="Benchmark"),
    ]
    brief = render_founder_brief(candidate, authors, signals)
    assert "- Recommendation: watch" in brief
    assert "- Confidence: medium" in brief
