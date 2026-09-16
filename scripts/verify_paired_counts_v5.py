"""Recompute paired discordant counts and McNemar p-values from stored predictions.

Written to reconcile the McNemar value quoted in the v3b manuscript with a direct
recomputation from the released per-row predictions.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from scipy.stats import binomtest

ROOT = Path(__file__).resolve().parents[1]
SEEDS = [42, 2024, 3407]


def rccf_predictions(seed: int) -> pd.DataFrame:
    df = pd.read_csv(ROOT / "results_rccf_cic_natural_v3b" / f"predictions_seed{seed}.csv")
    return df.rename(columns={"true_label": "y", "predicted_label": "yp"})[["row_id", "y", "yp"]]


def baseline_predictions(name: str, seed: int) -> pd.DataFrame:
    path = (ROOT / "results_cic_natural_baselines_v3b" / "predictions" /
            f"predictions_{name}_seed{seed}.csv")
    df = pd.read_csv(path).rename(columns={"y_true": "y", "y_pred": "yp"})
    return df[["row_id", "y", "yp"]]


def counts(name: str) -> pd.DataFrame:
    rows = []
    for seed in SEEDS:
        merged = rccf_predictions(seed).merge(
            baseline_predictions(name, seed), on="row_id", suffixes=("_a", "_b"))
        a_correct = merged["y_a"] == merged["yp_a"]
        b_correct = merged["y_b"] == merged["yp_b"]
        n10 = int((a_correct & ~b_correct).sum())
        n01 = int((~a_correct & b_correct).sum())
        total = n10 + n01
        rows.append({
            "baseline": name, "seed": seed, "n_rows": len(merged),
            "a_right_b_wrong": n10, "a_wrong_b_right": n01, "discordant": total,
            "mcnemar_p_seed": binomtest(min(n10, n01), total, 0.5).pvalue if total else 1.0,
        })
    df = pd.DataFrame(rows)
    n10, n01 = int(df["a_right_b_wrong"].sum()), int(df["a_wrong_b_right"].sum())
    df.loc[len(df)] = {
        "baseline": name, "seed": -1, "n_rows": int(df["n_rows"].sum()),
        "a_right_b_wrong": n10, "a_wrong_b_right": n01, "discordant": n10 + n01,
        "mcnemar_p_seed": binomtest(min(n10, n01), n10 + n01, 0.5).pvalue if n10 + n01 else 1.0,
    }
    return df


def main() -> None:
    frames = [counts(name) for name in ["equal_rf_chi2", "equal_rf_all", "extra_trees_chi2"]]
    out = pd.concat(frames, ignore_index=True)
    out["mcnemar_p_holm_within_baseline"] = out["mcnemar_p_seed"]
    target = ROOT / "results_equivalence_v5"
    target.mkdir(parents=True, exist_ok=True)
    out.to_csv(target / "paired_counts_recomputed.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
