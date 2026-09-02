from __future__ import annotations

from founder_radar.models import FounderSignal


def _get(obj, key: str):
    return getattr(obj, key) if hasattr(obj, key) else obj[key]


def rank_paper(signals: list[FounderSignal], identity_confidences: list[str]) -> dict:
    """Categorical sourcing-priority tier, per the decision recorded in issue #5.

    Tiers (decided, not fake-precise scores):
      - source_now: strong paper/person/company-shaped signal; worth active follow-up.
      - watch: relevant and plausibly useful, but not enough for outreach.
      - needs_evidence: promising topic but missing author/project/institution evidence.
      - skip: low sourcing value or too incremental/noisy.
    """

    signal_types = {_get(signal, "signal_type") for signal in signals}
    reasons: list[str] = []
    direct_builder = "code_repo_present" in signal_types or "project_page_present" in signal_types
    multiple_families = len(signal_types) >= 2

    if not signal_types:
        return {
            "priority_tier": "skip",
            "reasons": ["No founder-radar signals are present."],
        }

    if direct_builder and multiple_families:
        reasons.append("Direct builder evidence is present.")
        reasons.append("At least one additional founder-radar signal family is present.")
        return {
            "priority_tier": "source_now",
            "reasons": reasons,
        }

    if direct_builder:
        reasons.append("Direct builder evidence is present.")
        return {
            "priority_tier": "watch",
            "reasons": reasons,
        }

    if multiple_families:
        reasons.append("Multiple independent founder-radar signal families are present.")
        return {
            "priority_tier": "watch",
            "reasons": reasons,
        }

    reasons.append("One weaker founder-radar signal family is present.")
    if any(level in {"low", "medium", "high"} for level in identity_confidences):
        reasons.append("Some author identity evidence is available.")
    return {
        "priority_tier": "needs_evidence",
        "reasons": reasons,
    }
