from __future__ import annotations
import numpy as np
from sklearn.metrics import brier_score_loss, log_loss
from src.additional_metrics import calibration_errors

def _prob_metrics(y_true, probabilities, classes):
    y = np.asarray(y_true); p = np.asarray(probabilities, dtype=float); c = np.asarray(classes)
    return {
        "log_loss": float(log_loss(y, p, labels=c)),
        "brier_macro": float(np.mean([brier_score_loss((y == label).astype(int), p[:, i]) for i, label in enumerate(c)])),
        "ece": float(calibration_errors(y, p, class_labels=c)["ece"]),
    }

def bootstrap_probability_metrics(y_true, probabilities, classes, n_bootstrap=3000, confidence=.95, seed=42):
    y = np.asarray(y_true); p = np.asarray(probabilities); rng = np.random.default_rng(seed)
    values = {k: [] for k in ["log_loss", "brier_macro", "ece"]}
    for _ in range(int(n_bootstrap)):
        idx = rng.integers(0, len(y), len(y))
        m = _prob_metrics(y[idx], p[idx], classes)
        for k in values: values[k].append(m[k])
    alpha = (1-confidence)/2
    return {k: (float(np.quantile(v, alpha)), float(_prob_metrics(y,p,classes)[k]), float(np.quantile(v, 1-alpha))) for k,v in values.items()}

def paired_bootstrap_delta(y_true, pred_a, pred_b, n_bootstrap=3000, confidence=.95, seed=42):
    y = np.asarray(y_true); a = np.asarray(pred_a); b = np.asarray(pred_b); rng = np.random.default_rng(seed)
    from sklearn.metrics import f1_score
    point = float(f1_score(y,b,average='macro',zero_division=0)-f1_score(y,a,average='macro',zero_division=0))
    vals=[]
    for _ in range(int(n_bootstrap)):
        idx=rng.integers(0,len(y),len(y)); vals.append(float(f1_score(y[idx],b[idx],average='macro',zero_division=0)-f1_score(y[idx],a[idx],average='macro',zero_division=0)))
    alpha=(1-confidence)/2
    return {"low":float(np.quantile(vals,alpha)),"point":point,"high":float(np.quantile(vals,1-alpha))}
