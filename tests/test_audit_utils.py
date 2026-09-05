import numpy as np
import pandas as pd
import pytest

from src.audit_utils import assert_no_feature_overlap, flatten_aggregate_columns, validate_split_schema


def test_validate_split_schema_rejects_column_order_mismatch():
    train = pd.DataFrame({"x": [1], "y": [2], "target": ["A"]})
    valid = pd.DataFrame({"y": [2], "x": [1], "target": ["A"]})
    test = pd.DataFrame({"x": [3], "y": [4], "target": ["B"]})
    try:
        validate_split_schema(train, valid, test)
    except ValueError:
        return
    raise AssertionError("schema mismatch should be rejected")


def test_assert_no_feature_overlap_accepts_disjoint_splits():
    train = pd.DataFrame({"x": [1, 2], "target": ["A", "B"]})
    valid = pd.DataFrame({"x": [3], "target": ["A"]})
    test = pd.DataFrame({"x": [4], "target": ["B"]})
    report = assert_no_feature_overlap(train, valid, test)
    assert report["train_validation_overlap"] == 0
    assert report["train_test_overlap"] == 0
    assert report["validation_test_overlap"] == 0


def test_assert_no_feature_overlap_rejects_cross_split_duplicates():
    train = pd.DataFrame({"x": [1], "target": ["A"]})
    valid = pd.DataFrame({"x": [1], "target": ["A"]})
    test = pd.DataFrame({"x": [2], "target": ["B"]})
    with pytest.raises(ValueError, match="overlap"):
        assert_no_feature_overlap(train, valid, test)


def test_flatten_aggregate_columns_produces_single_level_names():
    table = pd.DataFrame({("accuracy", "mean"): [0.9], ("accuracy", "std"): [0.01]})
    flat = flatten_aggregate_columns(table)
    assert list(flat.columns) == ["accuracy_mean", "accuracy_std"]


def test_flatten_aggregate_columns_removes_reset_index_artifact():
    table = pd.DataFrame({"index": [0], "model": ["rf"], "accuracy_mean": [0.9]})
    flat = flatten_aggregate_columns(table)
    assert list(flat.columns) == ["model", "accuracy_mean"]
