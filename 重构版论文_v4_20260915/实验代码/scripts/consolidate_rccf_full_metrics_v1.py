"""Rebuild the aggregate RCCF artefacts from the per-seed files.

``run_rccf_cic_v1.py`` writes ``metrics_by_seed.csv`` and
``metrics_aggregate.csv`` from the seeds handled *in that invocation only*, so
when the full-corpus batch is resumed across several invocations (which is the
normal case at 2.3 h per seed) the aggregate files silently describe only the
last batch.  Supplementary item S29 points at ``metrics_by_seed.csv``, so the
aggregate has to be rebuilt from every per-seed file before the manuscript is
finalised.

The script is idempotent: it reads ``metrics_seed<seed>.csv`` for the canonical
seed list, sorts them into canonical order, rewrites ``metrics_by_seed.csv`` and
``metrics_aggregate.csv`` with the same column layout the runner uses, and
refreshes the ``seeds`` field of ``run_manifest.json``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SEEDS = [42, 2024, 3407, 7, 13, 101, 202, 303, 404, 505]


def consolidate(rccf_dir: Path, seeds: list[int]) -> pd.DataFrame:
    rows = []
    missing = []
    for seed in seeds:
        path = rccf_dir / f"metrics_seed{seed}.csv"
        if not path.exists():
            missing.append(seed)
            continue
        frame = pd.read_csv(path)
        # The runner already stamps a ``seed`` column; assert it matches the file
        # name instead of blindly inserting a duplicate column.
        if "seed" in frame.columns:
            recorded = frame["seed"].astype(int).tolist()
            if recorded != [int(seed)]:
                raise SystemExit(f"{path.name}: recorded seed {recorded} != {seed}")
        else:
            frame.insert(0, "seed", int(seed))
        rows.append(frame)
    if not rows:
        raise SystemExit(f"no per-seed metrics found in {rccf_dir}")
    frame = pd.concat(rows, ignore_index=True)
    frame.to_csv(rccf_dir / "metrics_by_seed.csv", index=False, encoding="utf-8-sig")

    numeric = [c for c in frame.columns if c not in {"model", "seed"}]
    aggregate = pd.DataFrame([{
        "model": str(frame["model"].iloc[0]),
        **{f"{c}_mean": float(frame[c].mean()) for c in numeric},
        **{f"{c}_std": float(frame[c].std(ddof=1)) if len(frame) > 1 else float("nan")
           for c in numeric},
    }])
    aggregate.to_csv(rccf_dir / "metrics_aggregate.csv", index=False, encoding="utf-8-sig")

    manifest_path = rccf_dir / "run_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["seeds"] = [int(s) for s in frame["seed"].tolist()]
        manifest["consolidated_from_per_seed_files"] = True
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2),
                                 encoding="utf-8")

    print(f"consolidated {len(frame)} seed(s): {frame['seed'].tolist()}")
    if missing:
        print(f"missing seeds (not yet run): {missing}")
    return frame


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rccf-dir", type=Path,
                        default=Path("results_rccf_cic_natural_v4_full"))
    parser.add_argument("--seeds", type=int, nargs="+", default=SEEDS)
    args = parser.parse_args(argv)
    consolidate(args.rccf_dir, list(args.seeds))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
