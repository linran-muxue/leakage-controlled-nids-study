"""Create a reproducible, memory-conscious five-class CIC-IDS2017 dataset."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# Support both ``python -m src.prepare_dataset`` and direct execution of the
# file path from PowerShell. In the latter case Python initially puts src/ on
# sys.path, not the project root.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data_pipeline import map_attack_label


def normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame.columns = [str(c).strip() for c in frame.columns]
    return frame


def collect_balanced_sample(raw_dir: Path, per_class_cap: int, include_other: bool, seed: int, chunksize: int, balance: bool = True):
    rng = np.random.default_rng(seed)
    buckets = {}
    feature_names = None
    seen_hashes = {}
    hash_row_counts = {}
    conflict_hashes = set()
    audit = {
        "source_rows": 0,
        "mapped_rows": 0,
        "invalid_rows": 0,
        "valid_rows": 0,
        "duplicate_rows": 0,
        "same_label_duplicate_rows": 0,
        "cross_label_mismatch_rows": 0,
        "conflicting_feature_hash_count": 0,
        "rows_in_conflicting_groups": 0,
        "unique_rows_removed_for_conflicts": 0,
        # Legacy aliases retained so older result readers do not break.
        "cross_label_conflicts": 0,
        "cross_label_conflict_hashes": 0,
        "cross_label_conflict_rows": 0,
        "unique_rows_before_conflict": 0,
        "unique_rows_after_conflict": 0,
        "dedup_fingerprint_bits": 128,
        "dedup_fingerprint_method": "pandas_hash_forward_and_reversed_columns",
        "capped_rows_before_balance": 0,
        # Kept for backward compatibility with older result readers. New
        # reports must use the explicit fields above.
        "retained_rows_before_balance": 0,
    }
    for path in sorted(raw_dir.rglob("*.csv")):
        for chunk in pd.read_csv(path, chunksize=chunksize, low_memory=False, encoding_errors="replace"):
            audit["source_rows"] += len(chunk)
            chunk = normalize_columns(chunk)
            # pandas preserves a monotonically increasing file-local index
            # across chunks; retain it as the provenance row identifier.
            source_row_ids = pd.Series(chunk.index.to_numpy(), index=chunk.index)
            label_col = next((c for c in chunk.columns if c.lower() == "label"), None)
            if label_col is None:
                raise ValueError(f"文件缺少Label列: {path}")
            mapped = chunk[label_col].map(lambda value: map_attack_label(value, include_other=include_other))
            keep = mapped.notna()
            chunk = chunk.loc[keep].copy()
            mapped = mapped.loc[keep]
            audit["mapped_rows"] += len(chunk)
            feature_names = feature_names or [
                c for c in chunk.columns if c not in {label_col, "Flow ID", "Timestamp"}
            ]
            # Clean numeric values before class capping. Otherwise invalid rows
            # removed after sampling can make class counts differ by a few rows.
            numeric = chunk[feature_names].apply(pd.to_numeric, errors="coerce")
            numeric = numeric.replace([np.inf, -np.inf], np.nan)
            valid = numeric.notna().all(axis=1)
            audit["invalid_rows"] += int((~valid).sum())
            audit["valid_rows"] += int(valid.sum())
            numeric = numeric.loc[valid].reset_index(drop=True)
            mapped = mapped.loc[valid].reset_index(drop=True)
            source_row_ids = source_row_ids.loc[keep].loc[valid].to_numpy()
            source_labels = chunk[label_col].loc[valid].astype(str).str.strip().to_numpy()
            row_hashes_forward = pd.util.hash_pandas_object(numeric, index=False).to_numpy(dtype=np.uint64)
            row_hashes_reverse = pd.util.hash_pandas_object(numeric[numeric.columns[::-1]], index=False).to_numpy(dtype=np.uint64)
            row_hashes = list(zip(row_hashes_forward, row_hashes_reverse))
            unique_mask = []
            for row_hash, label in zip(row_hashes, mapped):
                key = (int(row_hash[0]), int(row_hash[1]))
                hash_row_counts[key] = hash_row_counts.get(key, 0) + 1
                previous = seen_hashes.get(key)
                if previous is not None:
                    audit["duplicate_rows"] += 1
                    if previous != label:
                        audit["cross_label_mismatch_rows"] += 1
                        audit["cross_label_conflicts"] += 1
                        conflict_hashes.add(key)
                    else:
                        audit["same_label_duplicate_rows"] += 1
                    unique_mask.append(False)
                else:
                    seen_hashes[key] = label
                    unique_mask.append(True)
            if not unique_mask:
                continue
            numeric = numeric.loc[unique_mask].reset_index(drop=True)
            mapped = mapped.loc[unique_mask].reset_index(drop=True)
            source_row_ids = source_row_ids[np.asarray(unique_mask, dtype=bool)]
            source_labels = source_labels[np.asarray(unique_mask, dtype=bool)]
            numeric["target"] = mapped.to_numpy()
            # Preserve provenance as sidecar-only metadata. These columns are
            # removed before model CSVs are written and never enter features.
            numeric["_source_file"] = path.name
            numeric["_source_path"] = str(path)
            numeric["_source_row_id"] = source_row_ids
            numeric["_source_label"] = source_labels
            kept_hashes = [row_hashes[i] for i, keep_row in enumerate(unique_mask) if keep_row]
            numeric["_dedup_hash_forward"] = [int(item[0]) for item in kept_hashes]
            numeric["_dedup_hash_reverse"] = [int(item[1]) for item in kept_hashes]
            for label in numeric["target"].unique():
                group = numeric.loc[numeric["target"] == label].copy()
                buckets.setdefault(label, []).append(group)
    audit["unique_rows_before_conflict"] = int(len(seen_hashes))
    audit["conflicting_feature_hash_count"] = int(len(conflict_hashes))
    audit["rows_in_conflicting_groups"] = int(sum(hash_row_counts[key] for key in conflict_hashes))
    audit["unique_rows_removed_for_conflicts"] = int(len(conflict_hashes))
    audit["cross_label_conflict_hashes"] = int(len(conflict_hashes))
    audit["cross_label_conflict_rows"] = audit["rows_in_conflicting_groups"]
    audit["unique_rows_after_conflict"] = int(len(seen_hashes) - len(conflict_hashes))
    grouped = {label: pd.concat(parts, ignore_index=True) for label, parts in buckets.items()}
    # Apply the cap globally after all chunks have been merged. Applying it per
    # chunk changes the effective sample size with chunk size and harms
    # reproducibility.
    for label, group in list(grouped.items()):
        if len(group) > per_class_cap:
            grouped[label] = group.sample(per_class_cap, random_state=int(rng.integers(0, 2**31 - 1))).reset_index(drop=True)
    if conflict_hashes:
        for label in list(grouped):
            group = grouped[label]
            keys = list(zip(group["_dedup_hash_forward"].astype("uint64"), group["_dedup_hash_reverse"].astype("uint64")))
            grouped[label] = group.loc[[key not in conflict_hashes for key in keys]].copy()
    grouped = {label: group.drop(columns=["_dedup_hash_forward", "_dedup_hash_reverse"]) for label, group in grouped.items() if len(group)}
    audit["capped_rows_before_balance"] = int(sum(len(group) for group in grouped.values()))
    audit["retained_rows_before_balance"] = audit["capped_rows_before_balance"]
    target_per_class = min(per_class_cap, min(len(group) for group in grouped.values())) if balance else None
    samples = []
    for label, group in grouped.items():
        if balance and len(group) > target_per_class:
            group = group.sample(target_per_class, random_state=seed)
        samples.append(group)
    if not samples:
        raise ValueError("没有收集到可用的五分类样本")
    result = pd.concat(samples, ignore_index=True).sample(frac=1, random_state=seed).reset_index(drop=True)
    audit["balanced_rows"] = int(len(result))
    audit["balanced_per_class"] = int(target_per_class) if target_per_class is not None else None
    return result, feature_names, audit


def prepare_dataset(raw_dir: Path, processed_dir: Path, config: dict):
    frame, features, audit = collect_balanced_sample(raw_dir, **config)
    provenance_cols = ["_source_file", "_source_path", "_source_row_id", "_source_label"]
    train, temp = train_test_split(frame, test_size=0.30, stratify=frame["target"], random_state=config["seed"])
    valid, test = train_test_split(temp, test_size=0.50, stratify=temp["target"], random_state=config["seed"])
    processed_dir.mkdir(parents=True, exist_ok=True)
    for split_name, split_frame in [("train", train), ("validation", valid), ("test", test)]:
        split_frame.reset_index(drop=True)[["target", *provenance_cols]].assign(processed_row_id=lambda d: np.arange(len(d))).to_csv(processed_dir / f"{split_name}_source_provenance.csv", index=False, encoding="utf-8-sig")
    train = train.drop(columns=provenance_cols)
    valid = valid.drop(columns=provenance_cols)
    test = test.drop(columns=provenance_cols)
    train.to_csv(processed_dir / "train.csv", index=False, encoding="utf-8-sig")
    valid.to_csv(processed_dir / "validation.csv", index=False, encoding="utf-8-sig")
    test.to_csv(processed_dir / "test.csv", index=False, encoding="utf-8-sig")
    mapping = {
        "Normal": ["BENIGN"],
        "DoS/DDoS": ["DDoS", "DoS ..."],
        "Brute Force": ["FTP-Patator", "SSH-Patator", "Web Attack ... Brute Force"],
        "Web Attack": ["Web Attack ... XSS", "Web Attack ... Sql Injection"],
        "Bot": ["Bot"],
        "excluded_main": ["PortScan", "Infiltration", "Heartbleed"],
    }
    (processed_dir / "label_mapping.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = frame["target"].value_counts().rename_axis("target").reset_index(name="count")
    summary.to_csv(processed_dir / "dataset_summary.csv", index=False, encoding="utf-8-sig")
    (processed_dir / "preprocess_config.json").write_text(json.dumps({**config, "features": features}, ensure_ascii=False, indent=2), encoding="utf-8")
    (processed_dir / "dedup_audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, default=Path(r"E:\论文\data\raw\MachineLearningCVE"))
    parser.add_argument("--processed-dir", type=Path, default=Path(r"E:\论文\data\processed"))
    parser.add_argument("--per-class-cap", type=int, default=20_000)
    parser.add_argument("--include-other", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--chunksize", type=int, default=100_000)
    parser.add_argument("--no-balance", action="store_true", help="保留各类别自然数量，仅执行每类上限和去重")
    args = parser.parse_args()
    config = {"per_class_cap": args.per_class_cap, "include_other": args.include_other, "seed": args.seed, "chunksize": args.chunksize, "balance": not args.no_balance}
    summary = prepare_dataset(args.raw_dir, args.processed_dir, config)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
