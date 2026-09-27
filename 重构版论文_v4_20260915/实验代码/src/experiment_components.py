from __future__ import annotations

from typing import Sequence

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import chi2
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)


def select_chi2_features(X: pd.DataFrame, y: Sequence, k: int = 20):
    """Rank non-negative features with chi-square and return the top k."""
    if k < 1 or k > X.shape[1]:
        raise ValueError(f"k must be between 1 and {X.shape[1]}")
    values = np.asarray(X, dtype=float)
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("chi-square features must be finite and non-negative")
    scores, p_values = chi2(values, np.asarray(y))
    scores = np.nan_to_num(scores, nan=0.0, posinf=np.finfo(float).max, neginf=0.0)
    p_values = np.nan_to_num(p_values, nan=1.0, posinf=1.0, neginf=0.0)
    ranking = pd.DataFrame({"feature": list(X.columns), "chi2": scores, "p_value": p_values})
    ranking = ranking.sort_values(["chi2", "feature"], ascending=[False, True], kind="mergesort").reset_index(drop=True)
    ranking["rank"] = np.arange(1, len(ranking) + 1)
    return ranking.head(k)["feature"].tolist(), ranking


class WeightedRandomForest:
    """Random forest with validation-score weighted soft voting."""

    def __init__(self, n_estimators=200, random_state=42, max_depth=None, n_jobs=-1, min_samples_leaf=1, weight_metric="balanced_accuracy"):
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.max_depth = max_depth
        self.n_jobs = n_jobs
        self.min_samples_leaf = min_samples_leaf
        self.weight_metric = weight_metric

    def fit(self, X, y, X_valid, y_valid):
        self.model_ = RandomForestClassifier(
            n_estimators=self.n_estimators,
            random_state=self.random_state,
            max_depth=self.max_depth,
            n_jobs=self.n_jobs,
            min_samples_leaf=self.min_samples_leaf,
            class_weight="balanced_subsample",
        )
        self.model_.fit(X, y)
        scores = []
        for tree in self.model_.estimators_:
            pred = tree.predict(X_valid)
            # Individual sklearn trees may expose integer-encoded predictions
            # even when the forest was trained with string labels. Map them
            # back through the forest's class order before scoring.
            if not np.issubdtype(np.asarray(y_valid).dtype, np.number):
                pred = self.model_.classes_[pred.astype(int)]
            if self.weight_metric == "balanced_accuracy":
                score = balanced_accuracy_score(y_valid, pred)
            elif self.weight_metric == "accuracy":
                score = accuracy_score(y_valid, pred)
            elif self.weight_metric == "macro_f1":
                score = f1_score(y_valid, pred, average="macro", zero_division=0)
            else:
                raise ValueError("weight_metric must be balanced_accuracy, accuracy, or macro_f1")
            scores.append(score)
        scores = np.asarray(scores, dtype=float)
        eps = 1e-12
        self.tree_scores_ = scores
        self.tree_weights_ = (scores + eps) / (scores.sum() + eps * len(scores))
        self.classes_ = self.model_.classes_
        return self

    def predict_proba(self, X):
        probabilities = np.zeros((len(X), len(self.classes_)), dtype=float)
        class_index = {label: i for i, label in enumerate(self.classes_)}
        for weight, tree in zip(self.tree_weights_, self.model_.estimators_):
            tree_proba = tree.predict_proba(X)
            for i, label in enumerate(tree.classes_):
                if not np.issubdtype(np.asarray(self.classes_).dtype, np.number) and isinstance(label, (int, float, np.integer, np.floating)):
                    label = self.classes_[int(label)]
                probabilities[:, class_index[label]] += weight * tree_proba[:, i]
        return probabilities

    def predict(self, X):
        return self.classes_[np.argmax(self.predict_proba(X), axis=1)]


def compute_metrics(y_true, y_pred):
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "macro_precision": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "macro_recall": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
    }


def summarize_tree_weights(scores, weights):
    scores = np.asarray(scores, dtype=float)
    weights = np.asarray(weights, dtype=float)
    if len(scores) == 0 or len(scores) != len(weights):
        raise ValueError("scores and weights must have equal non-zero length")
    mean_weight = float(weights.mean())
    weight_std = float(weights.std(ddof=0))
    positive = weights[weights > 0]
    entropy = float(-(positive * np.log(positive)).sum())
    max_entropy = float(np.log(len(weights))) if len(weights) > 1 else 1.0
    return {
        "tree_count": int(len(scores)),
        "score_mean": float(scores.mean()),
        "score_std": float(scores.std(ddof=0)),
        "score_min": float(scores.min()),
        "score_max": float(scores.max()),
        "weight_min": float(weights.min()),
        "weight_max": float(weights.max()),
        "weight_cv": float(weight_std / mean_weight) if mean_weight else 0.0,
        "normalized_weight_entropy": float(entropy / max_entropy) if len(weights) > 1 else 1.0,
    }
