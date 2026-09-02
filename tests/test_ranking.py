from founder_radar.ranking import rank_paper
from founder_radar.models import FounderSignal


def test_rank_paper_source_now_for_builder_plus_another_family() -> None:
    signals = [
        FounderSignal(author_key=None, paper_id="p1", signal_type="code_repo_present", value=True, confidence="medium", evidence_url="https://github.com/x", evidence_note="Code"),
        FounderSignal(author_key=None, paper_id="p1", signal_type="infra_or_tooling_orientation", value=True, confidence="medium", evidence_url="https://arxiv.org/abs/x", evidence_note="Systems"),
    ]
    result = rank_paper(signals, identity_confidences=["unresolved"])
    assert result["priority_tier"] == "source_now"


def test_rank_paper_watch_for_multiple_non_builder_families() -> None:
    signals = [
        FounderSignal(author_key=None, paper_id="p1", signal_type="infra_or_tooling_orientation", value=True, confidence="medium", evidence_url="u1", evidence_note="Systems"),
        FounderSignal(author_key=None, paper_id="p1", signal_type="benchmark_or_dataset_created", value=True, confidence="low", evidence_url="u2", evidence_note="Benchmark"),
    ]
    result = rank_paper(signals, identity_confidences=["unresolved"])
    assert result["priority_tier"] == "watch"


def test_rank_paper_needs_evidence_for_single_weak_family() -> None:
    signals = [
        FounderSignal(author_key=None, paper_id="p1", signal_type="benchmark_or_dataset_created", value=True, confidence="low", evidence_url="u1", evidence_note="Benchmark"),
    ]
    result = rank_paper(signals, identity_confidences=["unresolved"])
    assert result["priority_tier"] == "needs_evidence"


def test_rank_paper_skip_for_no_signals() -> None:
    result = rank_paper([], identity_confidences=["unresolved"])
    assert result["priority_tier"] == "skip"
