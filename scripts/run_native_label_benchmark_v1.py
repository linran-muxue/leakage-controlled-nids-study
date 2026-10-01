"""Native-label benchmark with the same-members equal-fusion control.

``run_seeds10_v5.py`` is tied to the five CIC-IDS2017 classes; the new corpora
have their own label sets, so this runner derives the classes from the data.  It
trains conditional weighting, the unweighted mean of *the same four experts*,
and two single-view equal-weight forests, and writes per-seed predictions for
each arm.
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
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, log_loss
from sklearn.preprocessing import MinMaxScaler

from src.feature_selection import chi2_top_k
from src.rccf_forest import RCCFForest

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path):
    frame = pd.read_csv(path, low_memory=False)
    return (frame.drop(columns=["target"]).apply(pd.to_numeric).to_numpy(float),
            frame["target"].to_numpy())


def metrics(y_true, y_pred, probability, classes, labels) -> dict:
    order = [list(classes).index(label) for label in labels]
    index = np.array([list(labels).index(value) for value in y_true])
    return {
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", labels=labels,
                                   zero_division=0)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "log_loss": float(log_loss(index, probability[:, order],
                                   labels=np.arange(len(labels)))),
    }


def write_predictions(path: Path, y_true, prediction, probability, classes):
    frame = pd.DataFrame({
        "row_id": np.arange(len(y_true)), "true_label": y_true,
        "predicted_label": prediction,
        **{f"prob_{label}": probability[:, i] for i, label in enumerate(classes)},
    })
    frame.to_csv(path, index=False, encoding="utf-8-sig")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--seeds", nargs="+", type=int, default=[42, 2024, 3407])
    ap.add_argument("--n-estimators", type=int, default=100)
    ap.add_argument("--feature-k", type=int, default=60)
    args = ap.parse_args()

    data = ROOT / args.processed_dir
    out = ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    X_train, y_train = load(data / "train.csv")
    X_val, y_val = load(data / "validation.csv")
    X_test, y_test = load(data / "test.csv")
    labels = np.unique(y_train)
    print(f"train {X_train.shape} test {X_test.shape} classes {len(labels)}: "
          f"{list(labels)}", flush=True)
    rows = []
    for seed in args.seeds:
        model = RCCFForest(n_estimators=args.n_estimators, feature_k=args.feature_k,
                           cv=5, random_state=seed)
        start = time.perf_counter()
        model.fit(X_train, y_train, X_val, y_val)
        train_seconds = time.perf_counter() - start
        probability = model.predict_proba(X_test)
        prediction = model.classes_[probability.argmax(axis=1)]
        write_predictions(out / f"predictions_rccf_seed{seed}.csv", y_test, prediction,
                          probability, model.classes_)
        rows.append({"model": "rccf", "seed": seed,
                     "train_seconds": train_seconds,
                     **metrics(y_test, prediction, probability, model.classes_, labels)})

        probabilities = []
        for expert in model.experts_:
            probabilities.append(model._expert_proba(expert, X_test))
        classes = model.classes_
        equal = np.mean(probabilities, axis=0)
        equal_pred = classes[equal.argmax(axis=1)]
        write_predictions(out / f"predictions_equal_fusion_seed{seed}.csv", y_test,
                          equal_pred, equal, classes)
        rows.append({"model": "equal_fusion", "seed": seed, "train_seconds": np.nan,
                     **metrics(y_test, equal_pred, equal, classes, labels)})
        disagreements = int((equal_pred != prediction).sum())

        scaler = MinMaxScaler().fit(X_train)
        X_train_s, X_test_s = scaler.transform(X_train), scaler.transform(X_test)
        selection = chi2_top_k(X_train_s, y_train, args.feature_k)
        views = {
            "equal_rf_chi2": (selection.select(X_train_s), selection.select(X_test_s)),
            "equal_rf_all": (X_train_s, X_test_s),
        }
        for name, (Xa, Xb) in views.items():
            forest = RandomForestClassifier(n_estimators=args.n_estimators,
                                            min_samples_leaf=2, n_jobs=-1,
                                            class_weight="balanced_subsample",
                                            random_state=seed).fit(Xa, y_train)
            probability = forest.predict_proba(Xb)
            prediction = forest.classes_[probability.argmax(axis=1)]
            write_predictions(out / f"predictions_{name}_seed{seed}.csv", y_test,
                              prediction, probability, forest.classes_)
            rows.append({"model": name, "seed": seed, "train_seconds": np.nan,
                         **metrics(y_test, prediction, probability, forest.classes_,
                                   labels)})
        rccf_f1 = next(r["macro_f1"] for r in rows
                       if r["model"] == "rccf" and r["seed"] == seed)
        equal_f1 = next(r["macro_f1"] for r in rows
                        if r["model"] == "equal_fusion" and r["seed"] == seed)
        print(f"seed {seed}: rccf {rccf_f1:.6f} vs same-members equal {equal_f1:.6f} "
              f"(diff {rccf_f1 - equal_f1:+.6f}, {disagreements} labels differ)",
              flush=True)

    frame = pd.DataFrame(rows)
    frame.to_csv(out / "metrics_by_seed.csv", index=False, encoding="utf-8-sig")
    aggregate = frame.groupby("model").agg(
        macro_f1_mean=("macro_f1", "mean"), macro_f1_std=("macro_f1", "std"),
        accuracy_mean=("accuracy", "mean"), balanced_accuracy_mean=("balanced_accuracy", "mean"),
        log_loss_mean=("log_loss", "mean"), train_seconds_mean=("train_seconds", "mean"),
        test_samples_mean=("macro_f1", "size")).reset_index()
    aggregate.to_csv(out / "metrics_aggregate.csv", index=False, encoding="utf-8-sig")
    summary = {
        "population": args.processed_dir, "seeds": [int(seed) for seed in args.seeds],
        "classes": [str(label) for label in labels],
        "test_rows": int(len(y_test)),
        "rccf_mean_macro_f1": float(aggregate.set_index("model").loc["rccf", "macro_f1_mean"]),
        "equal_fusion_mean_macro_f1": float(
            aggregate.set_index("model").loc["equal_fusion", "macro_f1_mean"]),
        "same_members_difference": float(
            aggregate.set_index("model").loc["rccf", "macro_f1_mean"]
            - aggregate.set_index("model").loc["equal_fusion", "macro_f1_mean"]),
    }
    (out / "benchmark_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
