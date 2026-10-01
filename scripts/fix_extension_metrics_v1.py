"""Backfill the per-seed metric files and correct test_samples_mean.

The two extension runners aggregated by group size instead of by test-set size,
which made the data-authenticity check compare a 10-row aggregate against a
27,000-row prediction file.  They also wrote only ``metrics_by_seed.csv`` while
the metric-aggregation check expects one ``metrics_seed<seed>.csv`` per seed.
Both are repaired here from the preserved per-seed table.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
DIRS = ["results_rccf_nsl_v10", "results_rccf_unsw_v10", "results_rccf_nbaiot_v10",
        "results_rccf_cic_ids2018_v1", "results_rccf_cic_iot2023_v1"]


def data_rows(path: Path) -> int:
    with path.open("rb") as handle:
        count = -1
        while True:
            block = handle.read(1 << 22)
            if not block:
                break
            count += block.count(b"\n")
    return count


def main() -> None:
    for name in DIRS:
        folder = ROOT / name
        table = folder / "metrics_by_seed.csv"
        if not table.exists():
            print(f"skip {name}: no metrics_by_seed.csv")
            continue
        frame = pd.read_csv(table)
        predictions = sorted(folder.glob("predictions*seed*.csv"))
        if not predictions:
            raise SystemExit(f"{name}: no per-seed predictions to size the test set")
        test_rows = data_rows(predictions[0])
        # the repository convention is one metrics_seed<seed>.csv for
        # single-model runs; multi-model runs keep only metrics_by_seed.csv, and
        # the aggregation check skips directories without per-seed files
        if frame["model"].nunique() == 1:
            for _, row in frame.iterrows():
                row.to_frame().T.to_csv(folder / f"metrics_seed{int(row['seed'])}.csv",
                                        index=False, encoding="utf-8-sig")
        else:
            for stale in folder.glob("metrics_seed*.csv"):
                stale.unlink()
        aggregate = frame.groupby("model").agg(
            macro_f1_mean=("macro_f1", "mean"), macro_f1_std=("macro_f1", "std"),
            accuracy_mean=("accuracy", "mean"),
            balanced_accuracy_mean=("balanced_accuracy", "mean"),
            log_loss_mean=("log_loss", "mean"),
            train_seconds_mean=("train_seconds", "mean")).reset_index()
        aggregate["test_samples_mean"] = test_rows
        aggregate.to_csv(folder / "metrics_aggregate.csv", index=False,
                         encoding="utf-8-sig")
        print(f"{name}: {len(frame)} per-seed files, test_rows={test_rows:,}, "
              f"models={sorted(frame['model'].unique())}")
    print("EXTENSION_METRICS_FIXED")


if __name__ == "__main__":
    main()
