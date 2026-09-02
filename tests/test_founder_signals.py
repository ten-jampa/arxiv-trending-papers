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
        abstract="We apply reinforcement learning to improve tool use and verification for mathematical reasoning.",
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

    # No nearby ownership language was captured for this GitHub URL, so it should be
    # treated as an unverified reference rather than an overclaimed builder signal.
    assert ("related_code_reference", "https://github.com/example/repo") in signal_types_urls
    assert ("code_repo_present", "https://github.com/example/repo") not in signal_types_urls
    assert ("project_page_present", "https://doi.org/10.5281/zenodo.22210928") not in signal_types_urls
    assert ("project_page_present", "https://openrouter.ai/docs/api/a") not in signal_types_urls


def test_extract_founder_signals_adds_benchmark_or_dataset_signal_from_strong_metadata_cues() -> None:
    candidate = CandidatePaper(
        paper_id="arxiv:2608.31139v1",
        arxiv_id="2608.31139v1",
        source="arxiv",
        url="https://arxiv.org/abs/2608.31139v1",
        pdf_url="https://arxiv.org/pdf/2608.31139v1",
        title="Configurable Semantic Chunking for Biomedical Information Extraction in Retrieval-Augmented Generation",
        abstract="We evaluate the framework on biomedical relation extraction benchmarks and show consistent gains. The dataset setting remains unchanged.",
        authors=["Alice Smith"],
        published_at="2026-08-31T00:00:00Z",
        updated_at="2026-08-31T00:00:00Z",
        primary_category="cs.CL",
        categories=["cs.CL"],
        comment=None,
        journal_ref=None,
        doi=None,
        links=[EvidenceLink(url="https://arxiv.org/abs/2608.31139v1", label="paper", source="arxiv_link", confidence="high")],
        source_hits=[SourceHit(source="arxiv", source_url="https://arxiv.org/abs/2608.31139v1", observed_at="2026-09-01T00:00:00+00:00", raw_location=None, confidence="high")],
        candidate_reason=["user-supplied arXiv paper"],
        fetched_at="2026-09-01T00:00:00+00:00",
    )
    paper_text = PaperTextEvidence(
        paper_id=candidate.paper_id,
        pdf_url=candidate.pdf_url,
        download_status="success",
        text_extraction_status="success",
        text_chars=100,
        contact_block="Alice Smith",
        emails=[],
        email_domains=[],
        affiliation_lines=[],
        urls=[],
        github_urls=[],
        observed_at="2026-09-01T00:00:00+00:00",
        errors=[],
    )

    signals = extract_founder_signals(candidate, paper_text)
    signal_types = [s["signal_type"] for s in signals]

    assert "benchmark_or_dataset_created" in signal_types


