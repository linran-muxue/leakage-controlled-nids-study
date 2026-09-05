"""Generate fair feature-selection, probability, robustness and deployment evidence."""
from __future__ import annotations
import argparse
import json
import sys
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import chi2, f_classif, mutual_info_classif
from sklearn.metrics import brier_score_loss, classification_report, confusion_matrix, log_loss
from sklearn.preprocessing import MinMaxScaler, label_binarize

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.experiment_components import compute_metrics
from src.additional_metrics import calibration_errors, relative_metric_drop


def select_indices(method, x, y, k):
    if method == "all":
        return np.arange(x.shape[1], dtype=int)
    if method == "chi2":
        scores, _ = chi2(x, y)
    elif method == "anova":
        scores, _ = f_classif(x, y)
    else:
        scores = mutual_info_classif(x, y, random_state=0)
    scores = np.nan_to_num(np.asarray(scores, dtype=float), nan=0.0, posinf=np.finfo(float).max, neginf=0.0)
    ranked = np.argsort(-scores, kind="stable")[:min(k, x.shape[1])]
    return np.sort(ranked)

def build_selector(method, k):
    """Backward-compatible selector factory used by unit tests and callers."""
    if method == "all":
        return None
    from sklearn.feature_selection import SelectKBest
    score = chi2 if method == "chi2" else f_classif if method == "anova" else mutual_info_classif
    return SelectKBest(score_func=score, k=k)


def percentile_latency(values):
    values = np.asarray(values, dtype=float)
    return {"count": int(len(values)), "p50_ms": float(np.percentile(values, 50)), "p95_ms": float(np.percentile(values, 95)), "p99_ms": float(np.percentile(values, 99)), "mean_ms": float(values.mean())}


def make_shared_perturbations(x_test, scale_reference=None, seed=20260904, repeats=10):
    """Create reproducible full-dimensional perturbations.

    Noise scale is estimated from the training reference when supplied, so the
    robustness protocol does not use test-set distribution statistics.
    """
    x_test = np.asarray(x_test, dtype=float)
    scale_reference = x_test if scale_reference is None else np.asarray(scale_reference, dtype=float)
    rng = np.random.default_rng(seed)
    scale = np.maximum(np.std(scale_reference, axis=0), 1e-6)
    perturbations = []
    for _ in range(repeats):
        noise = rng.normal(0, 0.01 * scale, x_test.shape)
        mask = np.zeros(x_test.shape, dtype=bool)
        for row in range(x_test.shape[0]):
            cols = rng.choice(x_test.shape[1], max(1, int(x_test.shape[1] * 0.05)), replace=False)
            mask[row, cols] = True
        perturbations.append((noise, mask))
    return perturbations


