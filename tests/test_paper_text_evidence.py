from founder_radar.models import CandidatePaper, EvidenceLink, SourceHit
from founder_radar.paper_text import extract_paper_text_evidence, parse_pdf_text_evidence


def make_candidate(pdf_url: str | None = "https://example.com/paper.pdf") -> CandidatePaper:
    return CandidatePaper(
        paper_id="arxiv:2608.28447v1",
        arxiv_id="2608.28447v1",
        source="arxiv",
        url="https://arxiv.org/abs/2608.28447v1",
        pdf_url=pdf_url,
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


def test_parse_pdf_text_evidence_extracts_contact_details() -> None:
    text = """Alice Smith1, Bob Jones2
Example AI Lab, Example University
alice@example.edu, bob@company.ai
Project: https://example.com/project
Code: https://github.com/example/tool-rl

Abstract
This paper studies tools.
"""
    evidence = parse_pdf_text_evidence(
        paper_id="arxiv:2608.28447v1",
        pdf_url="https://example.com/paper.pdf",
        text=text,
        observed_at="2026-09-01T00:00:00+00:00",
    )
    data = evidence.to_dict()

    assert data["download_status"] == "success"
    assert data["text_extraction_status"] == "success"
    assert data["emails"] == ["alice@example.edu", "bob@company.ai"]
    assert data["email_domains"] == ["company.ai", "example.edu"]
    assert any("Example University" in line for line in data["affiliation_lines"])
    assert any(link["url"] == "https://example.com/project" for link in data["urls"])
    assert any(link["url"] == "https://github.com/example/tool-rl" for link in data["github_urls"])
    assert "Alice Smith1, Bob Jones2" in (data["contact_block"] or "")


def test_extract_paper_text_evidence_without_pdf_url() -> None:
    candidate = make_candidate(pdf_url=None)
    evidence = extract_paper_text_evidence(candidate)
    data = evidence.to_dict()

    assert data["download_status"] == "not_checked"
    assert data["text_extraction_status"] == "not_checked"
    assert data["errors"] == ["PDF URL not found in candidate paper artifact"]


def test_parse_pdf_text_evidence_stops_contact_block_at_abstract_variants() -> None:
    text = """Example Title
Alice Smith, Bob Jones
University of Example
Abstract— This section starts here.
More body text.
1. Introduction
"""
    evidence = parse_pdf_text_evidence(
        paper_id="arxiv:1",
        pdf_url="https://example.com/paper.pdf",
        text=text,
        observed_at="2026-09-01T00:00:00+00:00",
    )
    assert evidence.contact_block == "Example Title\nAlice Smith, Bob Jones\nUniversity of Example"


def test_parse_pdf_text_evidence_does_not_misclassify_title_substring_as_affiliation() -> None:
    text = """Depth Anything: Unleashing the Power of Large-Scale Unlabeled Data
Lihe Yang1
Bingyi Kang2

Abstract
This paper studies depth estimation.
"""
    evidence = parse_pdf_text_evidence(
        paper_id="arxiv:1",
        pdf_url="https://example.com/paper.pdf",
        text=text,
        observed_at="2026-09-01T00:00:00+00:00",
    )
    data = evidence.to_dict()

    assert data["affiliation_lines"] == []


def test_parse_pdf_text_evidence_does_not_classify_standalone_email_as_affiliation() -> None:
    text = """DeepSeek-V3 Technical Report
DeepSeek-AI
research@deepseek.com

Abstract
We present DeepSeek-V3.
"""
    evidence = parse_pdf_text_evidence(
        paper_id="arxiv:1",
        pdf_url="https://example.com/paper.pdf",
        text=text,
        observed_at="2026-09-01T00:00:00+00:00",
    )
    data = evidence.to_dict()

    assert data["emails"] == ["research@deepseek.com"]
    assert data["affiliation_lines"] == []


def test_parse_pdf_text_evidence_still_detects_real_affiliation_lines() -> None:
    text = """AutoGen: Enabling Next-Gen LLM Applications
Qingyun Wu, Gagan Bansal
Microsoft Research, Pennsylvania State University

Abstract
We present AutoGen.
"""
    evidence = parse_pdf_text_evidence(
        paper_id="arxiv:1",
        pdf_url="https://example.com/paper.pdf",
        text=text,
        observed_at="2026-09-01T00:00:00+00:00",
    )
    data = evidence.to_dict()

    assert any("Microsoft Research" in line for line in data["affiliation_lines"])


def test_parse_pdf_text_evidence_expands_brace_grouped_emails() -> None:
    text = """LLaMA: Open and Efficient Foundation Language Models
Hugo Touvron, Thibaut Lavril
Correspondence: {htouvron,thibautlav,gizacard}@meta.com

Abstract
We introduce LLaMA.
"""
    evidence = parse_pdf_text_evidence(
        paper_id="arxiv:1",
        pdf_url="https://example.com/paper.pdf",
        text=text,
        observed_at="2026-09-01T00:00:00+00:00",
    )
    data = evidence.to_dict()

    assert data["emails"] == ["gizacard@meta.com", "htouvron@meta.com", "thibautlav@meta.com"]
    assert data["email_domains"] == ["meta.com"]


def test_parse_pdf_text_evidence_flags_github_url_with_ownership_cue() -> None:
    text = """AutoGen: Enabling Next-Gen LLM Applications
Qingyun Wu, Gagan Bansal
Microsoft Research

Abstract
AutoGen is a framework. Code is available at https://github.com/microsoft/autogen.
For related tooling, see also https://github.com/yoheinakajima/babyagi.
"""
    evidence = parse_pdf_text_evidence(
        paper_id="arxiv:1",
        pdf_url="https://example.com/paper.pdf",
        text=text,
        observed_at="2026-09-01T00:00:00+00:00",
    )
    data = evidence.to_dict()
    by_url = {link["url"]: link for link in data["github_urls"]}

    assert by_url["https://github.com/microsoft/autogen"]["notes"] is not None
    assert by_url["https://github.com/yoheinakajima/babyagi"]["notes"] is None
