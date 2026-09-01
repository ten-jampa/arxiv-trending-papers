from __future__ import annotations

from founder_radar.models import CandidatePaper


def render_stub_brief(candidate: CandidatePaper) -> str:
    authors = ", ".join(candidate.authors) if candidate.authors else "not found"
    categories = ", ".join(candidate.categories) if candidate.categories else "not found"
    return f"""# Founder-Sourcing Brief: {candidate.title}

## Status
- This is the thin first slice.
- Only arXiv metadata fetch and `candidate_paper.json` are implemented.
- Author resolution, founder signals, and final sourcing judgment are not implemented yet.

## Paper
- arXiv: {candidate.url}
- PDF: {candidate.pdf_url or 'not found'}
- Authors: {authors}
- Published: {candidate.published_at}
- Categories: {categories}

## Abstract
{candidate.abstract}
"""
