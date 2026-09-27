"""Content-level audit: check every headline claim against the measured magnitudes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    ten = pd.read_csv(ROOT / "results_seeds10_v5" / "table4a_10seeds.csv").set_index("model")
    mlp = pd.read_csv(ROOT / "results_mlp_final_v5" / "metrics_aggregate.csv")
    power = pd.read_csv(ROOT / "results_seeds10_v5" / "power_analysis.csv")
    nested = pd.read_csv(ROOT / "results_nested_modelwise_v1_5x3" / "outer_modelwise_summary.csv",
                         header=[0, 1])
    nested.columns = ["_".join(str(c) for c in col if "Unnamed" not in str(c)).strip("_")
                      for col in nested.columns]
    ps = pd.read_csv(ROOT / "results_protocol_sensitivity_v4" / "protocol_sensitivity_metrics.csv")

    eff = {
        "aggregation (RCCF - equal RF chi2)":
            abs(float(power[power.comparison == "rccf_minus_equal_rf_chi2"]["mean_difference"].iloc[0])),
        "aggregation (RCCF - full-feature RF)":
            abs(float(power[power.comparison == "rccf_minus_equal_rf_all"]["mean_difference"].iloc[0])),
        "model family (RCCF - ExtraTrees)":
            abs(float(power[power.comparison == "rccf_minus_extra_trees_chi2"]["mean_difference"].iloc[0])),
        "model family (RCCF - MLP)":
            abs(ten.loc["rccf", "macro_f1"] - float(mlp["macro_f1_mean"].iloc[0])),
        "feature view (equal RF all - chi2)":
            abs(ten.loc["equal_rf_all", "macro_f1"] - ten.loc["equal_rf_chi2", "macro_f1"]),
        "class prior (balanced - natural)": abs(0.961807 - ten.loc["rccf", "macro_f1"]),
        "tuning budget (XGBoost - RF)":
            abs(float(nested.loc[nested["model"] == "xgboost", "macro_f1_mean"].iloc[0]) -
                float(nested.loc[nested["model"] == "random_forest", "macro_f1_mean"].iloc[0])),
        "dedup order (max single seed)":
            float((ps[ps.protocol == "split_first_training_only_dedup"]["macro_f1"].values -
                   ps[ps.protocol == "global_dedup_before_split"]["macro_f1"].values).max()),
    }
    print("=== measured effect sizes (absolute Macro-F1) ===")
    for k, v in sorted(eff.items(), key=lambda kv: -kv[1]):
        print(f"  {v:8.5f}  {k}")

    protocol = {k: v for k, v in eff.items()
                if k.startswith(("class prior", "tuning", "dedup", "feature view"))}
    model = {k: v for k, v in eff.items() if k.startswith(("aggregation", "model family"))}
    print()
    print(f"largest protocol effect: {max(protocol.values()):.5f} ({max(protocol, key=protocol.get)})")
    print(f"largest model effect:    {max(model.values()):.5f} ({max(model, key=model.get)})")
    print(f"largest aggregation-only effect: "
          f"{max(v for k, v in model.items() if k.startswith('aggregation')):.5f}")
    ex = max(model.values()) > max(protocol.values())
    print()
    print("claim A: 'protocol effects exceed model effects' -> "
          + ("CONTRADICTED" if ex else "supported"))
    print("  largest model-family difference "
          f"{max(model.values()):.5f} vs largest protocol effect {max(protocol.values()):.5f}")
    agg = max(v for k, v in model.items() if k.startswith("aggregation"))
    print("claim B: 'protocol effects exceed aggregation-rule differences' -> "
          + ("supported" if max(protocol.values()) > agg else "CONTRADICTED"))
    print(f"  smallest protocol effect {min(protocol.values()):.5f} vs aggregation {agg:.5f}")

    # diversity suite protocol vs main protocol
    div = json.loads((ROOT / "results_diversity_v5" / "diversity_gain_regression.json").read_text("utf-8"))
    print()
    print("=== protocol consistency between experiments ===")
    print("  main experiment cross-fitting folds: 5")
    print("  diversity suite cross-fitting folds: 3 (script default)")
    print("  gate-tuning folds explored: 3, 5, 10")
    print(f"  diversity regression points: {div['n_points']}")

    # cost-sensitive caveat
    print()
    print("=== cost-sensitive threshold selection ===")
    print("  thresholds were swept on the test partition itself")
    print("  -> reported normalised expected costs are optimistically biased")


if __name__ == "__main__":
    main()
