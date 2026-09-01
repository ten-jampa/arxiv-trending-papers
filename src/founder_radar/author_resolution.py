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
    for index, raw_author in enumerate(candidate.authors, start=1):
        author = ResolvedAuthor(
            author_key=f"author-{index}",
            name=raw_author,
            paper_author_string=raw_author,
            affiliation=None,
            profiles=dict(EMPTY_PROFILES),
            identity_confidence="unresolved",
            evidence=[
                EvidenceClaim(
                    claim="Raw author preserved from arXiv metadata",
                    source_url=candidate.url,
                    observed_at=candidate.fetched_at,
                    confidence="high",
                    notes=None,
                )
            ],
            ambiguities=[],
        )
        authors.append(author.to_dict())
    return authors
