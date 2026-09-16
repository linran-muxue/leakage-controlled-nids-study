"""Paired comparison between the neural baseline and RCCF on the locked protocol."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest
from sklearn.metrics import balanced_accuracy_score, f1_score

ROOT = Path(__file__).resolve().parents[1]
LABELS = ["Bot", "Brute Force", "DoS/DDoS", "Normal", "Web Attack"]
SEEDS = [42, 2024, 3407]


def load(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    rename = {}
    if "true_label" in df.columns:
        rename["true_label"] = "y"
    if "predicted_label" in df.columns:
        rename["predicted_label"] = "yp"
    return df.rename(columns=rename)[["row_id", "y", "yp"]]


def main() -> None:
    out = ROOT / "results_mlp_final_v5"
    rows = []
    for seed in SEEDS:
        mlp = load(out / f"predictions_seed{seed}.csv")
        rccf = load(ROOT / "results_rccf_cic_natural_v3b" / f"predictions_seed{seed}.csv")
        merged = mlp.merge(rccf, on="row_id", suffixes=("_mlp", "_rccf"))
        y = merged["y_mlp"].to_numpy()
        pred_mlp = merged["yp_mlp"].to_numpy()
        pred_rccf = merged["yp_rccf"].to_numpy()
        mlp_correct = pred_mlp == y
        rccf_correct = pred_rccf == y
        n10 = int((mlp_correct & ~rccf_correct).sum())
        n01 = int((~mlp_correct & rccf_correct).sum())
        total = n10 + n01
        rows.append({
            "seed": seed,
            "mlp_macro_f1": f1_score(y, pred_mlp, average="macro", labels=LABELS, zero_division=0),
            "rccf_macro_f1": f1_score(y, pred_rccf, average="macro", labels=LABELS, zero_division=0),
            "mlp_balanced_accuracy": balanced_accuracy_score(y, pred_mlp),
            "rccf_balanced_accuracy": balanced_accuracy_score(y, pred_rccf),
            "mlp_right_rccf_wrong": n10,
            "mlp_wrong_rccf_right": n01,
            "discordant": total,
            "mcnemar_p_vs_rccf": binomtest(min(n10, n01), total, 0.5).pvalue if total else 1.0,
        })
    df = pd.DataFrame(rows)
    n10 = int(df["mlp_right_rccf_wrong"].sum())
    n01 = int(df["mlp_wrong_rccf_right"].sum())
    summary = {
        "mlp_macro_f1_mean": float(df["mlp_macro_f1"].mean()),
        "rccf_macro_f1_mean": float(df["rccf_macro_f1"].mean()),
        "mlp_balanced_accuracy_mean": float(df["mlp_balanced_accuracy"].mean()),
        "rccf_balanced_accuracy_mean": float(df["rccf_balanced_accuracy"].mean()),
        "pooled_mlp_right_rccf_wrong": n10,
        "pooled_mlp_wrong_rccf_right": n01,
        "pooled_mcnemar_p": binomtest(min(n10, n01), n10 + n01, 0.5).pvalue,
    }
    df.to_csv(out / "mlp_vs_rccf_paired.csv", index=False, encoding="utf-8-sig")
    (out / "mlp_vs_rccf_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(df.to_string(index=False))
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
