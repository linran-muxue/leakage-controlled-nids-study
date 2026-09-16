"""Renumber figures so that numbering follows order of appearance.

New order of the eleven main figures:
  1 pipeline, 2 audit chain, 3 mechanism, 4 main results, 5 gate diagnostics,
  6 margin bound, 7 diversity dose-response, 8 protocol sensitivity,
  9 external class F1, 10 calibration/robustness, 11 latency.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

MAPPING = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 11: 6, 10: 7, 6: 8, 7: 9, 8: 10, 9: 11}
PATTERN = re.compile(r"(Figure|图)(\s*)(1[01]|[1-9])(?!\d)")


def renumber(path: Path) -> None:
    text = path.read_text(encoding="utf-8")

    def to_token(m: re.Match) -> str:
        word, space, num = m.group(1), m.group(2), int(m.group(3))
        return f"@@FIG{word}{num}@@"

    text = PATTERN.sub(to_token, text)
    for old, new in MAPPING.items():
        for word in ("Figure", "图"):
            text = text.replace(f"@@FIG{word}{old}@@", f"{word} {new}")
    if "@@FIG" in text:
        raise SystemExit(f"unresolved token in {path.name}")
    path.write_text(text, encoding="utf-8")
    print(f"RENUMBERED={path.name}")


def main() -> None:
    renumber(BASE / "中文SCI论文_v4_重构版.md")
    renumber(BASE / "English_SCI_Manuscript_v4.md")


if __name__ == "__main__":
    main()
