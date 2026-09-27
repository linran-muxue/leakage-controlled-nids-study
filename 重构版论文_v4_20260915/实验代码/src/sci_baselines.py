"""SCI baseline utilities with a common metric and probability interface."""
from __future__ import annotations

import numpy as np
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.feature_selection import chi2
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    brier_score_loss,
    f1_score,
    log_loss,
)

from src.additional_metrics import calibration_errors


def build_model_candidates(seed: int = 42, num_classes: int = 5):
    """Return representative strong baselines under a shared interface.

    The feature mode is explicit so callers can apply the same train-only
    selector to χ² models while retaining a full-feature RF control.
    """
    from xgboost import XGBClassifier

    return [
        (
            "random_forest",
            RandomForestClassifier(
                n_estimators=100,
                min_samples_leaf=2,
                class_weight="balanced_subsample",
                random_state=seed,
                n_jobs=-1,
            ),
            "all",
        ),
        (
            "extra_trees",
            ExtraTreesClassifier(
                n_estimators=100,
                min_samples_leaf=2,
                class_weight="balanced",
                random_state=seed,
                n_jobs=-1,
            ),
            "chi2",
        ),
        (
            "xgboost",
            XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.9,
                colsample_bytree=0.9,
                objective="multi:softprob",
                num_class=num_classes,
                eval_metric="mlogloss",
                tree_method="hist",
                n_jobs=-1,
                random_state=seed,
            ),
            "chi2",
        ),
    ]


def select_train_features(x, y, k: int = 60):
    """Select χ² top-k columns; caller must provide train-fold-fitted data."""
    values = np.asarray(x, dtype=float)
    if values.ndim != 2 or values.shape[0] != len(y):
        raise ValueError("x and y must have compatible two-dimensional shapes")
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("chi-square inputs must be finite and non-negative")
    if not 1 <= int(k) <= values.shape[1]:
        raise ValueError(f"k must be between 1 and {values.shape[1]}")
    scores, _ = chi2(values, np.asarray(y))
    scores = np.nan_to_num(scores, nan=0.0, posinf=np.finfo(float).max, neginf=0.0)
    # Keep original column order to make downstream model randomness
    # reproducible across scripts.
    return np.sort(np.argsort(-scores, kind="stable")[: int(k)])


def evaluate_predictions(y_true, predicted, probabilities, classes):
    """Compute discrimination and probability-quality metrics."""
    y = np.asarray(y_true)
    pred = np.asarray(predicted)
    p = np.asarray(probabilities, dtype=float)
    labels = np.asarray(classes)
    if p.ndim != 2 or p.shape[0] != len(y) or p.shape[1] != len(labels):
        raise ValueError("probabilities must have shape (n_samples, n_classes)")
    p = np.clip(p, 1e-15, 1.0)
    p = p / p.sum(axis=1, keepdims=True)
    brier = np.mean([
        brier_score_loss((y == label).astype(int), p[:, i])
        for i, label in enumerate(labels)
    ])
    return {
        "accuracy": float(accuracy_score(y, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "macro_f1": float(f1_score(y, pred, average="macro", zero_division=0)),
        "log_loss": float(log_loss(y, p, labels=labels)),
        "brier_macro": float(brier),
        "ece": float(calibration_errors(y, p, class_labels=labels)["ece"]),
    }
