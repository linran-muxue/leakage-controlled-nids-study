"""Spot-check that the citation numbers resolve to the intended works."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
EN = ROOT / "重构版论文_v4_20260915" / "English_SCI_Manuscript_v4.md"

EXPECT = {
    1: "Breiman", 3: "Geurts", 4: "XGBoost", 12: "Chi2",
    14: "Sharafaldin", 15: "Tavallaee", 16: "Moustafa", 18: "Engelen",
    20: "Arp", 22: "Buczak", 24: "Apruzzese", 25: "Geng", 27: "Guo",
    30: "Angelopoulos", 31: "Vovk", 34: "McNemar", 37: "Holm",
    38: "Efron", 39: "Lakens", 42: "Pedregosa", 45: "Hunter",
}


def main() -> None:
    text = EN.read_text(encoding="utf-8")
    block = text.split("## References")[-1]
    entries = dict(enumerate(re.findall(r"^\d+\.\s+(.*)$", block, flags=re.M), start=1))
    bad = []
    for num, needle in EXPECT.items():
        entry = entries.get(num, "")
        ok = needle.lower() in entry.lower()
        print(f"[{num:>2}] {needle:<14} {'OK ' if ok else 'MISMATCH'} {entry[:70]}")
        if not ok:
            bad.append(num)
    print()
    print("mismatches:", bad or "none")


if __name__ == "__main__":
    main()
