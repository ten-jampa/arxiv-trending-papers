import json
from pathlib import Path

from founder_radar.notable_people import find_notable_coauthor_matches, load_notable_people


def test_load_notable_people_returns_entries_with_required_fields(tmp_path: Path) -> None:
    data = [
        {
            "name": "Jure Leskovec",
            "note": "Stanford CS professor; co-founder of Kumo AI",
            "evidence_url": "https://cs.stanford.edu/people/jure/bio.html",
            "verified_at": "2026-09-02",
        }
    ]
    path = tmp_path / "notable_people.json"
    path.write_text(json.dumps(data))

    entries = load_notable_people(path)

    assert len(entries) == 1
    assert entries[0]["name"] == "Jure Leskovec"
    assert entries[0]["evidence_url"].startswith("https://")


def test_find_notable_coauthor_matches_finds_exact_name_case_insensitive(tmp_path: Path) -> None:
    data = [
        {
            "name": "Jure Leskovec",
            "note": "Stanford CS professor; co-founder of Kumo AI",
            "evidence_url": "https://cs.stanford.edu/people/jure/bio.html",
            "verified_at": "2026-09-02",
        }
    ]
    path = tmp_path / "notable_people.json"
    path.write_text(json.dumps(data))
    entries = load_notable_people(path)

    authors = ["Atindra Jha", "jure leskovec", "Luke Zettlemoyer"]
    matches = find_notable_coauthor_matches(authors, entries)

    assert len(matches) == 1
    assert matches[0]["author_name"] == "jure leskovec"
    assert matches[0]["entry"]["name"] == "Jure Leskovec"


def test_find_notable_coauthor_matches_returns_empty_when_no_match(tmp_path: Path) -> None:
    data = [
        {
            "name": "Jure Leskovec",
            "note": "Stanford CS professor; co-founder of Kumo AI",
            "evidence_url": "https://cs.stanford.edu/people/jure/bio.html",
            "verified_at": "2026-09-02",
        }
    ]
    path = tmp_path / "notable_people.json"
    path.write_text(json.dumps(data))
    entries = load_notable_people(path)

    authors = ["Alice Smith", "Bob Jones"]
    matches = find_notable_coauthor_matches(authors, entries)

    assert matches == []


def test_default_watchlist_file_loads_and_has_required_fields() -> None:
    entries = load_notable_people()
    assert len(entries) >= 1
    for entry in entries:
        assert entry["name"]
        assert entry["note"]
        assert entry["evidence_url"].startswith("https://")
        assert entry["verified_at"]
