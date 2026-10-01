"""Prepare the CIC-IoT-2023 corpus (8 coarse classes) from its parquet mirrors.

The corpus is large (30.8 M train + 7.7 M test rows), so the pipeline keeps a
per-class reservoir: rows are streamed, fingerprinted and admitted until the
class reaches its cap, with exact deduplication inside the reservoir.  Every
class count, duplicate count and the reservoir rules are written to the audit
JSON, and the resulting splits match the layout the other benchmarks use.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
LABEL_COLUMNS = {"Label", "attack_class", "label"}
CLASS_MAP = {"Benign": "Normal"}


def stream(path: Path, cap: int, seed: int, batch_size: int = 200_000):
    """Return (X, y, audit) for one parquet file under the reservoir rule."""
    parquet = pq.ParquetFile(path)
    columns = [name for name in parquet.schema.names if name not in LABEL_COLUMNS]
    seen: dict[str, set[tuple[int, int]]] = {}
    kept_x: list[np.ndarray] = []
    kept_y: list[np.ndarray] = []
    class_total: dict[str, int] = {}
    class_kept: dict[str, int] = {}
    class_duplicates: dict[str, int] = {}
    non_numeric_dropped: list[str] = []
    rng = np.random.default_rng(seed)
    for batch in parquet.iter_batches(batch_size=batch_size, columns=columns + ["attack_class"]):
        frame = batch.to_pandas()
        labels = frame.pop("attack_class").astype(str).map(
            lambda value: CLASS_MAP.get(value, value))
        numeric = frame.apply(pd.to_numeric, errors="coerce")
        bad = [name for name in numeric.columns if numeric[name].isna().all()]
        for name in bad:
            if name not in non_numeric_dropped:
                non_numeric_dropped.append(name)
        numeric = numeric.drop(columns=bad)
        finite = np.isfinite(numeric.to_numpy(dtype=float)).all(axis=1)
        forward = pd.util.hash_pandas_object(numeric, index=False).to_numpy(dtype=np.uint64)
        reverse = pd.util.hash_pandas_object(numeric[numeric.columns[::-1]],
                                             index=False).to_numpy(dtype=np.uint64)
        for label in pd.unique(labels):
            class_total[label] = class_total.get(label, 0) + int((labels == label).sum())
        for position in np.flatnonzero(finite):
            label = labels.iloc[position]
            bucket = seen.setdefault(label, set())
            if len(bucket) >= cap:
                continue
            key = (int(forward[position]), int(reverse[position]))
            if key in bucket:
                class_duplicates[label] = class_duplicates.get(label, 0) + 1
                continue
            bucket.add(key)
            kept_x.append(numeric.iloc[position].to_numpy(dtype=np.float32))
            kept_y.append(label)
            class_kept[label] = class_kept.get(label, 0) + 1
        if all(class_kept.get(label, 0) >= cap for label in seen):
            break
    X = np.vstack(kept_x)
    y = np.array(kept_y)
    audit = {"rows_scanned": int(sum(class_total.values())),
             "per_class_total": class_total, "per_class_kept": class_kept,
             "per_class_duplicates_in_reservoir": class_duplicates,
             "dropped_non_numeric_columns": non_numeric_dropped,
             "features": list(numeric.columns), "cap": cap}
    return X, y, audit


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", type=Path,
                    default=Path(r"E:\论文\data\external\CIC-IoT-2023\hf\random"))
    ap.add_argument("--processed-dir", default="data_processed_cic_iot2023_v1")
    ap.add_argument("--audit-dir", default="results_data_audit_cic_iot2023_v1")
    ap.add_argument("--train-cap", type=int, default=20_000)
    ap.add_argument("--test-cap", type=int, default=5_000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    train_path = args.raw_dir / "train-00000-of-00001.parquet"
    test_path = args.raw_dir / "test-00000-of-00001.parquet"
    if not train_path.exists() or not test_path.exists():
        raise SystemExit(f"missing parquet files under {args.raw_dir}")
    out = ROOT / args.processed_dir
    audit_dir = ROOT / args.audit_dir
    out.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)

    started = time.time()
    print("streaming train reservoir", flush=True)
    X_train_all, y_train_all, train_audit = stream(train_path, args.train_cap, args.seed)
    print(f"train reservoir {X_train_all.shape} in {time.time() - started:.0f}s", flush=True)
    print("streaming test reservoir", flush=True)
    X_test, y_test, test_audit = stream(test_path, args.test_cap, args.seed)
    print(f"test reservoir {X_test.shape}", flush=True)

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
        print(f"wrote {name}: {frame.shape}", flush=True)
    summary = pd.Series(y_train_all).value_counts()
    pd.DataFrame({"target": summary.index, "count": summary.to_numpy()}).to_csv(
        out / "dataset_summary.csv", index=False, encoding="utf-8-sig")
    config = {"dataset": "CIC-IoT-2023", "held-out split": "provider random split",
              "per_class_cap_train": args.train_cap, "per_class_cap_test": args.test_cap,
              "reservoir_rule": ("streamed rows admitted per class until the cap; exact "
                                 "128-bit fingerprint dedup inside the reservoir"),
              "seed": args.seed, "features": features,
              "label_column": "attack_class (8 coarse classes; Benign -> Normal)"}
    (out / "preprocess_config.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    audit = {"train": train_audit, "test": test_audit,
             "splits": {"train": int(len(X_train)), "validation": int(len(X_val)),
                        "test": int(len(X_test))},
             "file_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                             for path in (train_path, test_path)}}
    (audit_dir / "data_processing_audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(audit["splits"], ensure_ascii=False))


if __name__ == "__main__":
    main()
