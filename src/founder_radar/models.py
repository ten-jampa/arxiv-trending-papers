from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class EvidenceLink:
    url: str
    label: str
    source: str
    confidence: str
    notes: str | None = None


@dataclass(slots=True)
class SourceHit:
    source: str
    source_url: str
    observed_at: str
    raw_location: str | None
    confidence: str


@dataclass(slots=True)
class EvidenceClaim:
    claim: str
    source_url: str
    observed_at: str
    confidence: str
    notes: str | None = None


@dataclass(slots=True)
class CandidatePaper:
    paper_id: str
    arxiv_id: str
    source: str
    url: str
    pdf_url: str | None
    title: str
    abstract: str
    authors: list[str]
    published_at: str
    updated_at: str
    primary_category: str | None
    categories: list[str]
    comment: str | None
    journal_ref: str | None
    doi: str | None
    links: list[EvidenceLink]
    source_hits: list[SourceHit]
    candidate_reason: list[str]
    fetched_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class PaperTextEvidence:
    paper_id: str
    pdf_url: str | None
    download_status: str
    text_extraction_status: str
    text_chars: int
    contact_block: str | None
    emails: list[str]
    email_domains: list[str]
    affiliation_lines: list[str]
    urls: list[EvidenceLink]
    github_urls: list[EvidenceLink]
    observed_at: str
    errors: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ResolvedAuthor:
    author_key: str
    name: str
    paper_author_string: str
    affiliation: str | None
    profiles: dict[str, str | None]
    identity_confidence: str
    evidence: list[EvidenceClaim]
    ambiguities: list[str]
    paper_author_evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class FounderSignal:
    author_key: str | None
    paper_id: str
    signal_type: str
    value: str | int | float | bool
    confidence: str
    evidence_url: str
    evidence_note: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
