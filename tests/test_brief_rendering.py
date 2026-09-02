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


def test_render_founder_brief_outreach_angle_reflects_unresolved_identity() -> None:
    candidate = make_candidate()
    unresolved_author = ResolvedAuthor(
        author_key="author-1",
        name="Yisen Xi",
        paper_author_string="Yisen Xi",
        affiliation=None,
        profiles={"semantic_scholar": None, "homepage": None, "lab_page": None, "github": None, "google_scholar": None, "dblp": None, "x": None, "linkedin": None},
        identity_confidence="unresolved",
        evidence=[EvidenceClaim(claim="Raw author preserved from arXiv metadata", source_url="https://arxiv.org/abs/2608.31142v1", observed_at="2026-09-01T00:00:00+00:00", confidence="high", notes=None)],
        ambiguities=[],
    )
    brief = render_founder_brief(candidate, [unresolved_author], [])
    assert "not recommended" in brief.lower()
    assert "unresolved" in brief.lower()


def test_render_founder_brief_outreach_angle_reflects_resolved_profile() -> None:
    candidate = make_candidate()
    resolved_author = ResolvedAuthor(
        author_key="author-1",
        name="Yisen Xi",
        paper_author_string="Yisen Xi",
        affiliation="Independent Researcher, Beijing, China",
        profiles={"semantic_scholar": None, "homepage": "https://example.com/yisen", "lab_page": None, "github": None, "google_scholar": None, "dblp": None, "x": None, "linkedin": None},
        identity_confidence="high",
        evidence=[EvidenceClaim(claim="Homepage links this paper", source_url="https://example.com/yisen", observed_at="2026-09-01T00:00:00+00:00", confidence="high", notes=None)],
        ambiguities=[],
    )
    brief = render_founder_brief(candidate, [resolved_author], [])
    assert "homepage" in brief.lower()
    assert "not recommended" not in brief.lower()


def test_render_stub_brief_removed() -> None:
    import founder_radar.brief as brief_module
    assert not hasattr(brief_module, "render_stub_brief")


def test_render_founder_brief_surfaces_notable_coauthor_signal_next_to_author_name() -> None:
    candidate = make_candidate()
    author = ResolvedAuthor(
        author_key="author-1",
        name="Frank Hutter",
        paper_author_string="Frank Hutter",
        affiliation=None,
        profiles={"semantic_scholar": None, "homepage": None, "lab_page": None, "github": None, "google_scholar": None, "dblp": None, "x": None, "linkedin": None},
        identity_confidence="unresolved",
        evidence=[EvidenceClaim(claim="Raw author preserved from arXiv metadata", source_url="https://arxiv.org/abs/2608.31142v1", observed_at="2026-09-01T00:00:00+00:00", confidence="high", notes=None)],
        ambiguities=[],
    )
    signals = [
        FounderSignal(
            author_key=None,
            paper_id=candidate.paper_id,
            signal_type="notable_coauthor_name_match",
            value=True,
            confidence="low",
            evidence_url="https://priorlabs.ai/about",
            evidence_note="Author name 'Frank Hutter' is a name match only (not a verified identity resolution) against watchlist entry 'Frank Hutter': Founder and co-CEO of Prior Labs (TabPFN)",
        )
    ]

    brief = render_founder_brief(candidate, [author], signals)
    frank_section = brief.split("### Frank Hutter")[1].split("###")[0]

    assert "Notable network signal" in frank_section
    assert "Prior Labs" in frank_section
    assert "https://priorlabs.ai/about" in frank_section


def test_render_founder_brief_surfaces_paper_native_author_evidence() -> None:
    candidate = make_candidate()
    author = ResolvedAuthor(
        author_key="author-1",
        name="Minghui Xu",
        paper_author_string="Minghui Xu",
        affiliation="Stanford University",
        profiles={"semantic_scholar": None, "homepage": None, "lab_page": None, "github": None, "google_scholar": None, "dblp": None, "x": None, "linkedin": None},
        identity_confidence="unresolved",
        evidence=[EvidenceClaim(claim="Paper-level affiliation block from PDF contact block", source_url="https://arxiv.org/pdf/2608.28447v1", observed_at="2026-09-01T00:00:00+00:00", confidence="low", notes="Stanford University")],
        ambiguities=["Affiliation block was not explicitly mapped per author; stored as paper-level evidence."],
        paper_author_evidence={
            "emails": ["minghuix@stanford.edu"],
            "email_domains": ["stanford.edu"],
            "affiliation_lines": ["Stanford University"],
            "affiliation_scope": "paper_level",
            "paper_evidence_confidence": "high",
        },
    )

    brief = render_founder_brief(candidate, [author], [])

    assert "Paper-native evidence:" in brief
    assert "minghuix@stanford.edu" in brief
    assert "stanford.edu" in brief
    assert "Stanford University" in brief
    assert "paper_evidence_confidence=high" in brief
    assert "Identity confidence: unresolved" in brief


