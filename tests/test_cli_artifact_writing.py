import json
from pathlib import Path

from founder_radar import cli
from founder_radar.models import CandidatePaper, EvidenceLink, PaperTextEvidence, SourceHit


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

    monkeypatch.setattr(cli, "fetch_candidate_paper", lambda _: candidate)
    monkeypatch.setattr(cli, "extract_paper_text_evidence", lambda _candidate: paper_text_evidence)
    artifacts_dir = tmp_path / "artifacts"
    output_path = tmp_path / "founder_brief.md"

    exit_code = cli.main(["founder-brief", "2608.28447v1", "--artifacts-dir", str(artifacts_dir), "--output", str(output_path)])

    assert exit_code == 0
    candidate_path = artifacts_dir / "candidate_paper.json"
    assert candidate_path.exists()
    paper_text_path = artifacts_dir / "paper_text_evidence.json"
    assert output_path.exists()
    assert paper_text_path.exists()
    data = json.loads(candidate_path.read_text())
    paper_text_data = json.loads(paper_text_path.read_text())
    assert data["title"] == "Example Paper"
    assert paper_text_data["emails"] == ["alice@example.edu"]
    assert "Only arXiv metadata fetch" in output_path.read_text()
