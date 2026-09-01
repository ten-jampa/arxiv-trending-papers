import json
from pathlib import Path

from founder_radar.models import CandidatePaper, EvidenceLink, PaperTextEvidence, SourceHit
from founder_radar.author_resolution import resolve_authors


def make_candidate() -> CandidatePaper:
    return CandidatePaper(
        paper_id="arxiv:2608.28447v1",
        arxiv_id="2608.28447v1",
        source="arxiv",
        url="https://arxiv.org/abs/2608.28447v1",
        pdf_url="https://arxiv.org/pdf/2608.28447v1",
        title="Example Paper",
        abstract="Example abstract",
        authors=["Alice Smith", "Bob Jones"],
        published_at="2026-08-30T00:00:00Z",
        updated_at="2026-08-31T00:00:00Z",
        primary_category="cs.AI",
        categories=["cs.AI"],
        comment=None,
        journal_ref=None,
        doi=None,
        links=[EvidenceLink(url="https://arxiv.org/abs/2608.28447v1", label="paper", source="arxiv_link", confidence="high")],
        source_hits=[SourceHit(source="arxiv", source_url="https://arxiv.org/abs/2608.28447v1", observed_at="2026-09-01T00:00:00+00:00", raw_location=None, confidence="high")],
        candidate_reason=["user-supplied arXiv paper"],
        fetched_at="2026-09-01T00:00:00+00:00",
    )


def test_resolve_authors_preserves_raw_strings_and_marks_unresolved() -> None:
    candidate = make_candidate()
    paper_text = PaperTextEvidence(
        paper_id=candidate.paper_id,
        pdf_url=candidate.pdf_url,
        download_status="success",
        text_extraction_status="success",
        text_chars=100,
        contact_block="Alice Smith\nExample University\nalice@example.edu",
        emails=["alice@example.edu"],
        email_domains=["example.edu"],
        affiliation_lines=["Example University"],
        urls=[],
        github_urls=[],
        observed_at="2026-09-01T00:00:00+00:00",
        errors=[],
    )

    authors = resolve_authors(candidate, paper_text)

    assert [author["paper_author_string"] for author in authors] == ["Alice Smith", "Bob Jones"]
    assert [author["identity_confidence"] for author in authors] == ["unresolved", "unresolved"]
    assert all(author["profiles"]["linkedin"] is None for author in authors)
    assert all(author["ambiguities"] == [] for author in authors)
