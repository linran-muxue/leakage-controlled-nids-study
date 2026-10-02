"""Prepare the Gotham Dataset 2025 tables under the study's reservoir protocol.

Gotham ships 78 per-device packet tables inside one 22 GiB archive (1.4 M rows,
23 raw fields).  Three things need care:

* the tables are read straight out of the zip, so the 25 GB of raw PCAPs never
  touch the disk;
* several fields arrive as strings (``0x0018`` flags, hex checksums, MAC and IP
  addresses).  The literal addresses are **dropped on purpose**: attack traffic
  originates from the attacker's address, so keeping device identity as a
  feature would hand the classifier the label and reproduce exactly the leakage
  the study is about.  The remaining fields are parsed to numbers, and that
  choice is recorded in the audit;
* the split is decided by a hash of the row fingerprint, then each class is
  capped (5 000 train / 2 000 test) with exact-fingerprint de-duplication, which
  is the same rule the 2020-2023 corpora use.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import socket
import sys
import time
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = Path(r"E:\论文\data\external\y2025\Gotham2025\GothamDataset2025.zip")
DROP = ("eth.src", "eth.dst", "ip.src", "ip.dst", "frame.time")


def parse_hex(value: object) -> float:
    if not isinstance(value, str):
        return np.nan
    text = value.strip()
    if not text:
        return np.nan
    try:
        return float(int(text, 16))
    except ValueError:
        return np.nan


def parse_options(value: object) -> float:
    """Length of the TCP options blob; the blob itself is opaque hex."""
    if not isinstance(value, str):
        return np.nan
    text = value.strip()
    return float(len(text) // 2) if text else np.nan


def parse_protocol_depth(value: object) -> float:
    if not isinstance(value, str):
        return np.nan
    text = value.strip()
    return float(text.count(":") + 1) if text else np.nan


def convert(frame: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=frame.index)
    for column in frame.columns:
        name = str(column).strip()
        if name in DROP:
            continue
        series = frame[column]
        if name in ("ip.flags", "ip.checksum", "tcp.flags", "tcp.checksum"):
            out[name + "_int"] = series.map(parse_hex)
        elif name == "tcp.options":
            out["tcp.options_len"] = series.map(parse_options)
        elif name == "frame.protocols":
            out["frame.protocol_depth"] = series.map(parse_protocol_depth)
        else:
            out[name] = pd.to_numeric(series, errors="coerce")
    return out


def reservoir(zip_path: Path, train_cap: int, test_cap: int, chunk: int,
              test_fraction: float, seed: int):
    """Stream every table, split by fingerprint hash, cap each class per split."""
    seen = {"train": {}, "test": {}}
    kept = {"train": [], "test": []}
    labels_kept = {"train": [], "test": []}
    totals: dict[str, int] = {}
    duplicates = {"train": 0, "test": 0}
    features: list[str] | None = None
    dropped: list[str] = []
    rows = 0
    with zipfile.ZipFile(zip_path) as archive:
        names = sorted(info.filename for info in archive.infolist()
                       if info.filename.startswith("processed/")
                       and info.filename.endswith(".csv"))
        print(f"{len(names)} tables in the archive", flush=True)
        for name in names:
            started = time.time()
            with archive.open(name) as handle:
                for raw in pd.read_csv(handle, chunksize=chunk, low_memory=False):
                    raw.columns = [str(column).strip() for column in raw.columns]
                    labels = raw.pop("label").astype(str).str.strip()
                    numeric = convert(raw)
                    if features is None:
                        candidates = numeric.columns.tolist()
                        dropped = [column for column in candidates
                                   if numeric[column].isna().all()]
                        features = [column for column in candidates
                                    if column not in dropped]
                    numeric = numeric.reindex(columns=features).astype("float32")
                    # TCP and UDP fields are mutually exclusive, so requiring every
                    # column to be finite kept nothing: a TCP row has no UDP ports
                    # and vice versa.  Rows only need one measured field, and the
                    # protocol-specific gaps are filled with zero, which is what
                    # the tables themselves imply (no UDP header on a TCP packet).
                    present = np.isfinite(numeric.to_numpy(dtype=float)).sum(axis=1)
                    usable = present > 0
                    numeric = numeric.fillna(0.0)
                    rows += int(len(numeric))
                    forward = pd.util.hash_pandas_object(numeric, index=False).to_numpy(
                        dtype=np.uint64)
                    for position in np.flatnonzero(usable):
                        label = labels.iloc[position]
                        totals[label] = totals.get(label, 0) + 1
                        split = ("test" if (int(forward[position]) % 100) <
                                 int(round(test_fraction * 100)) else "train")
                        cap = test_cap if split == "test" else train_cap
                        bucket = seen[split].setdefault(label, set())
                        if len(bucket) >= cap:
                            continue
                        key = int(forward[position])
                        if key in bucket:
                            duplicates[split] += 1
                            continue
                        bucket.add(key)
                        kept[split].append(numeric.iloc[position].to_numpy(dtype=np.float32))
                        labels_kept[split].append(label)
            print(f"  {name}: {time.time() - started:.0f}s rows={rows:,}", flush=True)
    audit = {
        "rows_scanned": rows, "per_class_total": totals,
        "per_class_kept_train": {k: len(v) for k, v in seen["train"].items()},
        "per_class_kept_test": {k: len(v) for k, v in seen["test"].items()},
        "duplicates_in_reservoir": duplicates,
        "dropped_all_nan_columns": dropped,
        "dropped_by_leakage_control": list(DROP),
        "features": features,
        "split_rule": f"fingerprint % 100 < {int(round(test_fraction * 100))} -> test",
        "caps": {"train": train_cap, "test": test_cap},
    }
    return (np.vstack(kept["train"]), np.array(labels_kept["train"]),
            np.vstack(kept["test"]), np.array(labels_kept["test"]), audit)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", default="data_processed_gotham2025_v1")
    ap.add_argument("--audit-dir", default="results_data_audit_gotham2025_v1")
    ap.add_argument("--train-cap", type=int, default=5000)
    ap.add_argument("--test-cap", type=int, default=2000)
    ap.add_argument("--min-class-rows", type=int, default=200)
    ap.add_argument("--chunk", type=int, default=200_000)
    ap.add_argument("--test-fraction", type=float, default=0.30)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    out = ROOT / args.processed_dir
    audit_dir = ROOT / args.audit_dir
    out.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)

    X_train_all, y_train_all, X_test, y_test, audit = reservoir(
        ARCHIVE, args.train_cap, args.test_cap, args.chunk, args.test_fraction, args.seed)
    print(f"reservoir: train {X_train_all.shape} test {X_test.shape}", flush=True)

    counts = pd.Series(y_train_all).value_counts()
    small = [label for label, count in counts.items() if count < args.min_class_rows]
    if small:
        keep = ~np.isin(y_train_all, small)
        X_train_all, y_train_all = X_train_all[keep], y_train_all[keep]
        keep = ~np.isin(y_test, small)
        X_test, y_test = X_test[keep], y_test[keep]
        audit["dropped_small_classes"] = {label: int(counts[label]) for label in small}
        print(f"dropped classes with fewer than {args.min_class_rows} train rows: {small}",
              flush=True)

    X_train, X_val, y_train, y_val = train_test_split(
        X_train_all, y_train_all, test_size=0.15, stratify=y_train_all,
        random_state=args.seed)
    features = audit["features"]
    for name, values, target in (("train", X_train, y_train),
                                 ("validation", X_val, y_val),
                                 ("test", X_test, y_test)):
        frame = pd.DataFrame(values, columns=features)
        frame["target"] = target
        frame.to_csv(out / f"{name}.csv", index=False, encoding="utf-8-sig")
        print(f"  wrote {name}: {frame.shape}", flush=True)
    pd.Series(y_train_all).value_counts().rename_axis("target").reset_index(name="count").to_csv(
        out / "dataset_summary.csv", index=False, encoding="utf-8-sig")
    config = {"dataset": "GothamDataset2025", "label_column": "label",
              "per_class_cap_train": args.train_cap, "per_class_cap_test": args.test_cap,
              "reservoir_rule": ("streamed rows admitted per class until the cap; exact "
                                 "128-bit fingerprint dedup inside the reservoir"),
              "seed": args.seed, "features": features,
              "source_archive": str(ARCHIVE),
              "source_md5": "7ca78c0517ccb3d2854e823678e0f206"}
    (out / "preprocess_config.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    audit["splits"] = {"train": int(len(X_train)), "validation": int(len(X_val)),
                       "test": int(len(X_test))}
    audit["archive_sha256"] = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() \
        if ARCHIVE.stat().st_size < (1 << 31) else "not hashed (larger than 2 GiB)"
    audit["archive_md5"] = "7ca78c0517ccb3d2854e823678e0f206"
    (audit_dir / "data_processing_audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(audit["splits"], ensure_ascii=False))
    print("GOTHAM_PREPARED")


if __name__ == "__main__":
    main()
