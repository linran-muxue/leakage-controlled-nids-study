"""Spot-check that the citation numbers resolve to the intended works."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
EN = ROOT / "重构版论文_v4_20260915" / "English_SCI_Manuscript_v4.md"

EXPECT = {
    1: "Breiman", 3: "Geurts P", 4: "Chen T", 12: "Liu H",
    14: "Sharafaldin I", 15: "Tavallaee M", 16: "Moustafa N", 18: "UCI",
    20: "Engelen G", 22: "Arp D", 24: "Buczak A L", 25: "Khraisat A",
    27: "Geng C", 30: "Ovadia Y", 31: "Lakshminarayanan B", 34: "Shafer G",
    37: "Dietterich", 38: "Demsar", 39: "Holm", 42: "Han S",
    45: "Harris C R",
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
