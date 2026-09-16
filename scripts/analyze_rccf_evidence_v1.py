"""Generate auditable RCCF evidence from the locked CIC protocol.

This script deliberately reuses the same held-out rows for every model and
creates perturbation masks once per seed.  It does not tune a model or read
test labels to fit a threshold; test labels are used only for the reported
diagnostic metrics.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.feature_selection import chi2
from sklearn.metrics import f1_score
from sklearn.preprocessing import MinMaxScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.rccf_forest import RCCFForest
from src.rccf_metrics import holm_adjust, paired_sign_flip
from src.data_pipeline import map_attack_label


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _load_cic(processed: Path):
    train = pd.read_csv(processed / "train.csv", low_memory=False)
    valid = pd.read_csv(processed / "validation.csv", low_memory=False)
    test = pd.read_csv(processed / "test.csv", low_memory=False)
    names = [c for c in train.columns if c != "target"]
    scaler = MinMaxScaler().fit(train[names].apply(pd.to_numeric, errors="coerce"))
    return (scaler.transform(train[names]), scaler.transform(valid[names]),
            scaler.transform(test[names]), train.target.to_numpy(),
            valid.target.to_numpy(), test.target.to_numpy(), names)


def _select_chi2(x, y, k):
    scores, _ = chi2(x, y)
    scores = np.nan_to_num(scores, nan=0.0, posinf=np.finfo(float).max)
    return np.argsort(-scores, kind="stable")[: min(k, x.shape[1])]


def _shared_perturbations(x_test, x_train, seed, repeats=10):
    rng = np.random.default_rng(seed)
    scale = np.maximum(np.std(x_train, axis=0), 1e-6)
    out = []
    for _ in range(repeats):
        noise = rng.normal(0.0, 0.01 * scale, size=x_test.shape)
        mask = np.zeros(x_test.shape, dtype=bool)
        nmask = max(1, int(round(x_test.shape[1] * 0.05)))
        for row in range(len(x_test)):
            mask[row, rng.choice(x_test.shape[1], nmask, replace=False)] = True
        out.append((noise, mask))
    return out


def _paired_bootstrap(y, pred_a, pred_b, seed=42, n_resamples=2000):
    rng = np.random.default_rng(seed)
    y = np.asarray(y); a = np.asarray(pred_a); b = np.asarray(pred_b)
    labels = np.unique(y)
    values = np.empty(n_resamples, dtype=float)
    for i in range(n_resamples):
        idx = rng.integers(0, len(y), len(y))
        values[i] = f1_score(y[idx], a[idx], labels=labels, average="macro", zero_division=0) - f1_score(y[idx], b[idx], labels=labels, average="macro", zero_division=0)
    return {"estimate": float(f1_score(y, a, labels=labels, average="macro", zero_division=0) - f1_score(y, b, labels=labels, average="macro", zero_division=0)), "lower": float(np.quantile(values, .025)), "upper": float(np.quantile(values, .975))}


def _set_n_jobs(model, jobs):
    """Set all underlying forest workers before a latency measurement."""
    if hasattr(model, "set_params"):
        model.set_params(n_jobs=jobs)
        return
    model.n_jobs = jobs
    for expert in getattr(model, "experts_", []):
        expert["forest"].set_params(n_jobs=jobs)


def _coverage(raw_dir: Path, output: Path):
    labels = ["Normal", "DoS/DDoS", "Brute Force", "Web Attack", "Bot", "PortScan", "Infiltration", "Heartbleed", "Other"]
    rows = []
    for path in sorted(raw_dir.rglob("*.csv")):
        counts = {label: 0 for label in labels}; total = 0
        for chunk in pd.read_csv(path, chunksize=100_000, low_memory=False, encoding_errors="replace"):
            label_col = next(c for c in chunk.columns if str(c).strip().lower() == "label")
            raw = chunk[label_col].astype(str).str.strip()
            mapped = raw.map(lambda value: map_attack_label(value, include_other=False))
            mapped = mapped.where(mapped.notna(), raw.map(lambda value: value if value in {"PortScan", "Infiltration", "Heartbleed"} else "Other"))
            for label, count in mapped.value_counts().items():
                counts[str(label)] = counts.get(str(label), 0) + int(count)
            total += len(chunk)
        rows.append({"source_file": str(path.relative_to(raw_dir)), "raw_rows": total, **counts})
    frame = pd.DataFrame(rows)
    frame.to_csv(output / "file_label_coverage.csv", index=False, encoding="utf-8-sig")
    frame.set_index("source_file")[labels].to_csv(output / "file_label_matrix.csv", encoding="utf-8-sig")
    return frame


def run(processed_dir: Path, output_dir: Path, raw_dir: Path | None, seeds=(42, 2024, 3407), k=60, n_estimators=100):
    output_dir.mkdir(parents=True, exist_ok=True)
    xtr, xva, xte, ytr, yva, yte, names = _load_cic(processed_dir)
    model_rows = []
    robustness_rows = []
    latency_rows = []
    bootstrap_rows = []
    sign_rows = []
    for seed in seeds:
        cols = _select_chi2(xtr, ytr, k)
        rccf = RCCFForest(n_estimators=n_estimators, feature_k=k, cv=5, random_state=seed, n_jobs=-1, alpha=.1)
        rccf.fit(xtr, ytr, xva, yva)
        p_r = rccf.predict_proba(xte); pred_r = rccf.classes_[p_r.argmax(axis=1)]
        rf = RandomForestClassifier(n_estimators=n_estimators, min_samples_leaf=2, class_weight="balanced_subsample", random_state=seed, n_jobs=-1).fit(xtr[:, cols], ytr)
        p_f = rf.predict_proba(xte[:, cols]); pred_f = rf.classes_[p_f.argmax(axis=1)]
        et = ExtraTreesClassifier(n_estimators=n_estimators, min_samples_leaf=2, class_weight="balanced", random_state=seed, n_jobs=-1).fit(xtr[:, cols], ytr)
        p_e = et.predict_proba(xte[:, cols]); pred_e = et.classes_[p_e.argmax(axis=1)]
        for name, pred in (("rccf", pred_r), ("equal_rf_chi2", pred_f), ("extra_trees_chi2", pred_e)):
            model_rows.append({"seed": seed, "model": name, "macro_f1": float(f1_score(yte, pred, labels=np.unique(yte), average="macro", zero_division=0)), "correct": int(np.sum(pred == yte))})
        shared = _shared_perturbations(xte, xtr, seed)
        clean = {"rccf": float(f1_score(yte, pred_r, labels=np.unique(yte), average="macro", zero_division=0)), "equal_rf_chi2": float(f1_score(yte, pred_f, labels=np.unique(yte), average="macro", zero_division=0)), "extra_trees_chi2": float(f1_score(yte, pred_e, labels=np.unique(yte), average="macro", zero_division=0))}
        for model_name, model, transform in (("rccf", rccf, lambda z: z), ("equal_rf_chi2", rf, lambda z: z[:, cols]), ("extra_trees_chi2", et, lambda z: z[:, cols])):
            for rep, (noise, mask) in enumerate(shared):
                xpert = np.clip(xte + noise, 0, 1); xmask = xte.copy(); xmask[mask] = 0
                for condition, xvalue in (("gaussian_noise_1pct", xpert), ("feature_mask_5pct", xmask)):
                    pred = model.predict(transform(xvalue))
                    value = float(f1_score(yte, pred, labels=np.unique(yte), average="macro", zero_division=0))
                    robustness_rows.append({"seed": seed, "model": model_name, "rep": rep, "condition": condition, "macro_f1": value, "absolute_drop": clean[model_name] - value, "relative_drop": (clean[model_name] - value) / max(clean[model_name], 1e-12)})
            for jobs in (1, -1):
                _set_n_jobs(model, jobs)
                model.predict(transform(xte[:1]))
                values = []
                for _ in range(40):
                    start = time.perf_counter(); model.predict(transform(xte[:1])); values.append((time.perf_counter() - start) * 1000)
                latency_rows.append({"seed": seed, "model": model_name, "n_jobs": jobs, "batch_size": 1, "p50_ms": float(np.percentile(values, 50)), "p95_ms": float(np.percentile(values, 95)), "p99_ms": float(np.percentile(values, 99)), "mean_ms": float(np.mean(values))})
        boot = _paired_bootstrap(yte, pred_r, pred_f, seed=seed)
        bootstrap_rows.append({"seed": seed, "comparison": "rccf_minus_equal_rf_chi2", **boot})
        sign_rows.append({"seed": seed, "difference": clean["rccf"] - clean["equal_rf_chi2"]})
    model_frame = pd.DataFrame(model_rows); model_frame.to_csv(output_dir / "model_metrics.csv", index=False, encoding="utf-8-sig")
    robust = pd.DataFrame(robustness_rows); robust.to_csv(output_dir / "robustness_shared.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(latency_rows).to_csv(output_dir / "latency_percentiles.csv", index=False, encoding="utf-8-sig")
    boot = pd.DataFrame(bootstrap_rows); boot.to_csv(output_dir / "paired_bootstrap_macro_f1.csv", index=False, encoding="utf-8-sig")
    sign = pd.DataFrame(sign_rows)
    test = paired_sign_flip(sign.difference.to_numpy())
    sign["mean_difference"] = test["estimate"]
    sign["raw_p_value"] = test["p_value"]
    sign["adjusted_p_value"] = holm_adjust(np.array([test["p_value"]]))[0]
    sign.to_csv(output_dir / "macro_f1_paired_tests.csv", index=False, encoding="utf-8-sig")
    if raw_dir is not None and raw_dir.exists(): _coverage(raw_dir, output_dir)
    labels = sorted(map(str, np.unique(np.concatenate([ytr, yva, yte]))))
    class_counts = {
        split: {label: int((values == label).sum()) for label in labels}
        for split, values in (("train", ytr), ("validation", yva), ("test", yte))
    }
    manifest = {
        "dataset": "CIC-IDS2017",
        "protocol": "CIC-IDS2017 locked deduplicated balanced research subset",
        "protocol_name": "deduplicated balanced research subset",
        "rows": int(len(ytr) + len(yva) + len(yte)), "train_rows": int(len(ytr)),
        "validation_rows": int(len(yva)), "test_rows": int(len(yte)),
        "calibration_rows": int(len(yva)), "class_counts": class_counts,
        "feature_count_before_selection": int(xtr.shape[1]),
        "feature_count_after_selection": int(min(k, xtr.shape[1])),
        "deduplication_before_split": True,
        "feature_selection_fit_on": "training partition only",
        "risk_fit_on": "training cross-fitted predictions only",
        "calibration_fit_on": "validation partition only",
        "seeds": list(map(int, seeds)), "feature_k": int(k),
        "n_estimators": int(n_estimators),
        "shared_perturbation_seed_rule": "seed-specific Generator(seed)",
        "test_labels_used_for_fitting": False,
        "processed_hashes": {name: _sha256(processed_dir / f"{name}.csv") for name in ("train", "validation", "test")}
    }
    (output_dir / "evidence_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return model_frame


def main():
    parser = argparse.ArgumentParser()
    # Locked publication protocol; older audit directories are historical.
    parser.add_argument("--processed-dir", type=Path, default=ROOT / "data_processed_cic_natural_v3b")
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "data" / "raw" / "MachineLearningCVE")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results_rccf_evidence_v3b")
    parser.add_argument("--k", type=int, default=60)
    parser.add_argument("--n-estimators", type=int, default=100)
    parser.add_argument("--seeds", type=int, nargs="+", default=[42, 2024, 3407])
    args = parser.parse_args()
    print(run(args.processed_dir, args.output_dir, args.raw_dir, args.seeds, args.k, args.n_estimators).groupby("model").macro_f1.mean().to_string())


if __name__ == "__main__":
    main()
