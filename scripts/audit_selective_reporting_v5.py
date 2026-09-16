"""Scan every result table for conditional-vs-equal-weight comparisons.

Purpose: detect whether any stored experiment shows a large advantage for the
conditional mechanism that the manuscript does not report (selective-reporting risk).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]

COND = re.compile(r"(rccf|cfrg|weighted|gated|drc)", re.I)
EQ = re.compile(r"(equal|rf_all|rf_chi2|chi2|base)", re.I)
METRIC = re.compile(r"(macro_f1|f1)", re.I)


def find_frames():
    for path in ROOT.rglob("*.csv"):
        if any(part.startswith(".") for part in path.parts):
            continue
        if "_release_stage" in str(path):
            continue
        try:
            df = pd.read_csv(path, low_memory=False, nrows=400)
        except Exception:
            continue
        cols = [c for c in df.columns if METRIC.search(c)]
        if not cols:
            continue
        model_col = next((c for c in df.columns if c.lower() in {"model", "name"}), None)
        if model_col is None:
            continue
        names = [str(n) for n in df[model_col].dropna().unique()]
        has_cond = any(COND.search(n) for n in names)
        has_eq = any(EQ.search(n) for n in names)
        if has_cond and has_eq:
            yield path, df, model_col, cols[0]


def main() -> None:
    rows = []
    for path, df, model_col, metric in find_frames():
        try:
            group = df.groupby(model_col)[metric].mean()
        except Exception:
            continue
        cond = group[[n for n in group.index if COND.search(str(n))]]
        eq = group[[n for n in group.index if EQ.search(str(n))]]
        if cond.empty or eq.empty:
            continue
        best_cond, best_cond_name = cond.max(), cond.idxmax()
        best_eq, best_eq_name = eq.max(), eq.idxmax()
        rows.append({
            "file": str(path.relative_to(ROOT)),
            "metric": metric,
            "best_conditional": round(float(best_cond), 5),
            "conditional_model": best_cond_name,
            "best_equal_weight": round(float(best_eq), 5),
            "equal_model": best_eq_name,
            "delta": round(float(best_cond - best_eq), 5),
        })
    out = pd.DataFrame(rows).drop_duplicates(subset=["file", "metric"])
    target = ROOT / "results_review_v5"
    target.mkdir(exist_ok=True)
    out.to_csv(target / "conditional_vs_equal_scan.csv", index=False, encoding="utf-8-sig")
    print(f"tables scanned with both arms: {len(out)}")
    if len(out):
        print()
        print("largest conditional advantages:")
        print(out.sort_values("delta", ascending=False).head(8).to_string(index=False))
        print()
        print("largest conditional disadvantages:")
        print(out.sort_values("delta").head(5).to_string(index=False))


if __name__ == "__main__":
    main()
