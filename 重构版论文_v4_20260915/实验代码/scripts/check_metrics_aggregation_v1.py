"""Detect stale aggregate metric files left by partial batch runs.

``run_rccf_cic_v1.py`` rewrites ``metrics_by_seed.csv`` and
``metrics_aggregate.csv`` from the seeds handled *in that invocation*.  When a
ten-seed batch is resumed in several passes, the last pass silently truncates
both files to its own seeds.  That happened to the 413,209-flow run, whose
published aggregate described 7 seeds while the manuscript quoted 10, and to
the full-corpus run.  Both directories are now consolidated from the per-seed
files; this check makes sure a future partial run cannot ship unnoticed.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]


def scan(root: Path) -> tuple[list[tuple[str, int, int, str]], list[str]]:
    """Compare every results directory with its own per-seed metric files."""
    rows: list[tuple[str, int, int, str]] = []
    problems: list[str] = []
    for directory in sorted(root.glob("results_*")):
        if not directory.is_dir():
            continue
        per_seed = sorted(
            int(match.group(1))
            for match in (re.match(r"metrics_seed(\d+)\.csv$", path.name)
                          for path in directory.glob("metrics_seed*.csv"))
            if match
        )
        if not per_seed:
            continue
        aggregate = directory / "metrics_by_seed.csv"
        if not aggregate.exists():
            status = "MISSING AGGREGATE"
            count = -1
        else:
            try:
                count = len(pd.read_csv(aggregate))
            except Exception:
                count = -1
            status = "ok" if count == len(per_seed) else "TRUNCATED"
        if status != "ok":
            problems.append(f"{directory.name}: {len(per_seed)} per-seed files but "
                            f"metrics_by_seed.csv has {count} row(s)")
        rows.append((directory.name, len(per_seed), count, status))
    return rows, problems


def main() -> int:
    rows, problems = scan(ROOT)
    print(f"{'directory':<46}{'per-seed':>9}{'by_seed':>9}  status")
    for name, per_seed, count, status in rows:
        print(f"{name:<46}{per_seed:>9}{count:>9}  {status}")
    print()
    if problems:
        for problem in problems:
            print(f"ISSUE {problem}")
        print("METRICS_AGGREGATION_FAILED")
        return 1
    print("METRICS_AGGREGATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
