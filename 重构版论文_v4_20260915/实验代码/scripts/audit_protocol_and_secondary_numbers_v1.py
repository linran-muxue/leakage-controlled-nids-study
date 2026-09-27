"""Re-derive the Section 5.4 and 5.6 numbers the headline assertions skip."""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
passed = mismatches = 0


def check(label: str, claimed, recomputed, tol: float = 5e-6, scale: float = 1.0) -> None:
    global passed, mismatches
    value = float(recomputed) * scale
    if abs(float(claimed) - value) <= tol:
        passed += 1
        print(f"OK    {label:<50}{value:.6f}")
    else:
        mismatches += 1
        print(f"ISSUE {label:<50}claimed {claimed}, source {value:.6f}")


def protocol() -> None:
    print("== 5.4 protocol sensitivity ==")
    metrics = pd.read_csv(ROOT / "results_protocol_sensitivity_v4" /
                          "protocol_sensitivity_metrics.csv")
    pivot = metrics.pivot(index="seed", columns="protocol", values="macro_f1")
    split = pivot["split_first_training_only_dedup"]
    glob = pivot["global_dedup_before_split"]
    for seed, value in split.items():
        check(f"dedup-order (split first) seed {seed}", round(float(value), 6), value, 5e-7)
    for seed, value in glob.items():
        check(f"dedup-order (global) seed {seed}", round(float(value), 6), value, 5e-7)
    check("dedup-order mean (split first)", 0.957089, split.mean(), 5e-6)
    check("dedup-order mean (global)", 0.955682, glob.mean(), 5e-6)
    check("dedup-order difference", 0.00141, split.mean() - glob.mean(), 5e-5)
    check("dedup-order largest seed gap", 0.0060, (split - glob).abs().max(), 5e-5)

    ten = pd.read_csv(ROOT / "results_seeds10_v5" / "table4a_10seeds.csv").set_index("model")
    balanced = pd.read_csv(ROOT / "results_rccf_cic_balanced_v3b" / "metrics_aggregate.csv")
    balanced_f1 = float(balanced.macro_f1_mean.iloc[0])
    check("class prior (balanced control)", 0.961807, balanced_f1, 5e-7)
    check("class prior (natural prior)", 0.889278, ten.loc["rccf", "macro_f1"], 5e-7)
    check("class-prior difference", 0.0725, balanced_f1 - ten.loc["rccf", "macro_f1"], 5e-5)

    nested = pd.read_csv(ROOT / "results_nested_modelwise_v1_5x3" /
                         "outer_modelwise_summary.csv", header=[0, 1])
    nested = nested.set_index(nested.columns[0])
    check("nested XGBoost", 0.962177, nested.loc["xgboost", ("macro_f1", "mean")], 5e-7)
    check("nested random forest", 0.954423,
          nested.loc["random_forest", ("macro_f1", "mean")], 5e-7)
    check("nested extra trees", 0.947964,
          nested.loc["extra_trees", ("macro_f1", "mean")], 5e-7)
    paired = pd.read_csv(ROOT / "results_nested_modelwise_v1_5x3" /
                         "paired_macro_f1_statistics.csv").set_index("comparison")
    check("XGBoost - RF delta", 0.007755, paired.loc["xgboost_vs_random_forest", "mean_delta"], 5e-7)
    check("XGBoost CI low", 0.004424, paired.loc["xgboost_vs_random_forest", "ci_low"], 5e-7)
    check("XGBoost CI high", 0.010549, paired.loc["xgboost_vs_random_forest", "ci_high"], 5e-7)
    check("ExtraTrees - RF delta", -0.006459,
          paired.loc["extra_trees_vs_random_forest", "mean_delta"], 5e-7)
    check("ExtraTrees CI low", -0.012391,
          paired.loc["extra_trees_vs_random_forest", "ci_low"], 5e-7)
    check("ExtraTrees CI high", -0.002263,
          paired.loc["extra_trees_vs_random_forest", "ci_high"], 5e-7)
    check("nested permutation p", 0.0625,
          paired.loc["xgboost_vs_random_forest", "permutation_p"], 5e-7)

    mlp = pd.read_csv(ROOT / "results_mlp_final_v5" / "metrics_aggregate.csv").iloc[0]
    check("MLP model-family gap", 0.0916,
          ten.loc["rccf", "macro_f1"] - float(mlp.macro_f1_mean), 5e-5)
    check("ExtraTrees model-family gap", 0.0318,
          ten.loc["rccf", "macro_f1"] - ten.loc["extra_trees_chi2", "macro_f1"], 5e-5)


