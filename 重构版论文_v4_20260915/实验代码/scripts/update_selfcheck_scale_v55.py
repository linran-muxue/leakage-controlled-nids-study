"""Record the scale and fourth-dataset evidence in the self-check table."""
from __future__ import annotations
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
SC = ROOT / "重构版论文_v4_20260915" / "论文自查表.md"
D15 = ("| D15 | 规模与领域稳健性 | 结论不得依赖被截断的子集 | **通过** | "
       "规模实验把 CIC-IDS2017 总体扩大 7.8 倍（413 209 条，十种子）：平均配对差 −0.001137，"
       "90% 区间 [−0.002966, +0.000692]，TOST 在 0.005 与 0.01 边界下均成立；"
       "第四个数据集 N-BaIoT（18 万条、IoT 领域）上所有模型 Macro-F1 ≥ 0.9998，RCCF 与等权森林差异为 0"
       "（结果见 §5.7 与补充材料 S27、S28） |")
C11_OLD = ("| C11 | 数据集数量与代表性 | 多数据集但边界清楚 | **通过** | 3.3 节新增覆盖范围论证"
           "（三个采集时期、三种特征提取方式、三套标签体系、各自的已知缺陷），并说明第四个数据集的最大增量价值所在；"
           "覆盖矩阵见补充材料 S25 |")
C11_NEW = ("| C11 | 数据集数量与代表性 | 多数据集但边界清楚 | **通过** | 已使用四个公开数据集：3.3 节给出四种采集场景、"
           "四种特征提取方式、四套标签体系与各自缺陷的覆盖论证，N-BaIoT 补齐了此前指出的物联网场景缺口；"
           "覆盖矩阵见补充材料 S25，审计与结果见 S28 |")


def main() -> None:
    text = SC.read_text(encoding="utf-8")
    changed = []
    if "| D15 |" not in text:
        anchor = re.search(r"^\| D14 \|.*$", text, flags=re.M)
        if anchor:
            text = text[:anchor.end()] + "\n" + D15 + text[anchor.end():]
            changed.append("D15 added")
    for old, new, label in (
        (C11_OLD, C11_NEW, "C11 evidence"),
        ("| D 实验与统计 | 14 | 14 | 0 | 0 |", "| D 实验与统计 | 15 | 15 | 0 | 0 |", "layer D"),
        ("| **合计** | **68** | **64** | **4** | **0** |", "| **合计** | **69** | **65** | **4** | **0** |", "summary"),
        ("**68 项检查中 64 项通过、4 项部分通过、0 项缺失**", "**69 项检查中 65 项通过、4 项部分通过、0 项缺失**", "conclusion"),
        ("**68 项检查中 64 项通过、4 项部分通过、0 项缺失。**", "**69 项检查中 65 项通过、4 项部分通过、0 项缺失。**", "closing"),
        ("68 项检查中 64 项通过、4 项部分通过、0 项缺失；含每项的证据文件。",
         "69 项检查中 65 项通过、4 项部分通过、0 项缺失；含每项的证据文件。", "status stamp"),
    ):
        if old in text:
            text = text.replace(old, new, 1)
            changed.append(label)
        else:
            print(f"anchor absent: {label}")
    SC.write_text(text, encoding="utf-8")
    print("updated:", ", ".join(changed))


if __name__ == "__main__":
    main()
