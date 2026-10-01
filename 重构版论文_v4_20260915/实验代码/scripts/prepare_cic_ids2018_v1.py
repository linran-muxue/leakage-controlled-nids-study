"""Six-stage, leakage-controlled preparation of CIC-IDS2018.

Two passes over the ten official CSVs: the first hashes every row (the same
forward/reversed pandas fingerprint the 2017 pipeline uses) and records which
rows survive global deduplication, cross-label conflict removal and a per-class
cap; the second keeps only those rows and writes train / validation / test.
Nothing but the audit JSON and the derived splits is written outside the new
processed directory.
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

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]

RENAME = {
    "Dst Port": "Destination Port", "Flow Byts/s": "Flow Bytes/s",
    "Flow Pkts/s": "Flow Packets/s", "Fwd Header Len": "Fwd Header Length",
    "Bwd Header Len": "Bwd Header Length", "Fwd Pkts/s": "Fwd Packets/s",
    "Bwd Pkts/s": "Bwd Packets/s", "Pkt Len Min": "Min Packet Length",
    "Pkt Len Max": "Max Packet Length", "Pkt Len Mean": "Packet Length Mean",
    "Pkt Len Std": "Packet Length Std", "Pkt Len Var": "Packet Length Variance",
    "FIN Flag Cnt": "FIN Flag Count", "SYN Flag Cnt": "SYN Flag Count",
    "RST Flag Cnt": "RST Flag Count", "PSH Flag Cnt": "PSH Flag Count",
    "ACK Flag Cnt": "ACK Flag Count", "URG Flag Cnt": "URG Flag Count",
    "ECE Flag Cnt": "ECE Flag Count", "Pkt Size Avg": "Average Packet Size",
    "Fwd Seg Size Avg": "Avg Fwd Segment Size", "Bwd Seg Size Avg": "Avg Bwd Segment Size",
    "Subflow Fwd Pkts": "Subflow Fwd Packets", "Subflow Fwd Byts": "Subflow Fwd Bytes",
    "Subflow Bwd Pkts": "Subflow Bwd Packets", "Subflow Bwd Byts": "Subflow Bwd Bytes",
    "Init Fwd Win Byts": "Init_Win_bytes_forward",
    "Init Bwd Win Byts": "Init_Win_bytes_backward",
    "Fwd Act Data Pkts": "act_data_pkt_fwd", "Fwd Seg Size Min": "min_seg_size_forward",
}


def map_label(raw: str) -> str | None:
    value = str(raw).strip()
    low = value.lower()
    if low == "benign":
        return "Normal"
    if low.startswith(("dos attacks", "ddos attack", "dos attacks-")):
        return "DoS/DDoS"
    if low in ("ftp-bruteforce", "ssh-bruteforce"):
        return "Brute Force"
    if low in ("brute force -web", "brute force -xss"):
        return "Brute Force"
    if low == "sql injection":
        return "Web Attack"
    if low == "bot":
        return "Bot"
    return None


def fingerprint(frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    forward = pd.util.hash_pandas_object(frame, index=False).to_numpy(dtype=np.uint64)
    reversed_ = pd.util.hash_pandas_object(frame[frame.columns[::-1]],
                                           index=False).to_numpy(dtype=np.uint64)
    return forward, reversed_


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", type=Path,
                    default=Path(r"E:\论文\data\external\CIC-IDS2018\hf"))
    ap.add_argument("--processed-dir", default="data_processed_cic_ids2018_v1")
    ap.add_argument("--audit-dir", default="results_data_audit_cic_ids2018_v1")
    ap.add_argument("--per-class-cap", type=int, default=20_000)
    ap.add_argument("--chunksize", type=int, default=200_000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    files = sorted(p for p in args.raw_dir.glob("*.csv"))
    if not files:
        raise SystemExit(f"no CSV files in {args.raw_dir}")
    out = ROOT / args.processed_dir
    audit_dir = ROOT / args.audit_dir
    out.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)

    started = time.time()
    hashes_forward, hashes_reverse, labels, source_index = [], [], [], []
    source_rows = 0
    invalid_rows = 0
    excluded_rows = 0
    columns_seen: list[str] | None = None
    invalid_by_column = {}
    for file_index, path in enumerate(files):
        print(f"pass 1: {path.name}", flush=True)
        for chunk in pd.read_csv(path, chunksize=args.chunksize, low_memory=False):
            chunk.columns = [str(column).strip() for column in chunk.columns]
            if "Label" not in chunk.columns:
                continue
            if columns_seen is None:
                columns_seen = [column for column in chunk.columns
                                if column not in ("Label", "Timestamp")]
            features = chunk.drop(columns=[c for c in ("Label", "Timestamp")
                                           if c in chunk.columns])
            features = features.apply(pd.to_numeric, errors="coerce")
            features = features.reindex(columns=columns_seen)
            finite = np.isfinite(features.to_numpy(dtype=float)).all(axis=1)
            for column in features.columns:
                bad = ~np.isfinite(features[column].to_numpy(dtype=float))
                if bad.any():
                    invalid_by_column[column] = invalid_by_column.get(column, 0) + int(bad.sum())
            mapped = chunk["Label"].map(map_label)
            keep = finite & mapped.notna().to_numpy()
            invalid_rows += int((~finite).sum())
            excluded_rows += int((finite & mapped.isna()).sum())
            source_rows += len(chunk)
            if not keep.any():
                continue
            kept_features = features.loc[keep]
            forward, reverse = fingerprint(kept_features)
            hashes_forward.append(forward)
            hashes_reverse.append(reverse)
            labels.append(mapped[keep].to_numpy())
            source_index.append(np.full(int(keep.sum()), file_index, dtype=np.int16))
    forward = np.concatenate(hashes_forward)
    reverse = np.concatenate(hashes_reverse)
    label_values = np.concatenate(labels)
    source_values = np.concatenate(source_index)
    total_mapped = len(label_values)
    print(f"pass 1 done: source {source_rows:,}, mapped {total_mapped:,}, "
          f"{time.time() - started:.0f}s", flush=True)

    keys = np.stack([forward, reverse], axis=1)
    order = np.lexsort((reverse, forward))
    sorted_keys = keys[order]
    unique_mask = np.ones(len(order), dtype=bool)
    unique_mask[1:] = np.any(sorted_keys[1:] != sorted_keys[:-1], axis=1)
    first_index = order[unique_mask]
    unique_keys = keys[first_index]
    # cross-label conflicts: a fingerprint that carries more than one label
    frame = pd.DataFrame({"f": unique_keys[:, 0], "r": unique_keys[:, 1],
                          "label": label_values[first_index]})
    grouped = frame.groupby(["f", "r"])["label"].nunique()
    conflicting = grouped[grouped > 1]
    conflict_hashes = set(map(tuple, conflicting.index.to_numpy()))
    conflict_rows = int(conflicting.index.size)
    print(f"unique fingerprints {len(unique_keys):,}, conflict groups {conflict_rows:,}",
          flush=True)

    kept: list[int] = []
    per_class: dict[str, int] = {}
    duplicates = total_mapped - len(unique_keys)
    conflict_removed = 0
    for index in first_index:
        key = (int(keys[index, 0]), int(keys[index, 1]))
        if key in conflict_hashes:
            conflict_removed += 1
            continue
        label = label_values[index]
        if per_class.get(label, 0) >= args.per_class_cap:
            continue
        per_class[label] = per_class.get(label, 0) + 1
        kept.append(int(index))
    kept_sorted = np.sort(np.array(kept))
    print(f"kept {len(kept_sorted):,} rows: {per_class}", flush=True)

    keep_set = np.zeros(total_mapped, dtype=bool)
    keep_set[kept_sorted] = True
    rows_x, rows_y = [], []
    # keep_set is indexed by the count of rows that passed the finite+mapped
    # filter, not by the raw row number, so track that count separately
    kept_cursor = 0
    for file_index, path in enumerate(files):
        print(f"pass 2: {path.name}", flush=True)
        for chunk in pd.read_csv(path, chunksize=args.chunksize, low_memory=False):
            chunk.columns = [str(column).strip() for column in chunk.columns]
            if "Label" not in chunk.columns:
                continue
            features = chunk.drop(columns=[c for c in ("Label", "Timestamp")
                                           if c in chunk.columns])
            features = features.apply(pd.to_numeric, errors="coerce")
            features = features.reindex(columns=columns_seen)
            finite = np.isfinite(features.to_numpy(dtype=float)).all(axis=1)
            mapped = chunk["Label"].map(map_label)
            keep = finite & mapped.notna().to_numpy()
            positions = np.flatnonzero(keep)
            for position in positions:
                if keep_set[kept_cursor]:
                    rows_x.append(features.iloc[position].to_numpy(dtype=np.float32))
                    rows_y.append(mapped.iloc[position])
                kept_cursor += 1
    X = np.vstack(rows_x)
    y = np.array(rows_y)
    assert len(X) == len(kept_sorted), (len(X), len(kept_sorted))

    from sklearn.model_selection import train_test_split
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=args.seed)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=args.seed)
    for name, features, target in (("train", X_train, y_train),
                                   ("validation", X_val, y_val),
                                   ("test", X_test, y_test)):
        frame = pd.DataFrame(features, columns=columns_seen)
        frame["target"] = target
        frame.to_csv(out / f"{name}.csv", index=False, encoding="utf-8-sig")
        print(f"wrote {name}: {frame.shape}", flush=True)
    (out / "dataset_summary.csv").write_text(
        pd.DataFrame({"target": list(pd.Series(y).value_counts().index),
                      "count": pd.Series(y).value_counts().to_numpy()}).to_csv(index=False),
        encoding="utf-8")
    config = {"dataset": "CIC-IDS2018", "per_class_cap": args.per_class_cap,
              "seed": args.seed, "chunksize": args.chunksize, "balance": False,
              "strict_finite": True, "features": columns_seen,
              "label_mapping": {
                  "Normal": ["Benign"],
                  "DoS/DDoS": ["DoS attacks-*", "DDoS attacks-*", "DDOS attack-*"],
                  "Brute Force": ["FTP-BruteForce", "SSH-Bruteforce",
                                  "Brute Force -Web", "Brute Force -XSS"],
                  "Web Attack": ["SQL Injection"],
                  "Bot": ["Bot"],
                  "excluded": ["Infilteration", "any unmapped label"]}}
    (out / "preprocess_config.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    audit = {
        "source_rows": source_rows, "mapped_rows": total_mapped,
        "excluded_label_rows": excluded_rows, "invalid_rows": invalid_rows,
        "invalid_by_column": invalid_by_column,
        "valid_rows": total_mapped,
        "duplicate_rows": duplicates,
        "cross_label_conflict_groups": conflict_rows,
        "rows_removed_for_conflicts": conflict_removed,
        "per_class_kept": per_class, "retained_rows": int(len(X)),
        "splits": {"train": int(len(X_train)), "validation": int(len(X_val)),
                   "test": int(len(X_test))},
        "file_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                        for path in files},
        "raw_files": [path.name for path in files],
        "protocol": ("global 128-bit fingerprint deduplication, cross-label conflict "
                     "removal, per-class cap, stratified 70/15/15 split"),
    }
    (audit_dir / "data_processing_audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: audit[k] for k in
                      ("source_rows", "mapped_rows", "duplicate_rows",
                       "cross_label_conflict_groups", "retained_rows", "splits")},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
