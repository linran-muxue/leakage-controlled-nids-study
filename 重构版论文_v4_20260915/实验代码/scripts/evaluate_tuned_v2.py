from pathlib import Path
import argparse
import json
import sys
import time

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.feature_selection import chi2
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.experiment_components import compute_metrics


def select_idx(X, y, k):
    scores, _ = chi2(np.asarray(X, dtype=float), np.asarray(y))
    return np.argsort(-np.nan_to_num(scores, nan=0.0, posinf=np.finfo(float).max))[:k]


def build_model(family, config, seed):
    if family == "decision_tree":
        depth = config.get("max_depth")
        return DecisionTreeClassifier(max_depth=None if depth is None else int(depth), class_weight="balanced", random_state=seed)
    if family == "svm":
        return SVC(C=float(config["C"]), kernel="rbf", gamma="scale", class_weight="balanced")
    if family == "random_forest":
        return RandomForestClassifier(n_estimators=int(config["n_estimators"]), n_jobs=-1, class_weight="balanced_subsample", random_state=seed)
    if family == "extra_trees":
        return ExtraTreesClassifier(n_estimators=int(config["n_estimators"]), n_jobs=-1, class_weight="balanced", random_state=seed)
    raise ValueError(f"unknown model family: {family}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", type=Path, required=True)
    ap.add_argument("--config-file", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--seeds", type=int, nargs="+", default=[42, 2024, 3407])
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    train = pd.read_csv(args.processed_dir / "train.csv", low_memory=False)
    test = pd.read_csv(args.processed_dir / "test.csv", low_memory=False)
    names = [c for c in train.columns if c != "target"]
    X_raw = train[names].apply(pd.to_numeric, errors="raise").to_numpy(dtype=float)
    Xt_raw = test[names].apply(pd.to_numeric, errors="raise").to_numpy(dtype=float)
    y = train["target"].to_numpy()
    yt = test["target"].to_numpy()
    scaler = MinMaxScaler()
    X = scaler.fit_transform(X_raw)
    Xt = scaler.transform(Xt_raw)
    configs = json.loads(args.config_file.read_text(encoding="utf-8-sig"))
    all_rows = []
    labels = sorted(np.unique(np.concatenate([y, yt])))

    for family, config in configs.items():
        mode = config["feature_mode"]
        k = int(config["k"])
        idx = np.arange(X.shape[1]) if mode == "all" else select_idx(X, y, k)
        for seed in args.seeds:
            model = build_model(family, config, seed)
            start = time.perf_counter(); model.fit(X[:, idx], y); train_s = time.perf_counter() - start
            start = time.perf_counter(); pred = model.predict(Xt[:, idx]); predict_s = time.perf_counter() - start
            metrics = compute_metrics(yt, pred)
            row = {"model": "tuned_" + family, "seed": seed, **metrics,
                   "train_seconds": train_s, "predict_seconds": predict_s,
                   "feature_mode": mode, "k": k, "test_samples": len(yt)}
            all_rows.append(row)
            prefix = f"tuned_{family}_seed{seed}"
            pd.DataFrame({"y_true": yt, "y_pred": pred}).to_csv(args.output_dir / f"predictions_{prefix}.csv", index=False, encoding="utf-8-sig")
            pd.DataFrame(classification_report(yt, pred, labels=labels, output_dict=True, zero_division=0)).T.to_csv(args.output_dir / f"classification_report_{prefix}.csv", encoding="utf-8-sig")
            pd.DataFrame(confusion_matrix(yt, pred, labels=labels), index=labels, columns=labels).to_csv(args.output_dir / f"confusion_matrix_{prefix}.csv", encoding="utf-8-sig")

    result = pd.DataFrame(all_rows)
    result.to_csv(args.output_dir / "test_metrics_3seeds.csv", index=False, encoding="utf-8-sig")
    aggregate = result.groupby("model")[
        ["accuracy", "macro_precision", "macro_recall", "macro_f1", "train_seconds", "predict_seconds"]
    ].agg(["mean", "std"]).reset_index()
    aggregate.to_csv(args.output_dir / "test_metrics_aggregate.csv", index=False, encoding="utf-8-sig")
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
