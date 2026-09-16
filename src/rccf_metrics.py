"""Metrics used by the RCCF selective/open-set evaluation."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import balanced_accuracy_score, f1_score, log_loss, precision_score, recall_score


def _ece_mce(y_idx, p, bins=10):
    conf = p.max(axis=1); pred = p.argmax(axis=1); correct = (pred == y_idx)
    edges = np.linspace(0.0, 1.0, bins + 1); gaps=[]; ece=0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (conf >= lo) & (conf <= hi if hi == 1 else conf < hi)
        if not mask.any(): continue
        gap = abs(float(correct[mask].mean()) - float(conf[mask].mean()))
        gaps.append(gap); ece += mask.mean() * gap
    return float(ece), float(max(gaps, default=0.0))


def classification_metrics(y_true, probabilities, classes):
    y = np.asarray(y_true); p = np.asarray(probabilities, dtype=float); labels = np.asarray(classes)
    if p.ndim != 2 or p.shape[1] != len(labels) or len(y) != len(p):
        raise ValueError("incompatible labels and probabilities")
    yi = np.searchsorted(labels, y); pred = labels[p.argmax(axis=1)]
    ece, mce = _ece_mce(yi, p)
    onehot = np.eye(len(labels))[yi]
    return {"accuracy": float(np.mean(pred == y)),
            "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
            "macro_precision": float(precision_score(y, pred, labels=labels, average="macro", zero_division=0)),
            "macro_recall": float(recall_score(y, pred, labels=labels, average="macro", zero_division=0)),
            "macro_f1": float(f1_score(y, pred, labels=labels, average="macro", zero_division=0)),
            "log_loss": float(log_loss(yi, p, labels=np.arange(len(labels)))),
            "brier": float(np.mean((p - onehot) ** 2)), "ece": ece, "mce": mce}


def selective_metrics(y_true, probabilities, classes):
    y = np.asarray(y_true); p = np.asarray(probabilities, dtype=float); labels = np.asarray(classes)
    pred = labels[p.argmax(axis=1)]; conf = p.max(axis=1); order = np.argsort(-conf, kind="mergesort")
    sorted_error = (pred[order] != y[order]).astype(float)
    coverage = np.arange(1, len(y)+1) / len(y)
    risk = np.cumsum(sorted_error) / np.arange(1, len(y)+1)
    aurc = float(np.trapezoid(risk, coverage)) if len(y) > 1 else float(risk[0])
    out = {"aurc": aurc}
    for target in (0.90, 0.95):
        n = max(1, int(np.ceil(target * len(y))))
        out[f"risk_at_{int(target*100)}"] = float(risk[n-1])
    return out


def bootstrap_metric_ci(y_true, p_a, p_b=None, classes=None, metric="macro_f1", n_resamples=2000, seed=42):
    y=np.asarray(y_true); rng=np.random.default_rng(seed); n=len(y); vals=[]
    for _ in range(n_resamples):
        idx=rng.integers(0,n,n); pa=np.asarray(p_a)[idx]
        if p_b is None: vals.append(classification_metrics(y[idx],pa,classes)[metric])
        else: vals.append(classification_metrics(y[idx],pa,classes)[metric]-classification_metrics(y[idx],np.asarray(p_b)[idx],classes)[metric])
    return {"estimate": float(np.mean(vals)), "lower": float(np.quantile(vals,.025)), "upper": float(np.quantile(vals,.975))}


def paired_sign_flip(differences, n_permutations=65536, seed=42):
    d=np.asarray(differences,dtype=float); observed=float(d.mean()); rng=np.random.default_rng(seed)
    if len(d) <= 12:
        signs=np.array(np.meshgrid(*[[-1.,1.]]*len(d))).T.reshape(-1,len(d))
        null=np.mean(signs*d,axis=1)
    else:
        null=np.mean(rng.choice([-1.,1.],size=(n_permutations,len(d)))*d,axis=1)
    return {"estimate": observed, "p_value": float((np.sum(np.abs(null)>=abs(observed))+1)/(len(null)+1))}


def holm_adjust(p_values):
    p=np.asarray(p_values,dtype=float); order=np.argsort(p); adj=np.empty(len(p)); running=0.0
    for rank, idx in enumerate(order):
        running=max(running, min(1.0, (len(p)-rank)*p[idx])); adj[idx]=running
    return adj
