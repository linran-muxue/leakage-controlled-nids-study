"""The canonical selection must be bit-identical to what the ten-seed protocol did."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from sklearn.feature_selection import SelectKBest, chi2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.feature_selection import chi2_top_k  # noqa: E402


def _toy():
    rng = np.random.default_rng(0)
    x = rng.random((200, 12))
    y = np.array(["a", "b"] * 100)
    x[:, 4] += (y == "b") * 0.5
    # identical columns guarantee a tie at the boundary
    x[:, 5] = x[:, 4]
    x[:, 6] = x[:, 4]
    x[:, 7] = x[:, 4]
    return x, y


def test_selection_matches_selectkbest_transform():
    x, y = _toy()
    selection = chi2_top_k(x, y, 6, feature_names=[f"f{i}" for i in range(x.shape[1])])
    reference = SelectKBest(chi2, k=6).fit(x, y).transform(x)
    assert np.array_equal(selection.select(x), reference)


def test_selection_keeps_ascending_feature_order():
    x, y = _toy()
    selection = chi2_top_k(x, y, 6)
    assert selection.indices == sorted(selection.indices)
    assert len(selection.indices) == 6


def test_tied_features_at_the_boundary_are_reported():
    x, y = _toy()
    names = [f"f{i}" for i in range(x.shape[1])]
    # the four identical columns occupy ranks 1-4, so k = 3 puts the boundary
    # inside the tie
    selection = chi2_top_k(x, y, 3, feature_names=names)
    assert len(selection.tied_at_boundary) == 4
    assert set(selection.tied_at_boundary) <= set(names)


def test_k_larger_than_columns_is_clamped():
    x, y = _toy()
    selection = chi2_top_k(x, y, 999)
    assert len(selection.indices) == x.shape[1]
