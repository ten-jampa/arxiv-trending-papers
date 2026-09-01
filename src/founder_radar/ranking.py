from __future__ import annotations

from founder_radar.models import FounderSignal


def _get(obj, key: str):
    return getattr(obj, key) if hasattr(obj, key) else obj[key]


def rank_paper(signals: list[FounderSignal], identity_confidences: list[str]) -> dict:
    signal_types = {_get(signal, "signal_type") for signal in signals}
    reasons: list[str] = []
    direct_builder = "code_repo_present" in signal_types or "project_page_present" in signal_types
    multiple_families = len(signal_types) >= 2

    if not signal_types:
        return {
            "priority_bucket": "skip",
            "reasons": ["No founder-radar signals are present."],
        }

    if direct_builder and multiple_families:
        reasons.append("Direct builder evidence is present.")
        reasons.append("At least one additional founder-radar signal family is present.")
        return {
            "priority_bucket": "high",
            "reasons": reasons,
        }

    if direct_builder:
        reasons.append("Direct builder evidence is present.")
        return {
            "priority_bucket": "medium",
            "reasons": reasons,
        }

    if multiple_families:
        reasons.append("Multiple independent founder-radar signal families are present.")
        return {
            "priority_bucket": "medium",
            "reasons": reasons,
        }

    if signal_types:
        reasons.append("One weaker founder-radar signal family is present.")
        if any(level in {"low", "medium", "high"} for level in identity_confidences):
            reasons.append("Some author identity evidence is available.")
        return {
            "priority_bucket": "low",
            "reasons": reasons,
        }

    return {
        "priority_bucket": "skip",
        "reasons": ["No founder-radar signals are present."],
    }
