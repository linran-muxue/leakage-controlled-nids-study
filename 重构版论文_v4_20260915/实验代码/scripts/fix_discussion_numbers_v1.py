"""Two Section 6 numbers that do not describe the artifact they are attached to.

**Table 8, "best probability quality".**  The row read "Log Loss 0.0515 against
0.0528, but ECE is worse".  The ECE half is the ten-seed natural-prior result
quoted in Section 5.6 (RCCF 0.006849 against 0.004493), but the Log Loss pair
came from the three-seed runs (results_rccf_cic_natural_v3b 0.051477,
results_cic_natural_baselines_v3b 0.052828) while Section 5.6 quotes the
ten-seed pair (0.051826, 0.052201).  Supplementary S04-S07 and S20 are built
from different runs and the bundle warns that they must not be subtracted, so
one row quoting both is exactly the mixing that warning forbids.  The row now
uses the ten-seed pair, which is the run its ECE clause already came from.

**Section 6.5, near-duplicates.**  The sentence said "104 test rows (0.21% of
the test set) share a rounded feature vector with a training row".  The audit
records 104 rows in near-duplicate groups that span the partitions, and 17 test
rows overlapping training (0.21% of 7986 test rows = 0.2129%); 104 test rows
would be 1.3% of the test set.  The sentence now carries both counts with the
right labels.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

EDITS = {
    "English_SCI_Manuscript_v4.md": (
        ("Log Loss 0.0515 against 0.0528, but ECE is worse",
         "Log Loss 0.0518 against 0.0522, but ECE is worse", "Table 8 probability row"),
        ("and that 104 test rows (0.21% of the test set) share a rounded feature vector "
         "with a training row",
         "and that 104 rows sit in near-duplicate groups that span the partitions, of which "
         "17 test rows (0.21% of the test set) share a rounded feature vector with a "
         "training row",
         "Section 6.5 near-duplicate counts"),
    ),
    "中文SCI论文_v4_重构版.md": (
        ("Log Loss 0.0515 优于等权 0.0528，但 ECE 更差",
         "Log Loss 0.0518 优于等权 0.0522，但 ECE 更差", "表 8 概率质量行"),
        ("其中 104 条测试行（占测试集 0.21%）与训练行共享同一个舍入后特征向量",
         "其中 104 行位于跨划分的近重复组内，其中 17 条测试行（占测试集 0.21%）"
         "与训练行共享同一个舍入后特征向量",
         "第 6.5 节近重复计数"),
    ),
}


def sources() -> None:
    ten = pd.read_csv(ROOT / "results_seeds10_v5" / "table4a_10seeds.csv").set_index("model")
    if abs(float(ten.loc["rccf", "log_loss"]) - 0.051826) > 5e-7:
        raise SystemExit(f"ten-seed RCCF log loss changed: {ten.loc['rccf', 'log_loss']}")
    if abs(float(ten.loc["equal_rf_chi2", "log_loss"]) - 0.052201) > 5e-7:
        raise SystemExit("ten-seed equal-forest log loss changed")
    if abs(float(ten.loc["rccf", "ece"]) - 0.006849) > 5e-7:
        raise SystemExit("ten-seed RCCF ECE changed")
    if abs(float(ten.loc["equal_rf_chi2", "ece"]) - 0.004493) > 5e-7:
        raise SystemExit("ten-seed equal-forest ECE changed")
    three = pd.read_csv(ROOT / "results_rccf_cic_natural_v3b" / "metrics_aggregate.csv")
    if abs(float(three.log_loss_mean.iloc[0]) - 0.051477) > 5e-7:
        raise SystemExit("three-seed RCCF log loss changed")
    base = pd.read_csv(ROOT / "results_cic_natural_baselines_v3b" / "metrics_aggregate_flat.csv")
    base = base.set_index("model")
    if abs(float(base.loc["equal_rf_chi2", "log_loss_mean"]) - 0.052828) > 5e-7:
        raise SystemExit("three-seed equal-forest log loss changed")
    print("ten-seed pair 0.051826 / 0.052201 vs three-seed pair 0.051477 / 0.052828 "
          "(ECE 0.006849 / 0.004493 is ten-seed only)")

    summary = json.loads((ROOT / "results_near_duplicate_v5" /
                          "near_duplicate_summary.json").read_text(encoding="utf-8"))
    four = next(r for r in summary["results"] if r["significant_digits"] == 4)
    if four["rows_in_cross_split_groups"] != 104:
        raise SystemExit(f"cross-split rows changed: {four['rows_in_cross_split_groups']}")
    if abs(four["near_duplicate_row_fraction"] - 0.0035501624809812725) > 1e-12:
        raise SystemExit("near-duplicate row fraction changed")
    sensitivity = json.loads((ROOT / "results_near_duplicate_v5" /
                              "near_duplicate_sensitivity.json").read_text(encoding="utf-8"))
    test_rows = sensitivity["results"][0]["test_rows"]
    overlapping = sensitivity["test_rows_overlapping_training_at_this_resolution"]
    fraction = overlapping / test_rows
    worst = max(abs(r["delta"]) for r in sensitivity["results"])
    if (test_rows, overlapping) != (7986, 17):
        raise SystemExit(f"near-duplicate sensitivity changed: {test_rows}, {overlapping}")
    if abs(fraction - 0.002128725269221137) > 1e-12:
        raise SystemExit("overlap fraction changed")
    if abs(worst - 0.000569446076027269) > 1e-12:
        raise SystemExit("worst Macro-F1 change changed")
    print(f"near-duplicates: {four['near_duplicate_row_fraction']:.4%} of the population, "
          f"104 rows in cross-split groups, {overlapping} of {test_rows} test rows "
          f"({fraction:.4%}), worst Macro-F1 change {worst:.6f}")


def main() -> None:
    sources()
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
        if "0.0515" in text or "0.0528" in text:
            raise SystemExit(f"{name} still quotes the three-seed Log Loss pair")
        if "104 test rows" in text or "104 条测试行" in text:
            raise SystemExit(f"{name} still calls the 104 cross-split rows test rows")
    print("DISCUSSION_NUMBERS_FIXED")


if __name__ == "__main__":
    main()
