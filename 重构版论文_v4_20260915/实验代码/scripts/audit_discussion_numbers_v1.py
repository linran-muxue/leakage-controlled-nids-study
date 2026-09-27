"""Re-derive the Section 6 discussion and Section 7 conclusion numbers.

Sections 5.1-5.7 are covered by four audits; the discussion and the conclusion
were the last region where a number could drift unnoticed.  They are also where
numbers are most often re-used, so two defects surfaced here: the decision
matrix quoted a Log Loss pair from the three-seed runs beside an ECE clause from
the ten-seed run, and the limitations paragraph called 104 cross-split rows
"104 test rows" (17 test rows is 0.21% of the test set).

Everything is re-derived from the released artefacts; the two decision-matrix
values and the near-duplicate counts are additionally read back out of both
manuscripts so that an edit which is not re-derived fails the gate.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
passed = mismatches = 0
CLAIMED: set[str] = set()


def check(label: str, claimed, recomputed, tol: float = 5e-6) -> None:
    global passed, mismatches
    for digits in range(1, 7):
        CLAIMED.add(f"{abs(float(claimed)):.{digits}f}")
    value = float(recomputed)
    if abs(float(claimed) - value) <= tol:
        passed += 1
        print(f"OK    {label:<54}{value:.6f}")
    else:
        mismatches += 1
        print(f"ISSUE {label:<54}claimed {claimed}, source {value:.6f}")


def positive(label: str, recomputed: float) -> None:
    """For claims of the form "every run gains": the signature is the minimum."""
    global passed, mismatches
    if float(recomputed) > 0:
        passed += 1
        print(f"OK    {label:<54}{float(recomputed):.6f} (smallest)")
    else:
        mismatches += 1
        print(f"ISSUE {label:<54}smallest gain is {float(recomputed):.6f}, not positive")


def texts() -> tuple[str, str]:
    return tuple((BASE / name).read_text(encoding="utf-8") for name in
                 ("English_SCI_Manuscript_v4.md", "中文SCI论文_v4_重构版.md"))


def populations() -> None:
    """The dilution expression, re-derived on all three CIC-IDS2017 populations."""
    global passed, mismatches
    print("== 6.1 condition D: one expression on three populations ==")
    ten = pd.read_csv(ROOT / "results_seeds10_v5" / "table4a_10seeds.csv").set_index("model")
    scale = pd.read_csv(ROOT / "results_scale_sensitivity_v46" /
                        "metrics_aggregate.csv", header=[0, 1])
    scale = scale.set_index(scale.columns[0])
    full = pd.read_csv(ROOT / "results_full_corpus_v49" / "metrics_aggregate.csv", header=[0, 1])
    full = full.set_index(full.columns[0])
    summary = json.loads((ROOT / "results_full_corpus_v49" /
                          "full_corpus_summary.json").read_text(encoding="utf-8"))
    scaled = json.loads((ROOT / "results_scale_sensitivity_v46" /
                         "scale_sensitivity_summary.json").read_text(encoding="utf-8"))

    check("primary population, full-feature view", 0.887666, ten.loc["equal_rf_all", "macro_f1"])
    check("primary population, chi-square view", 0.889734, ten.loc["equal_rf_chi2", "macro_f1"])
    check("primary view gap", 0.002068,
          ten.loc["equal_rf_chi2", "macro_f1"] - ten.loc["equal_rf_all", "macro_f1"])
    check("primary predicted dilution", 0.000517,
          (ten.loc["equal_rf_chi2", "macro_f1"] - ten.loc["equal_rf_all", "macro_f1"]) / 4)
    check("primary measured deficit", -0.000456,
          ten.loc["rccf", "macro_f1"] - ten.loc["equal_rf_chi2", "macro_f1"])

    check("scale population, full-feature view", 0.852953,
          scale.loc["equal_rf_all", ("macro_f1", "mean")])
    check("scale population, chi-square view", 0.857202,
          scale.loc["equal_rf_chi2", ("macro_f1", "mean")])
    check("scale view gap", 0.004249,
          scale.loc["equal_rf_chi2", ("macro_f1", "mean")] -
          scale.loc["equal_rf_all", ("macro_f1", "mean")])
    check("scale predicted dilution", 0.001062,
          (scale.loc["equal_rf_chi2", ("macro_f1", "mean")] -
           scale.loc["equal_rf_all", ("macro_f1", "mean")]) / 4)
    check("scale measured deficit", -0.001137, scaled["mean_difference"], 5e-6)

    check("full corpus, full-feature view", 0.738143,
          full.loc["equal_rf_all", ("macro_f1", "mean")])
    check("full corpus, chi-square view", 0.759540,
          full.loc["equal_rf_chi2", ("macro_f1", "mean")])
    check("full-corpus view gap", 0.021397,
          full.loc["equal_rf_chi2", ("macro_f1", "mean")] -
          full.loc["equal_rf_all", ("macro_f1", "mean")])
    check("full-corpus predicted dilution", 0.005349,
          (full.loc["equal_rf_chi2", ("macro_f1", "mean")] -
           full.loc["equal_rf_all", ("macro_f1", "mean")]) / 4)
    check("full-corpus measured deficit", -0.005533, summary["mean_difference"], 5e-6)

    english, chinese = texts()
    for name, text in (("EN", english), ("ZH", chinese)):
        if "0.002068" not in text and "0.002068" not in text:
            mismatches += 1
            print(f"ISSUE {name} does not carry the primary-population view gap")
        else:
            passed += 1
            print(f"OK    {name} carries the three-population arithmetic")


def discussion() -> None:
    print()
    print("== 6.1-6.2 competing explanations ==")
    weight = pd.read_csv(ROOT / "results_weight_mechanism_v3" /
                         "weight_mechanism_summary.csv").iloc[0]
    check("mean probability L1 (condition B)", 0.000299, weight.mean_probability_l1, 5e-7)
    check("max probability L1 (condition B)", 0.003473, weight.max_probability_l1, 5e-7)
    check("normalised weight entropy (condition C)", 0.99998,
          weight.normalized_weight_entropy)
    margin = json.loads((ROOT / "results_margin_bound_v5" /
                         "margin_bound_summary.json").read_text(encoding="utf-8"))
    check("median decision margin", 1.0, margin["median_margin_mean"])
    check("provably immune share (%)", 99.91, margin["provable_by_bound_rate_mean"] * 100, 5e-3)

    splits = pd.read_csv(ROOT / "results_repeated_splits_v3" / "summary.csv", header=[0, 1])
    splits = splits.set_index(splits.columns[0])
    check("split noise (Macro-F1 sd over ten splits)", 0.011,
          splits.loc["rf_chi2", ("macro_f1", "std")], 5e-4)

    paired = pd.read_csv(ROOT / "results_nested_modelwise_v1_5x3" /
                         "paired_macro_f1_statistics.csv").set_index("comparison")
    check("tuning budget, XGBoost - RF", 0.0078,
          paired.loc["xgboost_vs_random_forest", "mean_delta"], 5e-5)
    ten = pd.read_csv(ROOT / "results_seeds10_v5" / "table4a_10seeds.csv").set_index("model")
    check("model-family gap, extra trees", 0.0318,
          ten.loc["rccf", "macro_f1"] - ten.loc["extra_trees_chi2", "macro_f1"], 5e-5)
    mlp = pd.read_csv(ROOT / "results_mlp_final_v5" / "metrics_aggregate.csv").iloc[0]
    check("model-family gap, neural baseline", 0.0916,
          ten.loc["rccf", "macro_f1"] - float(mlp.macro_f1_mean), 5e-5)
    balanced = pd.read_csv(ROOT / "results_rccf_cic_balanced_v3b" / "metrics_aggregate.csv")
    check("class prior (balanced - natural)", 0.0725,
          float(balanced.macro_f1_mean.iloc[0]) - ten.loc["rccf", "macro_f1"], 5e-5)
    protocol = pd.read_csv(ROOT / "results_protocol_sensitivity_v4" /
                           "protocol_sensitivity_metrics.csv")
    pivot = protocol.pivot(index="seed", columns="protocol", values="macro_f1")
    check("deduplication order, largest seed gap", 0.0060,
          (pivot["split_first_training_only_dedup"] -
           pivot["global_dedup_before_split"]).abs().max(), 5e-5)


def decision_matrix() -> None:
    print()
    print("== 6.3 Table 8 ==")
    ten = pd.read_csv(ROOT / "results_seeds10_v5" / "table4a_10seeds.csv").set_index("model")
    english, chinese = texts()
    found = re.search(r"Log Loss (\d+\.\d+) against (\d+\.\d+)", english)
    if not found:
        mismatches += 1
        print("ISSUE cannot find the Log Loss pair in the English decision matrix")
    else:
        check("decision matrix, Log Loss (RCCF)", float(found.group(1)),
              ten.loc["rccf", "log_loss"], 5e-5)
        check("decision matrix, Log Loss (equal forest)", float(found.group(2)),
              ten.loc["equal_rf_chi2", "log_loss"], 5e-5)
        check("decision matrix, ECE is worse for the conditional branch", 0.0024,
              ten.loc["rccf", "ece"] - ten.loc["equal_rf_chi2", "ece"], 5e-5)
    zh_found = re.search(r"Log Loss (\d+\.\d+) 优于等权 (\d+\.\d+)", chinese)
    if not zh_found:
        mismatches += 1
        print("ISSUE cannot find the Log Loss pair in the Chinese decision matrix")
    else:
        check("Chinese decision matrix, Log Loss (RCCF)", float(zh_found.group(1)),
              ten.loc["rccf", "log_loss"], 5e-5)
        check("Chinese decision matrix, Log Loss (equal forest)", float(zh_found.group(2)),
              ten.loc["equal_rf_chi2", "log_loss"], 5e-5)

    latency = pd.read_csv(ROOT / "results_rccf_evidence_v3b" / "latency_percentiles.csv")
    single = latency[latency.n_jobs == 1].groupby("model")["p50_ms"].mean()
    check("decision matrix, latency P50 (equal forest)", 2.96, single.loc["equal_rf_chi2"], 5e-3)
    check("decision matrix, latency P50 (conditional)", 14.62, single.loc["rccf"], 5e-3)
    files = pd.read_csv(ROOT / "results_file_external_generalization_v3b" /
                        "file_external_results.csv")
    check("decision matrix, file-level Macro-F1 floor", 0.3325, files.macro_f1_known.min(), 5e-5)
    check("decision matrix, file-level Macro-F1 ceiling", 0.9997,
          files.macro_f1_known.max(), 5e-5)
    summary = json.loads((ROOT / "results_full_corpus_v49" /
                          "full_corpus_summary.json").read_text(encoding="utf-8"))
    check("decision matrix, uncapped deficit", -0.005533, summary["mean_difference"])
    check("decision matrix, training-cost multiple", 175, summary["train_slowdown"], 0.2)


def limitations() -> None:
    global passed, mismatches
    print()
    print("== 6.5 limitations ==")
    summary = json.loads((ROOT / "results_near_duplicate_v5" /
                          "near_duplicate_summary.json").read_text(encoding="utf-8"))
    four = next(r for r in summary["results"] if r["significant_digits"] == 4)
    check("near-duplicate share of the population (%)", 0.36,
          100 * four["near_duplicate_row_fraction"], 5e-3)
    check("rows in cross-split near-duplicate groups", 104,
          four["rows_in_cross_split_groups"], 0)
    sensitivity = json.loads((ROOT / "results_near_duplicate_v5" /
                              "near_duplicate_sensitivity.json").read_text(encoding="utf-8"))
    test_rows = sensitivity["results"][0]["test_rows"]
    overlapping = sensitivity["test_rows_overlapping_training_at_this_resolution"]
    check("test rows overlapping training", 17, overlapping, 0)
    check("overlapping share of the test set (%)", 0.21, 100 * overlapping / test_rows, 5e-3)
    check("worst Macro-F1 change from removing them", 0.00057,
          max(abs(r["delta"]) for r in sensitivity["results"]), 5e-6)
    baselines = pd.read_csv(ROOT / "results_nbaiot_baselines_v48" /
                            "metrics_aggregate.csv", header=[0, 1])
    baselines = baselines.dropna(how="all").set_index(baselines.columns[0]).dropna(how="all")
    nbaiot = list(baselines[("macro_f1", "mean")]) + [0.999988]
    check("N-BaIoT, lowest Macro-F1 among all models", 0.9998, min(nbaiot), 5e-5)
    english, chinese = texts()
    if "104 rows sit in near-duplicate groups" in english and "17 test rows" in english:
        passed += 1
        print("OK    English limitations carry both near-duplicate counts")
    else:
        mismatches += 1
        print("ISSUE the English limitations no longer separate the two counts")
    if "104 行位于跨划分的近重复组内" in chinese and "17 条测试行" in chinese:
        passed += 1
        print("OK    Chinese limitations carry both near-duplicate counts")
    else:
        mismatches += 1
        print("ISSUE the Chinese limitations no longer separate the two counts")


def conclusion() -> None:
    print()
    print("== 7 conclusion ==")
    ten = pd.read_csv(ROOT / "results_seeds10_v5" / "table4a_10seeds.csv").set_index("model")
    power = pd.read_csv(ROOT / "results_seeds10_v5" / "power_analysis.csv").set_index("comparison")
    row = power.loc["rccf_minus_equal_rf_chi2"]
    check("conclusion, mean difference", -0.000456, row.mean_difference, 5e-6)
    check("conclusion, seed-level 90% interval low", -0.00112, row.ci90_low, 5e-5)
    check("conclusion, seed-level 90% interval high", 0.00021, row.ci90_high, 5e-5)
    equivalence = json.loads((ROOT / "results_equivalence_10seeds_v5" /
                              "equivalence_summary.json").read_text(encoding="utf-8"))
    pooled = equivalence["pooled"]
    check("conclusion, bootstrap interval low", -0.00425, pooled["pooled_ci_low"], 5e-5)
    check("conclusion, bootstrap interval high", 0.00338, pooled["pooled_ci_high"], 5e-5)
    check("conclusion, training-time multiple", 80,
          ten.loc["rccf", "train_seconds"] / ten.loc["equal_rf_chi2", "train_seconds"], 0.6)
    check("conclusion, batch-inference multiple", 5.3,
          ten.loc["rccf", "predict_seconds"] / ten.loc["equal_rf_chi2", "predict_seconds"],
          5e-2)

    weight = pd.read_csv(ROOT / "results_weight_mechanism_v3" /
                         "weight_mechanism_summary.csv").iloc[0]
    check("conclusion, weight entropy", 0.99998, weight.normalized_weight_entropy)
    margin = json.loads((ROOT / "results_margin_bound_v5" /
                         "margin_bound_summary.json").read_text(encoding="utf-8"))
    check("conclusion, provable share (%)", 99.91,
          margin["provable_by_bound_rate_mean"] * 100, 5e-3)
    check("conclusion, test rows", 23958, margin["total_rows"], 0)
    grid = pd.read_csv(ROOT / "results_gate_tuning_v5" / "gate_search_results.csv")
    check("conclusion, gate configurations", 108, len(grid), 0)
    check("conclusion, distinct validation values", 6, grid.val_macro_f1.nunique(), 0)
    regression = json.loads((ROOT / "results_diversity_v5" /
                             "diversity_gain_regression.json").read_text(encoding="utf-8"))
    check("conclusion, dose-response slope", 0.0646, regression["slope"], 5e-5)
    check("conclusion, dose-response correlation", 0.749, regression["pearson_r"], 5e-4)
    suite = pd.read_csv(ROOT / "results_diversity_v5" / "diversity_suite_results.csv")
    low = suite[suite.expert_set.isin(("rf_same_view_seeds", "rf_views_k60"))]
    high = suite[~suite.expert_set.isin(("rf_same_view_seeds", "rf_views_k60"))]
    mean_gain = suite.groupby("expert_set").gate_gain.mean()
    disagreement = suite.groupby("expert_set")["mean_pairwise_disagreement"].mean()
    decorrelated = ["rf_views_k20", "hetero_families", "disjoint_views_k60"]
    check("conclusion, low-diversity runs", 6, len(low), 0)
    check("conclusion, low-diversity gains all zero", 0.0, low.gate_gain.abs().max(), 0)
    check("conclusion, decorrelated runs", 9, len(high), 0)
    check("conclusion, smallest decorrelated mean gain", 0.00271, mean_gain[decorrelated].min(), 5e-6)
    check("conclusion, largest decorrelated mean gain", 0.00401, mean_gain[decorrelated].max(), 5e-6)
    positive("conclusion, decorrelated gains all positive", high.gate_gain.min())
    check("6.1 low-diversity disagreement floor (%)", 0.20,
          100 * disagreement[["rf_same_view_seeds", "rf_views_k60"]].min(), 5e-3)
    check("6.1 low-diversity disagreement ceiling (%)", 0.36,
          100 * disagreement[["rf_same_view_seeds", "rf_views_k60"]].max(), 5e-3)
    check("conclusion, strongest disagreement (%)", 6.44,
          100 * disagreement[decorrelated].max(), 5e-3)
    check("conclusion, weakest decorrelated disagreement (%)", 1.76,
          100 * disagreement[decorrelated].min(), 5e-3)


def cross_language() -> None:
    global passed, mismatches
    print()
    print("== 6-7 cross-language ==")
    english, chinese = texts()
    decimals = re.compile(r"\d+\.\d{3,}")
    for label, text in (("English", english), ("Chinese", chinese)):
        body = text.split("## References")[0].split("## 参考文献")[0]
        section = ""
        seen: set[str] = set()
        for line in body.splitlines():
            if line.startswith("#"):
                # sections and their subsections both count ("## 6. Discussion",
                # "### 6.1 ...", "## 7. Conclusion")
                section = line.lstrip("# ").strip()
                continue
            if section[:1] in ("6", "7"):
                seen.update(decimals.findall(line))
        globals()[f"{label.lower()}_decimals"] = seen
        print(f"  {label} sections 6-7: {len(seen)} distinct decimals")
    only_en = sorted(english_decimals - chinese_decimals)
    only_zh = sorted(chinese_decimals - english_decimals)
    if only_en or only_zh:
        mismatches += 1
        print(f"ISSUE sections 6-7 differ between the manuscripts: "
              f"English only {only_en}, Chinese only {only_zh}")
    else:
        passed += 1
        print("OK    sections 6-7 carry the same decimals in both manuscripts")
    # The audit is complete for these two sections: every decimal printed there
    # must have been asserted above, so a new number cannot be added without a
    # source.  This is the check that closes the coverage gap the number-coverage
    # audit kept pointing at.
    unasserted = sorted(token for token in english_decimals if token not in CLAIMED)
    if unasserted:
        mismatches += 1
        print(f"ISSUE sections 6-7 print decimals with no assertion here: {unasserted}")
    else:
        passed += 1
        print(f"OK    all {len(english_decimals)} decimals in sections 6-7 are asserted")


def main() -> int:
    populations()
    discussion()
    decision_matrix()
    limitations()
    conclusion()
    cross_language()
    print()
    print(f"assertions passed {passed} | mismatches {mismatches}")
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
