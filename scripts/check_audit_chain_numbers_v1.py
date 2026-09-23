"""Verify the CIC-IDS2017 audit chain end to end.

Table 3 and Figure 2 present the processing chain (raw archive -> label mapping
-> non-finite removal -> physical-range screening -> deduplication -> capping ->
split), and the same chain appears in the graphical abstract.  Every one of
those numbers is a literal in a figure builder or a Markdown table, so a
regenerated audit would leave the paper silently stale.  This checks the
arithmetic inside each audit record, the split files against the retained
totals, and the presence of every stage count in both manuscripts.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
problems: list[str] = []
checked = 0


def check(label: str, ok: bool, detail: str = "") -> None:
    global checked
    checked += 1
    if not ok:
        problems.append(f"{label}: {detail}")
        print(f"ISSUE {label}: {detail}")


def normalised(text: str) -> str:
    return text.replace(",", "").replace(" ", "").replace("\u2009", "")


english = normalised((BASE / "English_SCI_Manuscript_v4.md").read_text(encoding="utf-8"))
chinese = normalised((BASE / "中文SCI论文_v4_重构版.md").read_text(encoding="utf-8"))

# The balanced control is capped down from the same 53,237-record pool, so its
# retained count lives in ``balanced_rows`` rather than in the capping key.
POPULATIONS = {
    "primary": ("data_processed_cic_natural_v3b", "capped_rows_before_balance", 53237),
    "balanced control": ("data_processed_cic_balanced_v3b", "balanced_rows", 3365),
    "full corpus": ("data_processed_cic_natural_v4_full", "capped_rows_before_balance", 2429503),
}

REPORTED = {  # stage counts that must be stated in both manuscripts
    "primary": ["2830743", "2671766", "158977", "2669025", "2741", "2668729",
                "296", "239093", "133", "53237", "37265", "7986", "3365", "673"],
    "full corpus": ["2429503"],
}

for label, (directory, retained_key, retained) in POPULATIONS.items():
    audit = json.loads((ROOT / directory / "dedup_audit.json").read_text(encoding="utf-8"))
    excluded = audit["source_rows"] - audit["mapped_rows"]
    check(f"{label}: mapped = source - excluded",
          audit["mapped_rows"] + excluded == audit["source_rows"],
          f"{audit['mapped_rows']} + {excluded} != {audit['source_rows']}")
    check(f"{label}: valid = mapped - invalid",
          audit["mapped_rows"] - audit["invalid_rows"] == audit["valid_rows"],
          f"{audit['mapped_rows']} - {audit['invalid_rows']} != {audit['valid_rows']}")
    check(f"{label}: physical valid = valid - physical invalid",
          audit["valid_rows"] - audit["invalid_physical_rows"] == audit["physical_valid_rows"],
          f"{audit['valid_rows']} - {audit['invalid_physical_rows']} != {audit['physical_valid_rows']}")
    check(f"{label}: unique after conflicts = unique before - removed",
          audit["unique_rows_before_conflict"] - audit["unique_rows_removed_for_conflicts"]
          == audit["unique_rows_after_conflict"],
          "conflict arithmetic does not close")
    check(f"{label}: retained total",
          audit[retained_key] == retained,
          f"{audit[retained_key]} vs expected {retained}")
    sizes = {name: len(pd.read_csv(ROOT / directory / f"{name}.csv", usecols=["target"]))
             for name in ("train", "validation", "test")}
    check(f"{label}: split sums to the retained total",
          sum(sizes.values()) == retained,
          f"{sizes} sums to {sum(sizes.values())}, expected {retained}")
    print(f"  {label:<18} raw {audit['source_rows']:,} -> retained {retained:,} "
          f"(split {sizes['train']:,}/{sizes['validation']:,}/{sizes['test']:,})")
    for value in REPORTED.get(label, [str(retained)]):
        check(f"{label}: {value} stated in the English manuscript", value in english)
        check(f"{label}: {value} stated in the Chinese manuscript", value in chinese)

print()
print(f"audit-chain assertions: {checked}")
if problems:
    print("AUDIT_CHAIN_FAILED")
    raise SystemExit(1)
print("AUDIT_CHAIN_OK")
