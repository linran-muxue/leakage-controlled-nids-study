"""Correct the Train (s) column of Table 4(b) to the released run's means.

Table 4(b) is the balanced control population and is labelled with the three
seeds.  Six of its eight columns for the three forest rows reproduce
results_cic_balanced_baselines_v3b exactly (accuracy, balanced accuracy,
Macro-F1, Log Loss, Brier, ECE, predict time), but the Train (s) cell did not:
the table printed 0.451 / 0.299 / 0.494 where the released run gives
0.249586 / 0.235422 / 0.130834.  No artefact in the repository contains the
printed values - not the per-seed file, not the aggregate, not the two earlier
balanced runs - and they are not a constant multiple of the released times
(1.8x, 1.3x and 3.8x), so they are not a machine-speed difference either.

The row for the conditional mechanism (9.130 s) and the XGBoost row (0.398 s)
do reproduce their sources and are left alone.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
PY = sys.executable

EXPECTED = {
    "equal_rf_chi2": (0.249586, "0.451", "0.250"),
    "equal_rf_all": (0.235422, "0.299", "0.235"),
    "extra_trees_chi2": (0.130834, "0.494", "0.131"),
}

ROWS = {
    "English_SCI_Manuscript_v4.md": {
        "equal_rf_chi2": ("| Equal RF (chi-square) | 0.96304 | 0.96304 | **0.963215** | "
                          "0.13569 | 0.013453 | 0.026132 | 0.451 | 0.0284 |"),
        "equal_rf_all": ("| Equal RF (full features) | 0.96106 | 0.96106 | 0.960997 | "
                         "**0.12237** | **0.012542** | 0.025232 | 0.299 | 0.0283 |"),
        "extra_trees_chi2": ("| ExtraTrees (chi-square) | 0.96106 | 0.96106 | 0.960947 | "
                             "0.15179 | 0.014300 | 0.036976 | 0.494 | 0.0296 |"),
    },
    "中文SCI论文_v4_重构版.md": {
        "equal_rf_chi2": ("| 等权森林（χ²） | 0.96304 | 0.96304 | **0.963215** | 0.13569 | "
                          "0.013453 | 0.026132 | 0.451 | 0.0284 |"),
        "equal_rf_all": ("| 等权森林（全特征） | 0.96106 | 0.96106 | 0.960997 | "
                         "**0.12237** | **0.012542** | 0.025232 | 0.299 | 0.0283 |"),
        "extra_trees_chi2": ("| 极端随机树（χ²） | 0.96106 | 0.96106 | 0.960947 | 0.15179 | "
                             "0.014300 | 0.036976 | 0.494 | 0.0296 |"),
    },
}


def main() -> None:
    aggregate = pd.read_csv(ROOT / "results_cic_balanced_baselines_v3b" /
                            "metrics_aggregate_flat.csv").set_index("model")
    renders = {}
    for model, (expected, old, new) in EXPECTED.items():
        source = float(aggregate.loc[model, "train_seconds_mean"])
        if abs(source - expected) > 5e-7:
            raise SystemExit(f"source changed: {model} train_seconds_mean = {source}")
        if f"{source:.3f}" != new:
            raise SystemExit(f"{model}: {source} no longer renders as {new}")
        renders[model] = (old, new)
        print(f"source {model:<18}{source:.6f} -> {new} (printed {old})")

    for name, rows in ROWS.items():
        path = BASE / name
        text = path.read_text(encoding="utf-8")
        for model, old_row in rows.items():
            old, new = renders[model]
            if old_row not in text:
                raise SystemExit(f"{name}: row anchor not found for {model}")
            new_row = old_row.replace(f"| {old} |", f"| {new} |", 1)
            if new_row == old_row:
                raise SystemExit(f"{name}: train cell not found in the {model} row")
            if text.count(old_row) != 1:
                raise SystemExit(f"{name}: row anchor not unique for {model}")
            text = text.replace(old_row, new_row, 1)
        path.write_text(text, encoding="utf-8")
        print(f"updated {name}")

    audit = subprocess.run([PY, str(ROOT / "scripts" / "audit_main_tables_v1.py")],
                           cwd=ROOT, capture_output=True, text=True, errors="replace")
    control = audit.stdout
    tail = [line for line in control.splitlines() if line.startswith("ISSUE")]
    if audit.returncode != 0:
        raise SystemExit("audit_main_tables_v1 still reports:\n" + "\n".join(tail))
    print([line for line in control.splitlines() if "assertions passed" in line][-1])
    print("TABLE4_BALANCED_TRAIN_TIMES_FIXED")


if __name__ == "__main__":
    main()
