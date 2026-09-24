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
    "round": "14",
    "last_item": "14",
    "last_item_title": "NSL-KDD calibration figure: the printed ECE was the source MCE",
    "last_result": "fixed",
    "note": ("found by the decimal-coverage audit and confirmed against the source: Section 5.5 "
             "reported ECE of 0.4819 for NSL-KDD, but metrics_aggregate.csv gives ece_mean "
             "0.209651 and mce_mean 0.481856, so the printed value was the maximum calibration "
             "error under the ECE label (per-seed ECE 0.2089/0.2103/0.2097, MCE "
             "0.5314/0.4306/0.4835). UNSW ECE 0.073441 was correct, so only NSL was affected. The "
             "author asked for the real data, so both manuscripts now read ECE of 0.209651 with "
             "the label unchanged; the surrounding argument still holds and 0.209651 remains an "
             "order of magnitude above the CIC figure 0.006849. Applied by "
             "scripts/fix_nsl_ece_v1.py, which asserts both source values before editing. The "
             "audit_calibration_and_external_numbers_v1 gate check now asserts ECE and MCE "
             "separately and fails if either manuscript stops quoting 0.209651 or quotes 0.4819 "
             "as ECE again. Same round: extended number coverage from 54 to 93 decimals in the "
             "body (38 new assertions over Sections 5.5 and 5.7, all matching) and documented the "
             "coverage boundary itself in scripts/audit_number_coverage_v1.py. Gate 35 checks "
             "green; docx, manifest, bundle and desktop rebuilt."),
    "timestamp": "2026-09-25T01:45:00+08:00",
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
