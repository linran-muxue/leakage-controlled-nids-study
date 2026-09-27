"""S3 + S4: expert diversity, gate gain, and deliberately decorrelated experts.

Audit gaps 4.2 and 4.6.

S3 asks whether the gate gain is a function of expert diversity. S4 supplies the
reverse experiment: if the four experts are made genuinely diverse (heterogeneous
algorithm families, disjoint feature blocks, independent subsamples), does the gate
recover a gain? Together they turn "we saw no gain" into a falsifiable statement
about when conditional weighting can work at all.

Every expert set is evaluated with the same protocol: experts fitted on the training
partition, cross-fitted out-of-fold probabilities used to fit the risk models, and a
single locked test evaluation.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from itertools import combinations
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.feature_selection import SelectKBest, chi2, f_classif, mutual_info_classif
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
LABELS = ["Bot", "Brute Force", "DoS/DDoS", "Normal", "Web Attack"]


def load(path: Path):
    frame = pd.read_csv(path, low_memory=False)
    return frame.drop(columns=["target"]).apply(pd.to_numeric).to_numpy(), frame["target"].to_numpy()


def macro_f1(y, pred) -> float:
    return float(f1_score(y, pred, average="macro", labels=LABELS, zero_division=0))


def build_expert(spec: dict, X: np.ndarray, y, seed: int):
    """Fit one expert according to its specification; return a predictor closure."""
    scaler = MinMaxScaler().fit(X)
    Xs = scaler.transform(X)

    columns = spec.get("columns")
    if columns is not None:
        Xs = Xs[:, columns]

    selector = None
    if spec.get("selector") == "chi2":
        selector = SelectKBest(chi2, k=min(spec["k"], Xs.shape[1])).fit(Xs, y)
    elif spec.get("selector") == "mutual_info":
        selector = SelectKBest(lambda a, b: mutual_info_classif(a, b, random_state=seed),
                               k=min(spec["k"], Xs.shape[1])).fit(Xs, y)
    elif spec.get("selector") == "anova":
        selector = SelectKBest(f_classif, k=min(spec["k"], Xs.shape[1])).fit(Xs, y)
    if selector is not None:
        Xs = selector.transform(Xs)

    family = spec["family"]
    if family == "rf":
        model = RandomForestClassifier(n_estimators=100, min_samples_leaf=2,
                                       class_weight="balanced_subsample",
                                       random_state=seed, n_jobs=-1)
    elif family == "extra_trees":
        model = ExtraTreesClassifier(n_estimators=100, min_samples_leaf=2,
                                     class_weight="balanced", random_state=seed, n_jobs=-1)
    elif family == "xgboost":
        from xgboost import XGBClassifier
        model = XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.3,
                              tree_method="hist", n_jobs=-1, random_state=seed,
                              verbosity=0, objective="multi:softprob")
    elif family == "knn":
        model = KNeighborsClassifier(n_neighbors=5, n_jobs=-1)
    else:
        raise ValueError(f"unknown family {family}")

    # XGBoost requires consecutive integer class codes; every other family accepts
    # the native label strings directly.
    if family == "xgboost":
        model_labels = sorted(np.unique(y).tolist())
        label_to_code = {label: code for code, label in enumerate(model_labels)}
        model.fit(Xs, np.array([label_to_code[label] for label in y]))
    else:
        model.fit(Xs, y)
        model_labels = list(model.classes_)

    def predict_proba(Xnew, classes):
        Z = scaler.transform(Xnew)
        if columns is not None:
            Z = Z[:, columns]
        if selector is not None:
            Z = selector.transform(Z)
        p = model.predict_proba(Z)
        if list(model_labels) == list(classes):
            return p
        out = np.zeros((len(Xnew), len(classes)))
        idx = [list(classes).index(c) for c in model_labels]
        out[:, idx] = p
        return out

    return predict_proba


def diversity_metrics(probs: np.ndarray, classes, y_true) -> dict:
    """probs: (n_samples, n_experts, n_classes)."""
    q = probs.shape[1]
    preds = np.stack([classes[np.argmax(probs[:, i], axis=1)] for i in range(q)], axis=1)
    disagreements, kls, corrs = [], [], []
    for i, j in combinations(range(q), 2):
        disagreements.append(float((preds[:, i] != preds[:, j]).mean()))
        p = np.clip(probs[:, i], 1e-12, 1)
        r = np.clip(probs[:, j], 1e-12, 1)
        kls.append(float((p * (np.log(p) - np.log(r))).sum(axis=1).mean()))
        conf_i = probs[:, i].max(axis=1)
        conf_j = probs[:, j].max(axis=1)
        if conf_i.std() > 0 and conf_j.std() > 0:
            corrs.append(float(np.corrcoef(conf_i, conf_j)[0, 1]))
    return {
        "mean_pairwise_disagreement": float(np.mean(disagreements)),
        "max_pairwise_disagreement": float(np.max(disagreements)),
        "mean_pairwise_kl": float(np.mean(kls)),
        "mean_confidence_correlation": float(np.mean(corrs)) if corrs else float("nan"),
        "mean_single_expert_macro_f1": float(np.mean(
            [macro_f1(y_true, classes[np.argmax(probs[:, i], axis=1)]) for i in range(q)])),
        "max_single_expert_macro_f1": float(np.max(
            [macro_f1(y_true, classes[np.argmax(probs[:, i], axis=1)]) for i in range(q)])),
    }


def gate_fit_predict(specs, Xtr, ytr, Xte, yte, cv: int, seed: int, risk_C: float):
    classes = np.unique(ytr)
    q = len(specs)
    oof = np.zeros((len(ytr), q, len(classes)))
    splitter = StratifiedKFold(cv, shuffle=True, random_state=seed)
    for fold, (tr, va) in enumerate(splitter.split(Xtr, ytr)):
        for eidx, spec in enumerate(specs):
            predictor = build_expert(spec, Xtr[tr], ytr[tr], seed + fold * 97 + eidx)
            oof[va, eidx] = predictor(Xtr[va], classes)

    test_probs = np.zeros((len(Xte), q, len(classes)))
    train_probs = np.zeros((len(Xtr), q, len(classes)))
    for eidx, spec in enumerate(specs):
        predictor = build_expert(spec, Xtr, ytr, seed + 500 + eidx)
        test_probs[:, eidx] = predictor(Xte, classes)
        train_probs[:, eidx] = predictor(Xtr, classes)

    y_idx = np.searchsorted(classes, ytr)
    targets = np.stack([(np.argmax(oof[:, i], axis=1) != y_idx).astype(int) for i in range(q)], axis=1)
    risks = np.zeros((len(Xte), q))
    for eidx in range(q):
        scaler = StandardScaler().fit(oof.reshape(len(ytr), -1))
        target = targets[:, eidx]
        if np.unique(target).size == 1:
            risks[:, eidx] = float(target[0])
            continue
        model = LogisticRegression(C=risk_C, class_weight="balanced",
                                   max_iter=400, random_state=seed)
        model.fit(scaler.transform(oof.reshape(len(ytr), -1)), target)
        risks[:, eidx] = model.predict_proba(scaler.transform(test_probs.reshape(len(Xte), -1)))[:, 1]

    weights = np.exp(-np.clip(risks, 0.0, 20.0))
    weights /= np.maximum(weights.sum(axis=1, keepdims=True), 1e-12)
    gated = np.sum(test_probs * weights[:, :, None], axis=1)
    equal = test_probs.mean(axis=1)
    entropy = -(weights * np.log(np.clip(weights, 1e-12, 1.0))).sum(axis=1) / np.log(q)
    return {
        "gated_pred": classes[np.argmax(gated, axis=1)],
        "equal_pred": classes[np.argmax(equal, axis=1)],
        "test_probs": test_probs,
        "mean_weight_entropy": float(entropy.mean()),
        "disagreement_gated_vs_equal": int((np.argmax(gated, 1) != np.argmax(equal, 1)).sum()),
    }


TOP60 = list(range(60))


def expert_sets() -> dict[str, list[dict]]:
    rf = lambda **kw: {"family": "rf", **kw}
    return {
        "rf_views_k20": [rf(selector="chi2", k=20), rf(selector="mutual_info", k=20),
                         rf(selector="anova", k=20), rf(k=None)],
        "rf_views_k60": [rf(selector="chi2", k=60), rf(selector="mutual_info", k=60),
                         rf(selector="anova", k=60), rf(k=None)],
        "rf_same_view_seeds": [rf(selector="chi2", k=60), rf(selector="chi2", k=60),
                               rf(selector="chi2", k=60), rf(selector="chi2", k=60)],
        "hetero_families": [rf(k=None), {"family": "extra_trees", "k": None},
                            {"family": "xgboost", "k": None}, {"family": "knn", "k": None}],
        "disjoint_views_k60": [rf(columns=TOP60[i * 15:(i + 1) * 15]) for i in range(4)],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", default="data_processed_cic_natural_v3b")
    ap.add_argument("--output-dir", default="results_diversity_v5")
    ap.add_argument("--sets", nargs="+", default=list(expert_sets().keys()))
    ap.add_argument("--seeds", nargs="+", type=int, default=[42])
    ap.add_argument("--cv", type=int, default=3)
    ap.add_argument("--risk-C", type=float, default=1.0)
    args = ap.parse_args()

    proc = ROOT / args.processed_dir
    out = ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    Xtr, ytr = load(proc / "train.csv")
    Xte, yte = load(proc / "test.csv")

    registry = expert_sets()
    rows = []
    for name in args.sets:
        specs = registry[name]
        for seed in args.seeds:
            start = time.perf_counter()
            result = gate_fit_predict(specs, Xtr, ytr, Xte, yte, args.cv, seed, args.risk_C)
            metrics = diversity_metrics(result["test_probs"], np.unique(ytr), yte)
            gated_f1 = macro_f1(yte, result["gated_pred"])
            equal_f1 = macro_f1(yte, result["equal_pred"])
            rows.append({
                "expert_set": name, "seed": seed, "n_experts": len(specs), "cv": args.cv,
                "n_features": Xtr.shape[1],
                "test_macro_f1_equal_weight": equal_f1,
                "test_macro_f1_gated": gated_f1,
                "gate_gain": gated_f1 - equal_f1,
                "disagreement_gated_vs_equal": result["disagreement_gated_vs_equal"],
                "mean_weight_entropy": result["mean_weight_entropy"],
                "elapsed_seconds": time.perf_counter() - start,
                **metrics,
            })
            pd.DataFrame(rows).to_csv(out / "diversity_suite_results.csv",
                                      index=False, encoding="utf-8-sig")
            print(f"{name} seed={seed} gain={gated_f1 - equal_f1:+.5f} "
                  f"equalf1={equal_f1:.5f}", flush=True)

    df = pd.DataFrame(rows)
    if len(df) >= 3 and df["mean_pairwise_disagreement"].std() > 0:
        slope, intercept = np.polyfit(df["mean_pairwise_disagreement"], df["gate_gain"], 1)
        corr = float(df["mean_pairwise_disagreement"].corr(df["gate_gain"]))
        fit = {"slope": float(slope), "intercept": float(intercept),
               "pearson_r": corr, "n_points": int(len(df))}
    else:
        fit = {"note": "insufficient spread for regression", "n_points": int(len(df))}
    (out / "diversity_gain_regression.json").write_text(
        json.dumps(fit, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(fit, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
