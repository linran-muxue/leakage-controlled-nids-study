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
    "round": "18",
    "last_item": "18",
    "last_item_title": "Sections 6 and 7: two numbers described the wrong artifact",
    "last_result": "fixed",
    "note": ("finished the cross-document pass by closing Sections 6 and 7, the last region no "
             "audit covered. Two numbers there described the wrong artifact. (1) The decision "
             "matrix row for probability quality read 'Log Loss 0.0515 against 0.0528, but ECE "
             "is worse': the ECE half is the ten-seed result from Section 5.6 (0.006849 against "
             "0.004493) while the Log Loss pair came from the three-seed runs "
             "(results_rccf_cic_natural_v3b 0.051477, results_cic_natural_baselines_v3b "
             "0.052828), and the supplementary bundle explicitly warns that those two sets must "
             "not be subtracted. The row now uses the ten-seed pair 0.051826 / 0.052201, the run "
             "its ECE clause already came from. (2) The limitations paragraph said '104 test "
             "rows (0.21% of the test set) share a rounded feature vector with a training row'. "
             "The near-duplicate audit records 104 rows in near-duplicate groups spanning the "
             "partitions and 17 test rows overlapping training (17/7986 = 0.2129%); 104 test "
             "rows would be 1.3%. The sentence now carries both counts with the right labels. "
             "scripts/fix_discussion_numbers_v1.py asserts both runs' Log Loss values, both "
             "ECE values and every near-duplicate count before editing. The new check "
             "scripts/audit_discussion_numbers_v1.py adds 73 assertions and, more importantly, "
             "fails if any of the 33 decimals printed in Sections 6 and 7 is not asserted here - "
             "the coverage gap cannot reopen. It also re-derives the three-population dilution "
             "chain (0.002068/0.000517/-0.000456, 0.004249/0.001062/-0.001137, "
             "0.021397/0.005349/-0.005533), the 80.5x and 5.25x cost multiples, the equivalence "
             "bounds and the dose-response regression. Gate 39 checks green; docx, manifest, "
             "bundle and desktop rebuilt. Remaining for a later round: the open-set metrics "
             "still have no supplementary item of their own."),
    "timestamp": "2026-09-25T04:30:00+08:00",
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