def secondary() -> None:
    print()
    print("== 5.6 secondary metrics ==")
    ten = pd.read_csv(ROOT / "results_seeds10_v5" / "table4a_10seeds.csv").set_index("model")
    check("natural log loss (RCCF)", 0.05183, ten.loc["rccf", "log_loss"], 5e-6)
    check("natural log loss (equal RF)", 0.05220, ten.loc["equal_rf_chi2", "log_loss"], 5e-6)
    check("natural Brier (RCCF)", 0.006365, ten.loc["rccf", "brier"], 5e-7)
    check("natural Brier (equal RF)", 0.006255, ten.loc["equal_rf_chi2", "brier"], 5e-7)
    check("natural ECE (RCCF)", 0.006849, ten.loc["rccf", "ece"], 5e-7)
    check("natural ECE (equal RF)", 0.004493, ten.loc["equal_rf_chi2", "ece"], 5e-7)

    calibration = pd.read_csv(ROOT / "results_cfrg_calibration_v2_verified" / "metrics.csv")
    seed42 = calibration[calibration.seed == 42].set_index(["model", "variant"])
    check("balanced ECE before scaling", 0.0238,
          seed42.loc[("cfrg_forest", "uncalibrated"), "ece"], 5e-5)
    check("balanced ECE after scaling", 0.0119,
          seed42.loc[("cfrg_forest", "temperature_scaled"), "ece"], 5e-5)
    check("equal-forest temperature stays 1.0", 1.0,
          seed42.loc[("equal_rf", "temperature_scaled"), "temperature"], 0)

    robust = pd.read_csv(ROOT / "results_rccf_evidence_v3b" / "robustness_shared.csv")
    drops = robust.groupby(["model", "condition"])["relative_drop"].mean() * 100
    check("1% noise drop (RCCF %)", 43.30, drops[("rccf", "gaussian_noise_1pct")], 5e-2)
    check("1% noise drop (equal RF %)", 42.64,
          drops[("equal_rf_chi2", "gaussian_noise_1pct")], 5e-2)
    check("1% noise drop (extra trees %)", 11.57,
          drops[("extra_trees_chi2", "gaussian_noise_1pct")], 5e-2)
    check("5% mask drop (RCCF %)", 1.23, drops[("rccf", "feature_mask_5pct")], 5e-2)
    check("5% mask drop (equal RF %)", 1.27,
          drops[("equal_rf_chi2", "feature_mask_5pct")], 5e-2)

    latency = pd.read_csv(ROOT / "results_rccf_evidence_v3b" / "latency_percentiles.csv")
    single = latency[latency.n_jobs == 1].groupby("model")[["p50_ms", "p95_ms", "p99_ms"]].mean()
    multi = latency[latency.n_jobs == -1].groupby("model")[["p50_ms", "p95_ms", "p99_ms"]].mean()
    for column, claim in (("p50_ms", 14.62), ("p95_ms", 15.77), ("p99_ms", 16.12)):
        check(f"single-thread RCCF {column}", claim, single.loc["rccf", column], 5e-3)
    for column, claim in (("p50_ms", 2.96), ("p95_ms", 3.61), ("p99_ms", 4.18)):
        check(f"single-thread equal RF {column}", claim, single.loc["equal_rf_chi2", column], 5e-3)
    for column, claim in (("p50_ms", 69.93), ("p95_ms", 75.11), ("p99_ms", 76.22)):
        check(f"multi-thread RCCF {column}", claim, multi.loc["rccf", column], 5e-3)
    for column, claim in (("p50_ms", 16.69), ("p95_ms", 18.24), ("p99_ms", 18.47)):
        check(f"multi-thread equal RF {column}", claim, multi.loc["equal_rf_chi2", column], 5e-3)

    extended = pd.read_csv(ROOT / "results_robustness_extended_v5" /
                           "robustness_extended_summary_3seeds.csv")
    ext = extended.set_index(["model", "condition"])["relative_drop_pct"]
    check("label flip 5% (RCCF %)", 0.57, ext[("rccf", "label_noise_5pct")], 5e-3)
    check("label flip 10% (RCCF %)", 0.97, ext[("rccf", "label_noise_10pct")], 5e-3)
    check("label flip 5% (equal RF %)", 0.77, ext[("equal_rf_chi2", "label_noise_5pct")], 5e-3)
    check("label flip 10% (equal RF %)", 1.00, ext[("equal_rf_chi2", "label_noise_10pct")], 5e-3)
    check("missing 10% (RCCF %)", 4.21, ext[("rccf", "missing_10pct")], 5e-3)
    check("missing 10% (equal RF %)", 4.25, ext[("equal_rf_chi2", "missing_10pct")], 5e-3)
    check("offset drift (RCCF %)", 17.23, ext[("rccf", "offset_drift")], 5e-3)
    check("offset drift (equal RF %)", 18.24, ext[("equal_rf_chi2", "offset_drift")], 5e-3)

    resources = json.loads((ROOT / "results_resources_v5" /
                            "resource_profile_summary.json").read_text(encoding="utf-8"))
    summary = resources["summary"]
    check("RCCF model size (MB)", 9.09, summary["rccf"]["model_size_mb"], 5e-3)
    check("equal-RF model size (MB)", 2.21, summary["equal_rf_chi2"]["model_size_mb"], 5e-3)
    check("RCCF throughput (rows/s)", 43100, summary["rccf"]["rows_per_second"], 50)
    check("equal-RF throughput (rows/s)", 200300,
          summary["equal_rf_chi2"]["rows_per_second"], 50)
    check("RCCF peak RSS (MB)", 37.0, summary["rccf"]["peak_rss_mb"], 5e-2)
    check("equal-RF peak RSS (MB)", 78.3, summary["equal_rf_chi2"]["peak_rss_mb"], 5e-2)

    cost = pd.read_csv(ROOT / "results_cost_v5" / "cost_sensitive_summary.csv")
    cost = cost.set_index(["model", "cost_ratio_fn_fp"])["nec"]
    check("cost ratio 1 (RCCF)", 0.00913, cost[("rccf", 1)], 5e-6)
    check("cost ratio 1 (equal RF)", 0.00867, cost[("equal_rf_chi2", 1)], 5e-6)
    check("cost ratio 1 (extra trees)", 0.01917, cost[("extra_trees_chi2", 1)], 5e-6)
    check("cost ratio 100 (RCCF)", 0.07260, cost[("rccf", 100)], 5e-6)
    check("cost ratio 100 (equal RF)", 0.06753, cost[("equal_rf_chi2", 100)], 5e-6)
    check("cost ratio 100 (extra trees)", 0.06180, cost[("extra_trees_chi2", 100)], 5e-6)

    open_set = pd.read_csv(ROOT / "results_cfrg_open_set_v5_verified" / "open_set_metrics.csv")
    open_set_ranges(open_set)


