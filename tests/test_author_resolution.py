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
    assert authors[0]["paper_author_evidence"]["emails"] == []
    assert authors[1]["paper_author_evidence"]["emails"] == []
    assert "alice@example.edu" in authors[0]["paper_author_evidence"]["ambiguous_emails"]
    assert all(
        "Affiliation block was not explicitly mapped per author" in "; ".join(author["ambiguities"])
        for author in authors
    )


def test_resolve_authors_uses_single_author_paper_native_affiliation() -> None:
    candidate = CandidatePaper(
        paper_id="arxiv:2608.31142v1",
        arxiv_id="2608.31142v1",
        source="arxiv",
        url="https://arxiv.org/abs/2608.31142v1",
        pdf_url="https://arxiv.org/pdf/2608.31142v1",
        title="Single Author Paper",
        abstract="Example abstract",
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
        contact_block="Yisen Xi\nIndependent Researcher, Beijing, China\nxys21@tsinghua.org.cn",
        emails=["xys21@tsinghua.org.cn"],
        email_domains=["tsinghua.org.cn"],
        affiliation_lines=["Independent Researcher, Beijing, China"],
        urls=[],
        github_urls=[],
        observed_at="2026-09-01T00:00:00+00:00",
        errors=[],
    )

    authors = resolve_authors(candidate, paper_text)
    author = authors[0]

    assert author["identity_confidence"] == "unresolved"
    assert author["affiliation"] == "Independent Researcher, Beijing, China"
    claims = [item["claim"] for item in author["evidence"]]
    assert "Paper-native affiliation from PDF contact block" in claims
    assert "Paper-native email domain from PDF contact block" in claims


def test_resolve_authors_uses_shared_affiliation_for_two_author_paper_and_strong_email_match() -> None:
    candidate = CandidatePaper(
        paper_id="arxiv:2608.31170v1",
        arxiv_id="2608.31170v1",
        source="arxiv",
        url="https://arxiv.org/abs/2608.31170v1",
        pdf_url="https://arxiv.org/pdf/2608.31170v1",
        title="Two Author Paper",
        abstract="Example abstract",
        authors=["Carlos Bain", "Max Bain"],
        published_at="2026-08-31T00:00:00Z",
        updated_at="2026-08-31T00:00:00Z",
        primary_category="cs.CL",
        categories=["cs.CL"],
        comment=None,
        journal_ref=None,
        doi=None,
        links=[EvidenceLink(url="https://arxiv.org/abs/2608.31170v1", label="paper", source="arxiv_link", confidence="high")],
        source_hits=[SourceHit(source="arxiv", source_url="https://arxiv.org/abs/2608.31170v1", observed_at="2026-09-01T00:00:00+00:00", raw_location=None, confidence="high")],
        candidate_reason=["user-supplied arXiv paper"],
        fetched_at="2026-09-01T00:00:00+00:00",
    )
    paper_text = PaperTextEvidence(
        paper_id=candidate.paper_id,
        pdf_url=candidate.pdf_url,
        download_status="success",
        text_extraction_status="success",
        text_chars=100,
        contact_block="Carlos Bain, Max Bain\nUniversity of Oxford",
        emails=["carlos.o.bain@gmail.com"],
        email_domains=["gmail.com"],
        affiliation_lines=["University of Oxford"],
        urls=[],
        github_urls=[],
        observed_at="2026-09-01T00:00:00+00:00",
        errors=[],
    )

    authors = resolve_authors(candidate, paper_text)

    assert [author["affiliation"] for author in authors] == ["University of Oxford", "University of Oxford"]
    assert all(author["identity_confidence"] == "unresolved" for author in authors)
    for author in authors:
        claims = [item["claim"] for item in author["evidence"]]
        assert "Paper-level affiliation block from PDF contact block" in claims
    assert authors[0]["paper_author_evidence"]["emails"] == ["carlos.o.bain@gmail.com"]
    assert authors[0]["paper_author_evidence"]["email_domains"] == ["gmail.com"]
    assert authors[1]["paper_author_evidence"]["emails"] == []


def test_resolve_authors_attaches_stanford_email_and_affiliation_without_external_identity() -> None:
    candidate = CandidatePaper(
        paper_id="arxiv:2608.28447v1",
        arxiv_id="2608.28447v1",
        source="arxiv",
        url="https://arxiv.org/abs/2608.28447v1",
        pdf_url="https://arxiv.org/pdf/2608.28447v1",
        title="Learning to Use Tools",
        abstract="Example abstract",
        authors=["Minghui Xu", "Zi Wang"],
        published_at="2026-08-28T00:00:00Z",
        updated_at="2026-08-28T00:00:00Z",
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
    paper_text = PaperTextEvidence(
        paper_id=candidate.paper_id,
        pdf_url=candidate.pdf_url,
        download_status="success",
        text_extraction_status="success",
        text_chars=100,
        contact_block="Minghui Xu, Zi Wang\nDepartment of Energy Science and Engineering\nStanford University\nminghuix@stanford.edu, ziwang3@stanford.edu",
        emails=["minghuix@stanford.edu", "ziwang3@stanford.edu"],
        email_domains=["stanford.edu"],
        affiliation_lines=["Department of Energy Science and Engineering", "Stanford University"],
        urls=[],
        github_urls=[],
        observed_at="2026-09-01T00:00:00+00:00",
        errors=[],
    )

    authors = resolve_authors(candidate, paper_text)

    assert authors[0]["identity_confidence"] == "unresolved"
    assert authors[1]["identity_confidence"] == "unresolved"
    assert authors[0]["paper_author_evidence"]["emails"] == ["minghuix@stanford.edu"]
    assert authors[1]["paper_author_evidence"]["emails"] == ["ziwang3@stanford.edu"]
    assert authors[0]["paper_author_evidence"]["email_domains"] == ["stanford.edu"]
    assert authors[1]["paper_author_evidence"]["email_domains"] == ["stanford.edu"]
    assert "Stanford University" in authors[0]["paper_author_evidence"]["affiliation_lines"]
    assert "Stanford University" in authors[1]["paper_author_evidence"]["affiliation_lines"]
    assert authors[0]["paper_author_evidence"]["paper_evidence_confidence"] == "high"
    assert authors[1]["paper_author_evidence"]["paper_evidence_confidence"] == "high"
