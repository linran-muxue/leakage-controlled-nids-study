"""Re-derive the Section 5.3 mechanism numbers and Table 6 from their sources."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
passed = mismatches = 0


def check(label: str, claimed, recomputed, tol: float = 5e-6) -> None:
    global passed, mismatches
    if abs(float(claimed) - float(recomputed)) <= tol:
        passed += 1
        print(f"OK    {label:<52}{float(recomputed):.6f}")
    else:
        mismatches += 1
        print(f"ISSUE {label:<52}claimed {claimed}, source {float(recomputed):.6f}")


def check_printed(label: str, printed: str, value: float) -> None:
    """The printed string must be the source value rounded to its own precision."""
    global passed, mismatches
    decimals = len(printed.split(".")[1])
    rounded = f"{float(value):.{decimals}f}"
    if rounded == printed:
        passed += 1
        print(f"OK    {label:<52}{rounded}")
    else:
        mismatches += 1
        print(f"ISSUE {label:<52}printed {printed}, source rounds to {rounded}")


def main() -> int:
    weight = pd.read_csv(ROOT / "results_weight_mechanism_v3" /
                         "weight_mechanism_summary.csv").iloc[0]
    print("== measurements 1-3 ==")
    check("single-tree score std", 0.01143, weight.score_std, 5e-6)
    check("weight coefficient of variation", 0.01262, weight.weight_cv, 5e-6)
    check("normalised weight entropy", 0.99998, weight.normalized_weight_entropy, 5e-6)
    check("mean probability L1", 0.000299, weight.mean_probability_l1, 5e-7)
    check("max probability L1", 0.003473, weight.max_probability_l1, 5e-7)
    check("prediction disagreements", 0, weight.prediction_disagreement_count, 0)
    check("balanced-control test rows", 505, weight.test_samples, 0)

    print()
    print("== measurement 4 ==")
    margin = json.loads((ROOT / "results_margin_bound_v5" /
                         "margin_bound_summary.json").read_text(encoding="utf-8"))
    check("provable by a priori bound (%)", 99.91,
          margin["provable_by_bound_rate_mean"] * 100, 5e-3)
    check("provable by realised perturbation (%)", 99.996,
          margin["provable_by_actual_rate_mean"] * 100, 5e-4)
    check("rows whose label actually changes", 0, margin["empirical_changed_rows"], 0)
    check("median perturbation bound", 0.000231, margin["median_delta_bound_mean"], 5e-7)
    check("total test rows", 23958, margin["total_rows"], 0)
    per_seed = pd.read_csv(ROOT / "results_margin_bound_v5" / "margin_bound_summary.csv")
    ratio = per_seed.margin_to_bound_ratio_median
    check("median margin-to-bound ratio, lower end", 3469, ratio.min(), 1.0)
    check("median margin-to-bound ratio, upper end", 5038, ratio.max(), 1.0)

    print()
    print("== measurement 5 ==")
    grid = pd.read_csv(ROOT / "results_gate_tuning_v5" / "gate_search_results.csv")
    check("gate configurations x seeds", 108, len(grid), 0)
    values = grid.val_macro_f1
    print(f"      distinct validation values: {values.nunique()}, "
          f"range {float(values.max() - values.min()):.6f}")
    check("distinct validation Macro-F1 values", 6, values.nunique(), 0)
    check("total range of validation Macro-F1", 0.00117,
          values.max() - values.min(), 5e-6)
    check("row-level disagreements vs equal voting", 65,
          grid.disagreement_vs_equal_weight.sum(), 0)
    check("disagreement share (%)", 0.0075,
          100 * grid.disagreement_vs_equal_weight.sum() / (len(grid) * 7986), 5e-5)
    tuned = pd.read_csv(ROOT / "results_tuned_gate_test_v5" / "tuned_vs_default_test.csv")
    check("rows changed on the locked test partition", 0,
          tuned.rows_changed_vs_default.sum(), 0)
    check("test Macro-F1 difference", 0.0, tuned.difference.abs().max(), 0)

    print()
    print("== Table 6 (means over three seeds) ==")
    suite = pd.read_csv(ROOT / "results_diversity_v5" / "diversity_suite_results.csv")
    means = suite.groupby("expert_set").agg(
        dis=("mean_pairwise_disagreement", "mean"),
        conf=("mean_confidence_correlation", "mean"),
        ent=("mean_weight_entropy", "mean"),
        gain=("gate_gain", "mean"),
        changed=("disagreement_gated_vs_equal", "mean"))
    table = {
        "rf_same_view_seeds": (0.0020, "0.979", "0.99995", 0.00000, 0.0),
        "rf_views_k60": (0.0036, "0.967", "0.99995", 0.00000, 0.0),
        "rf_views_k20": (0.0176, "0.791", "0.99905", 0.00271, 9.3),
        "hetero_families": (0.0281, "0.493", "0.99842", 0.00332, 11.7),
        "disjoint_views_k60": (0.0644, "0.507", "0.99549", 0.00401, 33.7),
    }
    for name, (dis, corr, ent, gain, changed) in table.items():
        row = means.loc[name]
        check_printed(f"{name} confidence correlation", corr, row["conf"])
        check_printed(f"{name} weight entropy", ent, row["ent"])
        for label, claimed, recomputed, tol in (
                (f"{name} disagreement", dis, row["dis"], 5e-5),
                (f"{name} gate gain", gain, row["gain"], 5e-6),
                (f"{name} rows changed", changed, row["changed"], 5e-2)):
            check(label, claimed, recomputed, tol)

    print()
    print(f"assertions passed {passed} | mismatches {mismatches}")
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
