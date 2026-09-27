"""Add the CIC-IDS2017 scale ladder as a table and tie it to RQ3.

The paper's most striking finding - that the verdict flips between the capped
and the uncapped population - was buried in three dense paragraphs.  A reader
also had no way to see at a glance which population the headline claim is
conditioned on.  This adds Table 7 (the three populations side by side) and
renumbers the decision matrix to Table 8.

It also closes a structural gap: Section 1.3 promises that every research
question maps to one results subsection, but population size appeared in none
of them even though Section 5.7 tests exactly that.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

TABLE_EN = ("**Table 7. The CIC-IDS2017 scale ladder: the verdict depends on the population**\n\n"
            "| Population | Flows | Test rows | RCCF | Equal RF (chi-square) | Difference | TOST 0.005 | TOST 0.01 |\n"
            "|---|---:|---:|---:|---:|---:|---|---|\n"
            "| Capped, 20,000 per class | 53,237 | 7,986 | 0.889278 | 0.889734 | -0.000456 | equivalent | equivalent |\n"
            "| Capped, 200,000 per class | 413,209 | 61,982 | 0.856065 | 0.857202 | -0.001137 | equivalent | equivalent |\n"
            "| Uncapped (full deduplicated corpus) | 2,429,503 | 364,426 | 0.754007 | 0.759540 | -0.005533 | **not equivalent** | equivalent |\n\n")

TABLE_ZH = ("**表 7 CIC-IDS2017 的规模阶梯：结论取决于总体**\n\n"
            "| 总体 | 样本数 | 测试行数 | RCCF | 等权卡方森林 | 差值 | TOST 0.005 | TOST 0.01 |\n"
            "|---|---:|---:|---:|---:|---:|---|---|\n"
            "| 截断，每类 20 000 条 | 53 237 | 7 986 | 0.889278 | 0.889734 | −0.000456 | 等价 | 等价 |\n"
            "| 截断，每类 200 000 条 | 413 209 | 61 982 | 0.856065 | 0.857202 | −0.001137 | 等价 | 等价 |\n"
            "| 不截断（完整去重语料） | 2 429 503 | 364 426 | 0.754007 | 0.759540 | −0.005533 | **不等价** | 等价 |\n\n")

EN: list[tuple[str, str]] = [
    ("These conclusions are insensitive to deduplication order, class priors and split construction, "
     "so results can be compared across papers.",
     "These conclusions are insensitive to deduplication order, class priors, split construction and "
     "population size, so results can be compared across papers."),
    ("Are the conclusions robust to deduplication order, class priors, repeated splits and tuning "
     "budgets?",
     "Are the conclusions robust to deduplication order, class priors, repeated splits, tuning "
     "budgets and population size?"),
    ("Three further runs address the question directly.",
     "Three further runs address the question directly, and Table 7 shows that the verdict depends "
     "on the population."),
    ("**A population 7.8 times larger.**", TABLE_EN + "**A population 7.8 times larger.**"),
    ("Table 7 converts the evidence of this study into engineering guidance.",
     "Table 8 converts the evidence of this study into engineering guidance."),
    ("**Table 7. Decision matrix for practical objectives**",
     "**Table 8. Decision matrix for practical objectives**"),
]

ZH: list[tuple[str, str]] = [
    ("上述结论对去重顺序、类别先验与划分方式不敏感",
     "上述结论对去重顺序、类别先验、划分方式与总体规模不敏感"),
    ("结论对去重顺序、类别先验、重复划分与调参预算是否稳健？",
     "结论对去重顺序、类别先验、重复划分、调参预算与总体规模是否稳健？"),
    ("以下三组实验直接回答这一质疑。",
     "以下三组实验直接回答这一质疑，表 7 显示结论取决于总体。"),
    ("**总体扩大 7.8 倍。**", TABLE_ZH + "**总体扩大 7.8 倍。**"),
    ("表 7 把本文的证据整理为面向工程选择的决策表。",
     "表 8 把本文的证据整理为面向工程选择的决策表。"),
    ("**表 7 面向实践目标的决策矩阵**", "**表 8 面向实践目标的决策矩阵**"),
]


def apply(name: str, pairs: list[tuple[str, str]]) -> None:
    path = BASE / name
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if new in text:
            print(f"  [{name}] already applied: {old[:34]}...")
            continue
        if old not in text:
            raise SystemExit(f"anchor missing in {name}: {old[:70]}")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    print(f"  [{name}] scale ladder added, decision matrix renumbered")


def main() -> int:
    apply("English_SCI_Manuscript_v4.md", EN)
    apply("中文SCI论文_v4_重构版.md", ZH)
    print("SCALE_LADDER_TABLE_ADDED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
