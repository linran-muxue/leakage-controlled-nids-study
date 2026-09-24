"""Re-derive the Section 5.5 and 5.7 numbers the 69 headline assertions skip.

The number-coverage audit showed that only 54 of the 338 decimals in the
manuscript are matched by a traceability assertion.  This script closes the gap
for the external-benchmark and scale-ladder paragraphs, and it checks every
calibration claim against the *metric it names* - which is how the NSL-KDD
mislabel below surfaced.

Run it for a report; it stays out of the commit gate while the NSL-KDD label
question is open for the authors to decide.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
TOL = 5e-6
passed = mismatches = skipped = 0
notices: list[str] = []


def check(label: str, claimed: float, recomputed: float, tol: float = TOL) -> None:
    global passed, mismatches
    if abs(float(claimed) - float(recomputed)) <= tol:
        passed += 1
        print(f"OK    {label:<56}{float(recomputed):.6f}")
    else:
        mismatches += 1
        print(f"ISSUE {label:<56}claimed {claimed}, source {float(recomputed):.6f}")


def skip(label: str, why: str) -> None:
    global skipped
    skipped += 1
    print(f"SKIP  {label:<56}{why}")


def aggregates(directory: str, model: str = "rccf") -> pd.Series:
    frame = pd.read_csv(ROOT / directory / "metrics_aggregate.csv")
    return frame[frame.model == model].iloc[0]


def external() -> None:
    print("== external benchmarks (Section 5.5) ==")
    nsl = aggregates("results_rccf_nsl_v2_final")
    check("NSL accuracy", 0.747960, nsl.accuracy_mean)
    check("NSL balanced accuracy", 0.492837, nsl.balanced_accuracy_mean)
    check("NSL macro-F1", 0.514697, nsl.macro_f1_mean)
    check("NSL log loss", 1.6802, nsl.log_loss_mean, 5e-5)
    check("NSL coverage", 0.6198, nsl.coverage_mean, 5e-5)
    check("NSL MCE (the value the manuscript prints as ECE)", 0.4819, nsl.mce_mean, 5e-5)
    if abs(nsl.mce_mean - 0.4819) < 5e-5 and abs(nsl.ece_mean - 0.4819) > 1e-3:
        notices.append("NSL-KDD: the manuscript's 'ECE of 0.4819' is the source MCE "
                       f"({nsl.mce_mean:.6f}); the source ECE is {nsl.ece_mean:.6f}")

    unsw = aggregates("results_rccf_unsw_v2_final")
    check("UNSW accuracy", 0.715340, unsw.accuracy_mean)
    check("UNSW balanced accuracy", 0.566753, unsw.balanced_accuracy_mean)
    check("UNSW macro-F1", 0.493310, unsw.macro_f1_mean)
    check("UNSW log loss", 0.649577, unsw.log_loss_mean)
    check("UNSW ECE", 0.073441, unsw.ece_mean)
    check("UNSW coverage", 0.8957, unsw.coverage_mean, 5e-5)

    files = pd.read_csv(ROOT / "results_file_external_generalization_v3b" /
                        "file_external_results.csv")
    check("file-level minimum macro-F1", 0.3325, files.macro_f1_known.min(), 5e-5)
    check("file-level maximum macro-F1", 0.9997, files.macro_f1_known.max(), 5e-5)
    by_name = files.set_index("test_file")["macro_f1_known"]
    probes = (("Thursday-WorkingHours-Morning", 0.4314),
              ("Friday-WorkingHours-Afternoon-DDos", 0.4949),
              ("Tuesday", 0.5229),
              ("Monday", 0.9975),
              ("Friday-WorkingHours-Morning", 0.9997))
    for needle, claimed in probes:
        match = [v for k, v in by_name.items() if needle.lower() in str(k).lower()]
        if not match:
            skip(f"file-level {needle}", "no matching row")
        else:
            check(f"file-level {needle}", claimed, match[0], 5e-5)


def scale_ladder() -> None:
    print()
    print("== scale ladder (Section 5.7) ==")
    mid = pd.read_csv(ROOT / "results_scale_sensitivity_v46" / "metrics_by_seed.csv")
    means = mid.groupby("model")["macro_f1"].mean()
    check("413k equal RF (chi-square)", 0.857202, means["equal_rf_chi2"])
    check("413k XGBoost", 0.827656, means["xgboost_chi2"])
    check("413k equal RF (all features)", 0.852953, means["equal_rf_all"])
    check("413k extra trees", 0.783747, means["extra_trees_chi2"])
    check("413k decision tree", 0.809695, means["decision_tree_chi2"])
    check("413k view gap (chi2 - all)", 0.004249,
          means["equal_rf_chi2"] - means["equal_rf_all"])
    check("413k dilution prediction (gap/4)", 0.001062,
          (means["equal_rf_chi2"] - means["equal_rf_all"]) / 4)

    full = pd.read_csv(ROOT / "results_full_corpus_v49" / "metrics_by_seed.csv")
    fmeans = full.groupby("model")[["macro_f1", "accuracy"]].mean()
    check("full equal RF (chi-square)", 0.759540, fmeans.loc["equal_rf_chi2", "macro_f1"])
    check("full XGBoost", 0.800255, fmeans.loc["xgboost_chi2", "macro_f1"])
    check("full equal RF (all features)", 0.738143, fmeans.loc["equal_rf_all", "macro_f1"])
    check("full extra trees", 0.696629, fmeans.loc["extra_trees_chi2", "macro_f1"])
    check("full decision tree", 0.595653, fmeans.loc["decision_tree_chi2", "macro_f1"])
    check("full XGBoost accuracy", 0.9993, fmeans.loc["xgboost_chi2", "accuracy"], 5e-5)
    check("full equal-RF accuracy", 0.9958, fmeans.loc["equal_rf_chi2", "accuracy"], 5e-5)
    check("full view gap (chi2 - all)", 0.021397,
          fmeans.loc["equal_rf_chi2", "macro_f1"] - fmeans.loc["equal_rf_all", "macro_f1"])
    check("full dilution prediction (gap/4)", 0.005349,
          (fmeans.loc["equal_rf_chi2", "macro_f1"] - fmeans.loc["equal_rf_all", "macro_f1"]) / 4)
    check("model-family gap (XGBoost - chi2)", 0.041,
          fmeans.loc["xgboost_chi2", "macro_f1"] - fmeans.loc["equal_rf_chi2", "macro_f1"], 5e-4)

    # The primary gap must come from the ten-seed run, the same protocol as the
    # 413,209-flow and full-corpus gaps; the three-seed table gives 0.000910 and
    # is a different pair of models (reviewed in round 20k).
    primary = pd.read_csv(ROOT / "results_seeds10_v5" / "table4a_10seeds.csv").set_index("model")
    check("primary view gap (chi2 - all)", 0.002068,
          primary.loc["equal_rf_chi2", "macro_f1"] - primary.loc["equal_rf_all", "macro_f1"])
    check("primary dilution prediction (gap/4)", 0.000517,
          (primary.loc["equal_rf_chi2", "macro_f1"] - primary.loc["equal_rf_all", "macro_f1"]) / 4)


def main() -> int:
    external()
    scale_ladder()
    print()
    print(f"assertions passed {passed} | mismatches {mismatches} | skipped {skipped}")
    for notice in notices:
        print(f"NOTICE {notice}")
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
