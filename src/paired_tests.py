from __future__ import annotations

import numpy as np
from scipy.stats import binomtest


def mcnemar_exact(y_true, pred_a, pred_b):
    y_true, pred_a, pred_b = map(np.asarray, (y_true, pred_a, pred_b))
    if not (len(y_true) == len(pred_a) == len(pred_b) and len(y_true) > 0):
        raise ValueError("paired arrays must have equal non-zero length")
    a_correct = pred_a == y_true
    b_correct = pred_b == y_true
    b01 = int(np.count_nonzero(a_correct & ~b_correct))
    b10 = int(np.count_nonzero(~a_correct & b_correct))
    result = binomtest(min(b01, b10), n=b01 + b10, p=0.5, alternative="two-sided") if b01 + b10 else None
    return {"a_only_correct": b01, "b_only_correct": b10, "p_value": 1.0 if result is None else float(result.pvalue)}
