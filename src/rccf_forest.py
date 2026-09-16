"""Risk-Calibrated Conformal Forest (RCCF).

The implementation deliberately separates training, calibration and final
prediction.  Risk models are trained from out-of-fold predictions generated
inside the training partition; calibration parameters are fitted only from a
disjoint calibration partition.
"""

from __future__ import annotations

from typing import Sequence
from functools import partial
import warnings

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest, chi2, f_classif, mutual_info_classif
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from src.conformal_rejection import MondrianConformalRejector


DESCRIPTOR_SETS = {
    "all": (0, 1, 2),
    "confidence": (0,),
    "entropy": (1,),
    "margin": (2,),
}


def _descriptor(probabilities: np.ndarray) -> np.ndarray:
    p = np.asarray(probabilities, dtype=float)
    conf = p.max(axis=1)
    order = np.sort(p, axis=1)
    margin = order[:, -1] - order[:, -2] if p.shape[1] > 1 else conf
    entropy = -(p * np.log(np.clip(p, 1e-12, 1.0))).sum(axis=1)
    entropy /= max(np.log(p.shape[1]), 1e-12)
    return np.c_[conf, entropy, margin]


def _selector(name: str, k: int | None, random_state: int | None = None):
    if name == "full":
        return None
    score = {"chi2": chi2, "anova": f_classif}.get(name)
    if name == "mutual_info":
        # mutual_info_classif uses a stochastic nearest-neighbour estimator;
        # bind the seed so feature rankings are reproducible across runs.
        score = partial(mutual_info_classif, random_state=random_state)
    if score is None:
        raise ValueError(f"unknown expert: {name}")
    return SelectKBest(score_func=score, k=k or "all")


