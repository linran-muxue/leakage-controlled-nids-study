"""Keep the ten-seed basis in the Highlights after the population edit.

``fresh_audit_v7.py`` requires the Highlights to state the ten-seed basis of
the headline result; rewriting the first two items for the population
qualification dropped that phrase.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
HL = ROOT / "重构版论文_v4_20260915" / "Highlights_v4.md"

PAIRS = [
    ("- On the primary population the per-seed sign splits five to five, with no advantage.",
     "- Across ten seeds on the primary population the sign splits five to five."),
    ("- 主总体上逐种子方向五正五负，没有优势。",
     "- 主总体上十个种子的方向五正五负，没有优势。"),
]


def main() -> int:
    text = HL.read_text(encoding="utf-8")
    for old, new in PAIRS:
        if new in text:
            print(f"  already: {new[:40]}")
            continue
        if old not in text:
            raise SystemExit(f"anchor missing: {old}")
        text = text.replace(old, new, 1)
        print(f"  replaced: {old[:44]}")
    HL.write_text(text, encoding="utf-8")
    print("HIGHLIGHT_SEED_WORDING_FIXED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
