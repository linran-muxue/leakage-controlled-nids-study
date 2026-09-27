"""Build the N-BaIoT benchmark with the paper's leakage-controlled protocol.
N-BaIoT (Meidan et al., 2018) records Mirai and Gafgyt botnet traffic from nine
consumer IoT devices alongside benign traffic, with 115 flow-statistical
features. It is used here as an independent native-label benchmark whose domain
(IoT) the three existing datasets do not cover.

Protocol, identical to the CIC pipeline: global exact deduplication before any
split, a per-class cap applied by reservoir sampling so that file order cannot
bias the sample, then a stratified 70/15/15 split.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
LABEL_BY_FOLDER = {"benign": "Normal", "mirai_attacks_csv": "Mirai", "gafgyt_attacks_csv": "Gafgyt"}


def label_for(path: Path) -> str:
    parent = path.parent.name
    if parent in LABEL_BY_FOLDER:
        return LABEL_BY_FOLDER[parent]
    return path.stem.split("_")[0].capitalize()


def rows_in(path: Path, chunksize: int = 200_000):
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        first = handle.readline()
    header = 0 if not all(part.replace(".", "", 1).replace("-", "", 1).isdigit()
                          for part in first.strip().split(",")) else None
    for chunk in pd.read_csv(path, header=header, chunksize=chunksize,
                             low_memory=False, dtype=np.float64, on_bad_lines="skip"):
        yield chunk.astype(np.float32)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", type=Path, default=Path(r"E:\论文\data\external\N-BaIoT"))
    ap.add_argument("--processed-dir", type=Path, required=True)
    ap.add_argument("--per-class-cap", type=int, default=60_000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)

    files = sorted(p for p in args.raw_dir.rglob("*.csv") if p.name != "demonstrate_structure.csv")
    print(f"csv files: {len(files)}", flush=True)
    seen: set[str] = set()
    reservoirs: dict[str, list[np.ndarray]] = {}
    counts = {"raw": 0, "duplicate": 0, "kept": 0}
    for path in files:
        label = label_for(path)
        kept = reservoirs.setdefault(label, [])
        for chunk in rows_in(path):
            values = chunk.to_numpy(dtype=np.float32)
            for row in values:
                counts["raw"] += 1
                fingerprint = hashlib.blake2b(row.tobytes(), digest_size=16).hexdigest()
                if fingerprint in seen:
                    counts["duplicate"] += 1
                    continue
                seen.add(fingerprint)
                if len(kept) < args.per_class_cap:
                    kept.append(row)
                else:
                    slot = int(rng.integers(0, counts["raw"]))
                    if slot < args.per_class_cap:
                        kept[slot] = row
        print(f"  {label:<8} {path.name:<28} reservoir={len(kept)}", flush=True)

    frames = []
    for label, rows in reservoirs.items():
        frames.append(pd.DataFrame(np.vstack(rows), columns=None).assign(target=label))
    frame = pd.concat(frames, ignore_index=True)
    counts["kept"] = len(frame)
    counts["per_class"] = {k: int(v) for k, v in frame["target"].value_counts().items()}
    print("audit:", json.dumps(counts, ensure_ascii=False), flush=True)

    train, temp = train_test_split(frame, test_size=0.30, stratify=frame["target"],
                                   random_state=args.seed)
    valid, test = train_test_split(temp, test_size=0.50, stratify=temp["target"],
                                   random_state=args.seed)
    args.processed_dir.mkdir(parents=True, exist_ok=True)
    for name, part in (("train", train), ("validation", valid), ("test", test)):
        part.reset_index(drop=True).to_csv(args.processed_dir / f"{name}.csv",
                                           index=False, encoding="utf-8-sig")
    summary = frame["target"].value_counts().rename_axis("target").reset_index(name="count")
    summary.to_csv(args.processed_dir / "dataset_summary.csv", index=False, encoding="utf-8-sig")
    (args.processed_dir / "preprocess_config.json").write_text(json.dumps({
        "dataset": "N-BaIoT",
        "source": "UCI Machine Learning Repository, dataset 442 (detection of IoT botnet attacks)",
        "per_class_cap": args.per_class_cap, "seed": args.seed,
        "dedup": "global exact row hashing before splitting",
        "split": "stratified 70/15/15", "features": int(frame.shape[1] - 1),
        "labels": sorted(frame["target"].unique().tolist()),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(summary.to_string(index=False))
    print(f"rows: train={len(train)} validation={len(valid)} test={len(test)}")


if __name__ == "__main__":
    main()
