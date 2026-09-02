from __future__ import annotations

from founder_radar.models import CandidatePaper, FounderSignal, PaperTextEvidence
from founder_radar.notable_people import find_notable_coauthor_matches, load_notable_people

RL_HINTS = ("reinforcement learning", "rlhf", "grpo", "dapo", "policy optimization", "tool use", "tool-integrated")
TOOLING_HINTS = ("infrastructure", "reliability", "batching", "latency", "on-premise", "real-time", "production-grade", "throughput", "verification")
BENCHMARK_HINTS = ("benchmark", "benchmarks", "dataset", "datasets", "corpus")


def _signal(signal_type: str, paper_id: str, value: str | int | float | bool, confidence: str, evidence_url: str, evidence_note: str) -> dict:
    return FounderSignal(
        author_key=None,
        paper_id=paper_id,
        signal_type=signal_type,
        value=value,
        confidence=confidence,
        evidence_url=evidence_url,
        evidence_note=evidence_note,
    ).to_dict()


def extract_founder_signals(candidate: CandidatePaper, paper_text: PaperTextEvidence, notable_people_path=None) -> list[dict]:
    signals: list[dict] = []
    combined_text = f"{candidate.title} {candidate.abstract}".lower()

    for link in candidate.links:
        if link.label == "project":
            signals.append(_signal("project_page_present", candidate.paper_id, True, link.confidence, link.url, f"Project link from {link.source}"))
        if link.label == "code":
            signals.append(_signal("code_repo_present", candidate.paper_id, True, link.confidence, link.url, f"Code link from {link.source}"))
    for link in paper_text.github_urls:
        signals.append(_signal("code_repo_present", candidate.paper_id, True, link.confidence, link.url, "GitHub URL from PDF text"))

    if any(hint in combined_text for hint in RL_HINTS):
        signals.append(_signal("agent_or_rl_systems_focus", candidate.paper_id, True, "medium", candidate.url, "Title or abstract mentions RL or tool-use systems"))
    if any(hint in combined_text for hint in TOOLING_HINTS):
        signals.append(_signal("infra_or_tooling_orientation", candidate.paper_id, True, "medium", candidate.url, "Title or abstract suggests tooling, workflow, or systems orientation"))
    if any(hint in combined_text for hint in BENCHMARK_HINTS):
        signals.append(_signal("benchmark_or_dataset_created", candidate.paper_id, True, "low", candidate.url, "Title or abstract mentions benchmark, dataset, or corpus language"))

    notable_entries = load_notable_people(notable_people_path) if notable_people_path is not None else load_notable_people()
    for match in find_notable_coauthor_matches(candidate.authors, notable_entries):
        entry = match["entry"]
        signals.append(
            _signal(
                "notable_coauthor_name_match",
                candidate.paper_id,
                True,
                "low",
                entry["evidence_url"],
                f"Author name '{match['author_name']}' is a name match only (not a verified identity resolution) against watchlist entry '{entry['name']}': {entry['note']}",
            )
        )

    deduped: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    for signal in signals:
        # Include evidence_note in the key: two distinct facts (e.g. two different
        # people both linked from the same "About" page) must not be collapsed into
        # one just because they happen to share an evidence_url.
        key = (signal["signal_type"], signal["evidence_url"], signal["evidence_note"])
        if key not in seen:
            deduped.append(signal)
            seen.add(key)
    return deduped
