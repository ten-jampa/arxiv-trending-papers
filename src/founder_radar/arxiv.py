from __future__ import annotations

import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import UTC, datetime

from founder_radar.models import CandidatePaper, EvidenceLink, SourceHit

ARXIV_ID_LIST_API_URL = "https://export.arxiv.org/api/query?id_list={arxiv_id}&start=0&max_results=1"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
# New-style IDs (2007+), e.g. 2608.28447 or 2608.28447v1.
ARXIV_ID_RE = re.compile(r"^(?P<base>\d{4}\.\d{4,5})(?P<version>v\d+)?$")
# Old-style IDs (pre-2007), e.g. math/0211159, hep-th/9711200v1, cs.AI/0601001.
OLD_STYLE_ARXIV_ID_RE = re.compile(r"^(?P<archive>[a-z-]+(?:\.[A-Z]{2})?)/(?P<num>\d{7})(?P<version>v\d+)?$")
URL_RE = re.compile(r"https?://\S+")

# arXiv Terms of Use (info.arxiv.org/help/api/tou.html) and the API user manual
# both specify: no more than one request every 3 seconds, single connection at
# a time. See _docs/arxiv-rate-limits.md for the full research writeup.
ARXIV_MIN_REQUEST_INTERVAL_SECONDS = 3.0
ARXIV_MAX_RETRIES = 5
ARXIV_REQUEST_TIMEOUT_SECONDS = 30
USER_AGENT = "founder-radar/0.1 (research tool; single-paper lookups; see repo README)"


class ArxivNotFoundError(RuntimeError):
    pass


class ArxivRateLimiter:
    """Enforces a minimum delay between requests, per arXiv's Terms of Use.

    A fresh instance starts with no memory of a prior request, so the first
    call to `wait()` never sleeps. Subsequent calls sleep just long enough to
    keep the gap between requests at or above `min_interval` seconds.
    """

    def __init__(self, min_interval: float = ARXIV_MIN_REQUEST_INTERVAL_SECONDS) -> None:
        self.min_interval = min_interval
        self._last_request_at: float | None = None

    def wait(self, clock_fn=time.monotonic, sleep_fn=time.sleep) -> float:
        now = clock_fn()
        slept = 0.0
        if self._last_request_at is not None:
            elapsed = now - self._last_request_at
            if elapsed < self.min_interval:
                slept = self.min_interval - elapsed
                sleep_fn(slept)
        self._last_request_at = now
        return slept


_RATE_LIMITER = ArxivRateLimiter()


def parse_arxiv_id(value: str) -> str:
    raw = value.strip()
    if raw.startswith("http://") or raw.startswith("https://"):
        parsed = urllib.parse.urlparse(raw)
        path = parsed.path.rstrip("/")
        parts = [part for part in path.split("/") if part]
        if len(parts) >= 2 and parts[0] in {"abs", "pdf"}:
            # New-style URL: /abs/2608.28447 (2 segments).
            # Old-style URL: /abs/math/0211159 (3 segments: archive + number).
            candidate = "/".join(parts[1:])
            if candidate.endswith(".pdf"):
                candidate = candidate[:-4]
            raw = candidate
    match = ARXIV_ID_RE.fullmatch(raw) or OLD_STYLE_ARXIV_ID_RE.fullmatch(raw)
    if not match:
        raise ValueError(f"Invalid arXiv ID or URL: {value}")
    return raw


def canonical_paper_id(arxiv_id: str) -> str:
    if "v" in arxiv_id:
        return f"arxiv:{arxiv_id}"
    return f"arxiv:{arxiv_id}"


def build_query_url(arxiv_id: str) -> str:
    # id_list= is used uniformly (rather than search_query=id:) because it is the
    # only one of the two arXiv API query mechanisms that reliably resolves
    # old-style archive/NNNNNNN IDs (e.g. math/0211159) in addition to new-style
    # IDs; verified against the live arXiv API for both ID shapes.
    return ARXIV_ID_LIST_API_URL.format(arxiv_id=urllib.parse.quote(arxiv_id, safe=""))


def _fetch_url_with_backoff(
    url: str,
    timeout: int = ARXIV_REQUEST_TIMEOUT_SECONDS,
    max_retries: int = ARXIV_MAX_RETRIES,
    base_delay: float = ARXIV_MIN_REQUEST_INTERVAL_SECONDS,
    opener=None,
    sleep_fn=time.sleep,
) -> bytes:
    """Fetch a URL, retrying with exponential backoff on 429 or transient errors.

    Non-429 HTTP errors (e.g. 404) are raised immediately without retrying,
    since a retry cannot fix a genuinely missing resource. A 429 or a
    connection-level failure (timeout, hang, DNS, etc.) is retried with
    backoff, honoring a Retry-After header if the server sends one.
    """
    open_fn = opener or urllib.request.urlopen
    last_exc: Exception | None = None
    for attempt in range(max_retries + 1):
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            response = open_fn(request, timeout=timeout)
            try:
                return response.read()
            finally:
                close = getattr(response, "close", None)
                if close is not None:
                    close()
        except urllib.error.HTTPError as exc:
            if exc.code != 429:
                raise
            last_exc = exc
            retry_after = exc.headers.get("Retry-After") if exc.headers else None
            delay = float(retry_after) if retry_after else min(60.0, base_delay * (2 ** attempt))
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_exc = exc
            delay = min(60.0, base_delay * (2 ** attempt))
        if attempt < max_retries:
            sleep_fn(delay)
    raise RuntimeError(f"arXiv request failed after {max_retries + 1} attempts: {last_exc}") from last_exc


def fetch_arxiv_entry(
    arxiv_id: str,
    timeout: int = ARXIV_REQUEST_TIMEOUT_SECONDS,
    rate_limiter: ArxivRateLimiter | None = None,
    opener=None,
    sleep_fn=time.sleep,
    max_retries: int = ARXIV_MAX_RETRIES,
    base_delay: float = ARXIV_MIN_REQUEST_INTERVAL_SECONDS,
) -> ET.Element:
    limiter = rate_limiter if rate_limiter is not None else _RATE_LIMITER
    limiter.wait(sleep_fn=sleep_fn)
    url = build_query_url(arxiv_id)
    xml_bytes = _fetch_url_with_backoff(
        url,
        timeout=timeout,
        max_retries=max_retries,
        base_delay=base_delay,
        opener=opener,
        sleep_fn=sleep_fn,
    )
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
    # entry_id looks like "http://arxiv.org/abs/2608.28447v1" (new-style) or
    # "http://arxiv.org/abs/math/0211159v1" (old-style, archive-prefixed). A
    # plain rsplit("/", 1) would drop the archive prefix on old-style IDs, so
    # extract everything after the "/abs/" segment instead.
    abs_marker = "/abs/"
    marker_index = entry_id.find(abs_marker)
    if marker_index != -1:
        arxiv_id = entry_id[marker_index + len(abs_marker):]
    else:
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


def fetch_candidate_paper(arxiv_input: str, timeout: int = ARXIV_REQUEST_TIMEOUT_SECONDS) -> CandidatePaper:
    arxiv_id = parse_arxiv_id(arxiv_input)
    entry = fetch_arxiv_entry(arxiv_id=arxiv_id, timeout=timeout)
    return normalize_entry(entry)
