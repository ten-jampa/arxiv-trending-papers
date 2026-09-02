import json
from pathlib import Path

from founder_radar import cli
from founder_radar.models import CandidatePaper, EvidenceClaim, EvidenceLink, FounderSignal, PaperTextEvidence, ResolvedAuthor, SourceHit


def test_cli_writes_candidate_and_paper_text_artifacts_and_brief(tmp_path: Path, monkeypatch) -> None:
    candidate = CandidatePaper(
        paper_id="arxiv:2608.28447v1",
        arxiv_id="2608.28447v1",
        source="arxiv",
        url="https://arxiv.org/abs/2608.28447v1",
        pdf_url="https://arxiv.org/pdf/2608.28447v1",
        title="Example Paper",
        abstract="Example abstract",
        authors=["Alice Smith"],
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

    paper_text_evidence = PaperTextEvidence(
        paper_id="arxiv:2608.28447v1",
        pdf_url="https://arxiv.org/pdf/2608.28447v1",
        download_status="success",
        text_extraction_status="success",
        text_chars=42,
        contact_block="Alice Smith",
        emails=["alice@example.edu"],
        email_domains=["example.edu"],
        affiliation_lines=["Example University"],
        urls=[EvidenceLink(url="https://example.com/project", label="project", source="pdf_text", confidence="medium")],
        github_urls=[EvidenceLink(url="https://github.com/example/tool-rl", label="code", source="pdf_text", confidence="medium")],
        observed_at="2026-09-01T00:00:00+00:00",
        errors=[],
    )

    resolved_authors = [
        ResolvedAuthor(
            author_key="author-1",
            name="Alice Smith",
            paper_author_string="Alice Smith",
            affiliation=None,
            profiles={"semantic_scholar": None, "homepage": None, "lab_page": None, "github": None, "google_scholar": None, "dblp": None, "x": None, "linkedin": None},
            identity_confidence="unresolved",
            evidence=[EvidenceClaim(claim="Raw author preserved from arXiv metadata", source_url="https://arxiv.org/abs/2608.28447v1", observed_at="2026-09-01T00:00:00+00:00", confidence="high", notes=None)],
            ambiguities=[],
        ).to_dict()
    ]

    founder_signals = [
        FounderSignal(author_key=None, paper_id="arxiv:2608.28447v1", signal_type="project_page_present", value=True, confidence="medium", evidence_url="https://example.com/project", evidence_note="Project link from PDF text").to_dict()
    ]

    monkeypatch.setattr(cli, "fetch_candidate_paper", lambda _: candidate)
    monkeypatch.setattr(cli, "extract_paper_text_evidence", lambda _candidate, contact_parser=None: paper_text_evidence)
    monkeypatch.setattr(cli, "resolve_authors", lambda _candidate, _paper_text: resolved_authors)
    monkeypatch.setattr(cli, "extract_founder_signals", lambda _candidate, _paper_text: founder_signals)
    artifacts_dir = tmp_path / "artifacts"
    output_path = tmp_path / "founder_brief.md"
    people_dir = tmp_path / "people"

    exit_code = cli.main([
        "founder-brief", "2608.28447v1",
        "--artifacts-dir", str(artifacts_dir),
        "--output", str(output_path),
        "--people-dir", str(people_dir),
    ])

    assert exit_code == 0
    people_path = people_dir / "people.json"
    assert people_path.exists()
    people_data = json.loads(people_path.read_text())
    assert len(people_data) == 1
    assert next(iter(people_data.values()))["display_name"] == "Alice Smith"
    candidate_path = artifacts_dir / "candidate_paper.json"
    assert candidate_path.exists()
    paper_text_path = artifacts_dir / "paper_text_evidence.json"
    resolved_authors_path = artifacts_dir / "resolved_authors.json"
    founder_signals_path = artifacts_dir / "founder_signals.json"
    assert output_path.exists()
    assert paper_text_path.exists()
    assert resolved_authors_path.exists()
    assert founder_signals_path.exists()
    data = json.loads(candidate_path.read_text())
    paper_text_data = json.loads(paper_text_path.read_text())
    resolved_authors_data = json.loads(resolved_authors_path.read_text())
    founder_signals_data = json.loads(founder_signals_path.read_text())
    assert data["title"] == "Example Paper"
    assert paper_text_data["emails"] == ["alice@example.edu"]
    assert resolved_authors_data[0]["identity_confidence"] == "unresolved"
    assert founder_signals_data[0]["signal_type"] == "project_page_present"
    brief_text = output_path.read_text()
    assert "## Verdict" in brief_text
    assert "## Evidence Ledger" in brief_text


def test_cli_no_sync_people_flag_skips_registry(tmp_path: Path, monkeypatch) -> None:
    candidate = CandidatePaper(
        paper_id="arxiv:2608.28447v1",
        arxiv_id="2608.28447v1",
        source="arxiv",
        url="https://arxiv.org/abs/2608.28447v1",
        pdf_url="https://arxiv.org/pdf/2608.28447v1",
        title="Example Paper",
        abstract="Example abstract",
        authors=["Alice Smith"],
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
    paper_text_evidence = PaperTextEvidence(
        paper_id="arxiv:2608.28447v1",
        pdf_url="https://arxiv.org/pdf/2608.28447v1",
        download_status="success",
        text_extraction_status="success",
        text_chars=42,
        contact_block="Alice Smith",
        emails=["alice@example.edu"],
        email_domains=["example.edu"],
        affiliation_lines=["Example University"],
        urls=[],
        github_urls=[],
        observed_at="2026-09-01T00:00:00+00:00",
        errors=[],
    )
    resolved_authors = [
        ResolvedAuthor(
            author_key="author-1",
            name="Alice Smith",
            paper_author_string="Alice Smith",
            affiliation=None,
            profiles={"semantic_scholar": None, "homepage": None, "lab_page": None, "github": None, "google_scholar": None, "dblp": None, "x": None, "linkedin": None},
            identity_confidence="unresolved",
            evidence=[],
            ambiguities=[],
        ).to_dict()
    ]
    founder_signals: list = []

    monkeypatch.setattr(cli, "fetch_candidate_paper", lambda _: candidate)
    monkeypatch.setattr(cli, "extract_paper_text_evidence", lambda _candidate, contact_parser=None: paper_text_evidence)
    monkeypatch.setattr(cli, "resolve_authors", lambda _candidate, _paper_text: resolved_authors)
    monkeypatch.setattr(cli, "extract_founder_signals", lambda _candidate, _paper_text: founder_signals)
    artifacts_dir = tmp_path / "artifacts"
    output_path = tmp_path / "founder_brief.md"
    people_dir = tmp_path / "people"

    exit_code = cli.main([
        "founder-brief", "2608.28447v1",
        "--artifacts-dir", str(artifacts_dir),
        "--output", str(output_path),
        "--people-dir", str(people_dir),
        "--no-sync-people",
    ])

    assert exit_code == 0
    assert not people_dir.exists()
