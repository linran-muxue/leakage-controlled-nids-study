from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

def main():
    ap = argparse.ArgumentParser(description="Aggregate independent UNSW-NB15 runs.")
    ap.add_argument("--dirs", type=Path, nargs="+", required=True)
    ap.add_argument("--seeds", type=int, nargs="+", required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if len(args.dirs) != len(args.seeds):
        ap.error("--dirs and --seeds must have the same length")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frames = []
    for d, seed in zip(args.dirs, args.seeds):
        f = pd.read_csv(d / "metrics.csv")
        f.insert(1, "seed", int(seed))
        frames.append(f)
    allf = pd.concat(frames, ignore_index=True)
    allf.to_csv(args.output.parent / "metrics_3seeds.csv", index=False, encoding="utf-8-sig")
    metric_cols = ["accuracy", "balanced_accuracy", "macro_f1", "log_loss", "brier_macro", "ece"]
    summary = allf.groupby("model", sort=True)[metric_cols].agg(["mean", "std"]).reset_index()
    summary.to_csv(args.output, index=False, encoding="utf-8-sig")
    print(summary.to_string(index=False))
if __name__=="__main__": main()
