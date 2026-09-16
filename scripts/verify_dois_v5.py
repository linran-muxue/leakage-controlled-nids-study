"""Verify reference DOIs against Crossref.

Python's own TLS stack is unavailable in this environment, so HTTP is performed through
curl. For every entry that carries a DOI the Crossref record is fetched and its title is
compared with the cited text; entries whose DOI is missing are looked up by title.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "English_SCI_Manuscript_v4.md"
OUT = ROOT / "results_review_v5"
STOP = {"a", "an", "the", "of", "for", "and", "in", "on", "to", "with", "using", "via"}


def curl_json(url: str) -> dict | None:
    try:
        raw = subprocess.run(["curl.exe", "-s", "-m", "30", "-H",
                              "User-Agent: nids-repro-check/1.0 (mailto:research@example.org)",
                              url],
                             capture_output=True, text=True, timeout=60).stdout
        return json.loads(raw)
    except Exception:
        return None


def tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP and len(w) > 2}


def main() -> None:
    text = MD.read_text(encoding="utf-8")
    block = text.split("## References")[-1]
    entries = re.findall(r"^(\d+)\.\s+(.*)$", block, flags=re.M)
    rows = []
    for number, entry in entries:
        doi_match = re.search(r"DOI:\s*(10\.\S+?)\.?$", entry.strip())
        pending = "[DOI to verify]" in entry
        doi = doi_match.group(1).rstrip(".") if doi_match else ""
        record = None
        if doi:
            record = curl_json(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}")
            time.sleep(0.3)
        if record is None:
            # fall back to a bibliographic query built from the entry head
            query = " ".join(re.findall(r"[A-Za-z][A-Za-z\-]+", entry)[:14])
            record = curl_json("https://api.crossref.org/works?rows=1&query.bibliographic=" +
                               urllib.parse.quote(query))
            time.sleep(0.3)
            if record and record.get("message", {}).get("items"):
                record = {"message": record["message"]["items"][0]}
        title = ""
        found_doi = doi
        if record and "message" in record:
            msg = record["message"]
            title = (msg.get("title") or [""])[0]
            found_doi = msg.get("DOI", doi)
        overlap = 0.0
        if title:
            t = tokens(title)
            overlap = len(t & tokens(entry)) / len(t) if t else 0.0
        rows.append({
            "ref": int(number),
            "cited_doi": doi,
            "doi_pending_flag": pending,
            "crossref_title": title[:110],
            "crossref_doi": found_doi,
            "title_overlap": round(overlap, 3),
            "status": ("ok" if overlap >= 0.6 else
                       "check" if title else "unresolved"),
        })
        print(f"[{number:>2}] overlap={overlap:.2f} {rows[-1]['status']:<10} {title[:70]}", flush=True)

    OUT.mkdir(exist_ok=True)
    (OUT / "doi_verification.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    ok = sum(1 for r in rows if r["status"] == "ok")
    check = [r["ref"] for r in rows if r["status"] == "check"]
    unresolved = [r["ref"] for r in rows if r["status"] == "unresolved"]
    print()
    print(f"verified ok: {ok}/{len(rows)}")
    print("needs manual check:", check or "none")
    print("unresolved:", unresolved or "none")


if __name__ == "__main__":
    main()