class RCCFForest:
    """A risk-calibrated ensemble of feature-selector random forests."""

    expert_names = ("full", "chi2", "mutual_info", "anova")

    def __init__(self, n_estimators=100, feature_k=60, cv=5, random_state=42,
                 max_depth=None, min_samples_leaf=2, n_jobs=-1,
                 class_weight="balanced_subsample", alpha=0.1,
                 risk_C=1.0, descriptor_set="all"):
        if cv < 2 or n_estimators < 1 or feature_k < 1:
            raise ValueError("cv, n_estimators and feature_k must be positive")
        if not 0 < alpha < 1:
            raise ValueError("alpha must be in (0, 1)")
        if descriptor_set not in DESCRIPTOR_SETS:
            raise ValueError(f"descriptor_set must be one of {sorted(DESCRIPTOR_SETS)}")
        if risk_C <= 0:
            raise ValueError("risk_C must be positive")
        self.n_estimators = int(n_estimators)
        self.feature_k = int(feature_k)
        self.cv = int(cv)
        self.random_state = random_state
        self.max_depth = max_depth
        self.min_samples_leaf = int(min_samples_leaf)
        self.n_jobs = n_jobs
        self.class_weight = class_weight
        self.alpha = float(alpha)
        self.risk_C = float(risk_C)
        self.descriptor_set = descriptor_set
        self.descriptor_columns_ = DESCRIPTOR_SETS[descriptor_set]

    def _fit_expert(self, name, X, y, seed):
        selector = _selector(name, min(self.feature_k, X.shape[1]), random_state=seed)
        scaler = MinMaxScaler().fit(X)
        Xs = scaler.transform(X)
        if selector is not None:
            # Constant or degenerate columns are valid after corpus cleaning;
            # suppress the expected ANOVA runtime warning and make its score
            # deterministic rather than allowing a warning to pollute runs.
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=RuntimeWarning)
                warnings.filterwarnings("ignore", category=UserWarning,
                                        module="sklearn.feature_selection._univariate_selection")
                Xs = selector.fit_transform(Xs, y)
        forest = RandomForestClassifier(
            n_estimators=self.n_estimators, random_state=seed,
            max_depth=self.max_depth, min_samples_leaf=self.min_samples_leaf,
            class_weight=self.class_weight, n_jobs=self.n_jobs,
        ).fit(Xs, y)
        return {"name": name, "scaler": scaler, "selector": selector, "forest": forest}

    @staticmethod
    def _transform(expert, X):
        Xs = expert["scaler"].transform(X)
        if expert["selector"] is not None:
            Xs = expert["selector"].transform(Xs)
        return Xs

    def _expert_proba(self, expert, X):
        return expert["forest"].predict_proba(self._transform(expert, X))

    def fit(self, X, y: Sequence, X_cal=None, y_cal=None):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y)
        if X.ndim != 2 or len(X) != len(y):
            raise ValueError("X and y have incompatible shapes")
        self.classes_ = np.unique(y)
        if len(self.classes_) < 2:
            raise ValueError("at least two classes are required")
        self.risk_training_rows_ = len(y)
        self.final_test_rows_seen_ = 0
        splitter = StratifiedKFold(self.cv, shuffle=True, random_state=self.random_state)
        oof = np.zeros((len(y), len(self.expert_names), len(self.classes_)), dtype=float)
        oof_desc = np.zeros((len(y), len(self.expert_names), 3), dtype=float)
        for fold, (tr, va) in enumerate(splitter.split(X, y)):
            for eidx, name in enumerate(self.expert_names):
                expert = self._fit_expert(name, X[tr], y[tr], self.random_state + fold * 97 + eidx)
                p = self._expert_proba(expert, X[va])
                oof[va, eidx] = p
                oof_desc[va, eidx] = _descriptor(p)
        y_idx = np.searchsorted(self.classes_, y)
        desc_cols = self.descriptor_columns_
        risk_features = np.concatenate(
            [oof.reshape(len(y), -1), oof_desc[:, :, desc_cols].reshape(len(y), -1)], axis=1)
        risk_targets = np.stack([(np.argmax(oof[:, i], axis=1) != y_idx).astype(int) for i in range(len(self.expert_names))], axis=1)
        self.risk_models_ = []
        self.risk_scalers_ = []
        for eidx in range(len(self.expert_names)):
            scaler = StandardScaler().fit(risk_features)
            scaled = scaler.transform(risk_features)
            target = risk_targets[:, eidx]
            model = LogisticRegression(C=self.risk_C, class_weight="balanced",
                                       max_iter=400, random_state=self.random_state)
            if np.unique(target).size == 1:
                model = float(target[0])
            else:
                model.fit(scaled, target)
            self.risk_scalers_.append(scaler)
            self.risk_models_.append(model)
        self.experts_ = [self._fit_expert(name, X, y, self.random_state + i) for i, name in enumerate(self.expert_names)]
        self.calibration_classes_ = self.classes_.copy()
        if X_cal is None or y_cal is None:
            X_cal, y_cal = X, y
        p_cal = self._raw_predict_proba(np.asarray(X_cal, dtype=float))
        self.temperature_ = self._fit_temperature(p_cal, np.asarray(y_cal))
        p_cal = self._temperature_transform(p_cal)
        self.conformal_ = MondrianConformalRejector(alpha=self.alpha)
        self.conformal_.fit(p_cal, np.asarray(y_cal), self.classes_)
        self.calibration_rows_ = len(y_cal)
        return self

    def _risk_vector(self, feature_matrix, idx):
        model = self.risk_models_[idx]
        if isinstance(model, float):
            return np.full(len(feature_matrix), model)
        scaled = self.risk_scalers_[idx].transform(feature_matrix)
        return model.predict_proba(scaled)[:, 1]

    def _raw_predict_proba(self, X):
        probs = [self._expert_proba(expert, X) for expert in self.experts_]
        descriptors = [_descriptor(p) for p in probs]
        desc_cols = self.descriptor_columns_
        joined = np.concatenate(probs + [d[:, desc_cols] for d in descriptors], axis=1)
        risks = np.stack([self._risk_vector(joined, i) for i in range(len(self.experts_))], axis=1)
        weights = np.exp(-np.clip(risks, 0.0, 20.0))
        weights /= np.maximum(weights.sum(axis=1, keepdims=True), 1e-12)
        fused = np.sum(np.stack(probs, axis=1) * weights[:, :, None], axis=1)
        self.row_risk_ = np.sum(risks * weights, axis=1)
        self.expert_weights_ = weights
        return fused

    @staticmethod
    def _fit_temperature(probabilities, y):
        labels = np.unique(y)
        yi = np.searchsorted(labels, y)
        logits = np.log(np.clip(probabilities, 1e-12, 1.0))
        candidates = np.asarray((0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0))
        losses = []
        for t in candidates:
            z = logits / t; z -= z.max(axis=1, keepdims=True)
            p = np.exp(z); p /= p.sum(axis=1, keepdims=True)
            losses.append(log_loss(yi, p, labels=np.arange(probabilities.shape[1])))
        return float(candidates[int(np.argmin(losses))])

    def _temperature_transform(self, probabilities):
        z = np.log(np.clip(probabilities, 1e-12, 1.0)) / self.temperature_
        z -= z.max(axis=1, keepdims=True)
        p = np.exp(z); return p / np.maximum(p.sum(axis=1, keepdims=True), 1e-12)

    def predict_proba(self, X):
        if not hasattr(self, "experts_"):
            raise RuntimeError("RCCFForest must be fitted before prediction")
        return self._temperature_transform(self._raw_predict_proba(np.asarray(X, dtype=float)))

    def predict(self, X):
        return self.classes_[np.argmax(self.predict_proba(X), axis=1)]

    def predict_selective(self, X):
        p = self.predict_proba(X)
        labels = self.classes_[np.argmax(p, axis=1)].astype(object)
        pvals = self.conformal_.p_values(p)
        reject = pvals[np.arange(len(p)), np.argmax(p, axis=1)] < self.alpha
        labels[reject] = "unknown"
        return labels, reject
