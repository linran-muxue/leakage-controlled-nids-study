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
    "round": "20",
    "last_item": "20",
    "last_item_title": "Nine self-descriptions in the deliverables had drifted",
    "last_result": "fixed",
    "note": ("global sweep for statements the deliverables make about themselves. Nine had "
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
