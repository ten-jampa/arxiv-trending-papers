from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from founder_radar.arxiv import ArxivNotFoundError, fetch_candidate_paper, parse_arxiv_id
from founder_radar.author_resolution import resolve_authors
from founder_radar.brief import render_founder_brief
from founder_radar.contact_parser import apply_contact_parser, call_openai_contact_parser
from founder_radar.founder_signals import extract_founder_signals
from founder_radar.paper_text import extract_paper_text_evidence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="founder-radar")
    subparsers = parser.add_subparsers(dest="command", required=True)

    founder_brief = subparsers.add_parser("founder-brief", help="Generate a thin founder brief from one arXiv paper")
    founder_brief.add_argument("arxiv_id_or_url")
    founder_brief.add_argument("--output", type=Path, default=None, help="Write final Markdown brief to this path")
    founder_brief.add_argument("--artifacts-dir", type=Path, default=None, help="Directory for intermediate artifacts")
    founder_brief.add_argument("--llm-contact-parser", action="store_true", help="Use optional OpenAI contact-block cleanup after deterministic extraction")
    return parser


def _default_artifacts_dir(arxiv_id: str) -> Path:
    safe_id = arxiv_id.replace('/', '_')
    return Path("artifacts") / safe_id


def _maybe_llm_contact_parser(enabled: bool):
    if not enabled:
        return None
    def parser(evidence):
        result = call_openai_contact_parser(evidence)
        return apply_contact_parser(evidence, result)
    return parser


def cmd_founder_brief(args: argparse.Namespace) -> int:
    try:
        parsed_id = parse_arxiv_id(args.arxiv_id_or_url)
        candidate = fetch_candidate_paper(args.arxiv_id_or_url)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except ArxivNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"Unexpected arXiv fetch error: {exc}", file=sys.stderr)
        return 2

    artifacts_dir = args.artifacts_dir or _default_artifacts_dir(parsed_id)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    candidate_path = artifacts_dir / "candidate_paper.json"
    candidate_path.write_text(json.dumps(candidate.to_dict(), indent=2) + "\n")

    contact_parser = _maybe_llm_contact_parser(args.llm_contact_parser)
    paper_text_evidence = extract_paper_text_evidence(candidate, contact_parser=contact_parser)
    paper_text_path = artifacts_dir / "paper_text_evidence.json"
    paper_text_path.write_text(json.dumps(paper_text_evidence.to_dict(), indent=2) + "\n")

    resolved_authors = resolve_authors(candidate, paper_text_evidence)
    resolved_authors_path = artifacts_dir / "resolved_authors.json"
    resolved_authors_path.write_text(json.dumps(resolved_authors, indent=2) + "\n")

    founder_signals = extract_founder_signals(candidate, paper_text_evidence)
    founder_signals_path = artifacts_dir / "founder_signals.json"
    founder_signals_path.write_text(json.dumps(founder_signals, indent=2) + "\n")

    brief_text = render_founder_brief(candidate, resolved_authors, founder_signals)
    output_path = args.output or artifacts_dir / "founder_brief.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(brief_text)

    print(f"Wrote {candidate_path}")
    print(f"Wrote {paper_text_path}")
    print(f"Wrote {resolved_authors_path}")
    print(f"Wrote {founder_signals_path}")
    print(f"Wrote {output_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "founder-brief":
        return cmd_founder_brief(args)
    parser.error(f"Unknown command: {args.command}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
