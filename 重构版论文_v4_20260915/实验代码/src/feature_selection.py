"""Canonical chi-square feature selection.

The repository shipped two runners that select the top-k chi-square features
and then disagree on the released numbers for the same seed.  The cause is not
the score itself but the **column order of the design matrix**:

* ``run_cfrg_cic_v1.py`` builds ``X[:, argsort(-score)]`` - columns sorted by
  descending chi-square score;
* ``run_seeds10_v5.py`` uses ``SelectKBest(...).transform(X)`` - columns in the
  original feature order.

A random forest draws ``max_features`` columns per split by *index*, so the two
orders fit different trees even though the selected feature sets are the same
up to a boundary tie.  On the natural-prior split with seed 42 the two orders
give Macro-F1 0.890773 and 0.891714 respectively; see
``results_review_v5/baseline_reproduction_v1.json``.

This module defines one canonical selection so future runs cannot drift: it
returns the selected indices **in ascending feature order** - which is what
``SelectKBest.transform`` produces, and therefore what the current ten-seed
protocol already uses - and it reports any tie at the k-th boundary, because a
tie is the one case where two equally defensible selections exist.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from sklearn.feature_selection import SelectKBest, chi2


@dataclass
class Chi2Selection:
    """Result of a canonical top-k chi-square selection."""

    indices: list[int]                       # ascending feature order
    names: list[str]
    scores: np.ndarray
    k: int
    boundary_score: float
    tied_at_boundary: list[str] = field(default_factory=list)

    def select(self, matrix: np.ndarray) -> np.ndarray:
        """Apply the selection, keeping the canonical column order."""
        return matrix[:, self.indices]


def chi2_top_k(x: np.ndarray, y, k: int, feature_names: list[str] | None = None) -> Chi2Selection:
    """Select the top-k features by chi-square score on already-scaled data.

    ``x`` must be the non-negative training matrix (chi-square requires that);
    the callers fit ``MinMaxScaler`` on the training split first.  The selection
    is deliberately computed with ``SelectKBest`` so that it is bit-identical to
    the ten-seed protocol that produced the released numbers.
    """
    if feature_names is None:
        feature_names = [f"f{i}" for i in range(x.shape[1])]
    if len(feature_names) != x.shape[1]:
        raise ValueError("feature_names does not match the number of columns")
    k = min(int(k), x.shape[1])

    selector = SelectKBest(chi2, k=k).fit(x, y)
    mask = selector.get_support()
    indices = [i for i, keep in enumerate(mask) if keep]
    scores = np.nan_to_num(selector.scores_, nan=0.0, posinf=0.0)

    # A tie at the k-th boundary is the only case where two selections are
    # equally defensible, so it is reported rather than silently resolved.  The
    # canonical rule (SelectKBest) keeps the later feature of a tied pair; the
    # one time this bit, the two tied columns were element-wise identical, so
    # the rule changed the name of a column but not a single prediction.
    ranked = np.sort(scores)[::-1]
    boundary = float(ranked[k - 1])
    tied = [name for name, score in zip(feature_names, scores)
            if np.isclose(score, boundary, rtol=0, atol=1e-12)]
    return Chi2Selection(indices=indices, names=[feature_names[i] for i in indices],
                         scores=scores, k=k, boundary_score=boundary,
                         tied_at_boundary=sorted(tied))