CONDITIONAL = ("cfrg_forest", "cfrg_forest_temperature_scaled")
EQUAL = ("equal_rf", "equal_rf_temperature_scaled")

# The printed endpoints, read out of the deliverables rather than restated here,
# so that editing a manuscript without re-deriving its source fails the gate.
PATTERNS = {
    "EN Section 5.6": (
        "English_SCI_Manuscript_v4.md",
        r"AUROC\) of (\d+\.\d+) to (\d+\.\d+) with an unknown-class recall of "
        r"(\d+\.\d+) to (\d+\.\d+), whereas the equal-weight forest reaches an AUROC of "
        r"(\d+\.\d+) to (\d+\.\d+) with a recall of (\d+\.\d+) to (\d+\.\d+)"),
    "ZH Section 5.6": (
        "中文SCI论文_v4_重构版.md",
        r"AUROC 为 (\d+\.\d+) 至 (\d+\.\d+)，未知类召回率为 (\d+\.\d+) 至 (\d+\.\d+)；"
        r"等权森林的 AUROC 为 (\d+\.\d+) 至 (\d+\.\d+)，未知类召回率为 (\d+\.\d+) 至 (\d+\.\d+)"),
    "EN Table 8": (
        "English_SCI_Manuscript_v4.md",
        r"AUROC (\d+\.\d+)-(\d+\.\d+) against (\d+\.\d+)-(\d+\.\d+)"),
    "ZH Table 8": (
        "中文SCI论文_v4_重构版.md",
        r"AUROC (\d+\.\d+)–(\d+\.\d+) 显著高于条件加权分支 (\d+\.\d+)–(\d+\.\d+)"),
    "self-check E8": (
        "论文自查表.md",
        r"开放集 AUROC (\d+\.\d+)–(\d+\.\d+) 显著低于等权 (\d+\.\d+)–(\d+\.\d+)"),
}