def test_infra_or_tooling_signal_ignores_generic_ml_words_but_catches_specific_ops_language() -> None:
    generic_candidate = CandidatePaper(
        paper_id="arxiv:generic1",
        arxiv_id="generic1",
        source="arxiv",
        url="https://arxiv.org/abs/generic1",
        pdf_url="https://arxiv.org/pdf/generic1",
        title="A Multi-Agent System For Language-Grounded Control",
        abstract="We deploy a system that bridges model-based control and learned policies.",
        authors=["Alice Smith"],
        published_at="2026-08-31T00:00:00Z",
        updated_at="2026-08-31T00:00:00Z",
        primary_category="cs.RO",
        categories=["cs.RO"],
        comment=None,
        journal_ref=None,
        doi=None,
        links=[EvidenceLink(url="https://arxiv.org/abs/generic1", label="paper", source="arxiv_link", confidence="high")],
        source_hits=[SourceHit(source="arxiv", source_url="https://arxiv.org/abs/generic1", observed_at="2026-09-01T00:00:00+00:00", raw_location=None, confidence="high")],
        candidate_reason=["user-supplied arXiv paper"],
        fetched_at="2026-09-01T00:00:00+00:00",
    )
    specific_candidate = CandidatePaper(
        paper_id="arxiv:specific1",
        arxiv_id="specific1",
        source="arxiv",
        url="https://arxiv.org/abs/specific1",
        pdf_url="https://arxiv.org/pdf/specific1",
        title="Context-Aware Interleaved Batching for Real-Time Transcription",
        abstract="Our on-premise verification pipeline improves throughput and reliability.",
        authors=["Bob Jones"],
        published_at="2026-08-31T00:00:00Z",
        updated_at="2026-08-31T00:00:00Z",
        primary_category="cs.CL",
        categories=["cs.CL"],
        comment=None,
        journal_ref=None,
        doi=None,
        links=[EvidenceLink(url="https://arxiv.org/abs/specific1", label="paper", source="arxiv_link", confidence="high")],
        source_hits=[SourceHit(source="arxiv", source_url="https://arxiv.org/abs/specific1", observed_at="2026-09-01T00:00:00+00:00", raw_location=None, confidence="high")],
        candidate_reason=["user-supplied arXiv paper"],
        fetched_at="2026-09-01T00:00:00+00:00",
    )
    paper_text = PaperTextEvidence(
        paper_id="arxiv:x",
        pdf_url="https://arxiv.org/pdf/x",
        download_status="success",
        text_extraction_status="success",
        text_chars=100,
        contact_block=None,
        emails=[],
        email_domains=[],
        affiliation_lines=[],
        urls=[],
        github_urls=[],
        observed_at="2026-09-01T00:00:00+00:00",
        errors=[],
    )

    generic_signals = extract_founder_signals(generic_candidate, paper_text)
    specific_signals = extract_founder_signals(specific_candidate, paper_text)

    assert "infra_or_tooling_orientation" not in [s["signal_type"] for s in generic_signals]
    assert "infra_or_tooling_orientation" in [s["signal_type"] for s in specific_signals]


def test_extract_founder_signals_flags_notable_coauthor_name_match(tmp_path) -> None:
    import json

    watchlist = [
        {
            "name": "Jure Leskovec",
            "note": "Stanford CS professor; co-founder of Kumo AI",
            "evidence_url": "https://cs.stanford.edu/people/jure/bio.html",
            "corroborating_url": "https://en.wikipedia.org/wiki/Jure_Leskovec",
            "verified_at": "2026-09-02",
        }
    ]
    watchlist_path = tmp_path / "notable_people.json"
    watchlist_path.write_text(json.dumps(watchlist))

    candidate = CandidatePaper(
        paper_id="arxiv:2606.12688",
        arxiv_id="2606.12688",
        source="arxiv",
        url="https://arxiv.org/abs/2606.12688",
        pdf_url="https://arxiv.org/pdf/2606.12688",
        title="M*: A Modular, Extensible, Serving System for Multimodal Models",
        abstract="We present a universal serving system for composite AI models.",
        authors=["Atindra Jha", "Jure Leskovec", "Luke Zettlemoyer"],
        published_at="2026-06-10T21:22:22Z",
        updated_at="2026-06-10T21:22:22Z",
        primary_category="cs.LG",
        categories=["cs.LG", "cs.AI"],
        comment=None,
        journal_ref=None,
        doi=None,
        links=[EvidenceLink(url="https://arxiv.org/abs/2606.12688", label="paper", source="arxiv_link", confidence="high")],
        source_hits=[SourceHit(source="arxiv", source_url="https://arxiv.org/abs/2606.12688", observed_at="2026-09-02T00:00:00+00:00", raw_location=None, confidence="high")],
        candidate_reason=["user-supplied arXiv paper"],
        fetched_at="2026-09-02T00:00:00+00:00",
    )
    paper_text = PaperTextEvidence(
        paper_id=candidate.paper_id,
        pdf_url=candidate.pdf_url,
        download_status="success",
        text_extraction_status="success",
        text_chars=100,
        contact_block=None,
        emails=[],
        email_domains=[],
        affiliation_lines=[],
        urls=[],
        github_urls=[],
        observed_at="2026-09-02T00:00:00+00:00",
        errors=[],
    )

    signals = extract_founder_signals(candidate, paper_text, notable_people_path=watchlist_path)
    matches = [s for s in signals if s["signal_type"] == "notable_coauthor_name_match"]

    assert len(matches) == 1
    assert matches[0]["confidence"] == "low"
    assert matches[0]["evidence_url"] == "https://cs.stanford.edu/people/jure/bio.html"
    assert "name match only" in matches[0]["evidence_note"].lower() or "name only" in matches[0]["evidence_note"].lower()
    assert "Jure Leskovec" in matches[0]["evidence_note"]


