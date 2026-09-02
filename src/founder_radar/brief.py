from __future__ import annotations

from founder_radar.models import CandidatePaper, FounderSignal, ResolvedAuthor


def _get(obj, key: str):
    return getattr(obj, key) if hasattr(obj, key) else obj[key]


def _outreach_angle(author) -> str:
    identity_confidence = _get(author, "identity_confidence")
    profiles = _get(author, "profiles")
    resolved_profiles = [key for key, value in profiles.items() if value]
    if identity_confidence == "unresolved":
        return "not recommended yet: identity is unresolved; find a corroborating public profile before any outreach"
    if resolved_profiles:
        return f"identity confidence is {identity_confidence} via {', '.join(resolved_profiles)}; review the evidence ledger before outreach"
    return f"identity confidence is {identity_confidence} but no public profile is resolved; verify manually before outreach"


def _recommendation(candidate: CandidatePaper, signals: list[FounderSignal]) -> tuple[str, str, str]:
    signal_types = {_get(signal, "signal_type") for signal in signals}
    if not signal_types:
        return ("skip", "low", "The pipeline found no founder-relevant evidence from the current artifacts.")
    if "code_repo_present" in signal_types and len(signal_types) >= 2:
        return ("manual diligence needed", "medium", "Builder-like evidence exists, but identity and commercialization still need review.")
    if len(signal_types) >= 2:
        return ("watch", "medium", "Multiple founder-relevant signal families are present, but outreach evidence is still incomplete.")
    return ("watch", "low", "There is some paper-native signal, but evidence is still thin for outreach.")


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
        paper_evidence = author.get("paper_author_evidence", {}) if isinstance(author, dict) else getattr(author, "paper_author_evidence", {})
        profile_parts = [f"{key}={value or 'not found'}" for key, value in profiles.items()]
        evidence_claims = [_get(item, "claim") for item in evidence]
        paper_evidence_parts: list[str] = []
        if paper_evidence:
            emails = paper_evidence.get("emails") or []
            domains = paper_evidence.get("email_domains") or []
            affiliations = paper_evidence.get("affiliation_lines") or []
            confidence = paper_evidence.get("paper_evidence_confidence") or "none"
            scope = paper_evidence.get("affiliation_scope") or "none"
            if emails:
                paper_evidence_parts.append(f"emails={', '.join(emails)}")
            if domains:
                paper_evidence_parts.append(f"domains={', '.join(domains)}")
            if affiliations:
                paper_evidence_parts.append(f"affiliations={'; '.join(affiliations)} ({scope})")
            paper_evidence_parts.append(f"paper_evidence_confidence={confidence}")
        paper_evidence_line = "; ".join(paper_evidence_parts) if paper_evidence_parts else "not found"
        block_lines = [
            f"### {name}",
            f"- Identity confidence: {identity_confidence}",
            f"- Paper-native evidence: {paper_evidence_line}",
            f"- Affiliation: {affiliation}",
            f"- Profiles: {', '.join(profile_parts)}",
            f"- Founder-relevant evidence: {'; '.join(evidence_claims)}",
            f"- Suggested outreach angle: {_outreach_angle(author)}",
        ]
        for signal in signals:
            signal_type = _get(signal, "signal_type")
            evidence_note = _get(signal, "evidence_note")
            if signal_type == "notable_coauthor_name_match" and f"'{name}'" in evidence_note:
                evidence_url = _get(signal, "evidence_url")
                block_lines.append(f"- Notable network signal: {evidence_note} — {evidence_url}")
        author_blocks.append("\n".join(block_lines))
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
