"""Dual-layer Reliability--Cost Random Forest (DRC-Forest).

The estimator keeps all learned quantities on the training/validation side:
tree reliabilities are measured on ``X_valid, y_valid`` and class costs are
computed from the training class counts.  Test data are only passed to the
prediction methods after fitting is complete.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, recall_score


class DRCForest:
    """Random forest with class-conditional reliability and cost fusion."""

    def __init__(
        self,
        n_estimators: int = 100,
        random_state: int | None = 42,
        max_depth: int | None = None,
        n_jobs: int = -1,
        min_samples_leaf: int = 1,
        class_weight: str | dict | None = "balanced_subsample",
        cost_beta: float = 0.5,
        cost_min: float = 0.5,
        cost_max: float = 2.0,
        epsilon: float = 1e-12,
    ) -> None:
        if n_estimators < 1:
            raise ValueError("n_estimators must be positive")
        if min_samples_leaf < 1:
            raise ValueError("min_samples_leaf must be positive")
        if cost_beta < 0:
            raise ValueError("cost_beta must be non-negative")
        if cost_min <= 0 or cost_max < cost_min:
            raise ValueError("require 0 < cost_min <= cost_max")
        if epsilon <= 0:
            raise ValueError("epsilon must be positive")
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.max_depth = max_depth
        self.n_jobs = n_jobs
        self.min_samples_leaf = min_samples_leaf
        self.class_weight = class_weight
        self.cost_beta = float(cost_beta)
        self.cost_min = float(cost_min)
        self.cost_max = float(cost_max)
        self.epsilon = float(epsilon)

    def fit(self, X, y: Sequence, X_valid, y_valid):
        self.model_ = RandomForestClassifier(
            n_estimators=self.n_estimators,
            random_state=self.random_state,
            max_depth=self.max_depth,
            n_jobs=self.n_jobs,
            min_samples_leaf=self.min_samples_leaf,
            class_weight=self.class_weight,
        )
        self.model_.fit(X, y)
        self.classes_ = np.asarray(self.model_.classes_)
        n_classes = len(self.classes_)

        # Class costs are derived strictly from the training labels.
        _, counts = np.unique(np.asarray(y), return_counts=True)
        mean_count = float(np.mean(counts))
        raw_costs = (mean_count / counts.astype(float)) ** self.cost_beta
        self.class_costs_ = np.clip(raw_costs, self.cost_min, self.cost_max)

        y_valid_arr = np.asarray(y_valid)
        reliability = np.zeros((len(self.model_.estimators_), n_classes), dtype=float)
        for tree_idx, tree in enumerate(self.model_.estimators_):
            pred = self._map_tree_labels(tree.predict(X_valid))
            f1 = f1_score(
                y_valid_arr,
                pred,
                labels=self.classes_,
                average=None,
                zero_division=0,
            )
            rec = recall_score(
                y_valid_arr,
                pred,
                labels=self.classes_,
                average=None,
                zero_division=0,
            )
            reliability[tree_idx] = np.sqrt(np.maximum(f1, 0.0) * np.maximum(rec, 0.0))
        self.reliability_ = np.nan_to_num(reliability, nan=0.0, posinf=0.0, neginf=0.0)
        self.tree_class_weights_ = self._normalize_columns(self.reliability_ + self.epsilon)
        return self

    def _map_tree_labels(self, labels):
        """Map a sklearn tree's encoded labels back to the forest labels."""
        arr = np.asarray(labels)
        if np.issubdtype(self.classes_.dtype, np.number):
            return arr.astype(self.classes_.dtype, copy=False)
        encoded = arr.astype(int)
        return self.classes_[encoded]

    @staticmethod
    def _normalize_columns(values: np.ndarray) -> np.ndarray:
        denominator = values.sum(axis=0, keepdims=True)
        return values / np.maximum(denominator, np.finfo(float).tiny)

    def predict_proba(self, X):
        self._check_fitted()
        n_samples = len(X)
        n_classes = len(self.classes_)
        fused = np.zeros((n_samples, n_classes), dtype=float)
        for tree_idx, tree in enumerate(self.model_.estimators_):
            tree_proba = tree.predict_proba(X)
            # RandomForest trees use the forest's integer-encoded class order;
            # account for a missing class defensively if a backend omits it.
            aligned = np.zeros_like(fused)
            tree_classes = np.asarray(tree.classes_)
            for col, tree_label in enumerate(tree_classes):
                if np.issubdtype(self.classes_.dtype, np.number):
                    label_index = int(tree_label)
                else:
                    label_index = int(tree_label)
                if 0 <= label_index < n_classes:
                    aligned[:, label_index] = tree_proba[:, col]
            fused += aligned * self.tree_class_weights_[tree_idx][None, :]

        weighted = fused * self.class_costs_[None, :]
        normalizer = weighted.sum(axis=1, keepdims=True)
        probabilities = weighted / np.maximum(normalizer, np.finfo(float).tiny)
        return np.nan_to_num(probabilities, nan=1.0 / n_classes, posinf=0.0, neginf=0.0)

    def predict(self, X):
        probabilities = self.predict_proba(X)
        return self.classes_[np.argmax(probabilities, axis=1)]

    def _check_fitted(self):
        if not hasattr(self, "model_"):
            raise RuntimeError("DRCForest must be fitted before prediction")