def test_extract_founder_signals_no_notable_coauthor_signal_when_no_match(tmp_path) -> None:
    import json

    watchlist = [
        {
            "name": "Jure Leskovec",
            "note": "Stanford CS professor; co-founder of Kumo AI",
            "evidence_url": "https://cs.stanford.edu/people/jure/bio.html",
            "corroborating_url": "https://en.wikipedia.org/wiki/Jure_Leskovec",
            "verified_at": "2026-09-02",
        }
    ]
    watchlist_path = tmp_path / "notable_people.json"
    watchlist_path.write_text(json.dumps(watchlist))

    candidate = CandidatePaper(
        paper_id="arxiv:1234.5678",
        arxiv_id="1234.5678",
        source="arxiv",
        url="https://arxiv.org/abs/1234.5678",
        pdf_url="https://arxiv.org/pdf/1234.5678",
        title="Unrelated Paper",
        abstract="An unrelated abstract.",
        authors=["Alice Smith", "Bob Jones"],
        published_at="2026-06-10T21:22:22Z",
        updated_at="2026-06-10T21:22:22Z",
        primary_category="cs.LG",
        categories=["cs.LG"],
        comment=None,
        journal_ref=None,
        doi=None,
        links=[EvidenceLink(url="https://arxiv.org/abs/1234.5678", label="paper", source="arxiv_link", confidence="high")],
        source_hits=[SourceHit(source="arxiv", source_url="https://arxiv.org/abs/1234.5678", observed_at="2026-09-02T00:00:00+00:00", raw_location=None, confidence="high")],
        candidate_reason=["user-supplied arXiv paper"],
        fetched_at="2026-09-02T00:00:00+00:00",
    )
    paper_text = PaperTextEvidence(
        paper_id=candidate.paper_id,
        pdf_url=candidate.pdf_url,
        download_status="success",
        text_extraction_status="success",
        text_chars=100,
        contact_block=None,
        emails=[],
        email_domains=[],
        affiliation_lines=[],
        urls=[],
        github_urls=[],
        observed_at="2026-09-02T00:00:00+00:00",
        errors=[],
    )

    signals = extract_founder_signals(candidate, paper_text, notable_people_path=watchlist_path)
    matches = [s for s in signals if s["signal_type"] == "notable_coauthor_name_match"]

    assert matches == []


