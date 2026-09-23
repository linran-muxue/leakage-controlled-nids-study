"""Carry the population qualification into the Highlights and the graphical abstract.

Both are read before the manuscript.  The Highlights still opened with an
unqualified equivalence claim, and panel B of the graphical abstract still
presented the equivalence margin without noting that no such margin holds on
the full corpus - exactly the qualification Section 6.4 asks other authors to
provide.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

HL = BASE / "Highlights_v4.md"
GA = ROOT / "scripts" / "build_graphical_abstract_v5.py"

HL_PAIRS = [
    ("- Conditional ensemble weighting is equivalent to equal voting within 0.005 Macro-F1.",
     "- Weighting matches equal voting on capped data but loses 0.005533 on the full corpus."),
    ("- Across ten seeds the per-seed sign splits five to five, with no advantage.",
     "- Across ten seeds on the primary population the sign splits five to five."),
    ("- 条件集成加权与等权投票在 0.005 Macro-F1 边界内等价。",
     "- 条件加权在截断总体上与等权持平，全语料上反而落后 0.005533。"),
    ("- 十个种子上逐种子方向五正五负，无优势。",
     "- 主总体上十个种子的方向五正五负，没有优势。"),
]

GA_PAIRS = [
    ('ax.set_title("B  Ten seeds: no gain over equal voting", fontsize=10.5, weight="bold", loc="left")',
     'ax.set_title("B  Ten seeds: no gain on capped data", fontsize=10.5, weight="bold", loc="left")'),
    ('    ax.text(0.5, 0.12, f"mean {mean:+.6f}; five seeds up, five down",\n'
     '            transform=ax.transAxes, ha="center", fontsize=8.2, color="#b5525b")',
     '    ax.text(0.5, 0.12, f"mean {mean:+.6f}; five seeds up, five down",\n'
     '            transform=ax.transAxes, ha="center", fontsize=8.2, color="#b5525b")\n'
     '    ax.text(0.5, 0.01, "no margin holds on the full 2.4M corpus (-0.005533)",\n'
     '            transform=ax.transAxes, ha="center", fontsize=7.4, color="#8a6d1f")'),
]


def apply(path: Path, pairs: list[tuple[str, str]], label: str) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if new in text:
            print(f"  [{label}] already applied: {old[:40]}...")
            continue
        if old not in text:
            raise SystemExit(f"anchor missing in {label}: {old[:60]}")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    print(f"  [{label}] updated")


def main() -> int:
    apply(HL, HL_PAIRS, "Highlights")
    apply(GA, GA_PAIRS, "graphical abstract source")
    print("HIGHLIGHTS_AND_GA_QUALIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
