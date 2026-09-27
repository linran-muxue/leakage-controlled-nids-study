"""Near-duplicate audit of the study population (residual gap).

The introduction lists near-duplicate flows among the hazards of public datasets, but
the pipeline only removes *exact* duplicates. This script quantifies how many rows are
near-duplicates at a controlled numerical resolution, and how many of those pairs
straddle the train/test boundary.

Method: every numeric feature is rounded to k significant digits, the rounded rows are
hashed, and rows sharing a hash are treated as near-duplicates at that resolution. This
is a conservative, resolution-parameterised definition: it is reproducible and does not
depend on a distance metric or a clustering threshold.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]


def load(path: Path):
    frame = pd.read_csv(path, low_memory=False)
    return frame.drop(columns=["target"]).apply(pd.to_numeric).to_numpy(), frame["target"].to_numpy()


def round_sig(x: np.ndarray, digits: int) -> np.ndarray:
    """Round to a fixed number of significant digits (magnitude-aware)."""
    out = np.zeros_like(x)
    nonzero = x != 0
    mag = np.zeros_like(x)
    mag[nonzero] = np.floor(np.log10(np.abs(x[nonzero])))
    scale = np.power(10.0, mag - digits + 1)
    out[nonzero] = np.round(x[nonzero] / scale[nonzero]) * scale[nonzero]
    return out


def hash_rows(x: np.ndarray) -> np.ndarray:
    return np.array([hashlib.blake2b(row.tobytes(), digest_size=16).hexdigest()
                     for row in np.ascontiguousarray(x)])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", default="data_processed_cic_natural_v3b")
    ap.add_argument("--output-dir", default="results_near_duplicate_v5")
    ap.add_argument("--digits", nargs="+", type=int, default=[3, 4])
    args = ap.parse_args()

    proc = ROOT / args.processed_dir
    out = ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    frames = {}
    for split in ("train", "validation", "test"):
        X, y = load(proc / f"{split}.csv")
        frames[split] = (X, y)
    X_all = np.vstack([frames[s][0] for s in ("train", "validation", "test")])
    split_of = np.concatenate([np.full(len(frames[s][0]), s) for s in ("train", "validation", "test")])

    rows = []
    for digits in args.digits:
        rounded = round_sig(X_all, digits)
        hashes = hash_rows(rounded)
        frame = pd.DataFrame({"h": hashes, "split": split_of})
        sizes = frame.groupby("h").size()
        dup_groups = sizes[sizes > 1]
        rows_in_dup = int(dup_groups.sum())
        # pairs that straddle the train/test boundary
        cross = (frame.groupby("h")["split"].nunique() > 1)
        cross_hashes = int(cross.sum())
        cross_rows = int(sizes[cross].sum()) if cross_hashes else 0
        rows.append({
            "significant_digits": digits,
            "total_rows": int(len(X_all)),
            "near_duplicate_groups": int(len(dup_groups)),
            "rows_in_near_duplicate_groups": rows_in_dup,
            "near_duplicate_row_fraction": rows_in_dup / len(X_all),
            "groups_spanning_splits": cross_hashes,
            "rows_in_cross_split_groups": cross_rows,
            "cross_split_row_fraction": cross_rows / len(X_all),
        })
        print(f"digits={digits}: groups={len(dup_groups)} rows={rows_in_dup} "
              f"({rows_in_dup / len(X_all):.4%}) cross-split groups={cross_hashes}", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(out / "near_duplicate_summary.csv", index=False, encoding="utf-8-sig")
    (out / "near_duplicate_summary.json").write_text(json.dumps({
        "population": "natural-prior study population (train+validation+test)",
        "method": "features rounded to k significant digits, rows hashed, hash collisions counted",
        "results": rows,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print()
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
