"""Replace the NSL-KDD calibration figure with the metric it names.

Section 5.5 reported "ECE of 0.4819" for NSL-KDD.  The value 0.4819 is the
source MCE; the source ECE is 0.209651 (three-seed means from
results_rccf_nsl_v2_final/metrics_aggregate.csv).  Per the author's decision the
label stays and the number is corrected to the real ECE, in both manuscripts.

Nothing else changes: the surrounding sentence already argues that the high log
loss and calibration error follow from the rejection rate, and 0.209651 is still
an order of magnitude above the CIC-IDS2017 figure (0.006849).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
SOURCE = ROOT / "results_rccf_nsl_v2_final" / "metrics_aggregate.csv"

EN_OLD = "with a Log Loss of 1.6802, ECE of 0.4819 and coverage of 0.6198"
ZH_OLD = "Log Loss 1.6802，ECE 0.4819，覆盖率 0.6198"


def fix(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise SystemExit(f"anchor not found exactly once in {path.name}: {text.count(old)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"updated {path.name}")


def main() -> None:
    frame = pd.read_csv(SOURCE)
    row = frame[frame.model == "rccf"].iloc[0]
    ece, mce = float(row.ece_mean), float(row.mce_mean)
    if abs(ece - 0.209651) > 5e-6:
        raise SystemExit(f"source ECE changed: {ece}")
    if abs(mce - 0.481856) > 5e-6:
        raise SystemExit(f"source MCE changed: {mce}")
    print(f"source: ECE {ece:.6f}, MCE {mce:.6f} (three seeds, NSL-KDD)")

    new_value = f"{ece:.6f}"
    fix(BASE / "English_SCI_Manuscript_v4.md", EN_OLD, EN_OLD.replace("0.4819", new_value))
    fix(BASE / "中文SCI论文_v4_重构版.md", ZH_OLD, ZH_OLD.replace("0.4819", new_value))

    for name in ("English_SCI_Manuscript_v4.md", "中文SCI论文_v4_重构版.md"):
        text = (BASE / name).read_text(encoding="utf-8")
        if "ECE of 0.4819" in text or "ECE 0.4819" in text:
            raise SystemExit(f"{name} still quotes the MCE value as ECE")
    print("NSL_ECE_FIXED")


if __name__ == "__main__":
    main()
