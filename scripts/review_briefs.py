#!/usr/bin/env python3
"""Local-only review server for founder-radar briefs.

Serves a single HTML page listing generated founder briefs with Yes/No buttons.
Votes are written immediately to <batch_dir>/_votes.json. No external network
calls, no dependencies beyond the Python standard library.

Usage:
    python3 scripts/review_briefs.py [--batch-dir artifacts/review-batch-1] [--port 8765]
"""
from __future__ import annotations

import argparse
import html
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

LOCK = threading.Lock()


def load_summary(batch_dir: Path) -> list[dict]:
    return json.loads((batch_dir / "_summary.json").read_text())


def load_votes(batch_dir: Path) -> dict:
    votes_path = batch_dir / "_votes.json"
    if votes_path.exists():
        return json.loads(votes_path.read_text())
    return {}


def save_votes(batch_dir: Path, votes: dict) -> None:
    (batch_dir / "_votes.json").write_text(json.dumps(votes, indent=2))


VERDICT_COLORS = {
    "reach out": "#1f8a3f",
    "watch": "#2563eb",
    "manual diligence needed": "#b45309",
    "skip": "#6b7280",
}


CARD_TEMPLATE = """
<div class="card" data-id="{pid}">
  <div class="card-head">
    <span class="idx">#{idx}</span>
    <span class="verdict" style="background:{color}">{verdict}</span>
    <span class="conf">confidence: {confidence}</span>
  </div>
  <h3><a href="{url}" target="_blank" rel="noopener">{title}</a> <a class="pdf-link" href="{pdf_url}" target="_blank" rel="noopener">PDF</a></h3>
  <div class="meta">{pid} &middot; {categories} &middot; {n_authors} author(s)</div>
  <div class="signals">signals: {signals}</div>
  <div class="vote-row">
    <button class="vote-btn yes {yes_active}" onclick="vote('{pid}','yes')">Yes -- show me</button>
    <button class="vote-btn no {no_active}" onclick="vote('{pid}','no')">No</button>
    <button class="vote-btn clear {clear_active}" onclick="vote('{pid}','')">Clear</button>
    <button class="toggle-btn" onclick="toggleBrief('{pid}')">View full brief</button>
  </div>
  <pre class="brief" id="brief-{pid}" style="display:none">{brief_text}</pre>
</div>
"""