def test_extract_founder_signals_does_not_drop_distinct_notable_coauthor_matches_sharing_a_url(tmp_path) -> None:
    import json

    watchlist = [
        {
            "name": "Frank Hutter",
            "note": "Founder and co-CEO of Prior Labs",
            "evidence_url": "https://priorlabs.ai/about",
            "corroborating_url": "https://example.com/a",
            "verified_at": "2026-09-02",
        },
        {
            "name": "Noah Hollmann",
            "note": "Co-founder and CTO of Prior Labs",
            "evidence_url": "https://priorlabs.ai/about",
            "corroborating_url": "https://example.com/b",
            "verified_at": "2026-09-02",
        },
    ]
    watchlist_path = tmp_path / "notable_people.json"
    watchlist_path.write_text(json.dumps(watchlist))

    candidate = CandidatePaper(
        paper_id="arxiv:2207.01848",
        arxiv_id="2207.01848",
        source="arxiv",
        url="https://arxiv.org/abs/2207.01848",
        pdf_url="https://arxiv.org/pdf/2207.01848",
        title="TabPFN",
        abstract="A transformer for tabular classification.",
        authors=["Noah Hollmann", "Samuel Mueller", "Katharina Eggensperger", "Frank Hutter"],
        published_at="2022-07-05T00:00:00Z",
        updated_at="2022-07-05T00:00:00Z",
        primary_category="cs.LG",
        categories=["cs.LG"],
        comment=None,
        journal_ref=None,
        doi=None,
        links=[EvidenceLink(url="https://arxiv.org/abs/2207.01848", label="paper", source="arxiv_link", confidence="high")],
        source_hits=[SourceHit(source="arxiv", source_url="https://arxiv.org/abs/2207.01848", observed_at="2026-09-02T00:00:00+00:00", raw_location=None, confidence="high")],
        candidate_reason=["user-supplied arXiv paper"],
        fetched_at="2026-09-02T00:00:00+00:00",
    )
    paper_text = PaperTextEvidence(
        paper_id=candidate.paper_id,
        pdf_url=candidate.pdf_url,
        download_status="success",
        text_extraction_status="success",
        text_chars=100,
        contact_block=None,
        emails=[],
        email_domains=[],
        affiliation_lines=[],
        urls=[],
        github_urls=[],
        observed_at="2026-09-02T00:00:00+00:00",
        errors=[],
    )

    signals = extract_founder_signals(candidate, paper_text, notable_people_path=watchlist_path)
    matches = [s for s in signals if s["signal_type"] == "notable_coauthor_name_match"]

    matched_names = {m["evidence_note"].split("'")[1] for m in matches}
    assert len(matches) == 2
    assert matched_names == {"Noah Hollmann", "Frank Hutter"}


def test_extract_founder_signals_downgrades_third_party_github_urls_without_ownership_cue() -> None:
    candidate = make_candidate()
    paper_text = PaperTextEvidence(
        paper_id=candidate.paper_id,
        pdf_url=candidate.pdf_url,
        download_status="success",
        text_extraction_status="success",
        text_chars=100,
        contact_block="Alice Smith",
        emails=[],
        email_domains=[],
        affiliation_lines=[],
        urls=[],
        github_urls=[
            EvidenceLink(url="https://github.com/example/own-repo", label="code", source="pdf_text", confidence="medium", notes="Nearby text suggests this is the paper's own repository (cue: \"code is available\")"),
            EvidenceLink(url="https://github.com/other-org/cited-tool", label="code", source="pdf_text", confidence="medium", notes=None),
        ],
        observed_at="2026-09-01T00:00:00+00:00",
        errors=[],
    )

    signals = extract_founder_signals(candidate, paper_text)
    by_url = {s["evidence_url"]: s for s in signals if s["evidence_url"].startswith("https://github.com")}

    assert by_url["https://github.com/example/own-repo"]["signal_type"] == "code_repo_present"
    assert by_url["https://github.com/other-org/cited-tool"]["signal_type"] == "related_code_reference"
    assert by_url["https://github.com/other-org/cited-tool"]["confidence"] == "low"


def test_extract_founder_signals_does_not_duplicate_confirmed_repo_as_unconfirmed_reference() -> None:
    candidate = make_candidate()
    candidate.links = [
        EvidenceLink(url="https://arxiv.org/abs/2608.28447v1", label="paper", source="arxiv_link", confidence="high"),
        EvidenceLink(url="https://github.com/example/tool-rl", label="code", source="abstract", confidence="high"),
    ]
    paper_text = PaperTextEvidence(
        paper_id=candidate.paper_id,
        pdf_url=candidate.pdf_url,
        download_status="success",
        text_extraction_status="success",
        text_chars=100,
        contact_block="Alice Smith",
        emails=[],
        email_domains=[],
        affiliation_lines=[],
        urls=[],
        github_urls=[EvidenceLink(url="https://github.com/example/tool-rl", label="code", source="pdf_text", confidence="medium", notes=None)],
        observed_at="2026-09-01T00:00:00+00:00",
        errors=[],
    )

    signals = extract_founder_signals(candidate, paper_text)
    matching = [s for s in signals if s["evidence_url"] == "https://github.com/example/tool-rl"]

    assert len(matching) == 1
    assert matching[0]["signal_type"] == "code_repo_present"
