"""Widen the Section 5.6 open-set ranges to what the released suite produces.

Section 5.6 states that the conditional branch reaches an AUROC of 0.643 to
0.694 with an unknown-class recall of 0.0015 to 0.0088, against 0.919 to 0.940
with 0.057 to 0.128 for the equal-weight forest.  The four recall and equal-arm
ceiling values cannot be reproduced from the released, verified open-set run
``results_cfrg_open_set_v5_verified/open_set_metrics.csv`` (three seeds, 1726
known and 2047 unknown evaluation flows):

    conditional branch, uncalibrated and temperature-scaled exports
        AUROC  0.643513 0.674473 0.684460 | 0.651222 0.693891 0.687039
               -> 0.643 to 0.694 (unchanged)
        recall 0.001466 0.005862 0.036150 | 0.008793 0.010259 0.039570
               -> 0.0015 to 0.0396 (printed 0.0088)
    equal-weight forest, uncalibrated and temperature-scaled exports
        AUROC  0.919140 0.939964 0.947932 -> 0.919 to 0.948 (printed 0.940)
        recall 0.056668 0.127504 0.373718 -> 0.057 to 0.374 (printed 0.128)

The printed ceilings described two of the three released seeds, and for the
conditional branch only the uncalibrated export, so both spreads were
understated; the surviving endpoints are the same three seeds (0.643 is the
truncated minimum, 0.919 the rounded one).  Only the conformal rows are
excluded, because the conformal predictor is the rejection rule rather than the
score it thresholds -- those rows are recorded by the audit script instead.

Per the author's "use the real data" decision the endpoints are corrected in
both manuscripts, in Table 5 and in the self-check table, and the sentence now
names the scope the ranges span.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
SUITE = ROOT / "results_cfrg_open_set_v5_verified" / "open_set_metrics.csv"

CONDITIONAL = ("cfrg_forest", "cfrg_forest_temperature_scaled")
EQUAL = ("equal_rf", "equal_rf_temperature_scaled")

# label -> (printed endpoint, arm, column, rounding)
EXPECTED = {
    "conditional AUROC lower": ("0.643", CONDITIONAL, "auroc", "truncate"),
    "conditional AUROC upper": ("0.694", CONDITIONAL, "auroc", "round"),
    "conditional recall lower": ("0.0015", CONDITIONAL, "unknown_recall", "round"),
    "conditional recall upper": ("0.0396", CONDITIONAL, "unknown_recall", "round"),
    "equal AUROC lower": ("0.919", EQUAL, "auroc", "round"),
    "equal AUROC upper": ("0.948", EQUAL, "auroc", "round"),
    "equal recall lower": ("0.057", EQUAL, "unknown_recall", "round"),
    "equal recall upper": ("0.374", EQUAL, "unknown_recall", "round"),
}

EDITS = {
    "English_SCI_Manuscript_v4.md": (
        ("with an unknown-class recall of 0.0015 to 0.0088, whereas the equal-weight "
         "forest reaches an AUROC of 0.919 to 0.940 with a recall of 0.057 to 0.128.",
         "with an unknown-class recall of 0.0015 to 0.0396, whereas the equal-weight "
         "forest reaches an AUROC of 0.919 to 0.948 with a recall of 0.057 to 0.374. "
         "Both ranges span the three released seeds and the uncalibrated and "
         "temperature-scaled probability exports.",
         "Section 5.6 open-set ranges"),
        ("| AUROC 0.92-0.94 against 0.64-0.69 |",
         "| AUROC 0.92-0.95 against 0.64-0.69 |", "Table 5 open-set row"),
    ),
    "中文SCI论文_v4_重构版.md": (
        ("未知类召回率为 0.0015 至 0.0088；等权森林的 AUROC 为 0.919 至 0.940，"
         "未知类召回率为 0.057 至 0.128。",
         "未知类召回率为 0.0015 至 0.0396；等权森林的 AUROC 为 0.919 至 0.948，"
         "未知类召回率为 0.057 至 0.374（区间覆盖三个已发布种子，以及未校准与"
         "温度缩放两种概率导出）。",
         "第 5.6 节开放集区间"),
        ("AUROC 0.92–0.94 显著高于条件加权分支 0.64–0.69",
         "AUROC 0.92–0.95 显著高于条件加权分支 0.64–0.69", "表 5 开放集行"),
    ),
    "论文自查表.md": (
        ("开放集 AUROC 0.64–0.69 显著低于等权 0.92–0.94",
         "开放集 AUROC 0.64–0.69 显著低于等权 0.92–0.95", "E8 开放集区间"),
    ),
}

STALE = ("0.0015 to 0.0088", "0.919 to 0.940", "0.057 to 0.128", "0.92-0.94",
         "0.0015 至 0.0088", "0.919 至 0.940", "0.057 至 0.128", "0.92–0.94")


def endpoints() -> dict[str, str]:
    frame = pd.read_csv(SUITE)
    values: dict[str, str] = {}
    for label, (printed, models, column, rounding) in EXPECTED.items():
        rows = frame[frame.model.isin(models)]
        if len(rows) != len(models) * 3:
            raise SystemExit(f"{label}: expected three seeds per export, found {len(rows)} rows")
        low = "lower" in label
        source = rows[column].min() if low else rows[column].max()
        digits = len(printed.split(".")[1])
        if rounding == "truncate":
            if not low:
                raise SystemExit(f"{label}: only lower bounds may truncate")
            scaled = 10**digits
            rendered = f"{math.floor(source * scaled) / scaled:.{digits}f}"
        else:
            rendered = f"{round(source, digits):.{digits}f}"
        if rendered != printed:
            raise SystemExit(f"{label}: source {source:.6f} renders as {rendered}, not {printed}")
        values[label] = f"{source:.6f}"
        print(f"source {label:<24} {source:.6f} -> {printed}")
    return values


def main() -> None:
    endpoints()
    for name, edits in EDITS.items():
        path = BASE / name
        text = path.read_text(encoding="utf-8")
        for old, new, label in edits:
            if old in text:
                if text.count(old) != 1:
                    raise SystemExit(f"{label}: anchor not unique in {name}")
                text = text.replace(old, new, 1)
            elif new not in text:
                raise SystemExit(f"{label}: neither the old nor the new text is present in {name}")
        path.write_text(text, encoding="utf-8")
        print(f"updated {name}")

    for name in EDITS:
        text = (BASE / name).read_text(encoding="utf-8")
        for stale in STALE:
            if stale in text:
                raise SystemExit(f"{name} still contains the stale value {stale!r}")
    print("OPEN_SET_ENDPOINTS_FIXED")


if __name__ == "__main__":
    main()
