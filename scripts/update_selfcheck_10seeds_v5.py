"""Update the self-check table after the ten-seed extension."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "论文自查表.md"


def fix(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"anchor missing: {label}")
    return text.replace(old, new, 1)


def main() -> None:
    text = MD.read_text(encoding="utf-8")

    # summary table
    text = fix(text, "| D 实验与统计 | 14 | 9 | 4 | 1 |", "| D 实验与统计 | 14 | 12 | 2 | 0 |", "summary-D")
    text = fix(text, "| **合计** | **59** | **44** | **10** | **5** |",
               "| **合计** | **59** | **47** | **8** | **4** |", "summary-total")

    # D9 evidence
    text = fix(text,
               "| D9 | 等价性检验 | 主张\"无差异\"时有等价边界 | **通过** | TOST：合并 90% 区间 [−0.00290, +0.00550]，SESOI=0.01 下等价；SESOI 已在方法章预先声明 |",
               "| D9 | 等价性检验 | 主张\"无差异\"时有等价边界 | **通过** | 十种子 TOST：种子级 90% 区间 [−0.00112, +0.00021]、测试行级区间 [−0.00425, +0.00338]，**SESOI = 0.005 与 0.01 双双等价**；SESOI 已在方法章预先声明 |",
               "D9")

    # D10 missing -> pass
    text = fix(text,
               "| D10 | 统计功效 | 说明可检出效应量 | **缺失** | 未做事后功效分析，无法说明 3 个种子能检出多大差异 |",
               "| D10 | 统计功效 | 说明可检出效应量 | **通过** | 十种子事后功效分析：80% 功效下的最小可检出效应为 0.00115–0.00161 Macro-F1（`results_seeds10_v5/power_analysis.csv`） |",
               "D10")

    # D11 partial -> pass
    text = fix(text,
               "| D11 | 重复次数 | 多种子/多划分 | **部分通过** | 主实验 3 个种子；重复划分 10 次；嵌套 5×3。**主种子数偏少** |",
               "| D11 | 重复次数 | 多种子/多划分 | **通过** | 主实验已扩至 **10 个种子**；重复划分 10 次；嵌套 5×3。逐种子与 3 种子结果一致（前三个种子数值完全复现） |",
               "D11")

    # D12 partial -> pass
    text = fix(text,
               "| D12 | 效应量 | 报告标准化效应量 | **部分通过** | 有配对效应量与相对差；**缺 Cohen's h / Cliff's δ** |",
               "| D12 | 效应量 | 报告标准化效应量 | **通过** | 已补 Cohen's d_z 与配对优势度：对等权 χ² 森林 d_z = −0.40，对全特征森林 +1.17，对极端随机树 +19.68（`results_seeds10_v5/effect_sizes.csv`） |",
               "D12")

    # action list: drop D10
    text = fix(text,
               "| D10 | 统计功效分析 | 用现有三种子方差做事后功效计算，或扩至 10 种子后重算 | 否 |\n",
               "", "action-D10")
    text = fix(text, "### 缺失项（5 项，均不影响数据与论证正确性）",
               "### 缺失项（4 项，均不影响数据与论证正确性）", "action-head")

    # closing notes
    text = fix(text,
               "结论：**44 项通过、10 项部分通过、5 项缺失**。",
               "结论（十种子扩展后）：**47 项通过、8 项部分通过、4 项缺失**。", "closing")
    text = fix(text,
               "1. **C3 命题 3 仍为定义性陈述**",
               "（十种子扩展已解决 D9/D10/D11/D12 四项。）以下三条仍值得补：\n\n1. **C3 命题 3 仍为定义性陈述**",
               "closing-2")

    MD.write_text(text, encoding="utf-8")
    print("SELFCHECK_UPDATED")


if __name__ == "__main__":
    main()
