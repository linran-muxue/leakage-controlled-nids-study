"""Simple validation-only temperature scaling for multiclass probabilities."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import log_loss


class TemperatureScaler:
    def __init__(self, temperatures=(0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0)):
        self.temperatures = tuple(float(t) for t in temperatures)
        if not self.temperatures or any(t <= 0 for t in self.temperatures):
            raise ValueError("temperatures must be positive and non-empty")

    @staticmethod
    def _logits(probabilities):
        p = np.asarray(probabilities, dtype=float)
        if p.ndim != 2 or p.shape[1] < 2:
            raise ValueError("probabilities must be a 2-D array with at least two classes")
        p = np.clip(p, 1e-12, 1.0)
        p /= np.maximum(p.sum(axis=1, keepdims=True), np.finfo(float).tiny)
        return np.log(p)

    def fit(self, probabilities, y_true):
        logits = self._logits(probabilities)
        y = np.asarray(y_true)
        if len(y) != len(logits) or len(y) == 0:
            raise ValueError("probabilities and y_true must have equal non-zero length")
        self.classes_ = np.unique(y)
        if len(self.classes_) != logits.shape[1]:
            raise ValueError("y_true must contain one label per probability column")
        class_to_index = {label: i for i, label in enumerate(self.classes_)}
        y_encoded = np.asarray([class_to_index[label] for label in y], dtype=int)
        labels = np.arange(logits.shape[1])
        losses = []
        for temperature in self.temperatures:
            scaled = logits / temperature
            scaled -= scaled.max(axis=1, keepdims=True)
            p = np.exp(scaled); p /= p.sum(axis=1, keepdims=True)
            losses.append(log_loss(y_encoded, p, labels=labels))
        self.temperature_ = float(self.temperatures[int(np.argmin(losses))])
        self.calibration_log_loss_ = float(min(losses))
        return self

    def transform(self, probabilities):
        if not hasattr(self, "temperature_"):
            raise RuntimeError("TemperatureScaler must be fitted before transform")
        logits = self._logits(probabilities) / self.temperature_
        logits -= logits.max(axis=1, keepdims=True)
        p = np.exp(logits); p /= np.maximum(p.sum(axis=1, keepdims=True), np.finfo(float).tiny)
        return p
