from founder_radar.founder_signals import extract_founder_signals
from founder_radar.models import CandidatePaper, EvidenceLink, PaperTextEvidence, SourceHit


def make_candidate() -> CandidatePaper:
    return CandidatePaper(
        paper_id="arxiv:2608.28447v1",
        arxiv_id="2608.28447v1",
        source="arxiv",
        url="https://arxiv.org/abs/2608.28447v1",
        pdf_url="https://arxiv.org/pdf/2608.28447v1",
        title="Learning to Use Tools: Reinforcement Learning for Tool-Integrated Mathematical Reasoning",
        abstract="We apply reinforcement learning to improve tool use for mathematical reasoning.",
        authors=["Alice Smith"],
        published_at="2026-08-30T00:00:00Z",
        updated_at="2026-08-31T00:00:00Z",
        primary_category="cs.AI",
        categories=["cs.AI"],
        comment=None,
        journal_ref=None,
        doi=None,
        links=[
            EvidenceLink(url="https://arxiv.org/abs/2608.28447v1", label="paper", source="arxiv_link", confidence="high"),
            EvidenceLink(url="https://example.com/project", label="project", source="abstract", confidence="medium"),
            EvidenceLink(url="https://github.com/example/tool-rl", label="code", source="arxiv_comment", confidence="medium"),
        ],
        source_hits=[SourceHit(source="arxiv", source_url="https://arxiv.org/abs/2608.28447v1", observed_at="2026-09-01T00:00:00+00:00", raw_location=None, confidence="high")],
        candidate_reason=["user-supplied arXiv paper"],
        fetched_at="2026-09-01T00:00:00+00:00",
    )


def test_extract_founder_signals_from_metadata_and_pdf() -> None:
    candidate = make_candidate()
    paper_text = PaperTextEvidence(
        paper_id=candidate.paper_id,
        pdf_url=candidate.pdf_url,
        download_status="success",
        text_extraction_status="success",
        text_chars=100,
        contact_block="Alice Smith",
        emails=["alice@example.edu"],
        email_domains=["example.edu"],
        affiliation_lines=["Example University"],
        urls=[EvidenceLink(url="https://example.com/demo", label="project", source="pdf_text", confidence="medium")],
        github_urls=[EvidenceLink(url="https://github.com/example/tool-rl-2", label="code", source="pdf_text", confidence="medium")],
        observed_at="2026-09-01T00:00:00+00:00",
        errors=[],
    )

    signals = extract_founder_signals(candidate, paper_text)
    kinds = [signal["signal_type"] for signal in signals]

    assert "project_page_present" in kinds
    assert "code_repo_present" in kinds
    assert "agent_or_rl_systems_focus" in kinds
    assert "infra_or_tooling_orientation" in kinds
    assert all(signal["paper_id"] == candidate.paper_id for signal in signals)
    assert all(signal["author_key"] is None for signal in signals)


def test_extract_founder_signals_does_not_promote_generic_pdf_urls_to_project_pages() -> None:
    candidate = CandidatePaper(
        paper_id="arxiv:2608.31142v1",
        arxiv_id="2608.31142v1",
        source="arxiv",
        url="https://arxiv.org/abs/2608.31142v1",
        pdf_url="https://arxiv.org/pdf/2608.31142v1",
        title="Auditing Anonymous AI Models",
        abstract="A systems paper.",
        authors=["Yisen Xi"],
        published_at="2026-08-31T00:00:00Z",
        updated_at="2026-08-31T00:00:00Z",
        primary_category="cs.AI",
        categories=["cs.AI"],
        comment=None,
        journal_ref=None,
        doi=None,
        links=[EvidenceLink(url="https://arxiv.org/abs/2608.31142v1", label="paper", source="arxiv_link", confidence="high")],
        source_hits=[SourceHit(source="arxiv", source_url="https://arxiv.org/abs/2608.31142v1", observed_at="2026-09-01T00:00:00+00:00", raw_location=None, confidence="high")],
        candidate_reason=["user-supplied arXiv paper"],
        fetched_at="2026-09-01T00:00:00+00:00",
    )
    paper_text = PaperTextEvidence(
        paper_id=candidate.paper_id,
        pdf_url=candidate.pdf_url,
        download_status="success",
        text_extraction_status="success",
        text_chars=100,
        contact_block="Yisen Xi",
        emails=[],
        email_domains=[],
        affiliation_lines=[],
        urls=[
            EvidenceLink(url="https://doi.org/10.5281/zenodo.22210928", label="project", source="pdf_text", confidence="medium"),
            EvidenceLink(url="https://openrouter.ai/docs/api/a", label="project", source="pdf_text", confidence="medium"),
        ],
        github_urls=[EvidenceLink(url="https://github.com/example/repo", label="code", source="pdf_text", confidence="medium")],
        observed_at="2026-09-01T00:00:00+00:00",
        errors=[],
    )

    signals = extract_founder_signals(candidate, paper_text)
    signal_types_urls = [(s["signal_type"], s["evidence_url"]) for s in signals]

    assert ("code_repo_present", "https://github.com/example/repo") in signal_types_urls
    assert ("project_page_present", "https://doi.org/10.5281/zenodo.22210928") not in signal_types_urls
    assert ("project_page_present", "https://openrouter.ai/docs/api/a") not in signal_types_urls
