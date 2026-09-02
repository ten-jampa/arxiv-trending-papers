from __future__ import annotations

from founder_radar.models import CandidatePaper, FounderSignal, PaperTextEvidence, ResolvedAuthor

WITHDRAWN_ABSTRACT_MARKERS = ("this paper has been withdrawn", "paper has been withdrawn")

AUTHOR_SUMMARY_THRESHOLD = 10
MAX_PRINCIPAL_CONTACTS = 5
AUTHOR_DETAIL_FILENAME = "founder_brief_authors_detail.md"


def _get(obj, key: str):
    return getattr(obj, key) if hasattr(obj, key) else obj[key]


def _paper_evidence(author) -> dict:
    return author.get("paper_author_evidence", {}) if isinstance(author, dict) else getattr(author, "paper_author_evidence", {})


def _outreach_angle(author) -> str:
    identity_confidence = _get(author, "identity_confidence")
    profiles = _get(author, "profiles")
    resolved_profiles = [key for key, value in profiles.items() if value]
    if identity_confidence == "unresolved":
        return "not recommended yet: identity is unresolved; find a corroborating public profile before any outreach"
    if resolved_profiles:
        return f"identity confidence is {identity_confidence} via {', '.join(resolved_profiles)}; review the evidence ledger before outreach"
    return f"identity confidence is {identity_confidence} but no public profile is resolved; verify manually before outreach"


STRONG_SIGNAL_TYPES = {"code_repo_present", "notable_coauthor_name_match"}


def _recommendation(candidate: CandidatePaper, signals: list[FounderSignal]) -> tuple[str, str, str]:
    signal_types = {_get(signal, "signal_type") for signal in signals}
    if not signal_types:
        return ("skip", "low", "The pipeline found no founder-relevant evidence from the current artifacts.")
    if signal_types & STRONG_SIGNAL_TYPES and len(signal_types) >= 2:
        return ("manual diligence needed", "medium", "Builder-like or named-founder-adjacent evidence exists, but identity and commercialization still need review.")
    if len(signal_types) >= 2:
        return ("watch", "medium", "Multiple founder-relevant signal families are present, but outreach evidence is still incomplete.")
    return ("watch", "low", "There is some paper-native signal, but evidence is still thin for outreach.")


def _notable_match_names(signals: list[FounderSignal]) -> set[str]:
    names: set[str] = set()
    for signal in signals:
        if _get(signal, "signal_type") != "notable_coauthor_name_match":
            continue
        note = _get(signal, "evidence_note")
        parts = note.split("'")
        if len(parts) > 1:
            names.add(parts[1])
    return names


def _select_principal_contacts(authors: list[ResolvedAuthor], signals: list[FounderSignal], max_count: int = MAX_PRINCIPAL_CONTACTS) -> list:
    if not authors:
        return []
    notable_names = _notable_match_names(signals)
    selected: list = []
    selected_keys: set[str] = set()

    def _add(author) -> None:
        key = _get(author, "author_key") or _get(author, "name")
        if key in selected_keys or len(selected) >= max_count:
            return
        selected.append(author)
        selected_keys.add(key)

    _add(authors[0])
    if len(authors) > 1:
        _add(authors[-1])
    for author in authors:
        if _get(author, "name") in notable_names:
            _add(author)
    for author in authors:
        evidence = _paper_evidence(author)
        if evidence.get("emails"):
            _add(author)
    return selected[:max_count]


def _build_author_block(author, signals: list[FounderSignal]) -> str:
    name = _get(author, "name")
    identity_confidence = _get(author, "identity_confidence")
    affiliation = _get(author, "affiliation") or "not found"
    profiles = _get(author, "profiles")
    evidence = _get(author, "evidence")
    paper_evidence = _paper_evidence(author)
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
    return "\n".join(block_lines)


def _author_ledger_lines(author) -> list[str]:
    name = _get(author, "name")
    evidence = _get(author, "evidence")
    lines = []
    for item in evidence:
        claim = _get(item, "claim")
        source_url = _get(item, "source_url")
        notes = _get(item, "notes")
        line = f"- {name}: {claim} — {source_url}"
        if notes:
            line += f" ({notes})"
        lines.append(line)
    return lines


def render_author_detail_document(candidate: CandidatePaper, authors: list[ResolvedAuthor], signals: list[FounderSignal]) -> str:
    """Full per-author detail for every author, written as a companion artifact.

    Used when the author list is too large for the main brief to stay
    triage-useful (see AUTHOR_SUMMARY_THRESHOLD in render_founder_brief).
    """
    blocks = [_build_author_block(author, signals) for author in authors]
    sections = [
        f"# Full Author Detail: {candidate.title}",
        "",
        f"All {len(authors)} authors, in arXiv metadata order. The main founder_brief.md links here "
        "for readers who need the complete list beyond the principal-contacts summary.",
        "",
        "\n\n".join(blocks) if blocks else "- not found",
        "",
    ]
    return "\n".join(sections)


