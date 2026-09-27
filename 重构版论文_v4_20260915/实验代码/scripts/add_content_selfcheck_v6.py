"""Add a content-level section to the self-check table for the v6 findings."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "论文自查表.md"

SECTION = """
## G. 内容层专项审查（2026-09-16 增补）

前六层检查的是"材料是否齐全、格式是否规范"，本层检查**论文内部论证是否自洽**。做法是把每条主张与其数据逐一对照，并检查方法章声称做过的事是否真的出现在结果里。

| 编号 | 检查项 | 判定标准 | 结果 | 证据 |
|---|---|---|---|---|
| G1 | 标题与研究结论匹配 | 标题主张不得超出数据支持 | **通过** | 原题「协议敏感性主导模型选择」被证伪：最大模型族差异 0.0916（RCCF 对 MLP）**超过**最大协议效应 0.0725（类别先验）。已改为「协议敏感性主导**聚合规则差异**」，并在 5.4 节与结论中明确写出模型族差异更大（`scripts/content_audit_v6.py`） |
| G2 | 方法章声称的统计手段是否落地 | 声明做过的方法必须有对应结果 | **通过** | 方法章声称使用 Holm 多重比较校正，但结果中从未出现校正值。已补做十种子精确符号翻转检验并施加 Holm 校正：对极端随机树 p = 0.006、对全特征森林 p = 0.020、对等权 χ² 森林 p = 0.244，列于表 5（`results_seeds10_v5/signflip_holm.csv`） |
| G3 | 不同实验间的协议一致性 | 结论比较的实验必须协议可比 | **通过** | 专家多样性实验使用三折交叉拟合，主协议为五折。已在 5.3 节显式说明，并引用门控搜索（3/5/10 折下仅 6 个不同取值）说明其影响有限 |
| G4 | 分析过程中的选择偏差 | 阈值或工作点不得在测试集上选取 | **通过** | 代价敏感分析的工作点在测试分区上扫描得到，属乐观下界。已在 5.6 节明确声明该偏差及其方向 |
| G5 | 理论判据的适用口径 | 判据必须说明其计算所在的空间 | **通过** | 边距上界在温度缩放**之前**的融合概率上计算。已在 4.3 节补充说明温度缩放是 log 概率的单调变换、保持 argmax，故不变性结论适用于最终预测 |
| G6 | 参考文献的事实准确性 | 出版方标注必须正确 | **通过** | 一次批处理曾把 11 条"无 DOI"标注**全部错写成 JMLR**（实际为 IEEE CNS、USENIX、PMLR、NeurIPS、Scandinavian 等），其中 Liu 2022 本应有 DOI。已逐条重核并改为正确出版方，核对脚本见 `scripts/check_noDOI_notes_v5.py` |

### 内容层审查中同时确认的两点

- **聚合策略效应确为最小**：RCCF 与等权 χ² 森林差 0.00046、与全特征森林差 0.00161，均远小于任何协议效应与任何模型族差异。论文的窄化主张是成立的。
- **引文标注未引入错误**：45 条文献全部有正文标注，抽查 21 条编号指向正确，且 DOI 已全部核验。
"""


def main() -> None:
    text = MD.read_text(encoding="utf-8")
    if "## G. 内容层专项审查" in text:
        print("already present")
        return
    marker = "## 自查结论与行动清单"
    if marker not in text:
        raise SystemExit("marker missing")
    text = text.replace(marker, SECTION.strip() + "\n\n---\n\n" + marker, 1)
    text = text.replace("| **合计** | **59** | **51** | **7** | **1** |",
                        "| **合计** | **65** | **57** | **7** | **1** |", 1)
    MD.write_text(text, encoding="utf-8")
    print("CONTENT_SECTION_ADDED")


if __name__ == "__main__":
    main()
