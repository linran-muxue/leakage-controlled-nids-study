"""Remove reference annotations that leaked into the manuscript body.

An earlier reference-cleanup pass matched any line beginning with a number and a period,
which included numbered protocol steps and control lists. Four body locations were
affected in each language.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

EN_PAT = re.compile(r"\s*\[no DOI[^\]]*\](?=\s*$)", re.M)
ZH_PAT = re.compile(r"。?\s*\[无 DOI[^\]]*\](?=\s*$)", re.M)


def strip_body(name: str, pattern: re.Pattern[str], keep: str) -> None:
    path = BASE / name
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("## References")
                 or l.startswith("## 参考文献"))
    removed = 0
    for i in range(start):
        if pattern.search(lines[i]):
            lines[i] = pattern.sub(keep, lines[i]).rstrip()
            removed += 1
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"BODY_ANNOTATIONS_REMOVED={removed} in {name}")


def main() -> None:
    strip_body("English_SCI_Manuscript_v4.md", EN_PAT, "")
    strip_body("中文SCI论文_v4_重构版.md", ZH_PAT, "。")


if __name__ == "__main__":
    main()
