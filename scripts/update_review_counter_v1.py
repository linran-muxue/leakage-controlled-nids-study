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
    "round": "19",
    "last_item": "19",
    "last_item_title": "Open-set diagnostics had no supplementary item: added S30",
    "last_result": "fixed",
    "note": ("added the missing supplementary item for the open-set diagnostics. Section 5.6 "
             "reports the study's most adverse result - the conditional branch reaches "
             "0.643-0.694 AUROC against 0.919-0.948 for the equal-weight forest - and none of "
             "S01-S29 contained it: S15 covers calibration, robustness and latency, S18 the "
             "diversity suite, S20 the ten-seed run. That is how the range came to quote two of "
             "three seeds for three review rounds without anyone being able to check it from the "
             "bundle. S30 now ships results_cfrg_open_set_v5_verified/open_set_metrics.csv "
             "(three seeds x uncalibrated, temperature-scaled and conformal exports for both "
             "arms) and results_open_set_matrix_v2/open_set_matrix_metrics.csv (the seven "
             "family combinations Section 6.5 refers to). "
             "scripts/add_open_set_supplementary_v1.py asserts all eight endpoints Section 5.6 "
             "prints and the matrix shape before registering the item, adds the index row in "
             "both manuscripts, cites S30 from Sections 5.6 and 6.5, rebuilds the bundle "
             "(renaming it to 补充材料_S01_S30 and removing the superseded directories), syncs "
             "the mirror, and refreshes self-check F4 (30 items, 76 material files). Gate 39 "
             "checks green, including the supplementary index, mirror and JISA format checks; "
             "docx, manifest, bundle and desktop rebuilt."),
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