PAGE_TEMPLATE = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Founder-Radar Brief Review</title>
<style>
  body {{ font-family: -apple-system, Helvetica, Arial, sans-serif; background:#0b0f14; color:#e5e7eb; margin:0; padding:24px; }}
  h1 {{ font-size: 20px; margin-bottom: 4px; }}
  .sub {{ color:#9ca3af; margin-bottom: 20px; font-size: 13px; }}
  .card {{ background:#111827; border:1px solid #1f2937; border-radius:10px; padding:16px 18px; margin-bottom:14px; }}
  .card-head {{ display:flex; align-items:center; gap:10px; margin-bottom:6px; }}
  .idx {{ color:#6b7280; font-size:12px; }}
  .verdict {{ color:white; font-size:11px; padding:3px 8px; border-radius:6px; font-weight:600; text-transform:uppercase; letter-spacing:.03em; }}
  .conf {{ color:#9ca3af; font-size:12px; }}
  h3 {{ margin: 4px 0 6px; font-size: 15px; }}
  .meta {{ color:#9ca3af; font-size:12px; margin-bottom:4px; }}
  .signals {{ color:#a1a1aa; font-size:12px; margin-bottom:10px; }}
  .vote-row {{ display:flex; gap:8px; flex-wrap:wrap; align-items:center; }}
  .vote-btn {{ border:1px solid #374151; background:#1f2937; color:#e5e7eb; padding:6px 12px; border-radius:6px; cursor:pointer; font-size:13px; }}
  .vote-btn.yes.active {{ background:#166534; border-color:#22c55e; }}
  .vote-btn.no.active {{ background:#7f1d1d; border-color:#ef4444; }}
  .vote-btn.clear.active {{ background:#374151; }}
  .toggle-btn {{ border:1px solid #374151; background:transparent; color:#93c5fd; padding:6px 12px; border-radius:6px; cursor:pointer; font-size:13px; margin-left:auto; }}
  h3 a {{ color:#e5e7eb; text-decoration:none; border-bottom: 1px solid #374151; }}
  h3 a:hover {{ border-bottom-color:#93c5fd; color:#93c5fd; }}
  .pdf-link {{ font-size:11px; color:#6b7280; text-decoration:none; border:1px solid #374151; padding:2px 6px; border-radius:5px; vertical-align:middle; }}
  .pdf-link:hover {{ color:#93c5fd; border-color:#93c5fd; }}
  .brief {{ background:#0b0f14; border:1px solid #1f2937; border-radius:8px; padding:12px; margin-top:12px; white-space:pre-wrap; font-size:12.5px; line-height:1.5; max-height:480px; overflow:auto; }}
  #status {{ position: fixed; top: 12px; right: 20px; color:#22c55e; font-size:12px; opacity:0; transition: opacity .3s; }}
</style>
</head>
<body>
<div id="status">saved</div>
<h1>Founder-Radar Brief Review</h1>
<div class="sub">Yes = "I want to look at this one." No = skip. Not a quality rating either way. Votes save instantly to disk.</div>
{cards}
<script>
function toggleBrief(id) {{
  var el = document.getElementById("brief-" + id);
  el.style.display = (el.style.display === "none") ? "block" : "none";
}}
function vote(id, decision) {{
  fetch("/vote", {{
    method: "POST",
    headers: {{"Content-Type": "application/json"}},
    body: JSON.stringify({{id: id, decision: decision}})
  }}).then(function(r) {{ return r.json(); }}).then(function(data) {{
    var card = document.querySelector('[data-id="' + id + '"]');
    card.querySelectorAll(".vote-btn").forEach(function(b) {{ b.classList.remove("active"); }});
    if (decision) {{
      card.querySelector(".vote-btn." + decision).classList.add("active");
    }} else {{
      card.querySelector(".vote-btn.clear").classList.add("active");
    }}
    var s = document.getElementById("status");
    s.style.opacity = 1;
    setTimeout(function() {{ s.style.opacity = 0; }}, 600);
  }});
}}
</script>
</body>
</html>"""


def render_page(batch_dir: Path) -> str:
    rows = load_summary(batch_dir)
    votes = load_votes(batch_dir)
    cards = []
    for i, r in enumerate(rows, start=1):
        pid = r["id"]
        vote_value = votes.get(pid, {}).get("decision", "")
        color = VERDICT_COLORS.get(r["verdict"], "#374151")
        brief_path = Path(r["path"])
        brief_text = brief_path.read_text() if brief_path.exists() else "(brief not found)"
        cards.append(CARD_TEMPLATE.format(
            pid=html.escape(pid),
            idx=i,
            color=color,
            verdict=html.escape(r["verdict"]),
            confidence=html.escape(r["confidence"]),
            title=html.escape(r["title"]),
            url=html.escape(r.get("url", "#")),
            pdf_url=html.escape(r.get("pdf_url", "#")),
            categories=html.escape(", ".join(r["categories"])),
            n_authors=r["n_authors"],
            signals=html.escape(", ".join(r["signals"]) or "none"),
            yes_active="active" if vote_value == "yes" else "",
            no_active="active" if vote_value == "no" else "",
            clear_active="active" if vote_value == "" else "",
            brief_text=html.escape(brief_text),
        ))
    return PAGE_TEMPLATE.format(cards="".join(cards))


class Handler(BaseHTTPRequestHandler):
    batch_dir: Path = None  # set at startup

    def log_message(self, fmt, *args):
        pass  # keep console quiet

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            body = render_page(self.batch_dir).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif parsed.path == "/votes":
            with LOCK:
                body = json.dumps(load_votes(self.batch_dir)).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/vote":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            pid = data.get("id")
            decision = data.get("decision", "")
            with LOCK:
                votes = load_votes(self.batch_dir)
                if decision:
                    votes[pid] = {"decision": decision}
                elif pid in votes:
                    del votes[pid]
                save_votes(self.batch_dir, votes)
            body = json.dumps({"ok": True, "votes": votes}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-dir", default="artifacts/review-batch-1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    batch_dir = Path(args.batch_dir).resolve()
    if not (batch_dir / "_summary.json").exists():
        raise SystemExit(f"No _summary.json found in {batch_dir}")

    Handler.batch_dir = batch_dir
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Serving review UI for {batch_dir} at http://127.0.0.1:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
