"""Open-set CFRG experiment using known/unknown CSV artifacts.

The production invocation accepts a directory containing ``known.csv`` and
``unknown.csv`` with a numeric feature matrix, ``target``, and ``raw_label``.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import chi2
from sklearn.metrics import average_precision_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.cfrg_forest import CFRGForest
from src.selective_prediction import fit_rejection_threshold, apply_rejection
from src.data_pipeline import map_attack_label
from src.probability_calibration import TemperatureScaler
from src.conformal_rejection import MondrianConformalRejector

KNOWN = {"Normal", "DoS/DDoS", "Brute Force", "Web Attack", "Bot"}


def _load(raw_dir):
    if not (Path(raw_dir) / "known.csv").exists():
        return _collect_cic(raw_dir)
    known = pd.read_csv(Path(raw_dir) / "known.csv")
    unknown = pd.read_csv(Path(raw_dir) / "unknown.csv")
    excluded = {"target", "raw_label", "source_file"}
    features = [c for c in known.columns if c not in excluded and c in unknown.columns]
    return known, unknown, features


def _collect_cic(raw_dir, per_group=2000):
    known_parts, unknown_parts = [], []
    unknown_raw = {"PortScan", "Infiltration", "Heartbleed"}
    for path in sorted(Path(raw_dir).rglob("*.csv")):
        for chunk in pd.read_csv(path, chunksize=100000, low_memory=False, encoding_errors="replace"):
            chunk.columns = [str(c).strip() for c in chunk.columns]
            label_col = next(c for c in chunk.columns if c.lower() == "label")
            raw = chunk[label_col].astype(str).str.strip()
            mapped = raw.map(lambda v: map_attack_label(v, include_other=False))
            features = [c for c in chunk.columns if c not in {label_col, "Flow ID", "Timestamp"}]
            values = chunk[features].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
            good = values.notna().all(axis=1)
            frame = values.loc[good].copy(); frame["target"] = mapped.loc[good].to_numpy(); frame["raw_label"] = raw.loc[good].to_numpy()
            known_parts.append(frame[frame["target"].isin(KNOWN)])
            unknown_parts.append(frame[frame["raw_label"].isin(unknown_raw)].assign(target="unknown"))
    known = pd.concat(known_parts, ignore_index=True)
    unknown = pd.concat(unknown_parts, ignore_index=True)
    known = pd.concat([g.sample(min(len(g), per_group), random_state=0) for _, g in known.groupby("target")], ignore_index=True)
    unknown = pd.concat([g.sample(min(len(g), per_group), random_state=0) for _, g in unknown.groupby("raw_label")], ignore_index=True)
    return known, unknown, [c for c in known.columns if c not in {"target", "raw_label", "source_file"}]


def run_open_set(raw_dir, output_dir, per_group=2000, seeds=(42, 2024, 3407), n_estimators=100, chi2_k=60):
    raw_dir, output_dir = Path(raw_dir), Path(output_dir); output_dir.mkdir(parents=True, exist_ok=True)
    known, unknown, features = _load(raw_dir)
    known = known.sample(min(len(known), int(per_group) * max(1, known.target.nunique())), random_state=0).reset_index(drop=True)
    unknown = unknown.sample(min(len(unknown), int(per_group) * max(1, unknown.raw_label.nunique())), random_state=0).reset_index(drop=True)
    X_known, X_unknown = known[features].to_numpy(float), unknown[features].to_numpy(float); y = known.target.to_numpy()
    rows = []
    for seed in [int(s) for s in seeds]:
        out = output_dir / f"seed_{seed}"; out.mkdir(parents=True, exist_ok=True)
        tr_idx, rest_idx = train_test_split(np.arange(len(y)), test_size=.4, random_state=seed, stratify=y)
        cal_idx, eval_idx = train_test_split(rest_idx, test_size=.5, random_state=seed, stratify=y[rest_idx])
        scaler = MinMaxScaler().fit(X_known[tr_idx]); Xtr, Xcal, Xeval, Xu = scaler.transform(X_known[tr_idx]), scaler.transform(X_known[cal_idx]), scaler.transform(X_known[eval_idx]), scaler.transform(X_unknown)
        score, _ = chi2(Xtr, y[tr_idx]); idx = np.argsort(-np.nan_to_num(score, nan=0.0))[: min(int(chi2_k), Xtr.shape[1])]
        models = {"equal_rf": RandomForestClassifier(n_estimators=n_estimators, min_samples_leaf=2, class_weight="balanced_subsample", n_jobs=-1, random_state=seed), "cfrg_forest": CFRGForest(n_estimators=n_estimators, min_samples_leaf=2, class_weight="balanced_subsample", n_jobs=-1, random_state=seed, cost_beta=0.0, cost_min=1.0, cost_max=1.0)}
        for name, model in models.items():
            model.fit(Xtr[:, idx], y[tr_idx]); p_calibration = model.predict_proba(Xcal[:, idx]); p_eval = model.predict_proba(Xeval[:, idx]); p_unknown = model.predict_proba(Xu[:, idx]); classes = model.classes_
            variants = [(name, p_eval, p_unknown)]
            calibrator = TemperatureScaler().fit(p_calibration, y[cal_idx]); variants.append((f"{name}_temperature_scaled", calibrator.transform(p_eval), calibrator.transform(p_unknown)))
            for variant_name, p_known, p_unknown_variant in variants:
                threshold = fit_rejection_threshold(calibrator.transform(p_calibration) if "temperature_scaled" in variant_name else p_calibration, .95); pred_known = apply_rejection(p_known, classes, threshold); pred_unknown = apply_rejection(p_unknown_variant, classes, threshold)
                scores = np.concatenate([1.0 - p_known.max(axis=1), 1.0 - p_unknown_variant.max(axis=1)]); truth = np.concatenate([np.zeros(len(p_known), dtype=int), np.ones(len(p_unknown_variant), dtype=int)])
                rows.append({"model": variant_name, "seed": seed, "threshold": threshold, "known_macro_f1": float(f1_score(y[eval_idx], pred_known, labels=classes, average="macro", zero_division=0)), "unknown_recall": float(np.mean(pred_unknown == "unknown")), "known_false_rejection_rate": float(np.mean(pred_known == "unknown")), "auroc": float(roc_auc_score(truth, scores)), "aupr": float(average_precision_score(truth, scores)), "known_evaluation_samples": len(p_known), "unknown_samples": len(p_unknown_variant)})
                pd.DataFrame({"raw_label": unknown.get("raw_label", pd.Series(["unknown"] * len(unknown))), "max_known_probability": p_unknown_variant.max(axis=1), "predicted_label": pred_unknown}).to_csv(out / f"unknown_predictions_{variant_name}.csv", index=False, encoding="utf-8-sig")
            conformal = MondrianConformalRejector(alpha=0.1).fit(calibrator.transform(p_calibration), y[cal_idx], classes)
            p_eval_cal = calibrator.transform(p_eval)
            p_unknown_cal = calibrator.transform(p_unknown)
            pred_eval_conf = conformal.predict(p_eval_cal)
            pred_unknown_conf = conformal.predict(p_unknown_cal)
            # Conformal ranking metrics must use a conformal anomaly score,
            # rather than reusing the max-probability score from the previous
            # threshold branch.  A low maximum conformal p-value indicates
            # that the sample is atypical for every known class.
            eval_pvalues = conformal.p_values(p_eval_cal)
            unknown_pvalues = conformal.p_values(p_unknown_cal)
            conformal_scores = np.concatenate([
                1.0 - eval_pvalues.max(axis=1),
                1.0 - unknown_pvalues.max(axis=1),
            ])
            conformal_truth = np.concatenate([
                np.zeros(len(eval_pvalues), dtype=int),
                np.ones(len(unknown_pvalues), dtype=int),
            ])
            rows.append({"model": f"{name}_conformal", "seed": seed, "threshold": 0.1, "known_macro_f1": float(f1_score(y[eval_idx], pred_eval_conf, labels=classes, average="macro", zero_division=0)), "unknown_recall": float(np.mean(pred_unknown_conf == "unknown")), "known_false_rejection_rate": float(np.mean(pred_eval_conf == "unknown")), "auroc": float(roc_auc_score(conformal_truth, conformal_scores)), "aupr": float(average_precision_score(conformal_truth, conformal_scores)), "known_evaluation_samples": len(p_eval), "unknown_samples": len(p_unknown)})
        seed_rows = [r for r in rows if r["seed"] == seed]
        pd.DataFrame(seed_rows).to_csv(out / "open_set_metrics.csv", index=False, encoding="utf-8-sig")
        (out / "protocol.json").write_text(json.dumps({"known_labels": sorted(map(str, np.unique(y))), "unknown_rows_used_for_threshold": False, "threshold_fit": "known_calibration_confidence_only", "temperature_fit_on": "known_calibration_only", "known_evaluation_split": "held_out_known_rows", "seed": seed, "n_estimators": n_estimators, "chi2_k": chi2_k}, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.DataFrame(rows).to_csv(output_dir / "open_set_metrics.csv", index=False, encoding="utf-8-sig")
    return pd.DataFrame(rows)


def main():
    p = argparse.ArgumentParser(); p.add_argument("--raw-dir", type=Path, required=True); p.add_argument("--output-dir", type=Path, required=True); p.add_argument("--per-group", type=int, default=2000); p.add_argument("--n-estimators", type=int, default=100); p.add_argument("--chi2-k", type=int, default=60); p.add_argument("--seeds", type=int, nargs="+", default=[42, 2024, 3407]); args = p.parse_args(); run_open_set(args.raw_dir, args.output_dir, args.per_group, args.seeds, args.n_estimators, args.chi2_k)


if __name__ == "__main__": main()
