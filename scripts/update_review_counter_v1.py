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
    "round": "21",
    "last_item": "21",
    "last_item_title": "The cover letter claimed a 118-test suite; the suite collects 138",
    "last_result": "fixed",
    "note": ("front-matter pass. The cover letter claimed 'A 118-test suite runs in continuous "
             "integration' while the suite collects 138. The front-matter check could not see it "
             "for two reasons, both now closed in check_aux_documents_v13.py: it compared the "
             "auxiliary documents against the whole manuscript, so reference page ranges "
             "(1189-1232, 1157-1182) vouched for any three-digit number; and its token patterns "
             "matched only decimals and integers of four digits or more, so suite sizes, "
             "search-grid sizes and table counts were never compared at all. The comparison now "
             "uses the body without the reference list and requires every three-digit integer to "
             "appear there - it flagged the 118 immediately - and the suite size is additionally "
             "recomputed from pytest collection by check_deliverable_counts_v1.py, which now "
             "covers the cover letter as well. Fixed by fix_deliverable_counts_v1.py to 138. The "
             "rest of the cover letter was verified against source this round and reproduces: "
             "N-BaIoT 180,000 flows (three 60,000-row classes in dataset_summary.csv), the "
             "53,237 of 2,668,729 physically valid records (data_processing_audit.json), the "
             "7.8x scale-up, the 4.1x model size and 4.6x throughput, the 175x training penalty, "
             "and both TOST verdicts. The old note about the earlier deliverable-count sweep is "
             "kept below. "
             "PREVIOUS: global sweep for statements the deliverables make about themselves. Nine had "
             "drifted, all invisible to the existing gate because nothing recomputed them: the "
             "self-check table still said 118 unit tests (138 collect), 12,761 English words and "
             "35,338 Chinese characters (14,563 and 39,816), 507 numeric tokens per manuscript "
             "(589), and 7 main tables (8 captions, Table 1-8); README announced a 34-check gate "
             "(39 before this round, 40 after it); and the three working documents that open "
             "with a snapshot of the current state - the gap audit, the P0/P1 manual and the "
             "structure plan - still quoted the pre-Round-18 totals of 66 checks with 62 passing "
             "instead of 69 with 65. The gap audit's S8 status line also still described the "
             "English manuscript as 10,800 words with 10 tables. "
             "scripts/check_deliverable_counts_v1.py recomputes all nine from the artefacts "
             "(pytest collection, the gate table, the manuscripts, the figures directory and the "
             "self-check status counts) and fails if a deliverable states a different number; "
             "scripts/fix_deliverable_counts_v1.py re-measures through that check, rewrites the "
             "declarations and then requires the check to pass. The guard joins the gate, which "
             "is why README now says 40 rather than 39. Gate 40 checks green; docx, manifest, "
             "bundle and desktop rebuilt."),
    "timestamp": "2026-09-25T05:10:00+08:00",
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
