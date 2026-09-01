import json
from pathlib import Path

from founder_radar.contact_parser import apply_contact_parser, parse_llm_contact_json
from founder_radar.models import PaperTextEvidence


def make_evidence() -> PaperTextEvidence:
    return PaperTextEvidence(
        paper_id="arxiv:2608.31170v1",
        pdf_url="https://arxiv.org/pdf/2608.31170v1",
        download_status="success",
        text_extraction_status="success",
        text_chars=100,
        contact_block="Context-Aware Interleaved Batching for WhisperX\nCarlos Bain*, Max Bain†\nUniversity of Oxford†\nInput Audio (long-form)",
        emails=["carlos.o.bain@gmail.com"],
        email_domains=["gmail.com"],
        affiliation_lines=["University of Oxford†"],
        urls=[],
        github_urls=[],
        observed_at="2026-09-01T00:00:00+00:00",
        errors=[],
    )


def test_parse_llm_contact_json_strips_code_fences() -> None:
    raw = """```json
{"authors": ["Carlos Bain", "Max Bain"], "affiliation_lines": ["University of Oxford†"], "email_addresses": ["carlos.o.bain@gmail.com"], "shared_affiliation_for_all_authors": null, "notes": "ok"}
```"""
    parsed = parse_llm_contact_json(raw)
    assert parsed["authors"] == ["Carlos Bain", "Max Bain"]
    assert parsed["email_addresses"] == ["carlos.o.bain@gmail.com"]


def test_apply_contact_parser_updates_evidence_from_llm_result() -> None:
    evidence = make_evidence()
    llm_result = {
        "authors": ["Carlos Bain", "Max Bain"],
        "affiliation_lines": ["University of Oxford†"],
        "email_addresses": ["carlos.o.bain@gmail.com"],
        "shared_affiliation_for_all_authors": "University of Oxford†",
        "notes": "Removed figure text.",
    }
    updated = apply_contact_parser(evidence, llm_result)

    assert updated.affiliation_lines == ["University of Oxford†"]
    assert updated.emails == ["carlos.o.bain@gmail.com"]
    assert any("LLM contact parser note: Removed figure text." == err for err in updated.errors)