def load_cic(path):
    tr = pd.read_csv(path / "train.csv", low_memory=False)
    va = pd.read_csv(path / "validation.csv", low_memory=False)
    te = pd.read_csv(path / "test.csv", low_memory=False)
    names = [c for c in tr.columns if c != "target"]
    scaler = MinMaxScaler()
    x = scaler.fit_transform(tr[names].apply(pd.to_numeric, errors="raise"))
    xv = scaler.transform(va[names].apply(pd.to_numeric, errors="raise"))
    xt = scaler.transform(te[names].apply(pd.to_numeric, errors="raise"))
    return x, xv, xt, tr.target.to_numpy(), va.target.to_numpy(), te.target.to_numpy(), names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", type=Path, default=ROOT / "data_processed_audit_v4")
    ap.add_argument("--output-dir", type=Path, default=ROOT / "results_additional_evidence_v4")
    ap.add_argument("--k", type=int, default=60)
    ap.add_argument("--n-estimators", type=int, default=100)
    ap.add_argument("--min-samples-leaf", type=int, default=2)
    ap.add_argument("--seeds", type=int, nargs="+", default=[42, 2024, 3407])
    args = ap.parse_args(); args.output_dir.mkdir(parents=True, exist_ok=True)
    x, xv, xt, y, yv, yt, names = load_cic(args.processed_dir)
    labels = sorted(np.unique(np.concatenate([y, yt])))
    methods = ["all", "chi2", "mutual_info", "anova"]
    metric_rows = []; probability_rows = []; calibration_rows = []
    predictions = {}
    for seed in args.seeds:
        for method in methods:
            cols = select_indices(method, x, y, args.k)
            xtr, xte = x[:, cols], xt[:, cols]; feature_names = [names[i] for i in cols]
            model = RandomForestClassifier(n_estimators=args.n_estimators, min_samples_leaf=args.min_samples_leaf, class_weight="balanced_subsample", n_jobs=-1, random_state=seed)
            start = time.perf_counter(); model.fit(xtr, y); train_s = time.perf_counter() - start
            start = time.perf_counter(); pred = model.predict(xte); proba = model.predict_proba(xte); pred_s = time.perf_counter() - start
            cal = calibration_errors(yt, proba, n_bins=10, class_labels=model.classes_)
            metric_rows.append({"method": method, "seed": seed, "feature_count": len(cols), **compute_metrics(yt, pred), "log_loss": float(log_loss(yt, proba, labels=model.classes_)), "brier_macro": float(np.mean([brier_score_loss((yt == c).astype(int), proba[:, i]) for i, c in enumerate(model.classes_)])), "ece": cal["ece"], "mce": cal["mce"], "train_seconds": train_s, "predict_seconds": pred_s})
            pred_frame = pd.DataFrame({"y_true": yt, "y_pred": pred})
            for i, c in enumerate(model.classes_): pred_frame[f"proba_{c}"] = proba[:, i]
            pred_frame.to_csv(args.output_dir / f"predictions_{method}_seed{seed}.csv", index=False, encoding="utf-8-sig")
            pd.DataFrame(classification_report(yt, pred, labels=labels, output_dict=True, zero_division=0)).T.to_csv(args.output_dir / f"classification_report_{method}_seed{seed}.csv", encoding="utf-8-sig")
            pd.DataFrame(confusion_matrix(yt, pred, labels=labels), index=labels, columns=labels).to_csv(args.output_dir / f"confusion_matrix_{method}_seed{seed}.csv", encoding="utf-8-sig")
            predictions[(method, seed)] = (model, xte, proba, pred, feature_names)
            y_bin = label_binarize(yt, classes=model.classes_)
            for i, c in enumerate(model.classes_):
                prob_true, prob_pred = calibration_curve(y_bin[:, i], proba[:, i], n_bins=10, strategy="uniform")
                calibration_rows.extend({"method": method, "seed": seed, "class": c, "bin": j, "prob_true": float(a), "prob_pred": float(b)} for j, (a, b) in enumerate(zip(prob_true, prob_pred)))
    metrics = pd.DataFrame(metric_rows); metrics.to_csv(args.output_dir / "method_comparison_metrics.csv", index=False, encoding="utf-8-sig")
    metrics.groupby("method")[["accuracy", "balanced_accuracy", "macro_precision", "macro_recall", "macro_f1", "log_loss", "brier_macro", "ece", "mce", "train_seconds", "predict_seconds"]].agg(["mean", "std"]).reset_index().to_csv(args.output_dir / "method_comparison_summary.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(calibration_rows).to_csv(args.output_dir / "calibration_curve_points.csv", index=False, encoding="utf-8-sig")

    shared = make_shared_perturbations(xt, scale_reference=x, seed=20260904, repeats=10); robust_rows = []
    for method in methods:
        model, xte, _, _, _ = predictions[(method, args.seeds[0])]
        base = xte.copy(); feature_indices = select_indices(method, x, y, args.k)
        robust_rows.append({"method": method, "condition": "clean", **compute_metrics(yt, model.predict(base))})
        for rep, (noise_full, mask_full) in enumerate(shared):
            noise = noise_full[:, feature_indices]; robust_rows.append({"method": method, "condition": "gaussian_noise_1pct", "rep": rep, **compute_metrics(yt, model.predict(np.clip(base + noise, 0, 1)))})
            masked = base.copy(); masked[mask_full[:, feature_indices]] = 0; robust_rows.append({"method": method, "condition": "feature_mask_5pct", "rep": rep, **compute_metrics(yt, model.predict(masked))})
    robust = pd.DataFrame(robust_rows)
    clean = robust[robust.condition == "clean"].set_index("method")["macro_f1"]
    robust["relative_macro_f1_drop"] = robust.apply(lambda r: 0.0 if r.condition == "clean" else relative_metric_drop(clean.loc[r.method], r.macro_f1), axis=1)
    robust.to_csv(args.output_dir / "robustness_shared_perturbations.csv", index=False, encoding="utf-8-sig")

    latency_rows = []
    for method in ["all", "chi2"]:
        model, xte, _, _, _ = predictions[(method, args.seeds[0])]
        for n_jobs in [1, -1]:
            if hasattr(model, "n_jobs"): model.set_params(n_jobs=n_jobs); model.fit(xte, yt) if False else None
            for batch in [1, 32, 128, 512]:
                for _ in range(3): model.predict(xte[: min(batch, len(xte))])
                values = []
                for _ in range(30):
                    start = time.perf_counter()
                    for i in range(0, len(xte), batch): model.predict(xte[i:i + batch])
                    values.append((time.perf_counter() - start) / len(xte) * 1000)
                latency_rows.append({"method": method, "n_jobs": n_jobs, "batch_size": batch, **percentile_latency(values)})
    pd.DataFrame(latency_rows).to_csv(args.output_dir / "deployment_latency_percentiles.csv", index=False, encoding="utf-8-sig")
    (args.output_dir / "protocol.json").write_text(json.dumps({"methods": methods, "k": args.k, "n_estimators": args.n_estimators, "min_samples_leaf": args.min_samples_leaf, "shared_robustness_seed": 20260904, "robustness_noise_scale": "training_split_feature_std", "latency_repetitions": 30, "latency_warmup": 3, "calibration_bins": 10}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(metrics.groupby("method")[['accuracy','macro_f1','log_loss','brier_macro']].mean().to_string())


if __name__ == "__main__": main()
