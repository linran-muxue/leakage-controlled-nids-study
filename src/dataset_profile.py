"""Profile CIC-IDS2017 CSV files without loading them all into memory."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd


def find_label_column(columns):
    for col in columns:
        if str(col).strip().lower() == "label":
            return col
    raise ValueError("未找到Label列")


def profile_files(raw_dir: Path, output_dir: Path, chunksize: int = 100_000):
    files = sorted(raw_dir.rglob("*.csv"))
    if not files:
        raise FileNotFoundError(f"未找到CSV文件: {raw_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    file_rows = []
    label_counts = {}
    feature_columns = None
    for path in files:
        rows = 0
        missing = 0
        infinite = 0
        header = pd.read_csv(path, nrows=0, encoding_errors="replace")
        label_col = find_label_column(header.columns)
        normalized = [str(c).strip() for c in header.columns]
        feature_columns = feature_columns or normalized
        for chunk in pd.read_csv(path, chunksize=chunksize, low_memory=False, encoding_errors="replace"):
            rows += len(chunk)
            missing += int(chunk.isna().sum().sum())
            numeric = chunk.drop(columns=[label_col], errors="ignore").apply(pd.to_numeric, errors="coerce")
            infinite += int(np.isinf(numeric.to_numpy(dtype=float, na_value=np.nan)).sum())
            labels = chunk[label_col].astype(str).str.strip()
            for label, count in labels.value_counts(dropna=False).items():
                label_counts[str(label)] = label_counts.get(str(label), 0) + int(count)
        file_rows.append({"file": str(path), "rows": rows, "missing_cells": missing, "infinite_values": infinite, "columns": len(header.columns)})
    pd.DataFrame(file_rows).to_csv(output_dir / "dataset_profile.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(sorted(label_counts.items()), columns=["raw_label", "count"]).to_csv(output_dir / "label_counts.csv", index=False, encoding="utf-8-sig")
    (output_dir / "feature_columns.json").write_text(json.dumps(feature_columns, ensure_ascii=False, indent=2), encoding="utf-8")
    return file_rows, label_counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, default=Path(r"E:\论文\data\raw\MachineLearningCVE"))
    parser.add_argument("--output-dir", type=Path, default=Path(r"E:\论文\results"))
    args = parser.parse_args()
    files, labels = profile_files(args.raw_dir, args.output_dir)
    print(f"PROFILE_FILES={len(files)}")
    print(f"PROFILE_ROWS={sum(item['rows'] for item in files)}")
    print("LABEL_COUNTS=")
    for label, count in sorted(labels.items(), key=lambda item: (-item[1], item[0])):
        print(f"  {label}: {count}")


if __name__ == "__main__":
    main()
