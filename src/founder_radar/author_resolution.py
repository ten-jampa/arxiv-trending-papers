from __future__ import annotations

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


def resolve_authors(candidate: CandidatePaper, paper_text: PaperTextEvidence) -> list[dict]:
    authors: list[dict] = []
    single_affiliation = paper_text.affiliation_lines[0] if len(candidate.authors) == 1 and len(paper_text.affiliation_lines) == 1 else None
    single_domain = paper_text.email_domains[0] if len(candidate.authors) == 1 and len(paper_text.email_domains) == 1 else None

    for index, raw_author in enumerate(candidate.authors, start=1):
        evidence = [
            EvidenceClaim(
                claim="Raw author preserved from arXiv metadata",
                source_url=candidate.url,
                observed_at=candidate.fetched_at,
                confidence="high",
                notes=None,
            )
        ]
        if single_affiliation is not None:
            evidence.append(
                EvidenceClaim(
                    claim="Paper-native affiliation from PDF contact block",
                    source_url=candidate.pdf_url or candidate.url,
                    observed_at=paper_text.observed_at,
                    confidence="medium",
                    notes=single_affiliation,
                )
            )
        if single_domain is not None:
            evidence.append(
                EvidenceClaim(
                    claim="Paper-native email domain from PDF contact block",
                    source_url=candidate.pdf_url or candidate.url,
                    observed_at=paper_text.observed_at,
                    confidence="medium",
                    notes=single_domain,
                )
            )

        author = ResolvedAuthor(
            author_key=f"author-{index}",
            name=raw_author,
            paper_author_string=raw_author,
            affiliation=single_affiliation,
            profiles=dict(EMPTY_PROFILES),
            identity_confidence="unresolved",
            evidence=evidence,
            ambiguities=[],
        )
        authors.append(author.to_dict())
    return authors
