"""Bootstrap confidence intervals for UNSW-NB15 probability and classification metrics."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, log_loss

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.additional_metrics import calibration_errors


def score_frame(frame: pd.DataFrame, labels: list[str]) -> dict[str, float]:
    y = frame["y_true"].to_numpy(dtype=str)
    pred = frame["y_pred"].to_numpy(dtype=str)
    p = frame[[f"proba_{label}" for label in labels]].to_numpy(float)
    p = np.clip(p, 1e-15, 1.0); p /= p.sum(axis=1, keepdims=True)
    return {
        "accuracy": float(accuracy_score(y, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "macro_f1": float(f1_score(y, pred, labels=labels, average="macro", zero_division=0)),
        "log_loss": float(log_loss(y, p, labels=labels)),
        "ece": float(calibration_errors(y, p, class_labels=np.asarray(labels))["ece"]),
    }


def fast_scores_arrays(y: np.ndarray, pred: np.ndarray, p: np.ndarray, labels: list[str], indices: np.ndarray | None = None) -> dict[str, float]:
    """Vectorized bootstrap scoring on cached arrays."""
    if indices is not None:
        y, pred, p = y[indices], pred[indices], p[indices]
    p = np.clip(p, 1e-15, 1.0); p /= p.sum(axis=1, keepdims=True)
    label_to_idx = {label: i for i, label in enumerate(labels)}
    yi = np.asarray(pd.Categorical(y, categories=labels).codes, dtype=np.int64)
    pi = np.asarray(pd.Categorical(pred, categories=labels).codes, dtype=np.int64)
    correct = (pi == yi).astype(float)
    recalls = []
    brier = []
    f1s = []
    for j, label in enumerate(labels):
        mask = (yi == j)
        pred_mask = (pi == j)
        tp = float(np.sum(mask & pred_mask)); fp = float(np.sum((~mask) & pred_mask)); fn = float(np.sum(mask & (~pred_mask)))
        recalls.append(tp / (tp + fn) if (tp + fn) else 0.0)
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        f1s.append(2 * precision * recalls[-1] / (precision + recalls[-1]) if (precision + recalls[-1]) else 0.0)
        brier.append(float(np.mean((mask.astype(float) - p[:, j]) ** 2)))
    confidence = p.max(axis=1)
    ece = 0.0
    edges = np.linspace(0.0, 1.0, 11)
    for i in range(10):
        mask = (confidence >= edges[i]) & ((confidence < edges[i + 1]) if i < 9 else (confidence <= edges[i + 1]))
        if mask.any():
            ece += float(mask.mean()) * abs(float(correct[mask].mean()) - float(confidence[mask].mean()))
    return {"accuracy": float(correct.mean()), "balanced_accuracy": float(np.mean(recalls)), "macro_f1": float(np.mean(f1s)), "log_loss": float(-np.mean(np.log(p[np.arange(len(y)), yi]))), "brier_macro": float(np.mean(brier)), "ece": float(ece)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--replicates", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20260904)
    args = ap.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    rows: list[dict[str, object]] = []
    for path in sorted(args.run_dir.glob("predictions_*.csv")):
        model = path.stem.removeprefix("predictions_")
        frame = pd.read_csv(path)
        labels = sorted(frame["y_true"].astype(str).unique().tolist())
        y0 = frame["y_true"].to_numpy(dtype=str)
        pred0 = frame["y_pred"].to_numpy(dtype=str)
        p0 = frame[[f"proba_{label}" for label in labels]].to_numpy(float)
        estimate = fast_scores_arrays(y0, pred0, p0, labels)
        values = {metric: [] for metric in estimate}
        n = len(frame)
        for _ in range(args.replicates):
            scored = fast_scores_arrays(y0, pred0, p0, labels, rng.integers(0, n, size=n))
            for metric, value in scored.items():
                values[metric].append(value)
        for metric, draws in values.items():
            rows.append({"model": model, "metric": metric, "estimate": estimate[metric], "ci95_low": float(np.percentile(draws, 2.5)), "ci95_high": float(np.percentile(draws, 97.5)), "replicates": args.replicates, "seed": args.seed})
    out = pd.DataFrame(rows)
    out.to_csv(args.output, index=False, encoding="utf-8-sig")
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
