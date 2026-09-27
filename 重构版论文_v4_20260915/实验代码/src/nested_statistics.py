from __future__ import annotations

import itertools
import numpy as np


def exact_sign_permutation(deltas):
    d = np.asarray(deltas, dtype=float)
    if d.ndim != 1 or len(d) == 0:
        raise ValueError("deltas must be non-empty one-dimensional")
    observed = abs(float(d.mean()))
    values = []
    for signs in itertools.product((-1.0, 1.0), repeat=len(d)):
        values.append(abs(float((d * np.asarray(signs)).mean())))
    return float(np.mean(np.asarray(values) >= observed - 1e-15))


def paired_fold_summary(a, b, seed=42, n_bootstrap=3000, confidence=.95):
    a = np.asarray(a, dtype=float); b = np.asarray(b, dtype=float)
    if a.ndim != 1 or a.shape != b.shape or len(a) == 0:
        raise ValueError("paired fold arrays must be non-empty and equal length")
    delta = b - a
    rng = np.random.default_rng(seed)
    vals = np.array([delta[rng.integers(0, len(delta), len(delta))].mean() for _ in range(int(n_bootstrap))])
    alpha = (1 - confidence) / 2
    return {"mean_delta": float(delta.mean()), "ci_low": float(np.quantile(vals, alpha)), "ci_high": float(np.quantile(vals, 1-alpha)), "permutation_p": exact_sign_permutation(delta), "n_folds": int(len(delta))}
