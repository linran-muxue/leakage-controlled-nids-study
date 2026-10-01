"""Generic reservoir preparation for a labelled tabular corpus (CSV or parquet).

Used for the recent (2020-2023) corpora: RT-IoT2022, ACI-IoT-2023, LITNET-2020
and the preprocessed IoT-23 tables.  The rule is the same in every case: stream
the rows, keep at most ``cap`` unique fingerprints per class (exact 128-bit
pandas fingerprint inside the reservoir), split the training reservoir 85/15
and write the test reservoir as the held-out split.  Counts and the column list
go to an audit JSON.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
ID_LIKE = ("id", "unnamed", "file", "index", "timestamp", "time", "date", "flow id")


def batches(path: Path, batch_size: int):
    if path.suffix == ".parquet":
        parquet = pq.ParquetFile(path)
        for batch in parquet.iter_batches(batch_size=batch_size):
            yield batch.to_pandas()
    else:
        for chunk in pd.read_csv(path, chunksize=batch_size, low_memory=False):
            yield chunk


def reservoir(path: Path, label_col: str, cap: int, batch_size: int,
              label_map: dict[str, str]):
    seen: dict[str, set[tuple[int, int]]] = {}
    kept_x: list[np.ndarray] = []
    kept_y: list[str] = []
    total: dict[str, int] = {}
    duplicates: dict[str, int] = {}
    features: list[str] | None = None
    dropped: list[str] = []
    for frame in batches(path, batch_size):
        frame.columns = [str(column).strip() for column in frame.columns]
        labels = frame.pop(label_col).astype(str).map(
            lambda value: label_map.get(value, value))
        if features is None:
            candidates = [column for column in frame.columns
                          if not any(token in column.lower() for token in ID_LIKE)]
            converted = frame.reindex(columns=candidates).apply(pd.to_numeric, errors="coerce")
            dropped = [column for column in converted.columns
                       if converted[column].isna().all()]
            features = [column for column in candidates if column not in dropped]
        # every batch is aligned to the fixed feature list decided on batch one
        numeric = frame.reindex(columns=features).apply(pd.to_numeric, errors="coerce")
        finite = np.isfinite(numeric.to_numpy(dtype=float)).all(axis=1)
        forward = pd.util.hash_pandas_object(numeric, index=False).to_numpy(dtype=np.uint64)
        reverse = pd.util.hash_pandas_object(numeric[numeric.columns[::-1]],
                                             index=False).to_numpy(dtype=np.uint64)
        for label in pd.unique(labels):
            total[label] = total.get(label, 0) + int((labels == label).sum())
        for position in np.flatnonzero(finite):
            label = labels.iloc[position]
            bucket = seen.setdefault(label, set())
            if len(bucket) >= cap:
                continue
            key = (int(forward[position]), int(reverse[position]))
            if key in bucket:
                duplicates[label] = duplicates.get(label, 0) + 1
                continue
            bucket.add(key)
            kept_x.append(numeric.iloc[position].to_numpy(dtype=np.float32))
            kept_y.append(label)
        if all(len(seen.get(label, ())) >= cap for label in seen):
            break
    X = np.vstack(kept_x)
    y = np.array(kept_y)
    audit = {"rows_scanned": int(sum(total.values())), "per_class_total": total,
             "per_class_kept": {label: len(bucket) for label, bucket in seen.items()},
             "per_class_duplicates_in_reservoir": duplicates,
             "dropped_non_numeric_columns": dropped, "features": features,
             "cap": cap}
    return X, y, audit


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--train", type=Path, required=True)
    ap.add_argument("--test", type=Path, required=True)
    ap.add_argument("--label-col", required=True)
    ap.add_argument("--processed-dir", required=True)
    ap.add_argument("--audit-dir", required=True)
    ap.add_argument("--train-cap", type=int, default=5000)
    ap.add_argument("--test-cap", type=int, default=2000)
    ap.add_argument("--batch-size", type=int, default=200_000)
    ap.add_argument("--label-map-json", type=Path, default=None)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    label_map = {}
    if args.label_map_json and args.label_map_json.exists():
        raw = json.loads(args.label_map_json.read_text(encoding="utf-8"))
        label_map = {str(key): str(value) for key, value in raw.items()}
    out = ROOT / args.processed_dir
    audit_dir = ROOT / args.audit_dir
    out.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)

    started = time.time()
    print(f"{args.name}: streaming training reservoir", flush=True)
    X_train_all, y_train_all, train_audit = reservoir(
        args.train, args.label_col, args.train_cap, args.batch_size, label_map)
    print(f"  train {X_train_all.shape} in {time.time() - started:.0f}s", flush=True)
    print(f"{args.name}: streaming test reservoir", flush=True)
    X_test, y_test, test_audit = reservoir(
        args.test, args.label_col, args.test_cap, args.batch_size, label_map)
    print(f"  test {X_test.shape}", flush=True)

    from sklearn.model_selection import train_test_split
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_all, y_train_all, test_size=0.15, stratify=y_train_all,
        random_state=args.seed)
    features = train_audit["features"]
    for name, values, target in (("train", X_train, y_train),
                                 ("validation", X_val, y_val),
                                 ("test", X_test, y_test)):
        frame = pd.DataFrame(values, columns=features)
        frame["target"] = target
        frame.to_csv(out / f"{name}.csv", index=False, encoding="utf-8-sig")
        print(f"  wrote {name}: {frame.shape}", flush=True)
    counts = pd.Series(y_train_all).value_counts()
    pd.DataFrame({"target": counts.index, "count": counts.to_numpy()}).to_csv(
        out / "dataset_summary.csv", index=False, encoding="utf-8-sig")
    config = {"dataset": args.name, "label_column": args.label_col,
              "label_map": label_map, "per_class_cap_train": args.train_cap,
              "per_class_cap_test": args.test_cap,
              "reservoir_rule": ("streamed rows admitted per class until the cap; "
                                 "exact 128-bit fingerprint dedup inside the reservoir"),
              "seed": args.seed, "features": features}
    (out / "preprocess_config.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    audit = {"train": train_audit, "test": test_audit,
             "splits": {"train": int(len(X_train)), "validation": int(len(X_val)),
                        "test": int(len(X_test))},
             "file_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                             for path in (args.train, args.test)}}
    (audit_dir / "data_processing_audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(audit["splits"], ensure_ascii=False))


if __name__ == "__main__":
    main()
