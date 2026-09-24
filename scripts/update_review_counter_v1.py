"""Rewrite logs/review_round_counter.txt from explicit fields.

The counter is local state (logs/ is gitignored) but it is the only record of
which rotation item each review round covered, so it has to stay readable and
correct.  Editing it through a script avoids the long single-line note drifting
out of sync with the header.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
COUNTER = ROOT / "logs" / "review_round_counter.txt"

FIELDS = {
    "round": "12",
    "last_item": "12",
    "last_item_title": "Self-check table and gap report vs the artifacts they quote",
    "last_result": "fixed",
    "note": ("two stale counts in documents that ship to the reviewer. (1) Both the self-check "
             "table (A1) and the gap report quote the number of assertions run by "
             "audit_number_traceability_v5.py; they still said 50 while the script now runs 69 "
             "(four were added in round 20h for the Section 5.1 feature-degeneracy counts). "
             "(2) A3 of the self-check table still said 47 DOIs all verified via Crossref, which "
             "counts record rows rather than DOIs: after the round-20f rebuild the record has 36 "
             "cited DOIs verified against Crossref or DataCite and 11 entries explicitly marked "
             "as having no DOI. Both documents corrected, the self-check date now records the "
             "latest revision, and check_selfcheck_claims_v1 re-derives all four figures from "
             "number_traceability.csv and doi_verification.json so they cannot drift again. Also "
             "noted (no defect): the gap report stops at its seventh review round; rounds 18-20 "
             "are recorded in git history and in this counter file. Gate now 34 checks, all "
             "green; docx, manifest and bundle rebuilt; desktop copies refreshed."),
    "timestamp": "2026-09-24T23:58:00+08:00",
}


def main() -> int:
    COUNTER.parent.mkdir(parents=True, exist_ok=True)
    text = COUNTER.read_text(encoding="utf-8") if COUNTER.exists() else ""
    existing: dict[str, str] = {}
    for line in text.splitlines():
        if "=" in line and not line.startswith(" "):
            key, value = line.split("=", 1)
            existing[key] = value
    existing.update(FIELDS)
    order = ["round", "last_item", "last_item_title", "last_result", "note", "timestamp"]
    COUNTER.write_text("\n".join(f"{key}={existing[key]}" for key in order) + "\n",
                       encoding="utf-8")
    for key in order:
        print(f"{key}={existing[key][:90]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
