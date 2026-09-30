"""Does a higher-capacity gate restore the gain?  (the causality check)

The main study fits the gate's risk models with logistic regression, and finds
that the gate changes almost nothing.  A reviewer can object that the result is a
property of that weak risk model rather than of conditional weighting itself.
This script holds the four experts, the folds and the seeds fixed and swaps only
the risk model: logistic regression against a gradient-boosted tree ensemble with
far more capacity.  If a high-capacity gate still cannot beat equal voting over
the same four experts, the inertness is a property of the data, not of the
implementation.
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
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

from src.rccf_forest import RCCFForest, DESCRIPTOR_SETS, _descriptor

ROOT = Path(__file__).resolve().parents[1]
SEEDS = [42, 2024, 3407]


def load(path: Path):
    frame = pd.read_csv(path, low_memory=False)
    X = frame.drop(columns=["target"]).apply(pd.to_numeric).to_numpy()
    return X, frame["target"].to_numpy()


def risk_scores(features, target, kind: str, seed: int):
    """Return P(expert wrong | features) for one expert."""
    if np.unique(target).size == 1:
        return np.full(len(target), float(target[0]))
    scaler = StandardScaler().fit(features)
    scaled = scaler.transform(features)
    if kind == "logistic":
        model = LogisticRegression(C=1.0, class_weight="balanced", max_iter=400,
                                   random_state=seed)
    else:
        model = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1,
                                               max_leaf_nodes=31, random_state=seed)
    model.fit(scaled, target)
    return model, scaler, model.predict_proba(scaled)[:, 1]


def score_with(model, scaler, features) -> np.ndarray:
    return model.predict_proba(scaler.transform(features))[:, 1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", default="data_processed_cic_natural_v3b")
    ap.add_argument("--output-dir", default="results_gate_capacity_v1")
    ap.add_argument("--seeds", nargs="+", type=int, default=SEEDS)
    ap.add_argument("--n-estimators", type=int, default=100)
    ap.add_argument("--feature-k", type=int, default=60)
    ap.add_argument("--cv", type=int, default=5)
    ap.add_argument("--variants", nargs="+", default=["logistic", "hgb"],
                    choices=["logistic", "hgb"],
                    help="risk models to compare; the k-sweep runs logistic only")
    args = ap.parse_args()

    data = ROOT / args.processed_dir
    out = ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    X_train, y_train = load(data / "train.csv")
    X_test, y_test = load(data / "test.csv")
    labels = np.unique(y_train)
    y_index = np.searchsorted(labels, y_test)
    model = RCCFForest(n_estimators=args.n_estimators, feature_k=args.feature_k,
                       cv=args.cv, random_state=args.seeds[0])
    descriptor_columns = DESCRIPTOR_SETS["all"]

    rows = []
    for seed in args.seeds:
        started = time.time()
        splitter = StratifiedKFold(args.cv, shuffle=True, random_state=seed)
        oof = np.zeros((len(y_train), len(model.expert_names), len(labels)))
        descriptors = np.zeros((len(y_train), len(model.expert_names), 3))
        for fold, (tr, va) in enumerate(splitter.split(X_train, y_train)):
            for index, name in enumerate(model.expert_names):
                expert = model._fit_expert(name, X_train[tr], y_train[tr],
                                           seed + fold * 97 + index)
                probability = model._expert_proba(expert, X_train[va])
                oof[va, index] = probability
                descriptors[va, index] = _descriptor(probability)
        y_train_index = np.searchsorted(labels, y_train)
        features = np.concatenate(
            [oof.reshape(len(y_train), -1),
             descriptors[:, :, descriptor_columns].reshape(len(y_train), -1)], axis=1)
        targets = np.stack([(oof[:, i].argmax(axis=1) != y_train_index).astype(int)
                            for i in range(len(model.expert_names))], axis=1)

        experts = [model._fit_expert(name, X_train, y_train, seed + i)
                   for i, name in enumerate(model.expert_names)]
        probabilities = [model._expert_proba(expert, X_test) for expert in experts]
        expert_classes = experts[0]["forest"].classes_
        equal = np.mean(probabilities, axis=0)
        equal_pred = expert_classes[equal.argmax(axis=1)]

        row = {"seed": seed,
               "equal_fusion_macro_f1": float(f1_score(y_test, equal_pred, average="macro",
                                                       labels=labels, zero_division=0))}
        for kind in args.variants:
            weights = np.zeros((len(X_test), len(model.expert_names)))
            for index in range(len(model.expert_names)):
                fitted, scaler, _ = risk_scores(features, targets[:, index], kind,
                                                seed + index)
                risk_test = score_with(fitted, scaler,
                                       np.concatenate(
                                           [np.concatenate(probabilities, axis=1),
                                            np.concatenate([_descriptor(p)[:, descriptor_columns]
                                                            for p in probabilities], axis=1)],
                                           axis=1))
                weights[:, index] = np.exp(-np.clip(risk_test, 0.0, 20.0))
            weights /= np.maximum(weights.sum(axis=1, keepdims=True), 1e-12)
            fused = np.sum(np.stack(probabilities, axis=1) * weights[:, :, None], axis=1)
            predicted = expert_classes[fused.argmax(axis=1)]
            row[f"{kind}_macro_f1"] = float(f1_score(y_test, predicted, average="macro",
                                                     labels=labels, zero_division=0))
            row[f"{kind}_changed_labels"] = int((predicted != equal_pred).sum())
            row[f"{kind}_mean_weight_l1"] = float(
                np.abs(weights - 1.0 / len(model.expert_names)).sum(axis=1).mean())
        row["test_rows"] = int(len(y_test))
        row["seconds"] = time.time() - started
        rows.append(row)
        detail = ", ".join(f"{kind} {row[f'{kind}_macro_f1']:.6f} "
                           f"({row[f'{kind}_changed_labels']} labels changed)"
                           for kind in args.variants)
        print(f"seed {seed}: equal {row['equal_fusion_macro_f1']:.6f}, {detail}", flush=True)

    metrics = pd.DataFrame(rows)
    metrics.to_csv(out / "metrics_by_seed.csv", index=False, encoding="utf-8-sig")
    summary = {
        "population": args.processed_dir,
        "seeds": [int(seed) for seed in args.seeds],
        "test_rows": int(len(y_test)),
        "equal_fusion_mean_macro_f1": float(metrics["equal_fusion_macro_f1"].mean()),
        "comparisons": int(metrics["test_rows"].sum()),
    }
    for kind in args.variants:
        summary[f"{kind}_mean_macro_f1"] = float(metrics[f"{kind}_macro_f1"].mean())
        summary[f"{kind}_gain_vs_equal"] = float(
            (metrics[f"{kind}_macro_f1"] - metrics["equal_fusion_macro_f1"]).mean())
        summary[f"{kind}_changed_labels_total"] = int(metrics[f"{kind}_changed_labels"].sum())
    (out / "gate_capacity_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
