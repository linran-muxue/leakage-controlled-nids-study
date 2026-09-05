from __future__ import annotations

import pandas as pd


def validate_split_schema(train: pd.DataFrame, validation: pd.DataFrame, test: pd.DataFrame):
    """Require identical feature columns and a single target column in all splits."""
    frames = {"train": train, "validation": validation, "test": test}
    for name, frame in frames.items():
        if "target" not in frame.columns:
            raise ValueError(f"{name} split missing target column")
    expected = [c for c in train.columns if c != "target"]
    if not expected:
        raise ValueError("split schema has no feature columns")
    for name, frame in frames.items():
        actual = [c for c in frame.columns if c != "target"]
        if actual != expected:
            raise ValueError(f"inconsistent feature columns in {name} split")
    return {"feature_count": len(expected), "feature_columns": expected}


def _feature_hashes(frame: pd.DataFrame):
    features = frame.drop(columns=["target"], errors="ignore")
    return set(pd.util.hash_pandas_object(features, index=False).tolist()), int(features.duplicated().sum())


def assert_no_feature_overlap(train: pd.DataFrame, validation: pd.DataFrame, test: pd.DataFrame):
    train_h, train_internal = _feature_hashes(train)
    valid_h, valid_internal = _feature_hashes(validation)
    test_h, test_internal = _feature_hashes(test)
    report = {
        "train_internal_duplicates": train_internal,
        "validation_internal_duplicates": valid_internal,
        "test_internal_duplicates": test_internal,
        "train_validation_overlap": len(train_h & valid_h),
        "train_test_overlap": len(train_h & test_h),
        "validation_test_overlap": len(valid_h & test_h),
    }
    if any(report[key] > 0 for key in ["train_internal_duplicates", "validation_internal_duplicates", "test_internal_duplicates", "train_validation_overlap", "train_test_overlap", "validation_test_overlap"]):
        raise ValueError(f"feature overlap detected: {report}")
    return report


def flatten_aggregate_columns(table: pd.DataFrame):
    table = table.copy()
    if isinstance(table.columns, pd.MultiIndex):
        table.columns = ["_".join(str(part) for part in col if str(part) not in {"", "nan"}) for col in table.columns]
    table.columns = [str(c).replace("Unnamed: 0", "row_id") for c in table.columns]
    if "index" in table.columns:
        table = table.drop(columns=["index"])
    return table
