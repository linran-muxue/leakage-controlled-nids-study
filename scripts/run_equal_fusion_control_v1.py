"""Run the missing H2 control: equal-weight fusion of the same four experts.

The primary comparison in the paper pits the gated fusion of four feature views
against a *single* equal-weight chi-square forest.  That control answers "does
gating beat the best single member?", not "does gating beat equal voting over the
same members".  This script closes the gap: it rebuilds the identical four
experts (same views, same hyper-parameters, same per-expert seeds as
``src.rccf_forest.RCCFForest``) and evaluates their unweighted mean, per seed,
against the released gated predictions.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, log_loss

from src.rccf_forest import RCCFForest

ROOT = Path(__file__).resolve().parents[1]
SEEDS = [42, 2024, 3407, 7, 13, 101, 202, 303, 404, 505]


def load(path: Path):
    frame = pd.read_csv(path, low_memory=False)
    X = frame.drop(columns=["target"]).apply(pd.to_numeric).to_numpy()
    return X, frame["target"].to_numpy()


def ece(y: np.ndarray, proba: np.ndarray, classes: np.ndarray, labels) -> float:
    order = [list(classes).index(label) for label in labels]
    p = proba[:, order]
    y_idx = np.array([list(labels).index(v) for v in y])
    conf = p.max(axis=1)
    correct = (p.argmax(axis=1) == y_idx).astype(float)
    value = 0.0
    for lo in np.linspace(0.0, 0.9, 10):
        mask = (conf >= lo) & (conf < lo + 0.1)
        if mask.sum() > 0:
            value += mask.mean() * abs(correct[mask].mean() - conf[mask].mean())
    return float(value)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", default="data_processed_cic_natural_v3b")
    ap.add_argument("--output-dir", default="results_equal_fusion_control_v1")
    ap.add_argument("--gated-dir", default="results_seeds10_v5")
    ap.add_argument("--seeds", nargs="+", type=int, default=SEEDS)
    ap.add_argument("--n-estimators", type=int, default=100)
    ap.add_argument("--feature-k", type=int, default=60)
    args = ap.parse_args()

    data = ROOT / args.processed_dir
    out = ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    X_train, y_train = load(data / "train.csv")
    X_test, y_test = load(data / "test.csv")
    gated = pd.read_csv(ROOT / args.gated_dir / "metrics_by_seed.csv").set_index(["model", "seed"])
    labels = sorted(set(y_train))

    rows = []
    for seed in args.seeds:
        model = RCCFForest(n_estimators=args.n_estimators, feature_k=args.feature_k,
                           random_state=seed)
        start = time.time()
        experts = [model._fit_expert(name, X_train, y_train, seed + i)
                   for i, name in enumerate(model.expert_names)]
        probabilities = [model._expert_proba(expert, X_test) for expert in experts]
        classes = experts[0]["forest"].classes_
        fused = np.mean(probabilities, axis=0)
        train_seconds = time.time() - start
        predict_start = time.time()
        predicted = classes[fused.argmax(axis=1)]
        predict_seconds = time.time() - predict_start

        order = [list(classes).index(label) for label in labels]
        y_index = np.array([labels.index(value) for value in y_test])
        row = {
            "model": "equal_fusion", "seed": seed,
            "macro_f1": float(f1_score(y_test, predicted, average="macro", labels=labels,
                                       zero_division=0)),
            "accuracy": float(accuracy_score(y_test, predicted)),
            "balanced_accuracy": float(balanced_accuracy_score(y_test, predicted)),
            "log_loss": float(log_loss(y_index, fused[:, order], labels=np.arange(len(labels)))),
            "ece": ece(y_test, fused, classes, labels),
            "train_seconds": train_seconds, "predict_seconds": predict_seconds,
        }
        frame = pd.DataFrame({
            "row_id": np.arange(len(y_test)), "true_label": y_test, "predicted_label": predicted,
            **{f"prob_{label}": fused[:, index] for index, label in enumerate(classes)},
        })
        frame.to_csv(out / f"predictions_seed{seed}.csv", index=False, encoding="utf-8-sig")

        released = pd.read_csv(ROOT / args.gated_dir / f"predictions_seed{seed}.csv")
        disagreements = int((released["predicted_label"].to_numpy() != predicted).sum())
        row["rows_vs_gated"] = int(len(y_test))
        row["disagreements_vs_gated"] = disagreements
        row["gated_macro_f1"] = float(gated.loc[("rccf", seed), "macro_f1"])
        row["chi2_single_macro_f1"] = float(gated.loc[("equal_rf_chi2", seed), "macro_f1"])
        rows.append(row)
        print(f"seed {seed}: equal-fusion macro-F1 {row['macro_f1']:.6f} vs gated "
              f"{row['gated_macro_f1']:.6f} ({disagreements} rows differ), "
              f"single chi2 {row['chi2_single_macro_f1']:.6f}", flush=True)

    metrics = pd.DataFrame(rows)
    metrics.to_csv(out / "metrics_by_seed.csv", index=False, encoding="utf-8-sig")
    difference = metrics["macro_f1"] - metrics["gated_macro_f1"]
    sd = float(difference.std(ddof=1))
    mean = float(difference.mean())
    half_width = float(1.833 * sd / np.sqrt(len(difference)))  # t(9), 90% two-sided
    summary = {
        "control": "equal-weight fusion of the identical four experts",
        "compared_with": "released gated predictions (results_seeds10_v5)",
        "population": args.processed_dir,
        "n_seeds": int(len(metrics)),
        "test_rows": int(len(y_test)),
        "fusion_mean_macro_f1": float(metrics["macro_f1"].mean()),
        "gated_mean_macro_f1": float(metrics["gated_macro_f1"].mean()),
        "single_view_mean_macro_f1": float(metrics["chi2_single_macro_f1"].mean()),
        "mean_difference_fusion_minus_gated": mean,
        "sd_difference": sd,
        "seed_level_90_interval": [mean - half_width, mean + half_width],
        "total_rows_disagreeing_with_gated": int(metrics["disagreements_vs_gated"].sum()),
        "max_rows_disagreeing_with_gated": int(metrics["disagreements_vs_gated"].max()),
        "seeds_favouring_fusion": int((difference > 0).sum()),
        "seeds_favouring_gated": int((difference < 0).sum()),
    }
    (out / "equal_fusion_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
