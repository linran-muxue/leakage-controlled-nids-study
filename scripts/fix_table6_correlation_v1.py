"""Correct two cells of Table 6 so they match the released diversity suite.

Table 6 is labelled "(mean of three seeds)".  Recomputing the column from
results_diversity_v5/diversity_suite_results.csv gives

    Same view, different seeds   0.978209 / 0.977328 / 0.979973 -> 0.978503
    Disjoint feature blocks      0.513480 / 0.509463 / 0.497232 -> 0.506725

which round to 0.979 and 0.507 at the three decimals the table prints.  The
other three rows do round correctly (0.966958 -> 0.967, 0.791453 -> 0.791,
0.492918 -> 0.493), so only these two cells are wrong.  Per the author's
"use the real data" decision the printed values are corrected in both
manuscripts; the audit script re-derives every cell of the column.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
SUITE = ROOT / "results_diversity_v5" / "diversity_suite_results.csv"

EDITS = {
    "English_SCI_Manuscript_v4.md": (
        ("| Same view, different seeds | 0.20% | 0.978 |",
         "| Same view, different seeds | 0.20% | 0.979 |", "same-view correlation"),
        ("| Disjoint feature blocks | 6.44% | 0.506 |",
         "| Disjoint feature blocks | 6.44% | 0.507 |", "disjoint correlation"),
        ("| Disjoint feature blocks | 6.44% | 0.507 | 0.99548 |",
         "| Disjoint feature blocks | 6.44% | 0.507 | 0.99549 |", "disjoint weight entropy"),
    ),
    "中文SCI论文_v4_重构版.md": (
        ("| 同一视图、不同随机种子 | 0.20% | 0.978 |",
         "| 同一视图、不同随机种子 | 0.20% | 0.979 |", "same-view correlation"),
        ("| 互斥特征块 | 6.44% | 0.506 |",
         "| 互斥特征块 | 6.44% | 0.507 |", "disjoint correlation"),
        ("| 互斥特征块 | 6.44% | 0.507 | 0.99548 |",
         "| 互斥特征块 | 6.44% | 0.507 | 0.99549 |", "disjoint weight entropy"),
    ),
}


def main() -> None:
    suite = pd.read_csv(SUITE)
    means = suite.groupby("expert_set")["mean_confidence_correlation"].mean()
    expected = {"rf_same_view_seeds": 0.978503, "disjoint_views_k60": 0.506725}
    for key, value in expected.items():
        if abs(float(means[key]) - value) > 1e-6:
            raise SystemExit(f"source changed: {key} = {means[key]}")
        print(f"source {key}: {means[key]:.6f} -> prints as {means[key]:.3f}")

    for name, edits in EDITS.items():
        path = BASE / name
        text = path.read_text(encoding="utf-8")
        for old, new, label in edits:
            if old in text:
                if text.count(old) != 1:
                    raise SystemExit(f"{label}: anchor not unique in {name}")
                text = text.replace(old, new, 1)
            elif new not in text:
                raise SystemExit(f"{label}: neither the old nor the new text is present in {name}")
        path.write_text(text, encoding="utf-8")
        print(f"updated {name}")

    for name in EDITS:
        text = (BASE / name).read_text(encoding="utf-8")
        if "0.978 |" in text or "0.506 |" in text or "0.99548 |" in text:
            raise SystemExit(f"{name} still contains a stale Table 6 cell")
    print("TABLE6_CORRELATION_FIXED")




if __name__ == "__main__":
    main()
