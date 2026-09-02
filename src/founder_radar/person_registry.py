from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

PEOPLE_FILENAME = "people.json"
OBSERVATIONS_FILENAME = "author_observations.jsonl"
CLUSTERS_FILENAME = "identity_clusters.json"
REVIEW_FEEDBACK_FILENAME = "review_feedback.jsonl"


def _normalize_name(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().lower())


def _slug(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")
    return slug or "unknown"


def _short_hash(*parts: str) -> str:
    digest = hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()
    return digest[:8]


def _new_person_id(name: str, paper_id: str) -> str:
    return f"person_{_slug(name)}_{_short_hash(_normalize_name(name), paper_id)}"


def _new_observation_id(paper_id: str, raw_author_name: str) -> str:
    return f"obs_{_short_hash(paper_id, raw_author_name)}"


def _new_cluster_id(person_ids: list[str]) -> str:
    return f"cluster_{_short_hash(*sorted(person_ids))}"


@dataclass(slots=True)
class PersonRegistryStore:
    """JSON-backed person registry per _docs/specs/person-registry-v0.md."""

    people_dir: Path
    people: dict[str, dict] = field(default_factory=dict)
    observations: list[dict] = field(default_factory=list)
    clusters: list[dict] = field(default_factory=list)

    @classmethod
    def load(cls, people_dir: Path) -> "PersonRegistryStore":
        people_dir = Path(people_dir)
        people_path = people_dir / PEOPLE_FILENAME
        clusters_path = people_dir / CLUSTERS_FILENAME
        observations_path = people_dir / OBSERVATIONS_FILENAME

        people = json.loads(people_path.read_text()) if people_path.exists() else {}
        clusters = json.loads(clusters_path.read_text()) if clusters_path.exists() else []
        observations: list[dict] = []
        if observations_path.exists():
            for line in observations_path.read_text().splitlines():
                line = line.strip()
                if line:
                    observations.append(json.loads(line))
        return cls(people_dir=people_dir, people=people, observations=observations, clusters=clusters)

    def save(self) -> None:
        self.people_dir.mkdir(parents=True, exist_ok=True)
        (self.people_dir / PEOPLE_FILENAME).write_text(json.dumps(self.people, indent=2) + "\n")
        (self.people_dir / CLUSTERS_FILENAME).write_text(json.dumps(self.clusters, indent=2) + "\n")
        (self.people_dir / OBSERVATIONS_FILENAME).write_text(
            "".join(json.dumps(obs) + "\n" for obs in self.observations)
        )
        review_path = self.people_dir / REVIEW_FEEDBACK_FILENAME
        if not review_path.exists():
            review_path.write_text("")

    def _find_person_by_email(self, email: str) -> str | None:
        email = email.lower()
        for person_id, record in self.people.items():
            for entry in record.get("emails", []):
                if entry.get("value", "").lower() == email:
                    return person_id
        return None

    def _find_people_by_normalized_name(self, normalized_name: str) -> list[str]:
        return [
            person_id
            for person_id, record in self.people.items()
            if _normalize_name(record.get("display_name", "")) == normalized_name
        ]

    def _record_cluster(self, person_ids: list[str], reason: str) -> None:
        person_ids = sorted(set(person_ids))
        if len(person_ids) < 2:
            return
        cluster_id = _new_cluster_id(person_ids)
        if any(c["cluster_id"] == cluster_id for c in self.clusters):
            return
        self.clusters.append(
            {
                "cluster_id": cluster_id,
                "candidate_person_ids": person_ids,
                "reason": reason,
                "merge_status": "needs_review",
            }
        )

    def ingest_author(self, paper_id: str, paper_url: str, author: dict) -> dict:
        """Ingest one resolved_authors.json entry. Returns a summary of what happened."""

        raw_name = author.get("paper_author_string") or author.get("name", "")
        normalized_name = _normalize_name(raw_name)
        paper_evidence = author.get("paper_author_evidence", {}) or {}
        emails = list(dict.fromkeys(paper_evidence.get("emails", [])))
        domains = list(dict.fromkeys(paper_evidence.get("email_domains", [])))
        affiliation_lines = paper_evidence.get("affiliation_lines", [])
        affiliation = author.get("affiliation")

        linked_person_id: str | None = None
        link_reason = "new_person"

        for email in emails:
            existing = self._find_person_by_email(email)
            if existing is not None:
                linked_person_id = existing
                link_reason = "exact_email_match"
                break

        created = False
        if linked_person_id is None:
            name_matches = self._find_people_by_normalized_name(normalized_name)
            linked_person_id = _new_person_id(raw_name, paper_id)
            created = True
            if name_matches:
                self._record_cluster(
                    name_matches + [linked_person_id],
                    reason="same normalized name; not auto-merged without a hard identifier",
                )

        record = self.people.get(linked_person_id)
        if record is None:
            record = {
                "person_id": linked_person_id,
                "display_name": raw_name,
                "status": "watch",
                "identity_confidence": author.get("identity_confidence", "unresolved"),
                "current_best_affiliation": None,
                "emails": [],
                "domains": [],
                "profiles": dict(author.get("profiles", {})),
                "papers_seen": [],
                "strongest_founder_signals": [],
                "last_reviewed_at": None,
                "evidence": [],
            }
            self.people[linked_person_id] = record

        if affiliation and record["current_best_affiliation"] is None:
            record["current_best_affiliation"] = {
                "value": affiliation,
                "confidence": "paper_affiliation_block",
                "source": paper_id,
            }

        existing_email_values = {entry["value"].lower() for entry in record["emails"]}
        for email in emails:
            if email.lower() not in existing_email_values:
                record["emails"].append(
                    {
                        "value": email,
                        "source": "paper_contact_block",
                        "paper_id": paper_id,
                        "confidence": "high",
                    }
                )
                existing_email_values.add(email.lower())

        for domain in domains:
            if domain not in record["domains"]:
                record["domains"].append(domain)

        if paper_id not in record["papers_seen"]:
            record["papers_seen"].append(paper_id)

        observation = {
            "observation_id": _new_observation_id(paper_id, raw_name),
            "paper_id": paper_id,
            "raw_author_name": raw_name,
            "normalized_name": normalized_name,
            "paper_author_evidence": {
                "emails": emails,
                "affiliation_lines": affiliation_lines,
                "domains": domains,
                "affiliation_scope": paper_evidence.get("affiliation_scope"),
                "paper_evidence_confidence": paper_evidence.get("paper_evidence_confidence"),
            },
            "linked_person_id": linked_person_id,
            "link_reason": link_reason,
        }
        self.observations.append(observation)

        return {
            "person_id": linked_person_id,
            "created": created,
            "link_reason": link_reason,
        }


def ingest_resolved_authors(
    paper_id: str,
    paper_url: str,
    resolved_authors: list[dict],
    people_dir: Path,
) -> dict[str, Any]:
    """Load the JSON-backed person registry, ingest one paper's resolved authors, and save it.

    See _docs/specs/person-registry-v0.md for the schema and merge rules.
    """

    store = PersonRegistryStore.load(people_dir)
    results = [store.ingest_author(paper_id, paper_url, author) for author in resolved_authors]
    store.save()
    return {
        "paper_id": paper_id,
        "people_dir": str(people_dir),
        "results": results,
        "person_count": len(store.people),
        "cluster_count": len(store.clusters),
    }
