"""Family-decorrelated experts and expert-count sweeps.

Two questions the primary study leaves open:

  * experiment 1 - do *genuinely different* members (different model families,
    not only different filter views) let the gate act?  Config "families" mixes
    random forest, extremely randomised trees and gradient boosting over two
    feature views.
  * experiment 4 - is the inertness specific to four experts?  Configs q2, q3,
    q4 and q6 vary the number of members while sharing the same protocol.

All members are fitted once per seed (out-of-fold probabilities for the gate,
full-fit probabilities for the test comparison), so every configuration is
evaluated on exactly the same predictions.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from xgboost import XGBClassifier

from src.rccf_forest import _descriptor

ROOT = Path(__file__).resolve().parents[1]
MEMBERS = {
    "rf_full": ("full", "rf"),
    "rf_chi2": ("chi2", "rf"),
    "rf_mutual_info": ("mutual_info", "rf"),
    "rf_anova": ("anova", "rf"),
    "xgb_chi2": ("chi2", "xgb"),
    "et_chi2": ("chi2", "et"),
}
CONFIGS = {
    "families": ["rf_full", "rf_chi2", "xgb_chi2", "et_chi2"],
    "q2": ["rf_chi2", "rf_full"],
    "q3": ["rf_chi2", "rf_full", "rf_mutual_info"],
    "q4": ["rf_chi2", "rf_full", "rf_mutual_info", "rf_anova"],
    "q6": ["rf_chi2", "rf_full", "rf_mutual_info", "rf_anova", "xgb_chi2", "et_chi2"],
}


def load(path: Path):
    frame = pd.read_csv(path, low_memory=False)
    frame = frame.dropna(axis=1, how="all")
    return frame.drop(columns=["target"]).apply(pd.to_numeric).to_numpy(), frame["target"].to_numpy()


def select(view: str, X_fit, y_fit, X_apply, seed: int):
    if view == "full":
        return X_fit, X_apply
    from sklearn.feature_selection import SelectKBest, chi2, f_classif, mutual_info_classif
    from functools import partial
    scorer = {"chi2": chi2, "anova": f_classif}.get(view)
    if view == "mutual_info":
        scorer = partial(mutual_info_classif, random_state=seed)
    scaler = MinMaxScaler().fit(X_fit)
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        selector = SelectKBest(scorer, k=min(60, X_fit.shape[1])).fit(scaler.transform(X_fit), y_fit)
    return selector.transform(scaler.transform(X_fit)), selector.transform(scaler.transform(X_apply))


def fit_member(view: str, kind: str, X, y, seed: int):
    if kind == "rf":
        model = RandomForestClassifier(n_estimators=100, min_samples_leaf=2,
                                       class_weight="balanced_subsample", n_jobs=-1,
                                       random_state=seed)
    elif kind == "et":
        model = ExtraTreesClassifier(n_estimators=100, min_samples_leaf=2,
                                     class_weight="balanced_subsample", n_jobs=-1,
                                     random_state=seed)
    else:
        model = XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.1,
                              subsample=0.9, colsample_bytree=0.9, n_jobs=-1,
                              random_state=seed, verbosity=0, tree_method="hist")
    return model.fit(X, y)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", default="data_processed_cic_natural_v3b")
    ap.add_argument("--output-dir", default="results_member_family_v1")
    ap.add_argument("--seeds", nargs="+", type=int, default=[42, 2024, 3407])
    ap.add_argument("--cv", type=int, default=5)
    args = ap.parse_args()

    data = ROOT / args.processed_dir
    out = ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    X_train, y_train = load(data / "train.csv")
    X_test, y_test = load(data / "test.csv")
    labels = np.unique(y_train)
    # work in integer codes so every member (sklearn and XGBoost alike) sees the
    # same target encoding; the string labels are restored for the outputs
    y_train_codes = np.searchsorted(labels, y_train)
    y_test_codes = np.searchsorted(labels, y_test)
    print(f"train {X_train.shape} test {X_test.shape} classes {list(labels)}", flush=True)

    member_rows, gate_rows = [], []
    for seed in args.seeds:
        started = time.time()
        splitter = StratifiedKFold(args.cv, shuffle=True, random_state=seed)
        folds = list(splitter.split(X_train, y_train_codes))
        oof, test_prob = {}, {}
        for name, (view, kind) in MEMBERS.items():
            oof[name] = np.zeros((len(y_train), len(labels)))
            for fold_index, (tr, va) in enumerate(folds):
                Xtr, Xva = select(view, X_train[tr], y_train_codes[tr], X_train[va],
                                  seed + fold_index)
                model = fit_member(view, kind, Xtr, y_train_codes[tr], seed + fold_index)
                classes = model.classes_
                order = np.searchsorted(classes, np.arange(len(labels)))
                oof[name][va] = model.predict_proba(Xva)[:, order]
            Xfit, Xapply = select(view, X_train, y_train_codes, X_test, seed)
            model = fit_member(view, kind, Xfit, y_train_codes, seed)
            classes = model.classes_
            order = np.searchsorted(classes, np.arange(len(labels)))
            test_prob[name] = model.predict_proba(Xapply)[:, order]
            prediction = labels[test_prob[name].argmax(axis=1)]
            member_rows.append({
                "seed": seed, "member": name, "view": view, "family": kind,
                "macro_f1": float(f1_score(y_test, prediction, average="macro",
                                           labels=labels, zero_division=0)),
            })
            print(f"  seed {seed} {name}: fitted", flush=True)
        y_train_index = y_train_codes

        for config, members in CONFIGS.items():
            features = np.concatenate(
                [oof[name].reshape(len(y_train), -1) for name in members] +
                [_descriptor(oof[name]) for name in members], axis=1)
            targets = np.stack([(oof[name].argmax(axis=1) != y_train_index).astype(int)
                                for name in members], axis=1)
            weights = np.zeros((len(X_test), len(members)))
            for index in range(len(members)):
                target = targets[:, index]
                if np.unique(target).size == 1:
                    risk = np.full(len(X_test), float(target[0]))
                else:
                    scaler = StandardScaler().fit(features)
                    model = LogisticRegression(C=1.0, class_weight="balanced",
                                               max_iter=400, random_state=seed).fit(
                        scaler.transform(features), target)
                    joined = np.concatenate(
                        [test_prob[name] for name in members] +
                        [_descriptor(test_prob[name]) for name in members], axis=1)
                    risk = model.predict_proba(scaler.transform(joined))[:, 1]
                weights[:, index] = np.exp(-np.clip(risk, 0.0, 20.0))
            weights /= np.maximum(weights.sum(axis=1, keepdims=True), 1e-12)
            stack = np.stack([test_prob[name] for name in members], axis=1)
            equal = stack.mean(axis=1)
            fused = np.sum(stack * weights[:, :, None], axis=1)
            equal_pred = labels[equal.argmax(axis=1)]
            fused_pred = labels[fused.argmax(axis=1)]
            disagreement = np.mean([
                float(np.mean(test_prob[a].argmax(axis=1) != test_prob[b].argmax(axis=1)))
                for a, b in itertools.combinations(members, 2)])
            row = {
                "config": config, "seed": seed, "members": len(members),
                "member_names": "|".join(members),
                "equal_macro_f1": float(f1_score(y_test, equal_pred, average="macro",
                                                 labels=labels, zero_division=0)),
                "gate_macro_f1": float(f1_score(y_test, fused_pred, average="macro",
                                                labels=labels, zero_division=0)),
                "labels_changed": int((fused_pred != equal_pred).sum()),
                "test_rows": int(len(y_test)),
                "mean_pairwise_disagreement": disagreement,
                "mean_weight_l1": float(np.abs(weights - 1.0 / len(members)).sum(axis=1).mean()),
            }
            row["gain"] = row["gate_macro_f1"] - row["equal_macro_f1"]
            gate_rows.append(row)
            frame = pd.DataFrame({
                "row_id": np.arange(len(y_test)), "true_label": y_test,
                "equal_pred": equal_pred, "gate_pred": fused_pred,
                "equal_max_prob": equal.max(axis=1), "gate_max_prob": fused.max(axis=1),
                **{f"equal_prob_{label}": equal[:, i] for i, label in enumerate(labels)},
                **{f"gate_prob_{label}": fused[:, i] for i, label in enumerate(labels)},
            })
            frame.to_csv(out / f"predictions_{config}_seed{seed}.csv", index=False,
                         encoding="utf-8-sig")
            print(f"  seed {seed} {config}: gain {row['gain']:+.6f}, "
                  f"{row['labels_changed']} labels changed, "
                  f"disagreement {100 * disagreement:.3f}%", flush=True)
        print(f"seed {seed} done in {time.time() - started:.0f}s", flush=True)

    pd.DataFrame(member_rows).to_csv(out / "member_metrics_by_seed.csv", index=False,
                                     encoding="utf-8-sig")
    gate = pd.DataFrame(gate_rows)
    gate.to_csv(out / "gate_results_by_config.csv", index=False, encoding="utf-8-sig")
    summary = {}
    for config, group in gate.groupby("config"):
        summary[config] = {
            "members": int(group["members"].iloc[0]),
            "member_names": group["member_names"].iloc[0],
            "equal_mean_macro_f1": float(group["equal_macro_f1"].mean()),
            "gate_mean_macro_f1": float(group["gate_macro_f1"].mean()),
            "mean_gain": float(group["gain"].mean()),
            "labelled_changes_total": int(group["labels_changed"].sum()),
            "comparisons": int(group["test_rows"].sum()),
            "mean_pairwise_disagreement": float(group["mean_pairwise_disagreement"].mean()),
        }
    (out / "member_family_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
