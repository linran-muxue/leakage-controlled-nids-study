"""Cross-fitted risk-gated forest (CFRG-Forest).

The gate is trained from out-of-bag (OOB) tree predictions only.  At
prediction time it produces a sample-conditional reliability score for each
tree, instead of a fixed validation-derived tree weight.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_sample_weight

try:  # sklearn keeps these helpers private but stable across supported versions.
    from sklearn.ensemble._forest import _generate_sample_indices, _get_n_samples_bootstrap
except ImportError:  # pragma: no cover
    _generate_sample_indices = None
    _get_n_samples_bootstrap = None


def tree_probability_tensor(forest: RandomForestClassifier, X) -> np.ndarray:
    """Return aligned per-tree probabilities with shape (rows, trees, classes)."""
    if not hasattr(forest, "estimators_"):
        raise RuntimeError("forest must be fitted")
    classes = np.asarray(forest.classes_)
    n_rows = len(X)
    out = np.zeros((n_rows, len(forest.estimators_), len(classes)), dtype=float)
    for t, tree in enumerate(forest.estimators_):
        raw = np.asarray(tree.predict_proba(X), dtype=float)
        # sklearn's forest stores classes_ in the original label space, while
        # individual trees may expose encoded integer classes.  Align by the
        # forest class order when labels are strings; fall back to integer
        # positions only for genuinely numeric labels.
        for col, tree_label in enumerate(np.asarray(tree.classes_)):
            matches = np.flatnonzero(classes == tree_label)
            if len(matches):
                out[:, t, int(matches[0])] = raw[:, col]
            else:
                try:
                    encoded_label = int(tree_label)
                except (TypeError, ValueError):
                    continue
                if 0 <= encoded_label < len(classes):
                    out[:, t, encoded_label] = raw[:, col]
    out = np.clip(out, 0.0, 1.0)
    out /= np.maximum(out.sum(axis=2, keepdims=True), np.finfo(float).tiny)
    return out


def tree_descriptor_tensor(tree_probabilities: np.ndarray, epsilon: float = 1e-12, valid_mask: np.ndarray | None = None) -> np.ndarray:
    """Build confidence, normalized entropy, margin, and modal agreement."""
    p = np.asarray(tree_probabilities, dtype=float)
    if p.ndim != 3:
        raise ValueError("tree_probabilities must have shape (rows, trees, classes)")
    confidence = p.max(axis=2)
    order = np.sort(p, axis=2)
    margin = order[:, :, -1] - order[:, :, -2] if p.shape[2] > 1 else confidence
    entropy = -(p * np.log(np.clip(p, epsilon, 1.0))).sum(axis=2)
    entropy /= max(np.log(p.shape[2]), epsilon)
    tree_labels = np.argmax(p, axis=2)
    if valid_mask is None:
        valid = np.ones(tree_labels.shape, dtype=bool)
    else:
        valid = np.asarray(valid_mask, dtype=bool)
        if valid.shape != tree_labels.shape:
            raise ValueError("valid_mask must have shape (rows, trees)")
    modal = np.zeros(len(tree_labels), dtype=int)
    for row_idx in range(len(tree_labels)):
        candidates = tree_labels[row_idx][valid[row_idx]]
        modal[row_idx] = np.bincount(candidates, minlength=p.shape[2]).argmax() if len(candidates) else 0
    agreement = ((tree_labels == modal[:, None]) & valid).astype(float)
    if valid_mask is not None:
        confidence = np.where(valid, confidence, 0.0)
        entropy = np.where(valid, entropy, 0.0)
        margin = np.where(valid, margin, 0.0)
    return np.stack([confidence, entropy, margin, agreement], axis=2)


def tree_oob_mask(forest: RandomForestClassifier, n_samples: int) -> np.ndarray:
    """Reconstruct the fitted forest's OOB membership matrix."""
    if not getattr(forest, "bootstrap", False):
        raise ValueError("CFRGForest requires bootstrap=True for OOB gating")
    if _generate_sample_indices is None or _get_n_samples_bootstrap is None:  # pragma: no cover
        raise RuntimeError("this scikit-learn version does not expose bootstrap helpers")
    # sklearn 1.9 accepts a fourth sample-weight argument; older versions
    # accept the historical three-argument helper.  Keep both compatible.
    try:
        n_bootstrap = _get_n_samples_bootstrap(n_samples, forest.max_samples, None)
    except TypeError:  # pragma: no cover - compatibility with older sklearn
        n_bootstrap = _get_n_samples_bootstrap(n_samples, forest.max_samples)
    mask = np.zeros((n_samples, len(forest.estimators_)), dtype=bool)
    for t, tree in enumerate(forest.estimators_):
        try:
            sampled = _generate_sample_indices(tree.random_state, n_samples, n_bootstrap, None)
        except TypeError:  # pragma: no cover - compatibility with older sklearn
            sampled = _generate_sample_indices(tree.random_state, n_samples, n_bootstrap)
        counts = np.bincount(sampled, minlength=n_samples)
        mask[:, t] = counts == 0
    return mask


