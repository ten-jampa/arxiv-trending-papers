from __future__ import annotations

import re
import subprocess
import tempfile
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

from founder_radar.models import CandidatePaper, EvidenceLink, PaperTextEvidence

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
BRACE_EMAIL_RE = re.compile(r"\{([^{}]+)\}@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")
STANDALONE_EMAIL_LINE_RE = re.compile(
    r"^\s*(?:[A-Za-z0-9._%+-]+|\{[^{}]+\})@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\s*[.,;]?\s*$"
)
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
AFFILIATION_PATTERNS = tuple(
    re.compile(r"(?<![\w@.])" + re.escape(hint) + r"(?![\w])", re.IGNORECASE)
    for hint in AFFILIATION_HINTS
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
        if not line or STANDALONE_EMAIL_LINE_RE.match(line):
            continue
        if any(pattern.search(line) for pattern in AFFILIATION_PATTERNS):
            matches.append(line)
    return _dedupe_keep_order([line for line in matches if line])


OWNERSHIP_CUE_HINTS = (
    "code is available",
    "code available",
    "official implementation",
    "we release",
    "released at",
    "our code",
    "our implementation",
    "publicly available at",
    "open-source implementation",
    "open source implementation",
    "we open-source",
    "we open source",
    "code:",
    "github:",
    "project page:",
    "correspondence",
    "corresponding author",
)


def _ownership_hint_note(text: str, url_start: int, url_end: int, window_floor: int = 0) -> str | None:
    window_start = max(window_floor, url_start - 220)
    before = text[window_start:url_start]
    after = text[url_end:url_end + 60]
    before_lower = before.lower()
    for cue in OWNERSHIP_CUE_HINTS:
        if cue in before_lower:
            return f"Nearby text suggests this is the paper's own repository (cue: \"{cue}\")"
    # Common academic convention: the paper's own repo link is placed immediately
    # next to the corresponding-author contact email (before or after the URL),
    # not buried mid-paragraph like a related-work citation. Check both plain and
    # brace-grouped ({a,b,c}@domain) email shapes.
    nearby_email_window = before[-220:] + after
    if EMAIL_RE.search(nearby_email_window) or BRACE_EMAIL_RE.search(nearby_email_window):
        return "Nearby text includes a contact email, suggesting this is the paper's own repository"
    return None


def _expand_brace_emails(text: str) -> list[str]:
    expanded: list[str] = []
    for local_parts, domain in BRACE_EMAIL_RE.findall(text):
        for local in local_parts.split(","):
            local = local.strip()
            if local:
                expanded.append(f"{local}@{domain}")
    return expanded


def parse_pdf_text_evidence(paper_id: str, pdf_url: str, text: str, observed_at: str | None = None) -> PaperTextEvidence:
    observed = observed_at or datetime.now(UTC).isoformat()
    contact_block = _extract_contact_block(text)
    plain_emails = EMAIL_RE.findall(text)
    brace_emails = _expand_brace_emails(text)
    emails = _dedupe_keep_order(sorted(set(plain_emails) | set(brace_emails)))
    email_domains = sorted({email.split('@', 1)[1].lower() for email in emails})
    urls: list[EvidenceLink] = []
    github_urls: list[EvidenceLink] = []
    previous_url_end = 0
    for match in URL_RE.finditer(text):
        raw_url = match.group(0)
        cleaned = _clean_url(raw_url)
        is_github = 'github.com' in cleaned
        notes = _ownership_hint_note(text, match.start(), match.end(), previous_url_end) if is_github else None
        link = EvidenceLink(
            url=cleaned,
            label='code' if is_github else 'project',
            source='pdf_text',
            confidence='medium',
            notes=notes,
        )
        if is_github:
            github_urls.append(link)
        else:
            urls.append(link)
        previous_url_end = match.end()
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


def extract_paper_text_evidence(candidate: CandidatePaper, contact_parser=None) -> PaperTextEvidence:
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
        evidence = parse_pdf_text_evidence(candidate.paper_id, candidate.pdf_url, text, observed_at=observed_at)
        if contact_parser is not None:
            evidence = contact_parser(evidence)
        return evidence
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
