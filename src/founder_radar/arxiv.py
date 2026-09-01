from __future__ import annotations

import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import UTC, datetime

from founder_radar.models import CandidatePaper, EvidenceLink, SourceHit

ARXIV_API_URL = "https://export.arxiv.org/api/query?search_query=id:{arxiv_id}&start=0&max_results=1"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
ARXIV_ID_RE = re.compile(r"^(?P<base>\d{4}\.\d{4,5})(?P<version>v\d+)?$")
URL_RE = re.compile(r"https?://\S+")


class ArxivNotFoundError(RuntimeError):
    pass


def parse_arxiv_id(value: str) -> str:
    raw = value.strip()
    if raw.startswith("http://") or raw.startswith("https://"):
        parsed = urllib.parse.urlparse(raw)
        path = parsed.path.rstrip("/")
        parts = [part for part in path.split("/") if part]
        if len(parts) >= 2 and parts[-2] in {"abs", "pdf"}:
            candidate = parts[-1]
            if candidate.endswith(".pdf"):
                candidate = candidate[:-4]
            raw = candidate
    match = ARXIV_ID_RE.fullmatch(raw)
    if not match:
        raise ValueError(f"Invalid arXiv ID or URL: {value}")
    return raw


def canonical_paper_id(arxiv_id: str) -> str:
    if "v" in arxiv_id:
        return f"arxiv:{arxiv_id}"
    return f"arxiv:{arxiv_id}"


def build_query_url(arxiv_id: str) -> str:
    return ARXIV_API_URL.format(arxiv_id=arxiv_id)


def fetch_arxiv_entry(arxiv_id: str, timeout: int = 30) -> ET.Element:
    url = build_query_url(arxiv_id)
    with urllib.request.urlopen(url, timeout=timeout) as response:
        xml_bytes = response.read()
    root = ET.fromstring(xml_bytes)
    entry = root.find("atom:entry", ATOM_NS)
    if entry is None:
        raise ArxivNotFoundError(f"arXiv paper not found: {arxiv_id}")
    return entry


def _text(entry: ET.Element, path: str) -> str | None:
    node = entry.find(path, ATOM_NS)
    if node is None or node.text is None:
        return None
    text = " ".join(node.text.split())
    return text or None


def _extract_links(entry: ET.Element, comment: str | None, abstract: str) -> list[EvidenceLink]:
    links: list[EvidenceLink] = []
    seen: set[tuple[str, str]] = set()

    for link in entry.findall("atom:link", ATOM_NS):
        href = link.attrib.get("href")
        title = link.attrib.get("title")
        rel = link.attrib.get("rel")
        if not href:
            continue
        if title == "pdf":
            item = EvidenceLink(url=href, label="pdf", source="arxiv_link", confidence="high", notes=None)
        elif rel == "alternate":
            item = EvidenceLink(url=href, label="paper", source="arxiv_link", confidence="high", notes=None)
        else:
            continue
        key = (item.url, item.source)
        if key not in seen:
            links.append(item)
            seen.add(key)

    for source_text, source_name in ((comment, "arxiv_comment"), (abstract, "abstract")):
        if not source_text:
            continue
        for url in URL_RE.findall(source_text):
            cleaned = url.rstrip(').,;')
            label = "project" if "github.com" not in cleaned else "code"
            key = (cleaned, source_name)
            if key in seen:
                continue
            links.append(EvidenceLink(url=cleaned, label=label, source=source_name, confidence="medium", notes=None))
            seen.add(key)
    return links


def normalize_entry(entry: ET.Element, fetched_at: str | None = None) -> CandidatePaper:
    entry_id = _text(entry, "atom:id")
    if not entry_id:
        raise ValueError("Missing arXiv entry id")
    arxiv_id = entry_id.rsplit("/", 1)[-1]
    title = _text(entry, "atom:title") or ""
    abstract = _text(entry, "atom:summary") or ""
    comment = _text(entry, "arxiv:comment")
    authors = [" ".join((author.findtext("atom:name", default="", namespaces=ATOM_NS)).split()) for author in entry.findall("atom:author", ATOM_NS)]
    categories = []
    for cat in entry.findall("atom:category", ATOM_NS):
        term = cat.attrib.get("term")
        if term and term not in categories:
            categories.append(term)
    primary = entry.find("arxiv:primary_category", ATOM_NS)
    primary_category = primary.attrib.get("term") if primary is not None else None
    links = _extract_links(entry, comment, abstract)
    paper_url = next((link.url for link in links if link.label == "paper"), entry_id.replace("http://", "https://"))
    pdf_url = next((link.url for link in links if link.label == "pdf"), None)
    observed_at = fetched_at or datetime.now(UTC).isoformat()
    return CandidatePaper(
        paper_id=canonical_paper_id(arxiv_id),
        arxiv_id=arxiv_id,
        source="arxiv",
        url=paper_url,
        pdf_url=pdf_url,
        title=title,
        abstract=abstract,
        authors=authors,
        published_at=_text(entry, "atom:published") or "",
        updated_at=_text(entry, "atom:updated") or "",
        primary_category=primary_category,
        categories=categories,
        comment=comment,
        journal_ref=_text(entry, "arxiv:journal_ref"),
        doi=_text(entry, "arxiv:doi"),
        links=links,
        source_hits=[SourceHit(source="arxiv", source_url=paper_url, observed_at=observed_at, raw_location=None, confidence="high")],
        candidate_reason=["user-supplied arXiv paper"],
        fetched_at=observed_at,
    )


def fetch_candidate_paper(arxiv_input: str, timeout: int = 30) -> CandidatePaper:
    arxiv_id = parse_arxiv_id(arxiv_input)
    entry = fetch_arxiv_entry(arxiv_id=arxiv_id, timeout=timeout)
    return normalize_entry(entry)
