from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import replace
from pathlib import Path

from founder_radar.models import PaperTextEvidence


PROMPT_TEMPLATE = """You extract structured contact-block data from academic paper first-page text.
Only use the provided text and provided extracted emails. Do not infer from outside knowledge.
Return strict JSON with keys:
- authors: list of strings exactly as supported by text
- affiliation_lines: list of affiliation lines only; exclude title, abstract, figure labels, body text, and section headers
- email_addresses: list of exact emails from the provided extracted emails that are supported by the text context
- shared_affiliation_for_all_authors: string or null
- notes: short string
Return JSON only.

CONTACT_BLOCK:
<<<
{contact_block}
>>>

EXTRACTED_EMAILS:
{emails}
"""


def parse_llm_contact_json(raw_text: str) -> dict:
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[len("```json"):].strip()
    if text.startswith("```"):
        text = text[3:].strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    return json.loads(text)


def apply_contact_parser(evidence: PaperTextEvidence, llm_result: dict) -> PaperTextEvidence:
    errors = list(evidence.errors)
    notes = llm_result.get("notes")
    if notes:
        errors.append(f"LLM contact parser note: {notes}")
    emails = llm_result.get("email_addresses") or evidence.emails
    affiliation_lines = llm_result.get("affiliation_lines") or evidence.affiliation_lines
    return replace(
        evidence,
        emails=emails,
        email_domains=sorted({email.split("@", 1)[1].lower() for email in emails}),
        affiliation_lines=affiliation_lines,
        errors=errors,
    )


def _load_openai_api_key(env_path: str) -> str | None:
    if os.environ.get("OPENAI_API_KEY"):
        return os.environ["OPENAI_API_KEY"]
    path = Path(env_path)
    if not path.exists():
        return None
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        if key.strip() == "OPENAI_API_KEY":
            cleaned = value.strip().strip("\"").strip("'")
            if cleaned:
                os.environ["OPENAI_API_KEY"] = cleaned
                return cleaned
    return None


def call_openai_contact_parser(evidence: PaperTextEvidence, env_path: str = ".env", model: str = "gpt-4.1-mini") -> dict:
    api_key = _load_openai_api_key(env_path)
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not found in environment or .env")
    emails_text = "\n".join(evidence.emails) if evidence.emails else "none"
    prompt = PROMPT_TEMPLATE.format(contact_block=evidence.contact_block or "", emails=emails_text)
    payload = {
        "model": model,
        "input": [
            {"role": "system", "content": [{"type": "input_text", "text": "You are a careful information extractor. Return JSON only."}]},
            {"role": "user", "content": [{"type": "input_text", "text": prompt}]},
        ],
        "temperature": 0,
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        resp = json.loads(response.read().decode("utf-8"))
    chunks: list[str] = []
    for item in resp.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in ("output_text", "text") and "text" in content:
                chunks.append(content["text"])
    return parse_llm_contact_json("".join(chunks).strip())
