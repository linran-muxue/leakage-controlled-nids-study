"""Build grouped tables for the source-holdout protocol.

The CIC-IDS2017 experiments include a day-level holdout; the modern corpora have
no capture days, but two of them carry a natural grouping: Gotham ships one
table per IoT device (78 devices) and 6TiSCHSet ships one table per Cooja run
(206 runs).  "Train on some devices, test on devices never seen" is the modern
analogue of "train on four days, test on the fifth", and it is the split the
Gotham paper itself argues for, since its traffic is non-IID across devices.

The group identifier is written as a column so the holdout runner can split on
it, but it is never handed to the model.
"""
from __future__ import annotations

import argparse
import csv
import io
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]


def gotham(out: Path, per_group_cap: int) -> None:
    archive = Path(r"E:\论文\data\external\y2025\Gotham2025\GothamDataset2025.zip")
    rows: list[pd.DataFrame] = []
    with zipfile.ZipFile(archive) as z:
        names = sorted(n for n in z.namelist()
                       if n.startswith("processed/") and n.endswith(".csv"))
        for name in names:
            group = Path(name).stem
            with z.open(name) as handle:
                frame = pd.read_csv(handle, low_memory=False)
            frame.columns = [str(c).strip() for c in frame.columns]
            labels = frame.pop("label").astype(str).str.strip()
            keep = []
            for label in labels.unique():
                idx = labels.index[labels == label][:per_group_cap]
                keep.extend(idx)
            sub = frame.loc[keep].copy()
            sub["target"] = labels.loc[keep].to_numpy()
            sub["group"] = group
            rows.append(sub)
            print(f"  {group}: {len(sub):,} rows", flush=True)
    frame = pd.concat(rows, ignore_index=True)
    frame.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"{out}: {frame.shape}, groups={frame['group'].nunique()}")


def tisch(out: Path, per_group_cap: int) -> None:
    archive = Path(r"E:\论文\data\external\y2026\6TiSCHSet-2026"
                   r"\6tisch-attack-dataset-v1.0.0.zip")
    frames = []
    with zipfile.ZipFile(archive) as z:
        names = sorted(n for n in z.namelist()
                       if n.endswith(".csv") and ("/data/single/" in n
                                                  or "/data/multiattack/" in n))
        for name in names:
            group = Path(name).stem
            with z.open(name) as handle:
                frame = pd.read_csv(io.TextIOWrapper(handle, encoding="utf-8",
                                                     errors="replace"))
            frame = frame.drop(columns=["is_attacker", "timestamp", "node_id",
                                        "parent_id"], errors="ignore")
            label = frame.pop("attack_type").astype(int).astype(str)
            keep = []
            for value in label.unique():
                idx = label.index[label == value][:per_group_cap]
                keep.extend(idx)
            sub = frame.loc[keep].copy()
            sub["target"] = label.loc[keep].to_numpy()
            sub["group"] = group
            frames.append(sub)
    result = pd.concat(frames, ignore_index=True)
    result.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"{out}: {result.shape}, groups={result['group'].nunique()}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", choices=["gotham", "6tisch"], required=True)
    ap.add_argument("--per-group-cap", type=int, default=300)
    args = ap.parse_args()
    if args.dataset == "gotham":
        out = ROOT / "data_processed_gotham2025_grouped_v1"
        out.mkdir(parents=True, exist_ok=True)
        gotham(out / "all.csv", args.per_group_cap)
    else:
        out = ROOT / "data_processed_6tisch2026_grouped_v1"
        out.mkdir(parents=True, exist_ok=True)
        tisch(out / "all.csv", args.per_group_cap)
    print("GROUPED_CORPUS_DONE")


if __name__ == "__main__":
    main()
