"""Build a strict, non-mutating data-quality pack for the CIC protocols."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def row_hashes(frame: pd.DataFrame, feature_cols: list[str]) -> pd.Series:
    # Hash the parsed numeric bytes and target together. This is independent
    # of pandas' 64-bit hash used during streaming deduplication and provides
    # an exact post-processing duplicate audit for the saved artifacts.
    values = frame[feature_cols].to_numpy(dtype="<f8", copy=True)
    targets = frame["target"].astype(str).to_numpy()
    out = []
    for row, target in zip(values, targets):
        h = hashlib.sha256()
        h.update(row.tobytes())
        h.update(b"\0")
        h.update(target.encode("utf-8"))
        out.append(h.hexdigest())
    return pd.Series(out, index=frame.index)


def build(processed: Path, out: Path, raw_audit: Path | None = None) -> None:
    out.mkdir(parents=True, exist_ok=True)
    splits = {}
    split_frames = {}
    feature_cols: list[str] | None = None
    source_keys: dict[str, set[tuple[str, int]]] = {}
    exact_hashes: dict[str, set[str]] = {}
    for split in ("train", "validation", "test"):
        frame = pd.read_csv(processed / f"{split}.csv", low_memory=False)
        split_frames[split] = frame
        feature_cols = [c for c in frame.columns if c != "target"]
        prov = pd.read_csv(processed / f"{split}_source_provenance.csv", low_memory=False)
        keys = set(zip(prov["_source_file"].astype(str), prov["_source_row_id"].astype(int)))
        source_keys[split] = keys
        hashes = row_hashes(frame, feature_cols)
        exact_hashes[split] = set(hashes)
        numeric = frame[feature_cols].apply(pd.to_numeric, errors="coerce")
        splits[split] = {
            "rows": int(len(frame)),
            "feature_count": int(len(feature_cols)),
            "class_counts": {str(k): int(v) for k, v in frame["target"].value_counts().sort_index().items()},
            "class_proportions": {str(k): float(v) for k, v in frame["target"].value_counts(normalize=True).sort_index().items()},
            "missing_cells": int(numeric.isna().sum().sum()),
            "infinite_cells": int(np.isinf(numeric.to_numpy(dtype=float)).sum()),
            "constant_features": [c for c in feature_cols if numeric[c].nunique(dropna=False) <= 1],
            "source_rows": int(len(prov)),
            "source_composite_key_duplicates": int(prov.duplicated(["_source_file", "_source_row_id"]).sum()),
            "source_files": int(prov["_source_file"].nunique()),
            "csv_sha256": sha256(processed / f"{split}.csv"),
            "provenance_sha256": sha256(processed / f"{split}_source_provenance.csv"),
        }
    overlaps = {
        "train_validation": len(source_keys["train"] & source_keys["validation"]),
        "train_test": len(source_keys["train"] & source_keys["test"]),
        "validation_test": len(source_keys["validation"] & source_keys["test"]),
    }
    exact_overlaps = {
        "train_validation": len(exact_hashes["train"] & exact_hashes["validation"]),
        "train_test": len(exact_hashes["train"] & exact_hashes["test"]),
        "validation_test": len(exact_hashes["validation"] & exact_hashes["test"]),
    }
    class_rows = []
    for split, frame in split_frames.items():
        counts = frame["target"].value_counts().sort_index()
        for label, count in counts.items():
            class_rows.append({"split": split, "target": str(label), "count": int(count), "proportion": float(count / len(frame)), "support_warning": bool(split == "test" and count < 200)})
    pd.DataFrame(class_rows).to_csv(out / "class_support.csv", index=False, encoding="utf-8-sig")
    source_rows = sum(v["rows"] for v in splits.values())
    dedup_audit = None
    if raw_audit:
        candidate = Path(processed) / "dedup_audit.json"
        if candidate.exists():
            dedup_audit = json.loads(candidate.read_text(encoding="utf-8"))
    summary = {
        "processed_dir": str(processed),
        "protocol": "capped observed-prior CIC population",
        "split_rows": {k: v["rows"] for k, v in splits.items()},
        "total_rows": source_rows,
        "feature_count": len(feature_cols or []),
        "split_quality": splits,
        "source_composite_key_overlaps": overlaps,
        "exact_feature_label_hash_overlaps": exact_overlaps,
        "low_support_test_classes": [r["target"] for r in class_rows if r["split"] == "test" and r["support_warning"]],
        "raw_audit": str(raw_audit) if raw_audit else None,
        "physical_range_audit": {
            "strict_physical_enabled": bool(dedup_audit and dedup_audit.get("invalid_physical_rows", 0) is not None),
            "invalid_physical_rows": int((dedup_audit or {}).get("invalid_physical_rows", 0)),
            "invalid_physical_by_feature": (dedup_audit or {}).get("invalid_physical_by_feature", {}),
            "interpretation": "The two initial-window fields retain CICFlowMeter's -1 unavailable sentinel; other listed duration/rate/length/header fields must be non-negative.",
        },
        "interpretation": [
            "The capped observed-prior population is not the full CIC-IDS2017 corpus.",
            "Test classes with fewer than 200 rows require class-level uncertainty reporting.",
            "Zero source-key and exact row-hash overlaps support split isolation, but do not establish temporal generalization.",
        ],
    }
    (out / "data_quality_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.DataFrame([{"metric": "total_rows", "value": source_rows}, {"metric": "feature_count", "value": len(feature_cols or [])}, {"metric": "source_key_overlap_total", "value": sum(overlaps.values())}, {"metric": "exact_hash_overlap_total", "value": sum(exact_overlaps.values())}, {"metric": "low_support_test_class_count", "value": len(summary["low_support_test_classes"])}]).to_csv(out / "data_quality_summary.csv", index=False, encoding="utf-8-sig")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--raw-audit", type=Path)
    args = ap.parse_args()
    build(args.processed_dir, args.output_dir, args.raw_audit)


if __name__ == "__main__":
    main()
