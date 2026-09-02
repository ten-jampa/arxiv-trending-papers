from __future__ import annotations

import json
from pathlib import Path

DEFAULT_WATCHLIST_PATH = Path(__file__).parent / "data" / "notable_people.json"


def load_notable_people(path: Path | None = None) -> list[dict]:
    """Load the curated notable-people watchlist.

    Every entry must be individually verified against a primary or credible
    secondary source before being added -- see
    `_docs/notable-people-watchlist.md` for the verification policy. This is
    not a scraped or inferred list.
    """
    watchlist_path = path if path is not None else DEFAULT_WATCHLIST_PATH
    return json.loads(watchlist_path.read_text())


def find_notable_coauthor_matches(authors: list[str], entries: list[dict]) -> list[dict]:
    """Find raw author strings that match a watchlist entry by name only.

    This is a name-only match, not an identity resolution. Per this repo's
    identity rules (see CONTEXT.md), a name match alone must never be
    treated as a confirmed identity; callers must surface this as a weak,
    low-confidence hint that a human should verify, not as a resolved
    profile.
    """
    matches: list[dict] = []
    by_lower_name = {entry["name"].strip().lower(): entry for entry in entries}
    for author in authors:
        key = author.strip().lower()
        entry = by_lower_name.get(key)
        if entry is not None:
            matches.append({"author_name": author, "entry": entry})
    return matches