class CFRGForest:
    """OOB cross-fitted, sample-conditional risk-gated random forest."""

    def __init__(
        self,
        n_estimators: int = 100,
        random_state: int | None = 42,
        max_depth: int | None = None,
        min_samples_leaf: int = 2,
        class_weight: str | dict | None = "balanced_subsample",
        n_jobs: int = -1,
        temperature: float = 1.0,
        gate_c: float = 1.0,
        cost_beta: float = 0.0,
        cost_min: float = 0.5,
        cost_max: float = 2.0,
        epsilon: float = 1e-12,
        bootstrap: bool = True,
    ) -> None:
        if n_estimators < 1 or min_samples_leaf < 1:
            raise ValueError("n_estimators and min_samples_leaf must be positive")
        if temperature <= 0 or gate_c <= 0:
            raise ValueError("temperature and gate_c must be positive")
        if cost_beta < 0 or cost_min <= 0 or cost_max < cost_min:
            raise ValueError("invalid class-cost parameters")
        self.n_estimators = int(n_estimators)
        self.random_state = random_state
        self.max_depth = max_depth
        self.min_samples_leaf = int(min_samples_leaf)
        self.class_weight = class_weight
        self.n_jobs = n_jobs
        self.temperature = float(temperature)
        self.gate_c = float(gate_c)
        self.cost_beta = float(cost_beta)
        self.cost_min = float(cost_min)
        self.cost_max = float(cost_max)
        self.epsilon = float(epsilon)
        self.bootstrap = bool(bootstrap)

    def fit(self, X, y: Sequence):
        self.model_ = RandomForestClassifier(
            n_estimators=self.n_estimators,
            random_state=self.random_state,
            max_depth=self.max_depth,
            min_samples_leaf=self.min_samples_leaf,
            class_weight=self.class_weight,
            n_jobs=self.n_jobs,
            bootstrap=self.bootstrap,
        )
        self.model_.fit(X, y)
        self.classes_ = np.asarray(self.model_.classes_)
        probabilities = tree_probability_tensor(self.model_, X)
        oob = tree_oob_mask(self.model_, len(X))
        # Build training descriptors from OOB trees only.  In-bag tree
        # predictions are masked out so agreement cannot leak fitted labels.
        descriptors = tree_descriptor_tensor(probabilities, self.epsilon, valid_mask=oob)
        coverage = oob.sum(axis=1)
        self.oob_coverage_ = coverage.astype(int)

        # Each OOB tree prediction becomes one gate-training example.
        row_ids, tree_ids = np.where(oob)
        if len(row_ids) == 0:
            raise ValueError("no OOB predictions available for gate fitting")
        gate_X = descriptors[row_ids, tree_ids]
        tree_pred = np.argmax(probabilities[row_ids, tree_ids], axis=1)
        y_encoded = np.searchsorted(self.classes_, np.asarray(y)[row_ids])
        gate_y = (tree_pred == y_encoded).astype(int)
        self.descriptor_scaler_ = StandardScaler().fit(gate_X)
        gate_X_scaled = self.descriptor_scaler_.transform(gate_X)
        self.gate_model_ = LogisticRegression(C=self.gate_c, solver="lbfgs", max_iter=300, random_state=self.random_state)
        if np.unique(gate_y).size == 1:
            self._constant_gate_ = float(gate_y[0])
        else:
            self._constant_gate_ = None
            weights = compute_sample_weight("balanced", gate_y)
            self.gate_model_.fit(gate_X_scaled, gate_y, sample_weight=weights)

        _, counts = np.unique(np.asarray(y), return_counts=True)
        raw_costs = (float(np.mean(counts)) / counts.astype(float)) ** self.cost_beta
        self.class_costs_ = np.clip(raw_costs, self.cost_min, self.cost_max)
        self.gate_diagnostics_ = {
            "oob_coverage_min": int(coverage.min()),
            "oob_coverage_mean": float(coverage.mean()),
            "oob_coverage_max": int(coverage.max()),
            "gate_training_rows": int(len(gate_y)),
            "gate_correct_rate": float(gate_y.mean()),
            "changed_weight_fraction": 0.0,
        }
        return self

    def _tree_scores(self, descriptors: np.ndarray) -> np.ndarray:
        flat = descriptors.reshape(-1, descriptors.shape[-1])
        scaled = self.descriptor_scaler_.transform(flat)
        if self._constant_gate_ is not None:
            scores = np.full(len(flat), self._constant_gate_, dtype=float)
        else:
            scores = self.gate_model_.predict_proba(scaled)[:, 1]
        return np.clip(scores.reshape(descriptors.shape[:2]), self.epsilon, 1.0)

    def predict_proba(self, X):
        if not hasattr(self, "model_"):
            raise RuntimeError("CFRGForest must be fitted before prediction")
        probabilities = tree_probability_tensor(self.model_, X)
        descriptors = tree_descriptor_tensor(probabilities, self.epsilon)
        scores = self._tree_scores(descriptors)
        weights = np.exp(np.log(scores) / self.temperature)
        weights /= np.maximum(weights.sum(axis=1, keepdims=True), self.epsilon)
        self.gate_diagnostics_["changed_weight_fraction"] = float(np.mean(np.std(weights, axis=1) > 1e-12))
        fused = (probabilities * weights[:, :, None]).sum(axis=1)
        adjusted = fused * self.class_costs_[None, :]
        adjusted /= np.maximum(adjusted.sum(axis=1, keepdims=True), self.epsilon)
        return np.nan_to_num(adjusted, nan=1.0 / len(self.classes_), posinf=0.0, neginf=0.0)

    def predict(self, X):
        return self.classes_[np.argmax(self.predict_proba(X), axis=1)]
