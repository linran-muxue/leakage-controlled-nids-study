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
    "round": "16",
    "last_item": "16",
    "last_item_title": "Section 5.6 open-set ranges understated the released spread",
    "last_result": "fixed",
    "note": ("finished the protocol and secondary-metric audit (99 assertions over Sections 5.4 "
             "and 5.6): every protocol-sensitivity comparison, the nested-CV deltas, the "
             "calibration and robustness numbers, all twelve latency percentiles, the resource "
             "figures and the cost-sensitive table reproduce their sources exactly. The open-set "
             "sentence did not. From results_cfrg_open_set_v5_verified/open_set_metrics.csv the "
             "conditional branch spans AUROC 0.643513-0.693891 and unknown-class recall "
             "0.001466-0.039570 over three seeds and its two exported probability variants, and "
             "the equal-weight forest spans 0.919140-0.947932 and 0.056668-0.373718; the printed "
             "ceilings (0.0088, 0.940, 0.128) described two of the three released seeds, and the "
             "conditional recall ceiling only the seed-42 export, so both spreads were "
             "understated. Following the author's use-the-real-data decision "
             "scripts/fix_open_set_endpoints_v1.py re-derives all eight endpoints from the suite "
             "and rewrites Section 5.6, Table 8 and self-check E8 in both manuscripts; the "
             "sentence now names the scope the ranges span. The new gate check reads every "
             "printed endpoint back out of the deliverables, so an edit that is not re-derived "
             "from the suite fails. Open-set metrics still have no supplementary item of their "
             "own (S15 covers calibration, robustness and latency only) - the next candidate "
             "round. The two newest audits also still lack unit tests."),
    "timestamp": "2026-09-25T03:05:00+08:00",
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
