"""S2: tune the RCCF gate under the same budget as the baselines.

Audit gap 4.1: the gate hyper-parameters (risk-model regularisation C, descriptor
set, cross-fitting folds) were hard-coded while the baseline models were tuned in a
5x3 nested protocol. This script removes that asymmetry.

Efficiency note: the expensive part (fitting the four expert forests per fold) is
computed once per (cv, seed). Risk models are cheap to refit, so all C and
descriptor-set combinations reuse the same out-of-fold table. Selection uses the
validation partition only; the test partition is touched once, after selection.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

from src.rccf_forest import DESCRIPTOR_SETS, RCCFForest, _descriptor, _selector

ROOT = Path(__file__).resolve().parents[1]
LABELS = ["Bot", "Brute Force", "DoS/DDoS", "Normal", "Web Attack"]


def load(path: Path):
    frame = pd.read_csv(path, low_memory=False)
    return frame.drop(columns=["target"]).apply(pd.to_numeric), frame["target"].to_numpy()


def macro_f1(y, pred) -> float:
    return float(f1_score(y, pred, average="macro", labels=LABELS, zero_division=0))


def expert_table(Xtr, ytr, Xva, cv: int, seed: int, n_estimators: int, feature_k: int):
    """Return cross-fitted OOF probabilities/descriptors and validation probabilities."""
    classes = np.unique(ytr)
    n, q, c = len(ytr), len(RCCFForest.expert_names), len(classes)
    oof = np.zeros((n, q, c))
    oof_desc = np.zeros((n, q, 3))
    splitter = StratifiedKFold(cv, shuffle=True, random_state=seed)
    for fold, (tr, va) in enumerate(splitter.split(Xtr, ytr)):
        for eidx, name in enumerate(RCCFForest.expert_names):
            expert = _fit_expert(name, Xtr[tr], ytr[tr], seed + fold * 97 + eidx,
                                 n_estimators, feature_k)
            p = _expert_proba(expert, Xtr[va], classes)
            oof[va, eidx] = p
            oof_desc[va, eidx] = _descriptor(p)
    val_probs, val_desc = [], []
    for eidx, name in enumerate(RCCFForest.expert_names):
        expert = _fit_expert(name, Xtr, ytr, seed + eidx, n_estimators, feature_k)
        p = _expert_proba(expert, Xva, classes)
        val_probs.append(p)
        val_desc.append(_descriptor(p))
    return oof, oof_desc, np.stack(val_probs, axis=1), np.stack(val_desc, axis=1), classes


def _fit_expert(name, X, y, seed, n_estimators, feature_k):
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import MinMaxScaler
    import warnings

    selector = _selector(name, min(feature_k, X.shape[1]), random_state=seed)
    scaler = MinMaxScaler().fit(X)
    Xs = scaler.transform(X)
    if selector is not None:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            Xs = selector.fit_transform(Xs, y)
    forest = RandomForestClassifier(n_estimators=n_estimators, random_state=seed,
                                    min_samples_leaf=2, class_weight="balanced_subsample",
                                    n_jobs=-1).fit(Xs, y)
    return {"name": name, "scaler": scaler, "selector": selector, "forest": forest}


def _expert_proba(expert, X, classes):
    Xs = expert["scaler"].transform(X)
    if expert["selector"] is not None:
        Xs = expert["selector"].transform(Xs)
    p = expert["forest"].predict_proba(Xs)
    if list(expert["forest"].classes_) == list(classes):
        return p
    out = np.zeros((len(X), len(classes)))
    idx = [list(classes).index(c) for c in expert["forest"].classes_]
    out[:, idx] = p
    return out


def fuse(oof, oof_desc, ytr, val_probs, val_desc, classes, risk_C: float, desc_key: str):
    cols = DESCRIPTOR_SETS[desc_key]
    y_idx = np.searchsorted(classes, ytr)
    risk_features = np.concatenate(
        [oof.reshape(len(ytr), -1), oof_desc[:, :, cols].reshape(len(ytr), -1)], axis=1)
    targets = np.stack([(np.argmax(oof[:, i], axis=1) != y_idx).astype(int)
                        for i in range(oof.shape[1])], axis=1)
    risks = np.zeros((len(val_probs), oof.shape[1]))
    for eidx in range(oof.shape[1]):
        scaler = StandardScaler().fit(risk_features)
        model = LogisticRegression(C=risk_C, class_weight="balanced",
                                   max_iter=400, random_state=0)
        target = targets[:, eidx]
        if np.unique(target).size == 1:
            risks[:, eidx] = float(target[0])
            continue
        model.fit(scaler.transform(risk_features), target)
        joined = np.concatenate(
            [val_probs.reshape(len(val_probs), -1),
             val_desc[:, :, cols].reshape(len(val_probs), -1)], axis=1)
        risks[:, eidx] = model.predict_proba(scaler.transform(joined))[:, 1]
    weights = np.exp(-np.clip(risks, 0.0, 20.0))
    weights /= np.maximum(weights.sum(axis=1, keepdims=True), 1e-12)
    fused = np.sum(val_probs * weights[:, :, None], axis=1)
    return fused, weights


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", default="data_processed_cic_natural_v3b")
    ap.add_argument("--output-dir", default="results_gate_tuning_v5")
    ap.add_argument("--seeds", nargs="+", type=int, default=[42, 2024, 3407])
    ap.add_argument("--cv-grid", nargs="+", type=int, default=[3, 5, 10])
    ap.add_argument("--c-grid", nargs="+", type=float, default=[0.01, 0.1, 1.0, 10.0])
    ap.add_argument("--descriptor-grid", nargs="+",
                    default=["all", "entropy", "margin"])
    ap.add_argument("--n-estimators", type=int, default=100)
    ap.add_argument("--feature-k", type=int, default=60)
    args = ap.parse_args()

    proc = ROOT / args.processed_dir
    out = ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    Xtr, ytr = load(proc / "train.csv")
    Xva, yva = load(proc / "validation.csv")
    Xtr_np, Xva_np = Xtr.to_numpy(), Xva.to_numpy()

    rows = []
    for cv in args.cv_grid:
        for seed in args.seeds:
            start = time.perf_counter()
            oof, oof_desc, val_probs, val_desc, classes = expert_table(
                Xtr_np, ytr, Xva_np, cv, seed, args.n_estimators, args.feature_k)
            elapsed = time.perf_counter() - start
            # Reference 1: plain equal-weight averaging of the same four experts.
            equal_pred = classes[np.argmax(val_probs.mean(axis=1), axis=1)]
            equal_f1 = macro_f1(yva, equal_pred)
            preds: dict[tuple[float, str], np.ndarray] = {}
            for risk_C in args.c_grid:
                for desc_key in args.descriptor_grid:
                    fused, weights = fuse(oof, oof_desc, ytr, val_probs, val_desc,
                                          classes, risk_C, desc_key)
                    pred = classes[np.argmax(fused, axis=1)]
                    preds[(risk_C, desc_key)] = pred
                    entropy = -(weights * np.log(np.clip(weights, 1e-12, 1.0))).sum(axis=1)
                    entropy /= np.log(weights.shape[1])
                    rows.append({
                        "cv": cv, "seed": seed, "risk_C": risk_C,
                        "descriptor_set": desc_key,
                        "val_macro_f1": macro_f1(yva, pred),
                        "equal_weight_val_macro_f1": equal_f1,
                        "disagreement_vs_equal_weight": int((pred != equal_pred).sum()),
                        "mean_weight_entropy": float(entropy.mean()),
                        "min_weight_entropy": float(entropy.min()),
                        "expert_table_seconds": elapsed,
                    })
            # Every tuned configuration must be compared against the untouched default.
            default_pred = preds[(1.0, "all")]
            for row in rows[-len(args.c_grid) * len(args.descriptor_grid):]:
                row["disagreement_vs_default_gate"] = int(
                    (preds[(row["risk_C"], row["descriptor_set"])] != default_pred).sum())
            pd.DataFrame(rows).to_csv(out / "gate_search_results.csv",
                                      index=False, encoding="utf-8-sig")
            print(f"cv={cv} seed={seed} done in {elapsed:.1f}s", flush=True)

    results = pd.DataFrame(rows)
    summary = (results.groupby(["cv", "risk_C", "descriptor_set"])["val_macro_f1"]
               .agg(["mean", "std"]).reset_index()
               .sort_values("mean", ascending=False))
    summary.to_csv(out / "gate_search_summary.csv", index=False, encoding="utf-8-sig")
    best = summary.iloc[0]
    selected = {
        "cv": int(best["cv"]), "risk_C": float(best["risk_C"]),
        "descriptor_set": str(best["descriptor_set"]),
        "val_macro_f1_mean": float(best["mean"]),
        "val_macro_f1_std": float(best["std"]),
        "default_config": {"cv": 5, "risk_C": 1.0, "descriptor_set": "all"},
        "selection_data": "validation partition only; test partition untouched",
        "search_space": {"cv": args.cv_grid, "risk_C": args.c_grid,
                         "descriptor_set": args.descriptor_grid},
        "n_estimators": args.n_estimators, "feature_k": args.feature_k,
        "train_sha256": sha256(proc / "train.csv"),
    }
    (out / "selected_gate_config.json").write_text(
        json.dumps(selected, indent=2, ensure_ascii=False), encoding="utf-8")
    print(summary.head(10).to_string(index=False))
    print("SELECTED:", json.dumps(selected, ensure_ascii=False))


if __name__ == "__main__":
    main()
