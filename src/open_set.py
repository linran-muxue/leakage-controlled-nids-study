from __future__ import annotations

import numpy as np
from sklearn.metrics import roc_auc_score


def reject_by_threshold(probabilities, known_labels, threshold=0.7, unknown_label="unknown"):
    p = np.asarray(probabilities, dtype=float); labels = np.asarray(known_labels)
    if p.ndim != 2 or p.shape[1] != len(labels):
        raise ValueError("probabilities and known_labels have incompatible shapes")
    idx = p.argmax(axis=1); confidence = p.max(axis=1)
    result = labels[idx].astype(object)
    result[confidence < float(threshold)] = unknown_label
    return result


def open_set_scores(y_true, probabilities, known_labels, threshold=0.7, unknown_label="unknown"):
    y = np.asarray(y_true); p = np.asarray(probabilities, dtype=float); labels = np.asarray(known_labels)
    pred = reject_by_threshold(p, labels, threshold, unknown_label)
    unknown_true = y == unknown_label
    unknown_pred = pred == unknown_label
    unknown_recall = float((unknown_pred & unknown_true).sum() / max(1, unknown_true.sum()))
    # Anomaly score is one minus maximum known-class probability.
    score = 1.0 - p.max(axis=1)
    binary_true = unknown_true.astype(int)
    auc = float(roc_auc_score(binary_true, score)) if len(np.unique(binary_true)) == 2 else float("nan")
    return {"unknown_recall": unknown_recall, "unknown_auroc": auc, "coverage": float((~unknown_pred).mean()), "rejected_count": int(unknown_pred.sum())}
