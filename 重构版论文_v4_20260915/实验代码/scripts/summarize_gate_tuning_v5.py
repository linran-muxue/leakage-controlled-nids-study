"""Summarise the S2 gate-tuning grid."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    d = pd.read_csv(ROOT / "results_gate_tuning_v5" / "gate_search_results.csv")
    print("configurations:", len(d))
    print("distinct val_macro_f1 values:", d["val_macro_f1"].nunique())
    print("val_macro_f1 min/max:", d["val_macro_f1"].min(), d["val_macro_f1"].max())
    print("total disagreements vs equal weight:", int(d["disagreement_vs_equal_weight"].sum()))
    print("total disagreements vs default gate:", int(d["disagreement_vs_default_gate"].sum()))
    print("weight entropy min/max:", d["mean_weight_entropy"].min(), d["mean_weight_entropy"].max())
    print()
    print("by cv:")
    print(d.groupby("cv").agg(
        val_macro_f1=("val_macro_f1", "mean"),
        disagreements=("disagreement_vs_equal_weight", "sum"),
        entropy_mean=("mean_weight_entropy", "mean"),
        entropy_min=("mean_weight_entropy", "min"),
    ).round(8).to_string())
    print()
    print("distinct val_macro_f1 by cv:")
    for cv, sub in d.groupby("cv"):
        print(f"  cv={cv}: {sub['val_macro_f1'].nunique()} distinct values "
              f"({sub['val_macro_f1'].min():.8f} .. {sub['val_macro_f1'].max():.8f})")
    print()
    print("distinct val_macro_f1 by seed:")
    for seed, sub in d.groupby("seed"):
        print(f"  seed={seed}: {sub['val_macro_f1'].nunique()} distinct values")


if __name__ == "__main__":
    main()
