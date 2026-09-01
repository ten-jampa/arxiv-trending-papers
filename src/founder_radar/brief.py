from __future__ import annotations

from founder_radar.models import CandidatePaper, FounderSignal, ResolvedAuthor


def _get(obj, key: str):
    return getattr(obj, key) if hasattr(obj, key) else obj[key]


def _recommendation(candidate: CandidatePaper, signals: list[FounderSignal]) -> tuple[str, str, str]:
    signal_types = {_get(signal, "signal_type") for signal in signals}
    if "code_repo_present" in signal_types and "infra_or_tooling_orientation" in signal_types:
        return ("manual diligence needed", "medium", "Builder-like evidence exists, but identity and commercialization still need review.")
    if signal_types:
        return ("watch", "low", "There is some paper-native signal, but evidence is still thin for outreach.")
    return ("manual diligence needed", "low", "The pipeline found limited founder-specific evidence so far.")


def render_founder_brief(candidate: CandidatePaper, authors: list[ResolvedAuthor], signals: list[FounderSignal]) -> str:
    recommendation, confidence, reason = _recommendation(candidate, signals)
    categories = ", ".join(candidate.categories) if candidate.categories else "not found"
    authors_line = ", ".join(candidate.authors) if candidate.authors else "not found"

    commercial_points: list[str] = []
    signal_types = {_get(signal, "signal_type") for signal in signals}
    if "infra_or_tooling_orientation" in signal_types:
        commercial_points.append("- The paper appears oriented toward tooling, systems, or workflow infrastructure.")
    if "agent_or_rl_systems_focus" in signal_types:
        commercial_points.append("- The work touches agent or reinforcement-learning style system behavior.")
    if "code_repo_present" in signal_types:
        commercial_points.append("- Code-linked work can be a builder signal, but ownership and quality still need review.")
    if not commercial_points:
        commercial_points.append("- Commercial wedge: not found from current code-native evidence.")

    author_blocks: list[str] = []
    ledger_lines: list[str] = []
    for author in authors:
        name = _get(author, "name")
        identity_confidence = _get(author, "identity_confidence")
        affiliation = _get(author, "affiliation") or "not found"
        profiles = _get(author, "profiles")
        evidence = _get(author, "evidence")
        profile_parts = [f"{key}={value or 'not found'}" for key, value in profiles.items()]
        evidence_claims = [_get(item, "claim") for item in evidence]
        author_blocks.append("\n".join([
            f"### {name}",
            f"- Identity confidence: {identity_confidence}",
            f"- Affiliation: {affiliation}",
            f"- Profiles: {', '.join(profile_parts)}",
            f"- Founder-relevant evidence: {'; '.join(evidence_claims)}",
            "- Suggested outreach angle: manual diligence needed",
        ]))
        for item in evidence:
            claim = _get(item, "claim")
            source_url = _get(item, "source_url")
            notes = _get(item, "notes")
            line = f"- {name}: {claim} — {source_url}"
            if notes:
                line += f" ({notes})"
            ledger_lines.append(line)

    signal_lines: list[str] = []
    for signal in signals:
        signal_type = _get(signal, "signal_type")
        evidence_note = _get(signal, "evidence_note")
        evidence_url = _get(signal, "evidence_url")
        signal_lines.append(f"- {signal_type}: {evidence_note} — {evidence_url}")
        ledger_lines.append(f"- Signal {signal_type}: {evidence_note} — {evidence_url}")

    unknowns = [
        "- Most public profiles remain unresolved unless stronger evidence is added.",
        "- No founder intent is inferred from prestige, paper quality, or affiliation alone.",
    ]
    if "code_repo_present" not in signal_types:
        unknowns.append("- Code ownership: not found or not verified.")

    sections = [
        f"# Founder-Sourcing Brief: {candidate.title}",
        "",
        "## Verdict",
        f"- Recommendation: {recommendation}",
        f"- Confidence: {confidence}",
        f"- One-line reason: {reason}",
        "",
        "## Paper",
        f"- arXiv: {candidate.url}",
        f"- PDF: {candidate.pdf_url or 'not found'}",
        f"- Authors: {authors_line}",
        f"- Published: {candidate.published_at}",
        f"- Categories: {categories}",
        f"- Core idea: {candidate.abstract}",
        "",
        "## Why This Could Matter Commercially",
        *commercial_points,
        "",
        "## Authors To Watch",
        ("\n\n".join(author_blocks) if author_blocks else "- not found"),
        "",
        "## Founder-Signal Evidence",
        *(signal_lines or ["- not found"]),
        "",
        "## Unknowns / Do Not Overclaim",
        *unknowns,
        "",
        "## Evidence Ledger",
        *(ledger_lines or ["- not found"]),
        "",
    ]
    return "\n".join(sections)


def render_stub_brief(candidate: CandidatePaper) -> str:
    authors = ", ".join(candidate.authors) if candidate.authors else "not found"
    categories = ", ".join(candidate.categories) if candidate.categories else "not found"
    return f"""# Founder-Sourcing Brief: {candidate.title}

## Status
- This is the thin first slice.
- Only arXiv metadata fetch and `candidate_paper.json` are implemented.
- Author resolution, founder signals, and final sourcing judgment are not implemented yet.

## Paper
- arXiv: {candidate.url}
- PDF: {candidate.pdf_url or 'not found'}
- Authors: {authors}
- Published: {candidate.published_at}
- Categories: {categories}

## Abstract
{candidate.abstract}
"""
