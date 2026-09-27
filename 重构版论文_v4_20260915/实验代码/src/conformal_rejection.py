"""Mondrian-style class-conditional conformal rejection for known classes."""

from __future__ import annotations

import numpy as np


class MondrianConformalRejector:
    """Split-conformal predictor using class-conditional nonconformity scores.

    Calibration rows must be known-class rows and are never mixed with unknown
    attacks.  Prediction returns the argmax class when its conformal p-value
    exceeds ``alpha``; otherwise it returns ``unknown``.
    """

    def __init__(self, alpha: float = 0.1, unknown_label: str = "unknown"):
        if not 0 < alpha < 1:
            raise ValueError("alpha must be in (0, 1)")
        self.alpha = float(alpha)
        self.unknown_label = unknown_label

    def fit(self, probabilities, y_true, classes):
        p = np.asarray(probabilities, dtype=float)
        y = np.asarray(y_true)
        self.classes_ = np.asarray(classes)
        if p.ndim != 2 or p.shape[1] != len(self.classes_) or len(p) != len(y) or len(y) == 0:
            raise ValueError("calibration arrays have incompatible shapes")
        self.calibration_scores_ = {}
        for idx, label in enumerate(self.classes_):
            mask = y == label
            if not np.any(mask):
                raise ValueError(f"calibration set lacks class {label}")
            # Nonconformity is one minus probability assigned to the true class.
            self.calibration_scores_[label] = np.sort(1.0 - np.clip(p[mask, idx], 0.0, 1.0))
        return self

    def p_values(self, probabilities):
        if not hasattr(self, "classes_"):
            raise RuntimeError("rejector must be fitted before prediction")
        p = np.asarray(probabilities, dtype=float)
        if p.ndim != 2 or p.shape[1] != len(self.classes_):
            raise ValueError("probabilities have incompatible shape")
        p_values = np.zeros_like(p)
        for idx, label in enumerate(self.classes_):
            scores = self.calibration_scores_[label]
            nonconformity = 1.0 - np.clip(p[:, idx], 0.0, 1.0)
            # Plus-one correction yields finite-sample conservative p-values.
            greater_equal = len(scores) - np.searchsorted(scores, nonconformity, side="left")
            p_values[:, idx] = (1.0 + greater_equal) / (len(scores) + 1.0)
        return p_values

    def predict(self, probabilities):
        p = np.asarray(probabilities, dtype=float)
        pvals = self.p_values(p)
        best = np.argmax(p, axis=1)
        labels = self.classes_[best].astype(object)
        labels[pvals[np.arange(len(p)), best] < self.alpha] = self.unknown_label
        return labels
