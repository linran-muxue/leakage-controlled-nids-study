"""Validation-only rejection and selective-risk utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score


def _confidence(probabilities):
    p = np.asarray(probabilities, dtype=float)
    if p.ndim != 2 or p.shape[1] < 2:
        raise ValueError("probabilities must be a 2-D array with at least two classes")
    p = np.clip(p, 0.0, 1.0)
    p /= np.maximum(p.sum(axis=1, keepdims=True), np.finfo(float).tiny)
    return p.max(axis=1)


def fit_rejection_threshold(probabilities, target_coverage: float = 0.95) -> float:
    """Fit a confidence threshold using known validation rows only."""
    if not 0 < target_coverage <= 1:
        raise ValueError("target_coverage must be in (0, 1]")
    confidence = _confidence(probabilities)
    # Select the largest threshold that retains at least the requested
    # empirical coverage.  This is deterministic and never inspects unknowns.
    threshold = float(np.quantile(confidence, 1.0 - target_coverage, method="lower"))
    return float(np.clip(threshold, 0.0, 1.0))


def apply_rejection(probabilities, classes, threshold: float) -> np.ndarray:
    p = np.asarray(probabilities, dtype=float)
    labels = np.asarray(classes)
    if p.ndim != 2 or p.shape[1] != len(labels):
        raise ValueError("probability columns must match classes")
    confidence = _confidence(p)
    pred = labels[np.argmax(p, axis=1)].astype(object)
    pred[confidence < float(threshold)] = "unknown"
    return pred


def risk_coverage_curve(y_true, probabilities, classes) -> pd.DataFrame:
    y = np.asarray(y_true)
    p = np.asarray(probabilities, dtype=float)
    confidence = _confidence(p)
    pred = np.asarray(classes)[np.argmax(p, axis=1)]
    rows = []
    for threshold in np.unique(np.sort(confidence)[::-1]):
        keep = confidence >= threshold
        coverage = float(np.mean(keep))
        risk = float(np.mean(pred[keep] != y[keep])) if np.any(keep) else 0.0
        rows.append({"coverage": coverage, "selective_risk": risk, "threshold": float(threshold)})
    if not rows or rows[-1]["coverage"] < 1.0:
        rows.append({"coverage": 1.0, "selective_risk": float(np.mean(pred != y)), "threshold": 0.0})
    return pd.DataFrame(rows).sort_values("coverage", kind="stable").reset_index(drop=True)


def open_set_metrics(known_scores, unknown_scores, threshold: float) -> dict:
    known = np.asarray(known_scores, dtype=float).reshape(-1)
    unknown = np.asarray(unknown_scores, dtype=float).reshape(-1)
    if known.size == 0 or unknown.size == 0:
        raise ValueError("known_scores and unknown_scores must both be non-empty")
    scores = np.concatenate([known, unknown])
    truth = np.concatenate([np.zeros(known.size, dtype=int), np.ones(unknown.size, dtype=int)])
    rejected_known = known >= threshold
    rejected_unknown = unknown >= threshold
    return {
        "auroc": float(roc_auc_score(truth, scores)),
        "aupr": float(average_precision_score(truth, scores)),
        "unknown_recall": float(np.mean(rejected_unknown)),
        "known_false_rejection_rate": float(np.mean(rejected_known)),
        "known_count": int(known.size),
        "unknown_count": int(unknown.size),
        "threshold": float(threshold),
    }

