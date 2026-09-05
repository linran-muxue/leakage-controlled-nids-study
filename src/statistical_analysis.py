from __future__ import annotations

import numpy as np
from sklearn.metrics import accuracy_score, f1_score


def _metric(y_true, y_pred, metric):
    if metric == "accuracy":
        return float(accuracy_score(y_true, y_pred))
    if metric == "macro_f1":
        return float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    raise ValueError("metric must be 'accuracy' or 'macro_f1'")


def bootstrap_metric_ci(y_true, y_pred, metric="macro_f1", n_bootstrap=2000, confidence=0.95, seed=42):
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    if len(y_true) != len(y_pred) or len(y_true) == 0:
        raise ValueError("y_true and y_pred must have equal non-zero length")
    rng = np.random.default_rng(seed)
    values = np.empty(n_bootstrap, dtype=float)
    for i in range(n_bootstrap):
        idx = rng.integers(0, len(y_true), len(y_true))
        values[i] = _metric(y_true[idx], y_pred[idx], metric)
    alpha = (1 - confidence) / 2
    return tuple(float(x) for x in (np.quantile(values, alpha), _metric(y_true, y_pred, metric), np.quantile(values, 1 - alpha)))


def paired_permutation_accuracy(y_true, pred_a, pred_b, n_permutations=10000, seed=42):
    y_true = np.asarray(y_true)
    pred_a = np.asarray(pred_a)
    pred_b = np.asarray(pred_b)
    if not (len(y_true) == len(pred_a) == len(pred_b) and len(y_true) > 0):
        raise ValueError("paired arrays must have equal non-zero length")
    correct_a = (pred_a == y_true).astype(np.int8)
    correct_b = (pred_b == y_true).astype(np.int8)
    observed = float(correct_b.mean() - correct_a.mean())
    rng = np.random.default_rng(seed)
    diffs = np.empty(n_permutations, dtype=float)
    base = correct_b - correct_a
    for i in range(n_permutations):
        signs = rng.choice(np.array([-1, 1], dtype=np.int8), size=len(base))
        diffs[i] = float((base * signs).mean())
    # Account for floating-point representations of fractions such as 1/505.
    tolerance = 1e-15
    p_value = float((np.count_nonzero(np.abs(diffs) >= abs(observed) - tolerance) + 1) / (n_permutations + 1))
    return observed, p_value
