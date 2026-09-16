"""S5: neural baseline (multi-layer perceptron) on the locked protocol.

Audit gap 6.1. The study so far compared only tree-based learners and an SVM. A
reviewer will ask whether the conclusions survive a neural baseline. A single MLP is
added under the same feature budget and the same seed set; deeper sequence models
(CNN/LSTM) are deliberately out of scope because the object of study is aggregation
rather than representation learning, and adding them would introduce a second
confounded tuning budget.

The architecture and regularisation strength are selected on the validation partition
with seed 42 only, then frozen for all seeds.
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
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.metrics import f1_score
from sklearn.metrics import log_loss
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler

ROOT = Path(__file__).resolve().parents[1]
LABELS = ["Bot", "Brute Force", "DoS/DDoS", "Normal", "Web Attack"]


def load(path: Path):
    frame = pd.read_csv(path, low_memory=False)
    return frame.drop(columns=["target"]).apply(pd.to_numeric).to_numpy(), frame["target"].to_numpy()


def macro_f1(y, pred) -> float:
    return float(f1_score(y, pred, average="macro", labels=LABELS, zero_division=0))


def probability_metrics(y, proba, classes) -> dict:
    """Log loss, Brier and expected calibration error on the aligned class order."""
    order = [list(classes).index(label) for label in LABELS]
    p = proba[:, order]
    labels = np.asarray(LABELS)
    y_idx = np.array([list(LABELS).index(v) for v in y])
    onehot = np.zeros_like(p)
    onehot[np.arange(len(y)), y_idx] = 1.0
    conf = p.max(axis=1)
    correct = (p.argmax(axis=1) == y_idx).astype(float)
    ece = 0.0
    for lo in np.linspace(0.0, 0.9, 10):
        mask = (conf >= lo) & (conf < lo + 0.1)
        if mask.sum() > 0:
            ece += mask.mean() * abs(correct[mask].mean() - conf[mask].mean())
    return {
        "log_loss": float(log_loss(y_idx, p, labels=np.arange(len(LABELS)))),
        "brier_macro": float(((p - onehot) ** 2).sum(axis=1).mean()),
        "ece": float(ece),
    }


def build(hidden, alpha, seed, feature_k, max_iter=40, patience=5, tol=1e-4):
    return Pipeline([
        ("scale", MinMaxScaler()),
        ("select", SelectKBest(chi2, k=feature_k)),
        ("mlp", MLPClassifier(hidden_layer_sizes=hidden, alpha=alpha, batch_size=256,
                              learning_rate_init=1e-3, max_iter=max_iter, early_stopping=True,
                              n_iter_no_change=patience, tol=tol, validation_fraction=0.1,
                              random_state=seed)),
    ])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", default="data_processed_cic_natural_v3b")
    ap.add_argument("--output-dir", default="results_mlp_v5")
    ap.add_argument("--seeds", nargs="+", type=int, default=[42, 2024, 3407])
    ap.add_argument("--feature-k", type=int, default=60)
    ap.add_argument("--tuning-seed", type=int, default=42)
    ap.add_argument("--max-iter", type=int, default=40)
    ap.add_argument("--patience", type=int, default=5)
    ap.add_argument("--tol", type=float, default=1e-4)
    args = ap.parse_args()

    proc = ROOT / args.processed_dir
    out = ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    Xtr, ytr = load(proc / "train.csv")
    Xva, yva = load(proc / "validation.csv")
    Xte, yte = load(proc / "test.csv")

    grid = [((64,), 1e-4), ((128,), 1e-4), ((128, 64), 1e-4),
            ((128,), 1e-3), ((128, 64), 1e-3), ((128,), 1e-2)]
    tuning = []
    for hidden, alpha in grid:
        start = time.perf_counter()
        model = build(hidden, alpha, args.tuning_seed, args.feature_k,
                      args.max_iter, args.patience, args.tol).fit(Xtr, ytr)
        pred = model.predict(Xva)
        tuning.append({
            "hidden_layer_sizes": str(hidden), "alpha": alpha,
            "val_macro_f1": macro_f1(yva, pred),
            "val_accuracy": float((pred == yva).mean()),
            "fit_seconds": time.perf_counter() - start,
        })
        pd.DataFrame(tuning).to_csv(out / "mlp_tuning_results.csv",
                                    index=False, encoding="utf-8-sig")
        print(f"hidden={hidden} alpha={alpha} val_f1={tuning[-1]['val_macro_f1']:.5f}",
              flush=True)

    tuning_df = pd.DataFrame(tuning).sort_values("val_macro_f1", ascending=False)
    best = tuning_df.iloc[0]
    hidden = eval(best["hidden_layer_sizes"])
    alpha = float(best["alpha"])
    config = {
        "selected_hidden_layer_sizes": list(hidden), "selected_alpha": alpha,
        "selection_data": "validation partition, tuning seed only",
        "feature_k": args.feature_k, "tuning_seed": args.tuning_seed,
        "grid": [{"hidden": str(h), "alpha": a} for h, a in grid],
    }
    (out / "selected_mlp_config.json").write_text(
        json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")

    rows = []
    for seed in args.seeds:
        start = time.perf_counter()
        model = build(hidden, alpha, seed, args.feature_k,
                      args.max_iter, args.patience, args.tol).fit(Xtr, ytr)
        train_seconds = time.perf_counter() - start
        start = time.perf_counter()
        proba = model.predict_proba(Xte)
        pred = model.classes_[np.argmax(proba, axis=1)]
        predict_seconds = time.perf_counter() - start
        rows.append({
            "model": "mlp", "seed": seed,
            "macro_f1": macro_f1(yte, pred),
            "accuracy": float((pred == yte).mean()),
            "train_seconds": train_seconds, "predict_seconds": predict_seconds,
            **probability_metrics(yte, proba, model.classes_),
        })
        pd.DataFrame({
            "row_id": np.arange(len(yte)), "true_label": yte, "predicted_label": pred,
            **{f"prob_{c}": proba[:, i] for i, c in enumerate(model.classes_)},
        }).to_csv(out / f"predictions_seed{seed}.csv", index=False, encoding="utf-8-sig")
        pd.DataFrame(rows).to_csv(out / "metrics_by_seed.csv",
                                  index=False, encoding="utf-8-sig")
        print(f"seed={seed} macro_f1={rows[-1]['macro_f1']:.5f}", flush=True)

    df = pd.DataFrame(rows)
    aggregate = pd.DataFrame([{
        "model": "mlp",
        "macro_f1_mean": float(df["macro_f1"].mean()),
        "macro_f1_std": float(df["macro_f1"].std(ddof=1)),
        "accuracy_mean": float(df["accuracy"].mean()),
        "accuracy_std": float(df["accuracy"].std(ddof=1)),
        "log_loss_mean": float(df["log_loss"].mean()),
        "brier_macro_mean": float(df["brier_macro"].mean()),
        "ece_mean": float(df["ece"].mean()),
        "train_seconds_mean": float(df["train_seconds"].mean()),
        "predict_seconds_mean": float(df["predict_seconds"].mean()),
    }])
    aggregate.to_csv(out / "metrics_aggregate.csv", index=False, encoding="utf-8-sig")
    print(aggregate.to_string(index=False))


if __name__ == "__main__":
    main()
