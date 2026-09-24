"""Which decimals in the manuscript are not covered by the traceability check?

The number-traceability check re-derives 69 headline numbers.  The manuscript
contains many more decimals than that, so this script lists the decimals that no
assertion covers, grouped by the section they appear in, so a reviewer can see
exactly where the safety net ends.
"""
from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
EN = ROOT / "重构版论文_v4_20260915" / "English_SCI_Manuscript_v4.md"
TRACE = ROOT / "results_review_v5" / "number_traceability.csv"

DECIMAL = re.compile(r"\d+\.\d{3,}")


def covered() -> set[str]:
    values = set()
    for row in csv.DictReader(TRACE.open(encoding="utf-8-sig")):
        try:
            number = float(row["claimed"])
        except (KeyError, ValueError):
            continue
        for digits in range(3, 7):
            values.add(f"{number:.{digits}f}")
    return values


def main() -> int:
    text = EN.read_text(encoding="utf-8")
    body = text.split("## References")[0]
    section = "(front matter)"
    buckets: dict[str, set[str]] = defaultdict(set)
    for line in body.splitlines():
        if line.startswith("#"):
            section = line.lstrip("# ").strip()[:60]
            continue
        for token in DECIMAL.findall(line):
            buckets[section].add(token)

    known = covered()
    total = sum(len(v) for v in buckets.values())
    uncovered = {s: sorted(t for t in v if t not in known) for s, v in buckets.items()}
    missing = sum(len(v) for v in uncovered.values())
    print(f"distinct decimals with >=3 places in the body: {total}")
    print(f"matched by a traceability assertion: {total - missing}")
    print(f"not covered: {missing}")
    print()
    for section, values in uncovered.items():
        if values:
            print(f"[{section}] {len(values)}")
            print("   " + "  ".join(values))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
