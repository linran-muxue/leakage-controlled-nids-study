"""Split a single labelled table into train/test CSVs for the reservoir pipeline."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def read(path: Path) -> pd.DataFrame:
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path, low_memory=False)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--test-fraction", type=float, default=0.30)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    frame = read(args.input)
    rng = np.random.default_rng(args.seed)
    order = rng.permutation(len(frame))
    cut = int(round(len(frame) * (1 - args.test_fraction)))
    args.outdir.mkdir(parents=True, exist_ok=True)
    train = frame.iloc[order[:cut]]
    test = frame.iloc[order[cut:]]
    train.to_csv(args.outdir / "train.csv", index=False, encoding="utf-8-sig")
    test.to_csv(args.outdir / "test.csv", index=False, encoding="utf-8-sig")
    print(f"{args.input.name}: {len(train):,} train / {len(test):,} test -> {args.outdir}")


if __name__ == "__main__":
    main()
