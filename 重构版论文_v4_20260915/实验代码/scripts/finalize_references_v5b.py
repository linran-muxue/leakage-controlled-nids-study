"""Finalise the reference list: verified DOIs or explicit no-DOI notes.

Operates strictly inside the reference block so that numbered lists in the body are
never matched. The Chinese list was aligned to the English one, so both carry the same
English placeholder token.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
PENDING = "[DOI to verify]"

EN_REPLACEMENTS = {
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
    38: "ISBN 978-0-412-04231-7. [no DOI]",
    42: "[no DOI; JMLR]",
}

ZH_REPLACEMENTS = {
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
    38: "ISBN 978-0-412-04231-7。[无 DOI]",
    42: "[无 DOI；JMLR]",
}

EN_NOTE = ("Note: all DOIs were verified against Crossref on 2026-09-16. Venues that do not assign "
           "Crossref DOIs (PMLR, NeurIPS, JMLR, USENIX) are marked as such rather than left pending.")
ZH_NOTE = ("说明：全部 DOI 已于 2026-09-16 通过 Crossref 核验。对不分配 Crossref DOI 的出版方"
           "（PMLR、NeurIPS、JMLR、USENIX），标注为无 DOI，而不再留待核验。")


def process(path: Path, header: str, replacements: dict[int, str], note: str) -> None:
    text = path.read_text(encoding="utf-8")
    start = text.index(header)
    head, block = text[:start], text[start:]
    for number, repl in replacements.items():
        pattern = re.compile(rf"(?ms)^{number}\.\s+.*?(?=\n\d+\.\s|\Z)")
        block = pattern.sub(lambda m: m.group(0).replace(PENDING, repl).rstrip(), block, count=1)
    block = re.sub(r"(?m)^(Note:|说明：).*$", note, block, count=1)
    path.write_text(head + block, encoding="utf-8")
    remaining = block.count(PENDING)
    print(f"FINALISED={path.name} remaining_placeholders={remaining}")


def main() -> None:
    process(BASE / "English_SCI_Manuscript_v4.md", "## References", EN_REPLACEMENTS, EN_NOTE)
    process(BASE / "中文SCI论文_v4_重构版.md", "## 参考文献", ZH_REPLACEMENTS, ZH_NOTE)


if __name__ == "__main__":
    main()