def _make_large_author_list(count: int) -> list:
    authors = []
    for i in range(1, count + 1):
        authors.append(
            ResolvedAuthor(
                author_key=f"author-{i}",
                name=f"Author {i}",
                paper_author_string=f"Author {i}",
                affiliation="Shared Lab, Example University",
                profiles={"semantic_scholar": None, "homepage": None, "lab_page": None, "github": None, "google_scholar": None, "dblp": None, "x": None, "linkedin": None},
                identity_confidence="unresolved",
                evidence=[EvidenceClaim(claim="Raw author preserved from arXiv metadata", source_url="https://arxiv.org/abs/2608.31142v1", observed_at="2026-09-01T00:00:00+00:00", confidence="high", notes=None)],
                ambiguities=[],
                paper_author_evidence={
                    "emails": ["authorfive@example.edu"] if i == 5 else [],
                    "email_domains": ["example.edu"] if i == 5 else [],
                    "affiliation_lines": ["Shared Lab, Example University"],
                    "affiliation_scope": "paper_level",
                    "paper_evidence_confidence": "medium",
                },
            )
        )
    return authors


def test_render_founder_brief_summarizes_large_author_lists() -> None:
    candidate = make_candidate()
    authors = _make_large_author_list(25)
    signals = [
        FounderSignal(author_key=None, paper_id=candidate.paper_id, signal_type="code_repo_present", value=True, confidence="medium", evidence_url="https://github.com/example/repo", evidence_note="GitHub URL from PDF text"),
    ]

    brief = render_founder_brief(candidate, authors, signals)

    assert "## Authors (25 total)" in brief
    assert "### Principal Contacts" in brief
    assert "founder_brief_authors_detail.md" in brief
    # Only a bounded number of full author blocks should render in the main brief.
    assert brief.count("### Author ") <= 5
    # First and last authors should always be represented as principal contacts.
    assert "### Author 1" in brief
    assert "### Author 25" in brief
    # The evidence ledger should not repeat the same shared paper-level affiliation
    # claim once per every one of the 25 authors.
    assert brief.count("Shared Lab, Example University") < 25


def test_render_founder_brief_keeps_full_author_blocks_under_threshold() -> None:
    candidate = make_candidate()
    authors = _make_large_author_list(8)

    brief = render_founder_brief(candidate, authors, [])

    assert "## Authors To Watch" in brief
    assert "## Authors (8 total)" not in brief
    assert brief.count("### Author ") == 8


def test_render_author_detail_document_includes_every_author() -> None:
    from founder_radar.brief import render_author_detail_document

    candidate = make_candidate()
    authors = _make_large_author_list(25)

    detail = render_author_detail_document(candidate, authors, [])

    for i in range(1, 26):
        assert f"### Author {i}" in detail


def test_render_founder_brief_surfaces_withdrawn_paper_and_pdf_failure() -> None:
    from founder_radar.models import PaperTextEvidence

    candidate = CandidatePaper(
        paper_id="arxiv:0705.1442v2",
        arxiv_id="0705.1442v2",
        source="arxiv",
        url="https://arxiv.org/abs/0705.1442v2",
        pdf_url="https://arxiv.org/pdf/0705.1442v2",
        title="Does P=NP?",
        abstract="This paper has been withdrawn Abstract: This paper has been withdrawn by the author due to the publication.",
        authors=["Some Author"],
        published_at="2007-05-10T00:00:00Z",
        updated_at="2007-05-10T00:00:00Z",
        primary_category="cs.CC",
        categories=["cs.CC"],
        comment=None,
        journal_ref=None,
        doi=None,
        links=[EvidenceLink(url="https://arxiv.org/abs/0705.1442v2", label="paper", source="arxiv_link", confidence="high")],
        source_hits=[SourceHit(source="arxiv", source_url="https://arxiv.org/abs/0705.1442v2", observed_at="2026-09-01T00:00:00+00:00", raw_location=None, confidence="high")],
        candidate_reason=["user-supplied arXiv paper"],
        fetched_at="2026-09-01T00:00:00+00:00",
    )
    paper_text = PaperTextEvidence(
        paper_id=candidate.paper_id,
        pdf_url=candidate.pdf_url,
        download_status="failed",
        text_extraction_status="not_checked",
        text_chars=0,
        contact_block=None,
        emails=[],
        email_domains=[],
        affiliation_lines=[],
        urls=[],
        github_urls=[],
        observed_at="2026-09-01T00:00:00+00:00",
        errors=["PDF download failed: HTTP Error 404: Not Found"],
    )

    brief = render_founder_brief(candidate, [], [], paper_text=paper_text)

    assert "WITHDRAWN" in brief
    assert "PDF" in brief
    assert "404" in brief or "download failed" in brief.lower()


def test_render_founder_brief_omits_pdf_status_note_when_healthy() -> None:
    from founder_radar.models import PaperTextEvidence

    candidate = make_candidate()
    paper_text = PaperTextEvidence(
        paper_id=candidate.paper_id,
        pdf_url=candidate.pdf_url,
        download_status="success",
        text_extraction_status="success",
        text_chars=500,
        contact_block="Yisen Xi",
        emails=[],
        email_domains=[],
        affiliation_lines=[],
        urls=[],
        github_urls=[],
        observed_at="2026-09-01T00:00:00+00:00",
        errors=[],
    )
    brief = render_founder_brief(candidate, [], [], paper_text=paper_text)
    assert "WITHDRAWN" not in brief
    assert "PDF evidence unavailable" not in brief
