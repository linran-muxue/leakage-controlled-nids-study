"""Count self-check statuses from the item rows only."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
SC = (ROOT / "重构版论文_v4_20260915" / "论文自查表.md").read_text("utf-8")

item_rows = re.findall(r"^\| ([A-G]\d+) \|.*$", SC, flags=re.M)
passed = partial = missing = 0
for line in re.findall(r"^\| [A-G]\d+ \|.*$", SC, flags=re.M):
    if "**通过**" in line:
        passed += 1
    elif "**部分通过**" in line:
        partial += 1
    elif "**缺失**" in line:
        missing += 1
    else:
        print("  unlabelled row:", line[:70])
print(f"item rows: {len(item_rows)}")
print(f"pass={passed} partial={partial} missing={missing} total={passed + partial + missing}")
summary = re.search(r"\| \*\*合计\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \|", SC)
print("summary row:", summary.groups() if summary else "not found")

# supplementary naming format
EN = (ROOT / "重构版论文_v4_20260915" / "English_SCI_Manuscript_v4.md").read_text("utf-8")
print()
print("manuscript supplementary ids:", re.findall(r"^\| (S\d+) \|", EN, flags=re.M)[:6])
with (ROOT / "重构版论文_v4_20260915" / "补充材料_S1_S19" / "README.md").open(encoding="utf-8") as h:
    print("bundle supplementary ids:", re.findall(r"^\| (S\d+) \|", h.read(), flags=re.M)[:6])
