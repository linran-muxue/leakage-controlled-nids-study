"""Common-budget strong baseline comparison for the locked CIC protocol."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.feature_selection import chi2
from sklearn.metrics import accuracy_score, balanced_accuracy_score, brier_score_loss, f1_score, log_loss
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.additional_metrics import calibration_errors
from src.cfrg_forest import CFRGForest


def run_strong_baselines(processed_dir, output_dir, seeds=(42, 2024, 3407), n_estimators=100, chi2_k=60, use_xgboost=True):
    processed_dir, output_dir = Path(processed_dir), Path(output_dir); output_dir.mkdir(parents=True, exist_ok=True)
    train, valid, test = [pd.read_csv(processed_dir / f"{s}.csv") for s in ["train", "validation", "test"]]; features = [c for c in train.columns if c != "target"]; scaler = MinMaxScaler().fit(train[features]); Xtr, Xv, Xte = scaler.transform(train[features]), scaler.transform(valid[features]), scaler.transform(test[features]); ytr, yte = train.target.to_numpy(), test.target.to_numpy(); classes = np.unique(ytr); scores, _ = chi2(Xtr, ytr); idx = np.argsort(-np.nan_to_num(scores, nan=0.0))[: min(int(chi2_k), Xtr.shape[1])]; rows = []
    for seed in seeds:
        models = {"equal_rf": RandomForestClassifier(n_estimators=n_estimators, min_samples_leaf=2, class_weight="balanced_subsample", random_state=seed, n_jobs=-1), "extra_trees": ExtraTreesClassifier(n_estimators=n_estimators, min_samples_leaf=2, class_weight="balanced", random_state=seed, n_jobs=-1), "cfrg_forest": CFRGForest(n_estimators=n_estimators, min_samples_leaf=2, class_weight="balanced_subsample", random_state=seed, cost_beta=0.0, cost_min=1.0, cost_max=1.0, n_jobs=-1)}
        if use_xgboost:
            try:
                from xgboost import XGBClassifier
                models["xgboost"] = XGBClassifier(n_estimators=n_estimators, max_depth=6, learning_rate=0.1, subsample=0.8, colsample_bytree=0.8, objective="multi:softprob", eval_metric="mlogloss", n_jobs=-1, random_state=seed, num_class=len(classes))
            except ImportError:
                pass
        for name, model in models.items():
            if name == "xgboost":
                encoder = LabelEncoder().fit(classes); fit_y = encoder.transform(ytr)
            else:
                encoder = None; fit_y = ytr
            start = time.perf_counter(); model.fit(Xtr[:, idx], fit_y); train_s = time.perf_counter() - start; start = time.perf_counter(); p = model.predict_proba(Xte[:, idx]); pred = classes[np.argmax(p, axis=1)] if encoder is not None else model.classes_[np.argmax(p, axis=1)]; pred_s = time.perf_counter() - start; rows.append({"seed": int(seed), "model": name, "accuracy": float(accuracy_score(yte, pred)), "balanced_accuracy": float(balanced_accuracy_score(yte, pred)), "macro_f1": float(f1_score(yte, pred, labels=classes, average="macro", zero_division=0)), "log_loss": float(log_loss(yte, p, labels=list(classes))), "brier_macro": float(np.mean([brier_score_loss((yte == c).astype(int), p[:, i]) for i, c in enumerate(classes)])), **calibration_errors(yte, p, class_labels=classes), "train_seconds": train_s, "predict_seconds": pred_s})
    result = pd.DataFrame(rows); result.to_csv(output_dir / "metrics.csv", index=False, encoding="utf-8-sig"); result.groupby("model")[['accuracy', 'balanced_accuracy', 'macro_f1', 'log_loss', 'brier_macro', 'ece', 'mce', 'train_seconds', 'predict_seconds']].agg(['mean', 'std']).reset_index().to_csv(output_dir / "summary.csv", index=False, encoding="utf-8-sig"); return result


def main():
    p = argparse.ArgumentParser(); p.add_argument("--processed-dir", type=Path, required=True); p.add_argument("--output-dir", type=Path, required=True); p.add_argument("--n-estimators", type=int, default=100); p.add_argument("--chi2-k", type=int, default=60); p.add_argument("--seeds", type=int, nargs="+", default=[42, 2024, 3407]); p.add_argument("--no-xgboost", action="store_true"); args = p.parse_args(); run_strong_baselines(args.processed_dir, args.output_dir, args.seeds, args.n_estimators, args.chi2_k, not args.no_xgboost)


if __name__ == "__main__": main()
