"""Coverage-aware leave-one-file-out evaluation for CIC-IDS2017.

This is an external generalization audit, not a conventional complete
five-class score: labels absent from the training files are reported as
unseen-test labels and excluded from the known-label score.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import chi2
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.preprocessing import MinMaxScaler

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data_pipeline import map_attack_label


def coverage_report(test_labels, train_labels):
    test_set = set(map(str, test_labels)); train_set = set(map(str, train_labels))
    known = sorted(test_set & train_set); unseen = sorted(test_set - train_set)
    labels = np.asarray(list(map(str, test_labels)))
    return {"known_labels": known, "unseen_test_labels": unseen, "known_row_fraction": float(np.isin(labels, known).mean()) if len(labels) else 0.0}


def sample_file_frame(frame: pd.DataFrame, per_class_cap: int = 5000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed); parts = []
    for label, group in frame.groupby("target", sort=True):
        if len(group) > per_class_cap:
            group = group.sample(per_class_cap, random_state=int(rng.integers(0, 2**31 - 1)))
        parts.append(group)
    return pd.concat(parts, ignore_index=True).sample(frac=1, random_state=seed).reset_index(drop=True) if parts else frame.iloc[0:0].copy()


def load_file(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, low_memory=False, encoding_errors="replace")
    frame.columns = [str(c).strip() for c in frame.columns]
    label_col = next(c for c in frame.columns if c.lower() == "label")
    features = [c for c in frame.columns if c not in {label_col, "Flow ID", "Timestamp"}]
    target = frame[label_col].map(lambda x: map_attack_label(x, include_other=False))
    numeric = frame[features].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
    valid = target.notna() & numeric.notna().all(axis=1)
    out = numeric.loc[valid].copy(); out["target"] = target.loc[valid].to_numpy()
    return out.reset_index(drop=True)


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--raw-dir", type=Path, required=True); ap.add_argument("--output-dir", type=Path, required=True); ap.add_argument("--per-class-cap", type=int, default=5000); ap.add_argument("--chi2-k", type=int, default=60); ap.add_argument("--n-estimators", type=int, default=100); ap.add_argument("--seed", type=int, default=42); args = ap.parse_args(); args.output_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(args.raw_dir.glob("*.csv")); data = {p.name: load_file(p) for p in files}; rows = []
    for test_name, test_raw in data.items():
        train_parts = [sample_file_frame(df, args.per_class_cap, args.seed) for name, df in data.items() if name != test_name]
        train = pd.concat(train_parts, ignore_index=True); test = sample_file_frame(test_raw, args.per_class_cap, args.seed)
        names = [c for c in train.columns if c != "target"]; scaler = MinMaxScaler(); x = scaler.fit_transform(train[names]); xt = scaler.transform(test[names]); y = train["target"].to_numpy(); yt = test["target"].to_numpy(); labels = sorted(set(y)); scores, _ = chi2(x, y); idx = np.argsort(-np.nan_to_num(scores, nan=0.0))[:min(args.chi2_k, x.shape[1])]
        model = RandomForestClassifier(n_estimators=args.n_estimators, min_samples_leaf=2, class_weight="balanced_subsample", n_jobs=-1, random_state=args.seed); model.fit(x[:, idx], y); pred = model.predict(xt[:, idx]); coverage = coverage_report(yt, y); known = np.isin(yt, coverage["known_labels"]); row = {"test_file": test_name, "train_rows": len(train), "test_rows": len(test), "known_labels": ";".join(coverage["known_labels"]), "unseen_test_labels": ";".join(coverage["unseen_test_labels"]), "known_row_fraction": coverage["known_row_fraction"], "accuracy_known": float(accuracy_score(yt[known], pred[known])) if known.any() else np.nan, "balanced_accuracy_known": float(balanced_accuracy_score(yt[known], pred[known])) if known.any() else np.nan, "macro_f1_known": float(f1_score(yt[known], pred[known], labels=coverage["known_labels"], average="macro", zero_division=0)) if known.any() else np.nan}; rows.append(row)
    out = pd.DataFrame(rows); out.to_csv(args.output_dir / "file_external_results.csv", index=False, encoding="utf-8-sig"); (args.output_dir / "protocol.json").write_text(json.dumps({"protocol":"leave-one-file-out","unseen_labels_excluded_from_known_score":True,"per_class_cap":args.per_class_cap,"chi2_k":args.chi2_k,"n_estimators":args.n_estimators,"seed":args.seed}, ensure_ascii=False, indent=2), encoding="utf-8"); print(out.to_string(index=False))


if __name__ == "__main__": main()
