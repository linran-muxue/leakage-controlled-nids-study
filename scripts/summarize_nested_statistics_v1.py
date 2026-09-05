from __future__ import annotations

import argparse
import sys
from pathlib import Path
import pandas as pd

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.nested_statistics import paired_fold_summary


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--results-dir", type=Path, required=True); ap.add_argument("--output", type=Path, required=True); args = ap.parse_args(); args.output.parent.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.results_dir / "outer_modelwise_metrics.csv")
    pivot = df.pivot(index="fold", columns="model", values="macro_f1")
    rows=[]
    for candidate in ["xgboost", "extra_trees"]:
        out=paired_fold_summary(pivot["random_forest"].to_numpy(), pivot[candidate].to_numpy(), seed=42, n_bootstrap=5000)
        rows.append({"comparison":f"{candidate}_vs_random_forest","metric":"macro_f1",**out})
    pd.DataFrame(rows).to_csv(args.output,index=False,encoding="utf-8-sig"); print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__": main()
