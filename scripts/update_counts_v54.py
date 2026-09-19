"""Refresh the counts that changed with the fourth dataset.
References are 47 now (was 45) and the supplementary bundle is S01-S28.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
SC = ROOT / "重构版论文_v4_20260915" / "论文自查表.md"
COVERAGE = ROOT / "scripts" / "check_citation_coverage_v5.py"

EDITS = [
    ("中英各 45/45 全覆盖，抽查 21 条零失配；**45 条 DOI 已全部通过 Crossref 核验**",
     "中英各 47/47 全覆盖，抽查 21 条零失配；**47 条 DOI 已全部通过 Crossref 核验**（含新增的 N-BaIoT 论文与数据集 DOI）"),
    ("`补充材料_S01_S26/`：26 条目、58 个材料文件",
     "`补充材料_S01_S28/`：28 条目、69 个材料文件"),
    ("- **引文标注未引入错误**：45 条文献全部有正文标注",
     "- **引文标注未引入错误**：47 条文献全部有正文标注"),
    ("| F4 | `补充材料_S1_S19/`：19 条目、40 文件 | 目录内实为 S01–S26，58 个材料文件 | 目录重命名为 `补充材料_S01_S26/`，条目数重算 |",
     "| F4 | `补充材料_S1_S19/`：19 条目、40 文件 | 目录随后扩充至 S01–S28，69 个材料文件 | 目录重命名为 `补充材料_S01_S28/`，条目数重算 |"),
]


def main() -> None:
    text = SC.read_text(encoding="utf-8")
    for old, new in EDITS:
        if old in text:
            text = text.replace(old, new, 1)
            print(f"updated: {old[:44]}...")
        else:
            print(f"anchor absent: {old[:44]}...")
    SC.write_text(text, encoding="utf-8")

    script = COVERAGE.read_text(encoding="utf-8")
    script = script.replace('print(f"{label}: cited {len(have)}/45, uncited = {missing}")',
                            'print(f"{label}: cited {len(have)}/47, uncited = {missing}")')
    COVERAGE.write_text(script, encoding="utf-8")
    print("citation coverage denominator updated to 47")


if __name__ == "__main__":
    main()