def _paper_status_notes(candidate: CandidatePaper, paper_text: PaperTextEvidence | None) -> list[str]:
    notes: list[str] = []
    abstract_lower = (candidate.abstract or "").lower()
    if any(marker in abstract_lower for marker in WITHDRAWN_ABSTRACT_MARKERS):
        notes.append(
            "- WITHDRAWN: arXiv metadata indicates this paper has been withdrawn by its author(s). "
            "Treat any extracted evidence with extreme caution and verify independently before any outreach."
        )
    if paper_text is not None:
        download_status = _get(paper_text, "download_status")
        text_extraction_status = _get(paper_text, "text_extraction_status")
        if download_status != "success" or text_extraction_status not in ("success", "not_checked"):
            errors = _get(paper_text, "errors") or []
            error_text = "; ".join(errors) if errors else "no error detail recorded"
            notes.append(
                f"- PDF evidence unavailable: download_status={download_status}, "
                f"text_extraction_status={text_extraction_status} ({error_text}). "
                "Author and signal evidence below is limited to arXiv metadata only."
            )
    return notes


def render_founder_brief(
    candidate: CandidatePaper,
    authors: list[ResolvedAuthor],
    signals: list[FounderSignal],
    paper_text: PaperTextEvidence | None = None,
) -> str:
    recommendation, confidence, reason = _recommendation(candidate, signals)
    categories = ", ".join(candidate.categories) if candidate.categories else "not found"
    authors_line = ", ".join(candidate.authors) if candidate.authors else "not found"
    paper_status_notes = _paper_status_notes(candidate, paper_text)

    commercial_points: list[str] = []
    signal_types = {_get(signal, "signal_type") for signal in signals}
    if "infra_or_tooling_orientation" in signal_types:
        commercial_points.append("- The paper appears oriented toward tooling, systems, or workflow infrastructure.")
    if "agent_or_rl_systems_focus" in signal_types:
        commercial_points.append("- The work touches agent or reinforcement-learning style system behavior.")
    if "code_repo_present" in signal_types:
        commercial_points.append("- Code-linked work can be a builder signal, but ownership and quality still need review.")
    if "related_code_reference" in signal_types and "code_repo_present" not in signal_types:
        commercial_points.append("- GitHub links were found in the paper text, but none show ownership evidence; treat them as cited third-party tools, not a builder signal.")
    if not commercial_points:
        commercial_points.append("- Commercial wedge: not found from current code-native evidence.")

    is_large_author_list = len(authors) > AUTHOR_SUMMARY_THRESHOLD

    author_section_header = "## Authors To Watch"
    author_section_intro: list[str] = []
    ledger_lines: list[str] = []

    if is_large_author_list:
        principal_contacts = _select_principal_contacts(authors, signals)
        author_section_header = f"## Authors ({len(authors)} total)"
        shared_affiliations = list(dict.fromkeys(
            line for author in authors for line in (_paper_evidence(author).get("affiliation_lines") or [])
        ))
        author_section_intro = [
            f"This paper lists {len(authors)} authors. Showing {len(principal_contacts)} principal contacts "
            "below (first author, last author, any notable-watchlist match, and any author with a "
            "paper-native email match). Full per-author detail for all authors, including everyone not "
            f"shown here, is in `{AUTHOR_DETAIL_FILENAME}` and in `resolved_authors.json`.",
            "",
            f"- Paper-level affiliation evidence: {'; '.join(shared_affiliations) if shared_affiliations else 'not found'}",
            "",
            "### Principal Contacts",
            "",
        ]
        author_blocks = [_build_author_block(author, signals) for author in principal_contacts]
        for author in principal_contacts:
            ledger_lines.extend(_author_ledger_lines(author))
        if shared_affiliations:
            other_count = len(authors) - len(principal_contacts)
            if other_count > 0:
                ledger_lines.append(
                    f"- Shared paper-level affiliation evidence ({'; '.join(shared_affiliations)}) also applies to "
                    f"the remaining {other_count} authors not shown above; see {AUTHOR_DETAIL_FILENAME} for the full list."
                )
    else:
        author_blocks = [_build_author_block(author, signals) for author in authors]
        for author in authors:
            ledger_lines.extend(_author_ledger_lines(author))

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
        *paper_status_notes,
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
        author_section_header,
        *author_section_intro,
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
