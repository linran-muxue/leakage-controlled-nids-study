"""Add the neural baseline to Table 5(a) and report it in Section 5.2."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "中文SCI论文_v4_重构版.md"


def main() -> None:
    text = MD.read_text(encoding="utf-8")

    extra_trees_row = ("| 极端随机树（χ²） | 0.96369 | **0.96173** | 0.857713 | 0.08903 | "
                       "0.010849 | 0.015791 | 0.442 | 0.0368 |")
    mlp_row = ("| MLP（128 隐单元，k = 60） | 0.97679 | 0.79666 | 0.797654 | 0.06256 | "
               "0.036701 | 0.009705 | 21.88 | 0.0079 |")
    if mlp_row not in text:
        if extra_trees_row not in text:
            raise SystemExit("Table 5(a) anchor not found")
        text = text.replace(extra_trees_row, extra_trees_row + "\n" + mlp_row, 1)

    paragraph = (
        "**第五，一个神经基线显示准确率会严重误导。** 在相同特征预算下使用完整训练预算的多层感知机"
        "（128 个隐单元，超参数在验证分区选定），其自然先验测试准确率为 0.97679，与 RCCF 的 0.97792 "
        "几乎相同；但其 Macro-F1 仅为 0.797654，比 RCCF 低 0.092，平衡准确率为 0.79666 对 0.94920，"
        "Brier 分数为 0.036701 对 0.006312。值得注意的是，两者在总体正确率上的配对 McNemar 检验并不显著"
        "（合并 23 958 行 p = 0.383；逐种子为 1.000 / 0.768 / 0.261），因为两个模型的错误**数量**接近，"
        "差别在于错误**落在哪些类别**。这给出两条方法学结论：其一，在类别不平衡的入侵检测基准上，"
        "准确率可以完全掩盖接近 0.1 的 Macro-F1 差距；其二，McNemar 检验对错误的类别分布不敏感，"
        "不能单独作为判据，必须与类别级报告并列使用。"
    )
    anchor = "### 5.3 机制诊断"
    if "**第五，一个神经基线显示准确率会严重误导。**" not in text:
        if anchor not in text:
            raise SystemExit("Section 5.3 anchor not found")
        text = text.replace(anchor, paragraph + "\n\n" + anchor, 1)

    MD.write_text(text, encoding="utf-8")
    print("MLP_EDIT_APPLIED")


if __name__ == "__main__":
    main()