# position in each match -> (arm, column, low end?)
SECTION_SLOTS = (
    ("conditional", "auroc", True), ("conditional", "auroc", False),
    ("conditional", "unknown_recall", True), ("conditional", "unknown_recall", False),
    ("equal", "auroc", True), ("equal", "auroc", False),
    ("equal", "unknown_recall", True), ("equal", "unknown_recall", False),
)
SLOTS = {
    "EN Section 5.6": SECTION_SLOTS,
    "ZH Section 5.6": SECTION_SLOTS,
    "EN Table 8": (("equal", "auroc", True), ("equal", "auroc", False),
                   ("conditional", "auroc", True), ("conditional", "auroc", False)),
    "ZH Table 8": (("equal", "auroc", True), ("equal", "auroc", False),
                   ("conditional", "auroc", True), ("conditional", "auroc", False)),
    "self-check E8": (("conditional", "auroc", True), ("conditional", "auroc", False),
                      ("equal", "auroc", True), ("equal", "auroc", False)),
}


def open_set_ranges(open_set: "pd.DataFrame") -> None:
    """Compare every printed open-set endpoint with the released ranges.

    The released suite exports an uncalibrated and a temperature-scaled
    probability for each arm; the sentence in Section 5.6 spans both, which is
    also the only reading under which its AUROC bracket (0.643) is the true
    minimum.  The conformal rows are the rejection rule rather than the score it
    thresholds, so they are reported as context and not asserted.
    """
    ranges: dict[tuple[str, str], tuple[float, float]] = {}
    for arm, models in (("conditional", CONDITIONAL), ("equal", EQUAL)):
        rows = open_set[open_set.model.isin(models)]
        if len(rows) != len(models) * 3:
            raise SystemExit(f"{arm}: expected three seeds per export, got {len(rows)} rows")
        for column in ("auroc", "unknown_recall"):
            ranges[(arm, column)] = (float(rows[column].min()), float(rows[column].max()))
            printed = ("truncated" if column == "auroc" else "rounded")
            print(f"  source {arm:<12} {column:<15} "
                  f"{ranges[(arm, column)][0]:.6f} - {ranges[(arm, column)][1]:.6f}")
    conformal = open_set[open_set.model == "cfrg_forest_conformal"]
    print(f"  context: conformal layer AUROC {conformal.auroc.min():.6f} - "
          f"{conformal.auroc.max():.6f} (rejection rule, not asserted)")

    global passed, mismatches
    text = {name: (ROOT / "重构版论文_v4_20260915" / name).read_text(encoding="utf-8")
            for name in {source for source, _ in PATTERNS.values()}}
    for label, (source, pattern) in PATTERNS.items():
        found = re.search(pattern, text[source])
        if not found:
            mismatches += 1
            print(f"ISSUE {label:<50}cannot find the open-set sentence in {source}")
            continue
        for printed, (arm, column, low) in zip(found.groups(), SLOTS[label]):
            value = ranges[(arm, column)][0 if low else 1]
            digits = len(printed.split(".")[1])
            rounded = f"{round(value, digits):.{digits}f}"
            if low:
                scaled = 10**digits
                truncated = f"{math.floor(value * scaled) / scaled:.{digits}f}"
                accepted = {rounded, truncated}
            else:
                accepted = {rounded}
            if printed in accepted:
                passed += 1
                print(f"OK    {label + ' ' + arm + ' ' + column:<50}{printed}")
            else:
                mismatches += 1
                print(f"ISSUE {label + ' ' + arm + ' ' + column:<50}"
                      f"printed {printed}, source {value:.6f} renders as {rounded}")


def main() -> int:
    protocol()
    secondary()
    print()
    print(f"assertions passed {passed} | mismatches {mismatches}")
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
