"""Merge the robustness runs into a single three-seed summary."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
PARTS = [ROOT / "results_robustness_extended_v5" / "robustness_extended_by_seed.csv",
         ROOT / "results_robustness_extended_v5_seeds" / "robustness_extended_by_seed.csv"]
OUT = ROOT / "results_robustness_extended_v5"


def main() -> None:
    frames = [pd.read_csv(p) for p in PARTS if p.exists()]
    df = pd.concat(frames, ignore_index=True)
    df.to_csv(OUT / "robustness_extended_all_seeds.csv", index=False, encoding="utf-8-sig")
    summary = (df.groupby(["model", "condition"])["macro_f1"]
               .agg(["mean", "std", "count"]).round(6).reset_index())
    clean = summary[summary.condition == "clean"].set_index("model")["mean"]
    summary["relative_drop_pct"] = summary.apply(
        lambda r: 100 * (1 - r["mean"] / clean[r["model"]]) if r["condition"] != "clean" else 0.0,
        axis=1).round(3)
    summary.to_csv(OUT / "robustness_extended_summary_3seeds.csv", index=False, encoding="utf-8-sig")
    (OUT / "robustness_extended_summary_3seeds.json").write_text(json.dumps({
        "seeds": sorted(df["seed"].unique().tolist()),
        "summary": summary.to_dict(orient="records"),
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
