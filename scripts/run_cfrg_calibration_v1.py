"""Validation-only temperature scaling audit for CFRG and equal RF."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import chi2
from sklearn.metrics import brier_score_loss, f1_score, log_loss
from sklearn.preprocessing import MinMaxScaler

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.additional_metrics import calibration_errors
from src.cfrg_forest import CFRGForest
from src.probability_calibration import TemperatureScaler


def _brier(y, p, classes):
    return float(np.mean([brier_score_loss((y == c).astype(int), p[:, i]) for i, c in enumerate(classes)]))


def run_calibration(processed_dir, output_dir, n_estimators=100, chi2_k=60, seeds=(42, 2024, 3407)):
    processed_dir, output_dir = Path(processed_dir), Path(output_dir); output_dir.mkdir(parents=True, exist_ok=True)
    train = pd.read_csv(processed_dir / "train.csv"); valid = pd.read_csv(processed_dir / "validation.csv"); test = pd.read_csv(processed_dir / "test.csv")
    features = [c for c in train.columns if c != "target"]; scaler = MinMaxScaler().fit(train[features]); Xtr, Xv, Xte = scaler.transform(train[features]), scaler.transform(valid[features]), scaler.transform(test[features]); ytr, yv, yte = train.target.to_numpy(), valid.target.to_numpy(), test.target.to_numpy(); score, _ = chi2(Xtr, ytr); idx = np.argsort(-np.nan_to_num(score, nan=0.0))[: min(int(chi2_k), Xtr.shape[1])]; classes = np.unique(ytr)
    rows = []
    for seed in seeds:
        out = output_dir / f"seed_{int(seed)}"; out.mkdir(parents=True, exist_ok=True)
        models = {"equal_rf": RandomForestClassifier(n_estimators=n_estimators, min_samples_leaf=2, class_weight="balanced_subsample", random_state=seed, n_jobs=-1), "cfrg_forest": CFRGForest(n_estimators=n_estimators, min_samples_leaf=2, class_weight="balanced_subsample", random_state=seed, cost_beta=0.0, cost_min=1.0, cost_max=1.0, n_jobs=-1)}
        for name, model in models.items():
            model.fit(Xtr[:, idx], ytr); p_valid = model.predict_proba(Xv[:, idx]); p_test = model.predict_proba(Xte[:, idx]); classes_model = model.classes_; calibrator = TemperatureScaler().fit(p_valid, yv); p_cal = calibrator.transform(p_test); pred_before = classes_model[np.argmax(p_test, axis=1)]; pred_after = classes_model[np.argmax(p_cal, axis=1)]
            for variant, p, pred in [("uncalibrated", p_test, pred_before), ("temperature_scaled", p_cal, pred_after)]:
                row = {"seed": int(seed), "model": name, "variant": variant, "temperature": 1.0 if variant == "uncalibrated" else calibrator.temperature_, "macro_f1": float(f1_score(yte, pred, labels=classes_model, average="macro", zero_division=0)), "log_loss": float(log_loss(yte, p, labels=list(classes_model))), "brier_macro": _brier(yte, p, classes_model), **calibration_errors(yte, p, class_labels=classes_model)}; rows.append(row)
            pd.DataFrame({"y_true": yte, "pred_before": pred_before, "pred_after": pred_after}).to_csv(out / f"predictions_{name}.csv", index=False, encoding="utf-8-sig")
        (out / "protocol.json").write_text(json.dumps({"temperature_fit_on": "validation_only", "test_usage": "final_evaluation_only", "seed": int(seed), "chi2_k": int(chi2_k), "n_estimators": int(n_estimators)}, indent=2), encoding="utf-8")
    frame = pd.DataFrame(rows); frame.to_csv(output_dir / "metrics.csv", index=False, encoding="utf-8-sig")
    (output_dir / "protocol.json").write_text(json.dumps({"temperature_fit_on": "validation_only", "test_usage": "final_evaluation_only", "seeds": [int(s) for s in seeds], "chi2_k": int(chi2_k), "n_estimators": int(n_estimators)}, indent=2), encoding="utf-8")
    return frame


def main():
    p = argparse.ArgumentParser(); p.add_argument("--processed-dir", type=Path, required=True); p.add_argument("--output-dir", type=Path, required=True); p.add_argument("--n-estimators", type=int, default=100); p.add_argument("--chi2-k", type=int, default=60); p.add_argument("--seeds", type=int, nargs="+", default=[42, 2024, 3407]); args = p.parse_args(); run_calibration(args.processed_dir, args.output_dir, args.n_estimators, args.chi2_k, args.seeds)


if __name__ == "__main__": main()
