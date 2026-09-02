from __future__ import annotations

import re

from founder_radar.models import CandidatePaper, EvidenceClaim, PaperTextEvidence, ResolvedAuthor

EMPTY_PROFILES = {
    "semantic_scholar": None,
    "homepage": None,
    "lab_page": None,
    "github": None,
    "google_scholar": None,
    "dblp": None,
    "x": None,
    "linkedin": None,
}


def _alnum(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _name_parts(name: str) -> tuple[str, str, str, str]:
    parts = [_alnum(part) for part in name.split() if _alnum(part)]
    first = parts[0] if parts else ""
    last = parts[-1] if len(parts) > 1 else ""
    compact = "".join(parts)
    initials = "".join(part[:1] for part in parts)
    return first, last, compact, initials


def _email_user(email: str) -> str:
    return _alnum(email.split("@", 1)[0])


def _email_domain(email: str) -> str:
    return email.split("@", 1)[1].lower() if "@" in email else ""


def _email_match_score(author_name: str, email: str) -> int:
    """Return a conservative heuristic score for mapping a paper email to an author.

    This is paper-native evidence only. It never resolves external identity.
    """

    user = _email_user(email)
    first, last, compact, initials = _name_parts(author_name)
    if not user or not first:
        return 0
    if compact and compact in user:
        return 100
    if first and last and first in user and last in user:
        return 95
    if first and last and first in user and user.endswith(last[:1]):
        return 90
    if first and last and last in user and user.startswith(first[:1]):
        return 85
    if initials and len(initials) > 1 and initials in user:
        return 70
    if last and last in user and len(last) >= 4:
        return 65
    if first and first in user and len(first) >= 4:
        return 55
    return 0


def _assign_emails(authors: list[str], emails: list[str]) -> tuple[dict[str, list[str]], list[str]]:
    assignments = {author: [] for author in authors}
    if len(authors) == 1 and len(emails) == 1:
        assignments[authors[0]].append(emails[0])
        return assignments, []

    ambiguous: list[str] = []
    claimed: set[str] = set()

    for email in emails:
        scored = sorted(
            ((author, _email_match_score(author, email)) for author in authors),
            key=lambda item: item[1],
            reverse=True,
        )
        if not scored or scored[0][1] < 80:
            ambiguous.append(email)
            continue
        if len(scored) > 1 and scored[1][1] >= scored[0][1] - 10:
            ambiguous.append(email)
            continue
        author = scored[0][0]
        if email in claimed:
            ambiguous.append(email)
            continue
        assignments[author].append(email)
        claimed.add(email)

    return assignments, ambiguous


def _paper_evidence_confidence(emails: list[str], affiliations: list[str], ambiguous_emails: list[str]) -> str:
    if emails and affiliations:
        return "high"
    if emails or affiliations:
        return "medium"
    if ambiguous_emails:
        return "ambiguous"
    return "none"


def _affiliation_scope(author_count: int, affiliation_count: int) -> str:
    if affiliation_count == 0:
        return "none"
    if author_count == 1:
        return "per_author"
    return "paper_level"


def resolve_authors(candidate: CandidatePaper, paper_text: PaperTextEvidence) -> list[dict]:
    authors: list[dict] = []
    email_assignments, ambiguous_emails = _assign_emails(candidate.authors, paper_text.emails)
    affiliation_lines = list(dict.fromkeys(paper_text.affiliation_lines))
    scope = _affiliation_scope(len(candidate.authors), len(affiliation_lines))

    for index, raw_author in enumerate(candidate.authors, start=1):
        matched_emails = email_assignments.get(raw_author, [])
        domains = list(dict.fromkeys(_email_domain(email) for email in matched_emails if _email_domain(email)))
        evidence = [
            EvidenceClaim(
                claim="Raw author preserved from arXiv metadata",
                source_url=candidate.url,
                observed_at=candidate.fetched_at,
                confidence="high",
                notes=None,
            )
        ]
        ambiguities: list[str] = []
        if ambiguous_emails:
            ambiguities.append(
                "Paper contact block contains email(s) that could not be safely mapped to a specific author: "
                + ", ".join(ambiguous_emails)
            )

        affiliation = None
        if affiliation_lines:
            affiliation = affiliation_lines[0] if len(affiliation_lines) == 1 else "; ".join(affiliation_lines)
            claim = "Paper-native affiliation from PDF contact block" if scope == "per_author" else "Paper-level affiliation block from PDF contact block"
            evidence.append(
                EvidenceClaim(
                    claim=claim,
                    source_url=candidate.pdf_url or candidate.url,
                    observed_at=paper_text.observed_at,
                    confidence="medium" if scope == "per_author" else "low",
                    notes=affiliation,
                )
            )
            if scope == "paper_level":
                ambiguities.append("Affiliation block was not explicitly mapped per author; stored as paper-level evidence.")

        for email in matched_emails:
            evidence.append(
                EvidenceClaim(
                    claim="Paper-native email matched to author from PDF contact block",
                    source_url=candidate.pdf_url or candidate.url,
                    observed_at=paper_text.observed_at,
                    confidence="medium",
                    notes=email,
                )
            )
        for domain in domains:
            evidence.append(
                EvidenceClaim(
                    claim="Paper-native email domain from PDF contact block",
                    source_url=candidate.pdf_url or candidate.url,
                    observed_at=paper_text.observed_at,
                    confidence="medium",
                    notes=domain,
                )
            )

        paper_author_evidence = {
            "raw_author_name": raw_author,
            "emails": matched_emails,
            "email_domains": domains,
            "affiliation_lines": affiliation_lines,
            "affiliation_scope": scope,
            "ambiguous_emails": ambiguous_emails,
            "paper_evidence_confidence": _paper_evidence_confidence(matched_emails, affiliation_lines, ambiguous_emails),
            "source": "paper_contact_block" if paper_text.contact_block else "paper_text_evidence",
            "source_url": candidate.pdf_url or candidate.url,
            "notes": [
                "Paper-native evidence only; external identity remains unresolved without corroborating public profile evidence."
            ],
        }

        author = ResolvedAuthor(
            author_key=f"author-{index}",
            name=raw_author,
            paper_author_string=raw_author,
            affiliation=affiliation,
            profiles=dict(EMPTY_PROFILES),
            identity_confidence="unresolved",
            evidence=evidence,
            ambiguities=ambiguities,
            paper_author_evidence=paper_author_evidence,
        )
        authors.append(author.to_dict())
    return authors
