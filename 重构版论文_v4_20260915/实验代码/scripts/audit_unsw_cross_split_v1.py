"""Audit exact feature-vector overlap between UNSW-NB15 train and test files."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


def normalize_frame(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = pd.DataFrame(index=frame.index)
    for col in columns:
        series = frame[col]
        numeric = pd.to_numeric(series, errors="coerce")
        if numeric.notna().all():
            out[col] = numeric.astype("float64").round(12).map(lambda x: format(x, ".12g"))
        else:
            out[col] = series.fillna("<NA>").astype(str).str.strip()
    return out


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--test", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    train = pd.read_csv(args.train, low_memory=False)
    test = pd.read_csv(args.test, low_memory=False)
    label_col = "attack_cat"
    excluded = {"id", "label", label_col}
    columns = [c for c in train.columns if c not in excluded and c in test.columns]
    if not columns:
        raise ValueError("No shared feature columns after excluding id/label/attack_cat")

    train_norm = normalize_frame(train, columns)
    test_norm = normalize_frame(test, columns)
    train_keys = pd.util.hash_pandas_object(train_norm, index=False).astype("uint64")
    test_keys = pd.util.hash_pandas_object(test_norm, index=False).astype("uint64")

    train_groups = {}
    for idx, key in enumerate(train_keys.tolist()):
        train_groups.setdefault(int(key), []).append(idx)
    test_groups = {}
    for idx, key in enumerate(test_keys.tolist()):
        test_groups.setdefault(int(key), []).append(idx)

    common = set(train_groups).intersection(test_groups)
    exact_pairs = 0
    same_label_pairs = 0
    conflict_label_pairs = 0
    matched_train_rows = set()
    matched_test_rows = set()
    for key in common:
        for ti in train_groups[key]:
            for vi in test_groups[key]:
                if tuple(train_norm.iloc[ti]) != tuple(test_norm.iloc[vi]):
                    continue
                exact_pairs += 1
                matched_train_rows.add(ti)
                matched_test_rows.add(vi)
                if str(train.iloc[ti][label_col]).strip() == str(test.iloc[vi][label_col]).strip():
                    same_label_pairs += 1
                else:
                    conflict_label_pairs += 1

    result = {
        "train_file": args.train.name,
        "test_file": args.test.name,
        "train_sha256": file_sha256(args.train),
        "test_sha256": file_sha256(args.test),
        "excluded_columns": sorted(excluded),
        "feature_columns": columns,
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "train_duplicate_rows_by_feature_key": int(train_norm.duplicated().sum()),
        "test_duplicate_rows_by_feature_key": int(test_norm.duplicated().sum()),
        "cross_split_common_hash_keys": int(len(common)),
        "cross_split_exact_feature_pairs": int(exact_pairs),
        "cross_split_matched_train_rows": int(len(matched_train_rows)),
        "cross_split_matched_test_rows": int(len(matched_test_rows)),
        "cross_split_same_label_pairs": int(same_label_pairs),
        "cross_split_conflict_label_pairs": int(conflict_label_pairs),
        "test_matched_row_fraction": float(len(matched_test_rows) / len(test)),
        "normalization": "numeric values rounded to 12 decimals and formatted; categorical values stripped; id/label/attack_cat excluded",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
