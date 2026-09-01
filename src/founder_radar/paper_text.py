from __future__ import annotations

import re
import subprocess
import tempfile
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

from founder_radar.models import CandidatePaper, EvidenceLink, PaperTextEvidence

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
URL_RE = re.compile(r"https?://\S+")
AFFILIATION_HINTS = (
    "university",
    "institute",
    "lab",
    "laboratory",
    "school",
    "college",
    "department",
    "research",
    "google",
    "openai",
    "anthropic",
    "microsoft",
    "meta",
    "amazon",
    "nvidia",
)
STOP_CONTACT_BLOCK = ("abstract", "introduction")
SECTION_START_RE = re.compile(r"^\d+[.:]?\s+introduction\b", re.IGNORECASE)



def _dedupe_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)
    return result


def _clean_url(url: str) -> str:
    return url.rstrip(').,;')


def _extract_contact_block(text: str) -> str | None:
    lines = [line.strip() for line in text.splitlines()]
    kept: list[str] = []
    for line in lines:
        if not line and not kept:
            continue
        lower = line.lower()
        if lower in STOP_CONTACT_BLOCK or lower.startswith("abstract") or SECTION_START_RE.match(line):
            break
        kept.append(line)
        if len(kept) >= 12:
            break
    block = "\n".join(line for line in kept if line).strip()
    return block or None


def _extract_affiliation_lines(block: str | None) -> list[str]:
    if not block:
        return []
    lines = [" ".join(line.split()) for line in block.splitlines()]
    matches = []
    for line in lines:
        lower = line.lower()
        if any(hint in lower for hint in AFFILIATION_HINTS):
            matches.append(line)
    return _dedupe_keep_order([line for line in matches if line])


def parse_pdf_text_evidence(paper_id: str, pdf_url: str, text: str, observed_at: str | None = None) -> PaperTextEvidence:
    observed = observed_at or datetime.now(UTC).isoformat()
    contact_block = _extract_contact_block(text)
    emails = _dedupe_keep_order(sorted(set(EMAIL_RE.findall(text))))
    email_domains = sorted({email.split('@', 1)[1].lower() for email in emails})
    urls: list[EvidenceLink] = []
    github_urls: list[EvidenceLink] = []
    for raw_url in URL_RE.findall(text):
        cleaned = _clean_url(raw_url)
        link = EvidenceLink(
            url=cleaned,
            label='code' if 'github.com' in cleaned else 'project',
            source='pdf_text',
            confidence='medium',
            notes=None,
        )
        if 'github.com' in cleaned:
            github_urls.append(link)
        else:
            urls.append(link)
    return PaperTextEvidence(
        paper_id=paper_id,
        pdf_url=pdf_url,
        download_status='success',
        text_extraction_status='success',
        text_chars=len(text),
        contact_block=contact_block,
        emails=emails,
        email_domains=email_domains,
        affiliation_lines=_extract_affiliation_lines(contact_block),
        urls=urls,
        github_urls=github_urls,
        observed_at=observed,
        errors=[],
    )


def _download_pdf_bytes(pdf_url: str, timeout: int = 30) -> bytes:
    with urllib.request.urlopen(pdf_url, timeout=timeout) as response:
        return response.read()


def _extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = Path(tmpdir) / 'paper.pdf'
        pdf_path.write_bytes(pdf_bytes)
        result = subprocess.run(
            ['pdftotext', str(pdf_path), '-'],
            check=True,
            capture_output=True,
            text=True,
        )
    return result.stdout


def extract_paper_text_evidence(candidate: CandidatePaper) -> PaperTextEvidence:
    observed_at = datetime.now(UTC).isoformat()
    if not candidate.pdf_url:
        return PaperTextEvidence(
            paper_id=candidate.paper_id,
            pdf_url=None,
            download_status='not_checked',
            text_extraction_status='not_checked',
            text_chars=0,
            contact_block=None,
            emails=[],
            email_domains=[],
            affiliation_lines=[],
            urls=[],
            github_urls=[],
            observed_at=observed_at,
            errors=['PDF URL not found in candidate paper artifact'],
        )
    try:
        pdf_bytes = _download_pdf_bytes(candidate.pdf_url)
    except Exception as exc:
        return PaperTextEvidence(
            paper_id=candidate.paper_id,
            pdf_url=candidate.pdf_url,
            download_status='failed',
            text_extraction_status='not_checked',
            text_chars=0,
            contact_block=None,
            emails=[],
            email_domains=[],
            affiliation_lines=[],
            urls=[],
            github_urls=[],
            observed_at=observed_at,
            errors=[f'PDF download failed: {exc}'],
        )
    try:
        text = _extract_text_from_pdf_bytes(pdf_bytes)
        return parse_pdf_text_evidence(candidate.paper_id, candidate.pdf_url, text, observed_at=observed_at)
    except Exception as exc:
        return PaperTextEvidence(
            paper_id=candidate.paper_id,
            pdf_url=candidate.pdf_url,
            download_status='success',
            text_extraction_status='failed',
            text_chars=0,
            contact_block=None,
            emails=[],
            email_domains=[],
            affiliation_lines=[],
            urls=[],
            github_urls=[],
            observed_at=observed_at,
            errors=[f'PDF text extraction failed: {exc}'],
        )
