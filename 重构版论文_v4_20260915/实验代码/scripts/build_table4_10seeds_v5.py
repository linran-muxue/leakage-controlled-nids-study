"""Build the ten-seed main-results table and verify the Brier formula against the
three-seed value already reported in the manuscript."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "results_seeds10_v5"
LABELS = ["Bot", "Brute Force", "DoS/DDoS", "Normal", "Web Attack"]
SEEDS = [42, 2024, 3407, 7, 13, 101, 202, 303, 404, 505]


def load(seed: int, arm: str) -> pd.DataFrame:
    if arm == "rccf":
        path = RUN / f"predictions_seed{seed}.csv"
    else:
        path = RUN / "predictions" / f"predictions_{arm}_seed{seed}.csv"
    df = pd.read_csv(path)
    rename = {}
    for src, dst in (("true_label", "y"), ("predicted_label", "yp"),
                     ("y_true", "y"), ("y_pred", "yp")):
        if src in df.columns:
            rename[src] = dst
    df = df.rename(columns=rename)
    prob_cols = [c for c in df.columns if c.startswith(("prob_", "proba__"))]
    df = df.rename(columns={c: "p_" + c.split("_", 1)[1].split("__")[-1] for c in prob_cols})
    return df


def brier(df: pd.DataFrame) -> float:
    """Macro (per-class averaged) Brier score, matching the convention used by the
    three-seed pipeline so that the two runs are directly comparable."""
    cols = [f"p_{label}" for label in LABELS]
    p = df[cols].to_numpy()
    y_idx = np.array([LABELS.index(v) for v in df["y"]])
    onehot = np.zeros_like(p)
    onehot[np.arange(len(df)), y_idx] = 1.0
    return float(((p - onehot) ** 2).sum(axis=1).mean() / p.shape[1])


def main() -> None:
    arms = ["rccf", "equal_rf_chi2", "equal_rf_all", "extra_trees_chi2"]
    rows = []
    for arm in arms:
        values = {"macro_f1": [], "accuracy": [], "balanced_accuracy": [], "log_loss": [],
                  "brier": [], "ece": [], "train_seconds": [], "predict_seconds": []}
        for seed in SEEDS:
            df = load(seed, arm)
            values["brier"].append(brier(df))
        metrics = pd.read_csv(RUN / "metrics_by_seed.csv")
        sub = metrics[metrics.model == arm]
        rows.append({
            "model": arm,
            "accuracy": sub["accuracy"].mean(),
            "balanced_accuracy": sub["balanced_accuracy"].mean(),
            "macro_f1": sub["macro_f1"].mean(),
            "log_loss": sub["log_loss"].mean(),
            "brier": float(np.mean(values["brier"])),
            "ece": sub["ece"].mean(),
            "train_seconds": sub["train_seconds"].mean(),
            "predict_seconds": sub["predict_seconds"].mean(),
        })
    table = pd.DataFrame(rows)
    table.to_csv(RUN / "table4a_10seeds.csv", index=False, encoding="utf-8-sig")
    print(table.round(6).to_string(index=False))

    # sanity check: seed 42 only, compare with the three-seed manuscript values
    print()
    print("seed-42 only (compare with the three-seed published numbers):")
    for arm in ["rccf", "equal_rf_chi2"]:
        print(f"  {arm}: brier={brier(load(42, arm)):.6f}")

    pretty = {"rccf": "RCCF", "equal_rf_chi2": "Equal RF (chi-square, k = 60)",
              "equal_rf_all": "Equal RF (full features)",
              "extra_trees_chi2": "ExtraTrees (chi-square)"}
    lines = ["| Model | Accuracy | Balanced accuracy | Macro-F1 | Log Loss | Brier | ECE | Train (s) | Predict (s) |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for _, r in table.iterrows():
        lines.append(f"| {pretty[r['model']]} | {r['accuracy']:.5f} | {r['balanced_accuracy']:.5f} | "
                     f"**{r['macro_f1']:.6f}** | {r['log_loss']:.5f} | {r['brier']:.6f} | "
                     f"{r['ece']:.6f} | {r['train_seconds']:.3f} | {r['predict_seconds']:.4f} |")
    (RUN / "table4a_10seeds.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print()
    print("\n".join(lines))


if __name__ == "__main__":
    main()
