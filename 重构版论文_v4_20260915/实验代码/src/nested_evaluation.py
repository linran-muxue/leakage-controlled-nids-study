"""Leakage-controlled nested evaluation utilities for SCI experiments."""
from __future__ import annotations

from typing import Iterable

import numpy as np
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.feature_selection import chi2
from sklearn.model_selection import StratifiedKFold


def nested_split_indices(y, outer_splits=3, inner_splits=3, seed=42):
    """Return disjoint outer folds and inner folds contained in each outer train."""
    y = np.asarray(y)
    if y.ndim != 1 or len(y) == 0:
        raise ValueError("y must be a non-empty one-dimensional array")
    outer = StratifiedKFold(n_splits=outer_splits, shuffle=True, random_state=seed)
    result = []
    indices = np.arange(len(y))
    for outer_train, outer_test in outer.split(indices, y):
        inner = StratifiedKFold(n_splits=inner_splits, shuffle=True, random_state=seed + len(result) + 1)
        inner_folds = [(outer_train[it], outer_train[iv]) for it, iv in inner.split(outer_train, y[outer_train])]
        result.append((outer_train, outer_test, inner_folds))
    return result


def select_features_fold(x, y, k=60):
    x = np.asarray(x, dtype=float)
    if x.ndim != 2 or len(x) != len(y):
        raise ValueError("x and y must have compatible shapes")
    if not np.isfinite(x).all() or (x < 0).any():
        raise ValueError("chi-square inputs must be finite and non-negative")
    if not 1 <= int(k) <= x.shape[1]:
        raise ValueError(f"k must be between 1 and {x.shape[1]}")
    scores, _ = chi2(x, np.asarray(y))
    scores = np.nan_to_num(scores, nan=0.0, posinf=np.finfo(float).max, neginf=0.0)
    return np.sort(np.argsort(-scores, kind="stable")[: int(k)])


def make_candidate_specs(seed=42, n_classes=5):
    from xgboost import XGBClassifier
    return [
        ("random_forest", RandomForestClassifier(n_estimators=100, min_samples_leaf=2, class_weight="balanced_subsample", n_jobs=-1, random_state=seed), "all", "rf100_all"),
        ("random_forest", RandomForestClassifier(n_estimators=100, min_samples_leaf=2, class_weight="balanced_subsample", n_jobs=-1, random_state=seed), "chi2", "rf100_chi2"),
        ("extra_trees", ExtraTreesClassifier(n_estimators=100, min_samples_leaf=2, class_weight="balanced", n_jobs=-1, random_state=seed), "chi2", "et100_chi2"),
        ("xgboost", XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, subsample=.9, colsample_bytree=.9, objective="multi:softprob", num_class=n_classes, eval_metric="mlogloss", tree_method="hist", n_jobs=-1, random_state=seed), "chi2", "xgb100_d6"),
    ]


def filter_candidate_specs(model_name, seed=42, n_classes=5, k_values=(20, 40, 60)):
    """Return candidates for one model family under an identical search API."""
    from xgboost import XGBClassifier
    rows = []
    if model_name == "random_forest":
        rows.append({"model": model_name, "mode": "all", "k": None, "config": "rf_all_t100", "estimator": RandomForestClassifier(n_estimators=100, min_samples_leaf=2, class_weight="balanced_subsample", n_jobs=-1, random_state=seed)})
        for k in k_values:
            rows.append({"model": model_name, "mode": "chi2", "k": k, "config": f"rf_chi2_k{k}_t100", "estimator": RandomForestClassifier(n_estimators=100, min_samples_leaf=2, class_weight="balanced_subsample", n_jobs=-1, random_state=seed)})
    elif model_name == "extra_trees":
        for k in k_values:
            rows.append({"model": model_name, "mode": "chi2", "k": k, "config": f"et_chi2_k{k}_t100", "estimator": ExtraTreesClassifier(n_estimators=100, min_samples_leaf=2, class_weight="balanced", n_jobs=-1, random_state=seed)})
    elif model_name == "xgboost":
        for k in k_values:
            rows.append({"model": model_name, "mode": "chi2", "k": k, "config": f"xgb_chi2_k{k}_t100_d6", "estimator": XGBClassifier(n_estimators=100, max_depth=6, learning_rate=.1, subsample=.9, colsample_bytree=.9, objective="multi:softprob", num_class=n_classes, eval_metric="mlogloss", tree_method="hist", n_jobs=-1, random_state=seed)})
    else:
        raise ValueError("unknown model family")
    return rows
