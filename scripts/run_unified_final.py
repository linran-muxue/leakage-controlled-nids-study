"""Run the publication-facing experiments under one locked RF protocol.

The proposed and unweighted comparison models both use the same chi-square
feature set and RF hyperparameters.  All preprocessing is fitted on the
training split only; validation is used only for tree weighting.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.feature_selection import chi2
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

# Permit direct execution from PowerShell, where Python otherwise places only
# the scripts/ directory on sys.path.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiment_components import WeightedRandomForest, compute_metrics
from src.paired_tests import mcnemar_exact
from src.statistical_analysis import bootstrap_metric_ci, paired_permutation_accuracy


def select_idx(x: np.ndarray, y: np.ndarray, k: int) -> np.ndarray:
    scores, _ = chi2(x, y)
    scores = np.nan_to_num(scores, nan=0.0, posinf=np.finfo(float).max)
    # Preserve original feature-column order after ranking.  This makes the
    # matrix passed to tree models deterministic across scripts; the selected
    # set is unchanged, but column order otherwise changes RNG feature draws.
    return np.sort(np.argsort(-scores, kind="stable")[:k])


def load_data(path: Path):
    tr = pd.read_csv(path / "train.csv", low_memory=False)
    va = pd.read_csv(path / "validation.csv", low_memory=False) if (path / "validation.csv").exists() else None
    te = pd.read_csv(path / "test.csv", low_memory=False)
    names = [c for c in tr.columns if c != "target"]
    scaler = MinMaxScaler()
    x = scaler.fit_transform(tr[names].apply(pd.to_numeric, errors="raise"))
    xv = scaler.transform(va[names].apply(pd.to_numeric, errors="raise")) if va is not None else None
    xt = scaler.transform(te[names].apply(pd.to_numeric, errors="raise"))
    return x, tr.target.to_numpy(), xv, None if va is None else va.target.to_numpy(), xt, te.target.to_numpy(), names, scaler


def report(output: Path, prefix: str, y_true: np.ndarray, pred: np.ndarray, labels):
    pd.DataFrame({"y_true": y_true, "y_pred": pred}).to_csv(output / f"predictions_{prefix}.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(classification_report(y_true, pred, labels=labels, output_dict=True, zero_division=0)).T.to_csv(output / f"classification_report_{prefix}.csv", encoding="utf-8-sig")
    pd.DataFrame(confusion_matrix(y_true, pred, labels=labels), index=labels, columns=labels).to_csv(output / f"confusion_matrix_{prefix}.csv", encoding="utf-8-sig")


def build_model_specs(n_estimators: int, min_samples_leaf: int, seed: int, selected_count: int, total_features: int):
    return [
        ("decision_tree_chi2", DecisionTreeClassifier(max_depth=10, class_weight="balanced", random_state=seed), "chi2"),
        ("svm_all", SVC(C=100, kernel="rbf", gamma="scale", class_weight="balanced"), "all"),
        ("extra_trees_chi2", ExtraTreesClassifier(n_estimators=n_estimators, class_weight="balanced", n_jobs=-1, random_state=seed, min_samples_leaf=min_samples_leaf), "chi2"),
        ("random_forest_all", RandomForestClassifier(n_estimators=n_estimators, class_weight="balanced_subsample", n_jobs=-1, random_state=seed, min_samples_leaf=min_samples_leaf), "all"),
        ("random_forest_chi2", RandomForestClassifier(n_estimators=n_estimators, class_weight="balanced_subsample", n_jobs=-1, random_state=seed, min_samples_leaf=min_samples_leaf), "chi2"),
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--chi2-k", type=int, default=60)
    ap.add_argument("--n-estimators", type=int, default=100)
    ap.add_argument("--min-samples-leaf", type=int, default=2)
    ap.add_argument("--seeds", type=int, nargs="+", default=[42, 2024, 3407])
    args = ap.parse_args(); args.output_dir.mkdir(parents=True, exist_ok=True)
    x, y, xv, yv, xt, yt, names, scaler = load_data(args.processed_dir)
    idx = select_idx(x, y, args.chi2_k)
    selected = [names[i] for i in idx]
    labels = sorted(np.unique(np.concatenate([y, yt])))
    np.save(args.output_dir / "selected_feature_indices.npy", idx)
    (args.output_dir / "final_config.json").write_text(json.dumps({"chi2_k": args.chi2_k, "n_estimators": args.n_estimators, "min_samples_leaf": args.min_samples_leaf, "seeds": args.seeds, "selected_features": selected}, ensure_ascii=False, indent=2), encoding="utf-8")

    pred_dir = args.output_dir / "predictions"; pred_dir.mkdir(exist_ok=True)
    rows = []
    model_names = ["decision_tree_chi2", "svm_all", "extra_trees_chi2", "random_forest_all", "random_forest_chi2", "weighted_rf_chi2"]
    for seed in args.seeds:
        models = build_model_specs(args.n_estimators, args.min_samples_leaf, seed, len(idx), x.shape[1])
        for name, model, feature_mode in models:
            cols = np.arange(x.shape[1]) if feature_mode == "all" else idx
            start = time.perf_counter(); model.fit(x[:, cols], y); train_s = time.perf_counter() - start
            start = time.perf_counter(); pred = model.predict(xt[:, cols]); pred_s = time.perf_counter() - start
            rows.append({"model": name, "seed": seed, **compute_metrics(yt, pred), "train_seconds": train_s, "predict_seconds": pred_s, "feature_count": len(cols), "test_samples": len(yt)})
            report(args.output_dir, f"{name}_seed{seed}", yt, pred, labels)
        weighted = WeightedRandomForest(n_estimators=args.n_estimators, random_state=seed, min_samples_leaf=args.min_samples_leaf, weight_metric="balanced_accuracy")
        start = time.perf_counter(); weighted.fit(x[:, idx], y, xv[:, idx], yv); train_s = time.perf_counter() - start
        start = time.perf_counter(); pred = weighted.predict(xt[:, idx]); pred_s = time.perf_counter() - start
        rows.append({"model": "weighted_rf_chi2", "seed": seed, **compute_metrics(yt, pred), "train_seconds": train_s, "predict_seconds": pred_s, "feature_count": len(idx), "test_samples": len(yt)})
        report(args.output_dir, f"weighted_rf_chi2_seed{seed}", yt, pred, labels)
        pd.DataFrame({"tree_score": weighted.tree_scores_, "tree_weight": weighted.tree_weights_}).to_csv(args.output_dir / f"tree_weights_seed{seed}.csv", index=False, encoding="utf-8-sig")

    metrics = pd.DataFrame(rows); metrics.to_csv(args.output_dir / "metrics_3seeds.csv", index=False, encoding="utf-8-sig")
    metrics.groupby("model")[["accuracy", "macro_precision", "macro_recall", "macro_f1", "train_seconds", "predict_seconds"]].agg(["mean", "std"]).reset_index().to_csv(args.output_dir / "metrics_aggregate.csv", index=False, encoding="utf-8-sig")

    ci_rows = []
    for model in model_names:
        for seed in args.seeds:
            p = pd.read_csv(args.output_dir / f"predictions_{model}_seed{seed}.csv")
            alo, a, ahi = bootstrap_metric_ci(p.y_true, p.y_pred, "accuracy", n_bootstrap=3000, seed=seed)
            flo, f, fhi = bootstrap_metric_ci(p.y_true, p.y_pred, "macro_f1", n_bootstrap=3000, seed=seed + 100)
            ci_rows.append({"model": model, "seed": seed, "accuracy": a, "accuracy_ci_low": alo, "accuracy_ci_high": ahi, "macro_f1": f, "macro_f1_ci_low": flo, "macro_f1_ci_high": fhi, "test_samples": len(p)})
    pd.DataFrame(ci_rows).to_csv(args.output_dir / "bootstrap_confidence_intervals.csv", index=False, encoding="utf-8-sig")

    tests = []
    for seed in args.seeds:
        base = pd.read_csv(args.output_dir / f"predictions_random_forest_chi2_seed{seed}.csv")
        for other in ["weighted_rf_chi2", "extra_trees_chi2"]:
            cand = pd.read_csv(args.output_dir / f"predictions_{other}_seed{seed}.csv")
            mc = mcnemar_exact(base.y_true, base.y_pred, cand.y_pred)
            delta, pvalue = paired_permutation_accuracy(base.y_true, base.y_pred, cand.y_pred, n_permutations=20000, seed=seed)
            tests.append({"seed": seed, "comparison": f"{other}_vs_random_forest_chi2", **mc, "accuracy_delta_b_minus_a": delta, "permutation_p_value": pvalue})
    pd.DataFrame(tests).to_csv(args.output_dir / "paired_significance_tests.csv", index=False, encoding="utf-8-sig")

    ablation = []
    for metric in ["balanced_accuracy", "accuracy", "macro_f1"]:
        for seed in args.seeds:
            w = WeightedRandomForest(n_estimators=args.n_estimators, random_state=seed, min_samples_leaf=args.min_samples_leaf, weight_metric=metric)
            w.fit(x[:, idx], y, xv[:, idx], yv); p = w.predict(xt[:, idx])
            ablation.append({"weight_metric": metric, "seed": seed, **compute_metrics(yt, p)})
    pd.DataFrame(ablation).to_csv(args.output_dir / "weight_ablation.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(ablation).groupby("weight_metric")[["accuracy", "macro_precision", "macro_recall", "macro_f1"]].agg(["mean", "std"]).reset_index().to_csv(args.output_dir / "weight_ablation_summary.csv", index=False, encoding="utf-8-sig")

    dep = args.output_dir / "deployment"; dep.mkdir(exist_ok=True)
    deploy_models = {
        "rf_chi2": (RandomForestClassifier(n_estimators=args.n_estimators, class_weight="balanced_subsample", n_jobs=-1, random_state=42, min_samples_leaf=args.min_samples_leaf).fit(x[:, idx], y), x[:, idx], xt[:, idx]),
        "weighted_rf_chi2": (WeightedRandomForest(n_estimators=args.n_estimators, random_state=42, min_samples_leaf=args.min_samples_leaf).fit(x[:, idx], y, xv[:, idx], yv), x[:, idx], xt[:, idx]),
        "extra_trees_chi2": (ExtraTreesClassifier(n_estimators=args.n_estimators, class_weight="balanced", n_jobs=-1, random_state=42, min_samples_leaf=args.min_samples_leaf).fit(x[:, idx], y), x[:, idx], xt[:, idx]),
    }
    dep_rows, rob_rows = [], []; rng = np.random.default_rng(42)
    for name, (model, xtr, xte) in deploy_models.items():
        path = dep / f"{name}.joblib"; joblib.dump(model, path, compress=3); size = path.stat().st_size
        for batch in [1, 32, 128, 512]:
            start = time.perf_counter()
            for i in range(0, len(xte), batch): model.predict(xte[i:i + batch])
            elapsed = time.perf_counter() - start
            dep_rows.append({"model": name, "batch_size": batch, "total_seconds": elapsed, "latency_ms_per_sample": elapsed / len(xte) * 1000, "samples_per_second": len(xte) / elapsed, "model_bytes": size})
        base = model.predict(xte); rob_rows.append({"model": name, "condition": "clean", **compute_metrics(yt, base)})
        scale = np.maximum(np.std(xtr, axis=0), 1e-6)
        for noise in [0.01, 0.05]:
            vals = [compute_metrics(yt, model.predict(np.clip(xte + rng.normal(0, noise * scale, xte.shape), 0, 1))) for _ in range(10)]
            rob_rows.append({"model": name, "condition": f"gaussian_noise_{int(noise * 100)}pct_mean", **{k: float(np.mean([v[k] for v in vals])) for k in ["accuracy", "macro_precision", "macro_recall", "macro_f1"]}})
        for mask in [0.01, 0.05]:
            vals = []
            for _ in range(10):
                z = xte.copy(); cols = rng.choice(z.shape[1], max(1, int(z.shape[1] * mask)), replace=False); z[:, cols] = 0; vals.append(compute_metrics(yt, model.predict(z)))
            rob_rows.append({"model": name, "condition": f"feature_mask_{int(mask * 100)}pct_mean", **{k: float(np.mean([v[k] for v in vals])) for k in ["accuracy", "macro_precision", "macro_recall", "macro_f1"]}})
    pd.DataFrame(dep_rows).to_csv(dep / "deployment_benchmark.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(rob_rows).to_csv(dep / "robustness_metrics.csv", index=False, encoding="utf-8-sig")
    print(metrics.to_string(index=False))


if __name__ == "__main__":
    main()
