"""Small, dependency-light metrics used by the publication audit."""
from __future__ import annotations

import numpy as np


def calibration_errors(y_true, probabilities, n_bins=10, class_labels=None):
    y = np.asarray(y_true)
    p = np.asarray(probabilities, dtype=float)
    if p.ndim == 2:
        confidence = p.max(axis=1)
        if class_labels is not None:
            labels = np.asarray(class_labels)
            if labels.ndim != 1 or labels.size != p.shape[1]:
                raise ValueError("class_labels must match probability columns")
            predicted = labels[p.argmax(axis=1)]
            correct = (predicted == y).astype(float)
        else:
            correct = (p.argmax(axis=1) == y).astype(float)
    else:
        confidence = p.ravel()
        correct = y.astype(float)
    if len(confidence) == 0 or len(confidence) != len(correct):
        raise ValueError("inputs must have equal non-zero length")
    edges = np.linspace(0.0, 1.0, int(n_bins) + 1)
    ece = 0.0
    mce = 0.0
    for i in range(int(n_bins)):
        mask = (confidence >= edges[i]) & ((confidence < edges[i + 1]) if i < n_bins - 1 else (confidence <= edges[i + 1]))
        if not np.any(mask):
            continue
        gap = abs(float(correct[mask].mean()) - float(confidence[mask].mean()))
        ece += float(mask.mean()) * gap
        mce = max(mce, gap)
    return {"ece": float(ece), "mce": float(mce)}


def holm_adjust(p_values):
    values = np.asarray(list(p_values), dtype=float)
    if np.any((values < 0) | (values > 1)):
        raise ValueError("p-values must be in [0, 1]")
    order = np.argsort(values)
    adjusted_sorted = np.minimum(1.0, (len(values) - np.arange(len(values))) * values[order])
    adjusted_sorted = np.maximum.accumulate(adjusted_sorted)
    result = np.empty_like(adjusted_sorted)
    result[order] = adjusted_sorted
    return [float(x) for x in result]


def relative_metric_drop(clean, perturbed):
    clean = float(clean)
    perturbed = float(perturbed)
    if clean == 0:
        raise ValueError("clean metric must be non-zero")
    return float((clean - perturbed) / clean)


def percentile_latency(values):
    values = np.asarray(list(values), dtype=float)
    if values.size == 0:
        raise ValueError("values must be non-empty")
    return {"p50": float(np.percentile(values, 50)), "p95": float(np.percentile(values, 95)), "p99": float(np.percentile(values, 99))}
