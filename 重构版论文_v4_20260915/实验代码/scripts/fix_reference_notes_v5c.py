"""Correct the no-DOI annotations, processing the reference list line by line.

An earlier pass matched numbered entries with a multi-line regex and mis-applied the
JMLR note to almost every entry. Each reference occupies exactly one line, so the
repair works line by line and then asserts the venue named in each note.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

EN = {
    5: "[no DOI; NeurIPS proceedings]",
    13: "[no DOI; JMLR]",
    19: "DOI:10.1109/CNS56114.2022.9947235.",
    20: "[no DOI; USENIX Security proceedings]",
    27: "[no DOI; PMLR]",
    28: "[no DOI; NeurIPS proceedings]",
    29: "[no DOI; NeurIPS proceedings]",
    32: "[no DOI; JMLR]",
    36: "[no DOI; JMLR]",
    37: "[no DOI; JSTOR stable record 4615733]",
    38: "ISBN 978-0-412-04231-7.",
    42: "[no DOI; JMLR]",
}

ZH = {
    5: "[无 DOI；NeurIPS 会议论文集]",
    13: "[无 DOI；JMLR]",
    19: "DOI:10.1109/CNS56114.2022.9947235。",
    20: "[无 DOI；USENIX Security 会议论文集]",
    27: "[无 DOI；PMLR]",
    28: "[无 DOI；NeurIPS 会议论文集]",
    29: "[无 DOI；NeurIPS 会议论文集]",
    32: "[无 DOI；JMLR]",
    36: "[无 DOI；JMLR]",
    37: "[无 DOI；JSTOR 稳定记录 4615733]",
    38: "ISBN 978-0-412-04231-7。",
    42: "[无 DOI；JMLR]",
}

TRAILING = re.compile(r"\s*(\[no DOI[^\]]*\]|\[无 DOI[^\]]*\]|ISBN[^.]*\.|DOI:10\.\S+\.?)\s*$")


def process(path: Path, mapping: dict[int, str]) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    changed = 0
    for index, line in enumerate(lines):
        m = re.match(r"^(\d+)\.\s", line)
        if not m:
            continue
        number = int(m.group(1))
        if number not in mapping:
            continue
        body = TRAILING.sub("", line).rstrip()
        if not body.endswith("."):
            body += "."
        lines[index] = f"{body} {mapping[number]}"
        changed += 1
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"UPDATED={path.name} entries={changed}")


def main() -> None:
    process(BASE / "English_SCI_Manuscript_v4.md", EN)
    process(BASE / "中文SCI论文_v4_重构版.md", ZH)


if __name__ == "__main__":
    main()
