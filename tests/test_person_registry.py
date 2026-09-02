from __future__ import annotations

import json
from pathlib import Path

from founder_radar.person_registry import PersonRegistryStore, ingest_resolved_authors


def _author(name: str, emails=None, affiliation=None, affiliation_lines=None):
    return {
        "author_key": f"author-{name}",
        "name": name,
        "paper_author_string": name,
        "affiliation": affiliation,
        "profiles": {},
        "identity_confidence": "unresolved",
        "evidence": [],
        "ambiguities": [],
        "paper_author_evidence": {
            "raw_author_name": name,
            "emails": emails or [],
            "email_domains": [e.split("@", 1)[1] for e in (emails or [])],
            "affiliation_lines": affiliation_lines or [],
            "affiliation_scope": "per_author" if emails else "none",
            "ambiguous_emails": [],
            "paper_evidence_confidence": "high" if emails else "none",
            "source": "paper_contact_block",
            "source_url": "https://arxiv.org/pdf/1234.5678",
            "notes": [],
        },
    }


def test_new_person_created_for_first_observation(tmp_path: Path) -> None:
    people_dir = tmp_path / "people"
    author = _author("Jane Doe", emails=["jane@stanford.edu"], affiliation="Stanford University")

    summary = ingest_resolved_authors("arxiv:1234.5678", "https://arxiv.org/abs/1234.5678", [author], people_dir)

    assert summary["person_count"] == 1
    people = json.loads((people_dir / "people.json").read_text())
    assert len(people) == 1
    record = next(iter(people.values()))
    assert record["display_name"] == "Jane Doe"
    assert record["emails"][0]["value"] == "jane@stanford.edu"
    assert record["current_best_affiliation"]["value"] == "Stanford University"
    assert record["papers_seen"] == ["arxiv:1234.5678"]

    observations = [
        json.loads(line) for line in (people_dir / "author_observations.jsonl").read_text().splitlines()
    ]
    assert len(observations) == 1
    assert observations[0]["link_reason"] == "new_person"


def test_exact_email_match_links_to_existing_person_across_papers(tmp_path: Path) -> None:
    people_dir = tmp_path / "people"
    author_a = _author("J. Doe", emails=["jane@stanford.edu"])
    author_b = _author("Jane Doe", emails=["jane@stanford.edu"])

    ingest_resolved_authors("arxiv:1111.1111", "url1", [author_a], people_dir)
    summary_b = ingest_resolved_authors("arxiv:2222.2222", "url2", [author_b], people_dir)

    assert summary_b["person_count"] == 1
    people = json.loads((people_dir / "people.json").read_text())
    record = next(iter(people.values()))
    assert sorted(record["papers_seen"]) == ["arxiv:1111.1111", "arxiv:2222.2222"]

    observations = [
        json.loads(line) for line in (people_dir / "author_observations.jsonl").read_text().splitlines()
    ]
    assert observations[1]["link_reason"] == "exact_email_match"


def test_same_name_without_hard_identifier_creates_cluster_not_merge(tmp_path: Path) -> None:
    people_dir = tmp_path / "people"
    author_a = _author("Wei Zhang", emails=["wei.zhang@mit.edu"])
    author_b = _author("Wei Zhang", emails=["wzhang@berkeley.edu"])

    ingest_resolved_authors("arxiv:aaa", "url1", [author_a], people_dir)
    summary_b = ingest_resolved_authors("arxiv:bbb", "url2", [author_b], people_dir)

    assert summary_b["person_count"] == 2, "must not auto-merge on name alone"
    assert summary_b["cluster_count"] == 1
    clusters = json.loads((people_dir / "identity_clusters.json").read_text())
    assert len(clusters) == 1
    assert clusters[0]["merge_status"] == "needs_review"
    assert len(clusters[0]["candidate_person_ids"]) == 2


def test_store_load_roundtrip(tmp_path: Path) -> None:
    people_dir = tmp_path / "people"
    author = _author("Ada Lovelace", emails=["ada@example.edu"])
    ingest_resolved_authors("arxiv:xyz", "url", [author], people_dir)

    reloaded = PersonRegistryStore.load(people_dir)
    assert len(reloaded.people) == 1
    assert len(reloaded.observations) == 1
