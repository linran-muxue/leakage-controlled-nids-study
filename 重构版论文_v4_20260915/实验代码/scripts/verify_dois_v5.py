"""Verify reference DOIs against Crossref.

Python's own TLS stack is unavailable in this environment, so HTTP is performed through
curl. For every entry that carries a DOI the record is fetched from the registry that
serves it (Crossref, or DataCite for dataset DOIs) and its title is compared with the
cited text. Entries without a DOI are looked up by title, but a candidate is only kept
when its title really matches: the first version of this script recorded the first hit of
a loose bibliographic query, which filled the record with unrelated works.
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


def curl_json(url: str, attempts: int = 3) -> dict | None:
    # A burst of lookups occasionally comes back empty from the public API; a
    # single failed request must not be recorded as "this DOI does not exist".
    for attempt in range(attempts):
        try:
            raw = subprocess.run(["curl.exe", "-s", "-m", "30", "-H",
                                  "User-Agent: nids-repro-check/1.0 (mailto:research@example.org)",
                                  url],
                                 capture_output=True, text=True, timeout=60).stdout
            return json.loads(raw)
        except Exception:
            time.sleep(2.0 + 2.0 * attempt)
    return None


def tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP and len(w) > 2}


def title_overlap(title: str, entry: str) -> float:
    t = tokens(title)
    return len(t & tokens(entry)) / len(t) if t else 0.0


def main() -> None:
    text = MD.read_text(encoding="utf-8")
    block = text.split("## References")[-1]
    entries = re.findall(r"^(\d+)\.\s+(.*)$", block, flags=re.M)
    rows = []
    for number, entry in entries:
        doi_match = re.search(r"DOI:\s*(10\.\S+?)\.?$", entry.strip())
        pending = "[DOI to verify]" in entry
        doi = doi_match.group(1).rstrip(".") if doi_match else ""
        title = ""
        found_doi = ""
        matched_by = ""
        registry = ""
        if doi:
            record = curl_json(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}")
            time.sleep(0.8)
            if record and record.get("message", {}).get("title"):
                msg = record["message"]
                title = (msg.get("title") or [""])[0]
                found_doi = msg.get("DOI", doi)
                matched_by = "doi"
                registry = "crossref"
            else:
                # dataset DOIs such as the UCI repository ones live in DataCite
                record = curl_json(f"https://api.datacite.org/dois/{urllib.parse.quote(doi)}")
                time.sleep(0.8)
                attributes = (record or {}).get("data", {}).get("attributes") or {}
                data_title = (attributes.get("titles") or [{}])[0].get("title", "")
                if data_title:
                    title = data_title.replace("_", " ")
                    found_doi = attributes.get("doi", doi)
                    matched_by = "doi"
                    registry = "datacite"
        else:
            # The entry cites no DOI, so there is nothing to resolve. A
            # bibliographic query is deliberately not used: the first version of
            # this script recorded whatever it returned, which is how the record
            # ended up listing DOIs of unrelated works.
            pass
        overlap = title_overlap(title, entry) if title else 0.0
        if not title:
            status = "unresolved" if doi else "no-doi"
        elif overlap >= 0.6:
            status = "ok" if matched_by == "doi" else "title-match"
        else:
            status = "check"
        rows.append({
            "ref": int(number),
            "cited_doi": doi,
            "doi_pending_flag": pending,
            "crossref_title": title[:110],
            "crossref_doi": found_doi,
            "title_overlap": round(overlap, 3),
            "status": status,
            "matched_by": matched_by,
            "registry": registry,
        })
        print(f"[{number:>2}] overlap={overlap:.2f} {status:<12} {matched_by or '-':<6} {title[:60]}",
              flush=True)

    # A burst of lookups occasionally comes back empty from the public APIs.
    # One extra pass over the entries whose DOI did not resolve keeps a transient
    # outage from being written down as "this DOI does not exist".
    retry = [index for index, row in enumerate(rows) if row["status"] == "unresolved"]
    if retry:
        print(f"\nretrying {len(retry)} unresolved entries after a pause", flush=True)
        time.sleep(20)
        for index in retry:
            row, (_, entry) = rows[index], entries[index]
            record = curl_json(f"https://api.crossref.org/works/{urllib.parse.quote(row['cited_doi'])}")
            time.sleep(0.8)
            title = ""
            registry = ""
            found_doi = ""
            if record and record.get("message", {}).get("title"):
                title = (record["message"].get("title") or [""])[0]
                found_doi = record["message"].get("DOI", row["cited_doi"])
                registry = "crossref"
            else:
                record = curl_json(f"https://api.datacite.org/dois/{urllib.parse.quote(row['cited_doi'])}")
                time.sleep(0.8)
                attributes = (record or {}).get("data", {}).get("attributes") or {}
                data_title = (attributes.get("titles") or [{}])[0].get("title", "")
                if data_title:
                    title = data_title.replace("_", " ")
                    found_doi = attributes.get("doi", row["cited_doi"])
                    registry = "datacite"
            if title:
                overlap = title_overlap(title, entry)
                row.update(crossref_title=title[:110], crossref_doi=found_doi,
                           title_overlap=round(overlap, 3),
                           status="ok" if overlap >= 0.6 else "check",
                           matched_by="doi", registry=registry)
            print(f"[{row['ref']:>2}] retry -> {row['status']:<12} {row['crossref_title'][:60]}",
                  flush=True)

    OUT.mkdir(exist_ok=True)
    (OUT / "doi_verification.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print()
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    print(f"checked {len(rows)} entries: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    print("needs manual check:", [r["ref"] for r in rows if r["status"] == "check"] or "none")
    print("unresolved (not served by Crossref or DataCite):",
          [r["ref"] for r in rows if r["status"] == "unresolved"] or "none")
    print("no DOI in the entry:", [r["ref"] for r in rows if r["status"] == "no-doi"] or "none")
    print("no DOI in the entry, matching record found:",
          [r["ref"] for r in rows if r["status"] == "title-match"] or "none")


if __name__ == "__main__":
    main()
