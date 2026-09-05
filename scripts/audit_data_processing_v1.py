"""Produce a complete, non-mutating audit of dataset processing stages."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data_pipeline import map_attack_label


def file_hash(path: Path, block: int = 1024 * 1024) -> dict[str, object]:
    md5 = hashlib.md5(); sha = hashlib.sha256(); size = 0
    with path.open("rb") as fh:
        while True:
            data = fh.read(block)
            if not data: break
            size += len(data); md5.update(data); sha.update(data)
    return {"bytes": size, "md5": md5.hexdigest(), "sha256": sha.hexdigest()}


def audit_frame(frame: pd.DataFrame, include_other: bool = False) -> dict:
    frame = frame.copy()
    frame.columns = [str(c).strip() for c in frame.columns]
    label_col = next((c for c in frame.columns if c.lower() == "label"), None)
    if label_col is None:
        raise ValueError("raw frame requires a Label column")
    feature_cols = [c for c in frame.columns if c not in {label_col, "Flow ID", "Timestamp"}]
    mapped = frame[label_col].map(lambda x: map_attack_label(x, include_other=include_other))
    mapped_mask = mapped.notna()
    numeric = frame.loc[mapped_mask, feature_cols].apply(pd.to_numeric, errors="coerce")
    inf_mask = np.isinf(numeric.to_numpy(dtype=float)).any(axis=1)
    missing_mask = numeric.isna().any(axis=1) & ~inf_mask
    invalid_mask = inf_mask | missing_mask
    valid_mapped = mapped.loc[mapped_mask].loc[~pd.Series(invalid_mask, index=mapped.loc[mapped_mask].index)]
    return {
        "source_rows": int(len(frame)),
        "mapped_rows": int(mapped_mask.sum()),
        "excluded_label_rows": int((~mapped_mask).sum()),
        "invalid_rows": int(invalid_mask.sum()),
        "invalid_infinite_rows": int(inf_mask.sum()),
        "invalid_missing_rows": int(missing_mask.sum()),
        "valid_rows": int((~invalid_mask).sum()),
        "feature_count": int(len(feature_cols)),
        "feature_columns": feature_cols,
        "raw_label_counts": {str(k): int(v) for k, v in frame[label_col].fillna("<NA>").astype(str).str.strip().value_counts().items()},
        "class_counts": {str(k): int(v) for k, v in valid_mapped.value_counts().items()},
    }


def summarize_split(frame: pd.DataFrame, split: str) -> dict:
    features = [c for c in frame.columns if c != "target"]
    return {"split": split, "rows": int(len(frame)), "feature_count": int(len(features)), "feature_columns": features, "class_counts": {str(k): int(v) for k, v in frame["target"].value_counts().items()}}


def audit_raw(raw_dir: Path) -> tuple[list[dict], dict]:
    files = []
    totals = {k: 0 for k in ["source_rows", "mapped_rows", "excluded_label_rows", "invalid_rows", "invalid_infinite_rows", "invalid_missing_rows", "valid_rows"]}
    for path in sorted(raw_dir.rglob("*.csv")):
        result = audit_frame(pd.read_csv(path, low_memory=False, encoding_errors="replace"))
        result["file"] = path.name
        result["file_hash"] = file_hash(path)
        files.append(result)
        for key in totals: totals[key] += result[key]
    return files, totals


def audit_processed(processed_dir: Path) -> dict:
    splits = {}
    hashes = {}
    provenance = {}
    for split in ("train", "validation", "test"):
        frame = pd.read_csv(processed_dir / f"{split}.csv", low_memory=False)
        splits[split] = summarize_split(frame, split)
        prov_path = processed_dir / f"{split}_source_provenance.csv"
        if prov_path.exists():
            prov = pd.read_csv(prov_path, low_memory=False)
            provenance[split] = {"rows": int(len(prov)), "expected_rows": int(len(frame)), "coverage": float(len(prov) / max(1, len(frame))), "duplicate_processed_row_ids": int(prov["processed_row_id"].duplicated().sum()) if "processed_row_id" in prov else None}
        else:
            provenance[split] = {"rows": 0, "expected_rows": int(len(frame)), "coverage": 0.0, "duplicate_processed_row_ids": None}
        features = [c for c in frame.columns if c != "target"]
        hashes[split] = set(pd.util.hash_pandas_object(frame[features], index=False).tolist())
    overlap = {"train_validation": len(hashes["train"] & hashes["validation"]), "train_test": len(hashes["train"] & hashes["test"]), "validation_test": len(hashes["validation"] & hashes["test"])}
    quality = {}
    train = pd.read_csv(processed_dir / "train.csv", low_memory=False)
    features = [c for c in train.columns if c != "target"]
    numeric = train[features].apply(pd.to_numeric, errors="coerce")
    quality["missing_cells"] = int(numeric.isna().sum().sum())
    quality["infinite_cells"] = int(np.isinf(numeric.to_numpy(dtype=float)).sum())
    quality["constant_features"] = [c for c in features if numeric[c].nunique(dropna=False) <= 1]
    quality["near_zero_variance_features"] = [c for c in features if numeric[c].nunique(dropna=False) / max(1, len(numeric)) < 0.001]
    quality["feature_stats"] = [{"feature": c, "dtype": str(train[c].dtype), "min": float(numeric[c].min()), "max": float(numeric[c].max()), "mean": float(numeric[c].mean()), "std": float(numeric[c].std(ddof=0))} for c in features]
    return {"splits": splits, "provenance_sidecars": provenance, "cross_split_exact_feature_overlap": overlap, "train_feature_quality": quality}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", type=Path, required=True)
    ap.add_argument("--processed-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args(); args.output_dir.mkdir(parents=True, exist_ok=True)
    files, totals = audit_raw(args.raw_dir)
    processed = audit_processed(args.processed_dir)
    result = {"raw_dir": str(args.raw_dir), "processed_dir": str(args.processed_dir), "raw_totals": totals, "raw_files": files, "processed": processed, "protocol_notes": ["Raw invalid rows are classified as excluded-label, infinite, or missing/non-numeric.", "Processed sidecar provenance is metadata only and is excluded from model features.", "Cross-split overlap is checked on exact processed feature vectors."]}
    (args.output_dir / "data_processing_audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    flat_files = []
    for row in files:
        flat = {k: v for k, v in row.items() if k not in {"class_counts", "raw_label_counts", "feature_columns", "file_hash"}}
        flat["class_counts"] = json.dumps(row["class_counts"], ensure_ascii=False)
        flat["raw_label_counts"] = json.dumps(row["raw_label_counts"], ensure_ascii=False)
        flat["feature_count"] = row["feature_count"]
        flat.update({f"hash_{k}": v for k, v in row["file_hash"].items()})
        flat_files.append(flat)
    pd.DataFrame(flat_files).to_csv(args.output_dir / "raw_file_stage_counts.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame([processed["splits"][s] for s in ("train", "validation", "test")]).drop(columns=["feature_columns"]).to_csv(args.output_dir / "processed_split_summary.csv", index=False, encoding="utf-8-sig")
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    try:
        print(payload)
    except UnicodeEncodeError:
        sys.stdout.buffer.write(payload.encode("utf-8", errors="replace"))
        sys.stdout.buffer.write(b"\n")


if __name__ == "__main__": main()
