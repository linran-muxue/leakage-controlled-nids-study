"""Recompute every headline number in the manuscript from its source file."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]

checks: list[tuple[str, float, float, float]] = []  # label, claimed, recomputed, tolerance


def add(label: str, claimed: float, recomputed: float, tol: float = 5e-6) -> None:
    checks.append((label, claimed, float(recomputed), tol))


def main() -> None:
    # --- CIC natural prior -------------------------------------------------
    nat = pd.read_csv(ROOT / "results_rccf_cic_natural_v3b" / "metrics_aggregate.csv")
    add("RCCF natural Macro-F1", 0.889955, nat["macro_f1_mean"].iloc[0])
    add("RCCF natural accuracy", 0.977920, nat["accuracy_mean"].iloc[0])
    add("RCCF natural log loss", 0.051477, nat["log_loss_mean"].iloc[0])
    add("RCCF natural train seconds", 60.997, nat["train_seconds_mean"].iloc[0], 5e-3)

    base = pd.read_csv(ROOT / "results_cic_natural_baselines_v3b" / "metrics_aggregate_flat.csv")
    for model, claimed in [("equal_rf_chi2", 0.888870), ("equal_rf_all", 0.887960),
                           ("extra_trees_chi2", 0.857713)]:
        add(f"{model} natural Macro-F1", claimed,
            base.loc[base.model == model, "macro_f1_mean"].iloc[0])

    mlp = pd.read_csv(ROOT / "results_mlp_final_v5" / "metrics_aggregate.csv")
    add("MLP Macro-F1", 0.797654, mlp["macro_f1_mean"].iloc[0])
    add("MLP accuracy", 0.97679, mlp["accuracy_mean"].iloc[0], 1e-5)

    # --- balanced control ---------------------------------------------------
    bal = pd.read_csv(ROOT / "results_rccf_cic_balanced_v3b" / "metrics_aggregate.csv")
    add("RCCF balanced Macro-F1", 0.961807, bal["macro_f1_mean"].iloc[0])
    balb = pd.read_csv(ROOT / "results_cic_balanced_baselines_v3b" / "metrics_aggregate_flat.csv")
    add("equal_rf_chi2 balanced Macro-F1", 0.963215,
        balb.loc[balb.model == "equal_rf_chi2", "macro_f1_mean"].iloc[0])
    strong = pd.read_csv(ROOT / "results_cfrg_strong_baselines_v2_verified" / "summary.csv", header=[0, 1])
    strong.columns = ["_".join(str(c) for c in col if "Unnamed" not in str(c)).strip("_") for col in strong.columns]
    add("XGBoost balanced Macro-F1", 0.963241,
        strong.loc[strong["model"] == "xgboost", "macro_f1_mean"].iloc[0])
    add("XGBoost balanced log loss", 0.103753,
        strong.loc[strong["model"] == "xgboost", "log_loss_mean"].iloc[0])

    # --- equivalence --------------------------------------------------------
    eq = json.loads((ROOT / "results_equivalence_v5" / "equivalence_summary.json").read_text("utf-8"))
    pooled = eq["pooled"]
    add("pooled mean delta", 0.001085, pooled["mean_delta"])
    add("pooled 90% low", -0.002898, pooled["pooled_ci_low"], 1e-5)
    add("pooled 90% high", 0.005501, pooled["pooled_ci_high"], 1e-5)
    add("TOST equivalent at 0.01 (1=yes)", 1.0, float(pooled["tost_equivalent_at_0.01"]), 0)
    add("TOST equivalent at 0.005 (1=yes)", 0.0, float(pooled["tost_equivalent_at_0.005"]), 0)

    # --- margin bound -------------------------------------------------------
    mb = json.loads((ROOT / "results_margin_bound_v5" / "margin_bound_summary.json").read_text("utf-8"))
    add("provable by bound rate (%)", 99.91, mb["provable_by_bound_rate_mean"] * 100, 5e-3)
    add("provable by actual rate (%)", 99.996, mb["provable_by_actual_rate_mean"] * 100, 5e-3)
    add("rows with changed labels", 0.0, float(mb["empirical_changed_rows"]), 0)
    add("total test rows", 23958.0, float(mb["total_rows"]), 0)

    # --- gate tuning --------------------------------------------------------
    gate = pd.read_csv(ROOT / "results_gate_tuning_v5" / "gate_search_results.csv")
    add("gate configs", 108.0, float(len(gate)), 0)
    add("distinct validation values", 6.0, float(gate["val_macro_f1"].nunique()), 0)
    add("validation range", 0.00117, gate["val_macro_f1"].max() - gate["val_macro_f1"].min(), 1e-4)
    add("disagreements vs equal weight", 65.0, float(gate["disagreement_vs_equal_weight"].sum()), 0)
    add("row-level denominator", 862488.0, float(len(gate) * 7986), 0)

    # --- diversity ----------------------------------------------------------
    div = pd.read_csv(ROOT / "results_diversity_v5" / "diversity_suite_results.csv")
    fit = json.loads((ROOT / "results_diversity_v5" / "diversity_gain_regression.json").read_text("utf-8"))
    add("diversity observations", 15.0, float(len(div)), 0)
    add("diversity slope", 0.0646, fit["slope"], 1e-4)
    add("diversity pearson r", 0.749, fit["pearson_r"], 1e-3)
    lows = div[div.expert_set.isin(["rf_same_view_seeds", "rf_views_k60"])]
    add("low-diversity runs", 6.0, float(len(lows)), 0)
    add("low-diversity gains all zero", 6.0, float((lows["gate_gain"] == 0).sum()), 0)
    highs = div[~div.expert_set.isin(["rf_same_view_seeds", "rf_views_k60"])]
    add("decorrelated runs", 9.0, float(len(highs)), 0)
    add("decorrelated gains all positive", 9.0, float((highs["gate_gain"] > 0).sum()), 0)

    # --- protocol -----------------------------------------------------------
    ps = pd.read_csv(ROOT / "results_protocol_sensitivity_v4" / "protocol_sensitivity_metrics.csv")
    g = ps[ps.protocol == "global_dedup_before_split"]["macro_f1"].mean()
    q = ps[ps.protocol == "split_first_training_only_dedup"]["macro_f1"].mean()
    add("global-first dedup mean", 0.955682, g, 1e-5)
    add("split-first dedup mean", 0.957089, q, 1e-5)

    nested = pd.read_csv(ROOT / "results_nested_modelwise_v1_5x3" / "outer_modelwise_summary.csv", header=[0, 1])
    nested.columns = ["_".join(str(c) for c in col if "Unnamed" not in str(c)).strip("_") for col in nested.columns]
    add("nested RF Macro-F1", 0.954423,
        nested.loc[nested["model"] == "random_forest", "macro_f1_mean"].iloc[0])
    add("nested XGBoost Macro-F1", 0.962177,
        nested.loc[nested["model"] == "xgboost", "macro_f1_mean"].iloc[0])

    # --- external -----------------------------------------------------------
    nsl = pd.read_csv(ROOT / "results_rccf_nsl_v2_final" / "metrics_aggregate.csv")
    add("NSL Macro-F1", 0.514697, nsl["macro_f1_mean"].iloc[0])
    add("NSL balanced accuracy", 0.492837, nsl["balanced_accuracy_mean"].iloc[0])
    unsw = pd.read_csv(ROOT / "results_rccf_unsw_v2_final" / "metrics_aggregate.csv")
    add("UNSW Macro-F1", 0.493310, unsw["macro_f1_mean"].iloc[0])
    add("UNSW balanced accuracy", 0.566753, unsw["balanced_accuracy_mean"].iloc[0])
    fx = pd.read_csv(ROOT / "results_file_external_generalization_v3b" / "file_external_results.csv")
    add("file-external min Macro-F1", 0.3325, fx["macro_f1_known"].min(), 1e-4)
    add("file-external max Macro-F1", 0.9997, fx["macro_f1_known"].max(), 1e-4)

    # --- robustness and latency --------------------------------------------
    rob = pd.read_csv(ROOT / "results_rccf_evidence_v3b" / "robustness_shared.csv")
    gr = rob.groupby(["model", "condition"])["relative_drop"].mean() * 100
    add("RCCF 1% noise drop", 43.30, gr.loc[("rccf", "gaussian_noise_1pct")], 5e-3)
    add("equal RF 1% noise drop", 42.64, gr.loc[("equal_rf_chi2", "gaussian_noise_1pct")], 5e-3)
    add("ExtraTrees 1% noise drop", 11.57, gr.loc[("extra_trees_chi2", "gaussian_noise_1pct")], 5e-3)
    add("RCCF 5% mask drop", 1.23, gr.loc[("rccf", "feature_mask_5pct")], 5e-3)
    lat = pd.read_csv(ROOT / "results_rccf_evidence_v3b" / "latency_percentiles.csv")
    lp = lat[(lat.model == "rccf") & (lat.n_jobs == 1)]["p50_ms"].mean()
    le = lat[(lat.model == "equal_rf_chi2") & (lat.n_jobs == 1)]["p50_ms"].mean()
    add("RCCF P50 ms", 14.62, lp, 5e-3)
    add("equal RF P50 ms", 2.96, le, 5e-3)

    # --- report -------------------------------------------------------------
    # --- ten-seed extension -------------------------------------------------
    ten = pd.read_csv(ROOT / "results_seeds10_v5" / "table4a_10seeds.csv")
    add("10-seed RCCF Macro-F1", 0.889278,
        ten.loc[ten.model == "rccf", "macro_f1"].iloc[0])
    add("10-seed equal RF chi2 Macro-F1", 0.889734,
        ten.loc[ten.model == "equal_rf_chi2", "macro_f1"].iloc[0])
    add("10-seed equal RF all Macro-F1", 0.887666,
        ten.loc[ten.model == "equal_rf_all", "macro_f1"].iloc[0])
    add("10-seed ExtraTrees Macro-F1", 0.857490,
        ten.loc[ten.model == "extra_trees_chi2", "macro_f1"].iloc[0])

    power = pd.read_csv(ROOT / "results_seeds10_v5" / "power_analysis.csv")
    chi2_row = power[power.comparison == "rccf_minus_equal_rf_chi2"].iloc[0]
    add("10-seed mean difference vs equal RF chi2", -0.000456, chi2_row["mean_difference"], 1e-6)
    add("10-seed seed-level 90% low", -0.001124, chi2_row["ci90_low"], 1e-6)
    add("10-seed seed-level 90% high", 0.000212, chi2_row["ci90_high"], 1e-6)
    add("10-seed TOST equivalent at 0.005 (1=yes)", 1.0,
        float(chi2_row["tost_equivalent_at_0.005"]), 0)
    add("10-seed minimum detectable effect", 0.001146,
        chi2_row["min_detectable_effect_80pct"], 1e-5)
    effects = pd.read_csv(ROOT / "results_seeds10_v5" / "effect_sizes.csv")
    add("10-seed Cohen dz vs equal RF chi2", -0.40,
        float(effects[effects.comparison == "rccf_minus_equal_rf_chi2"]["cohens_dz"].iloc[0]), 5e-3)
    add("10-seed seeds favouring RCCF vs equal RF chi2", 5.0,
        float(effects[effects.comparison == "rccf_minus_equal_rf_chi2"]["seeds_favouring_rccf"].iloc[0]), 0)
    eq10 = json.loads((ROOT / "results_equivalence_10seeds_v5" /
                       "equivalence_summary.json").read_text("utf-8"))["pooled"]
    add("10-seed row-level 90% low", -0.004251, eq10["pooled_ci_low"], 1e-5)
    add("10-seed row-level 90% high", 0.003382, eq10["pooled_ci_high"], 1e-5)

    failures = 0
    print(f"{'check':<42}{'claimed':>14}{'recomputed':>16}{'status':>10}")
    for label, claimed, recomputed, tol in checks:
        ok = abs(claimed - recomputed) <= max(tol, 1e-9)
        failures += 0 if ok else 1
        print(f"{label:<42}{claimed:>14.6f}{recomputed:>16.6f}{'OK' if ok else 'MISMATCH':>10}")
    print()
    print(f"total checks: {len(checks)}, mismatches: {failures}")
    out = ROOT / "results_review_v5"
    out.mkdir(exist_ok=True)
    pd.DataFrame(checks, columns=["check", "claimed", "recomputed", "tolerance"]).to_csv(
        out / "number_traceability.csv", index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main()
