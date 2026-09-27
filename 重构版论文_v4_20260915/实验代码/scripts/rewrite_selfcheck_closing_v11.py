"""Replace the closing section of the self-check table with one that matches it.

The section had survived several rounds: it still announced "only one missing
item", listed ten partial items and told the reader to write a Dockerfile and a
CI workflow, all of which had long since been done. Because the section sat
below the table it was never re-read after the table was updated.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
SC_PATH = ROOT / "重构版论文_v4_20260915" / "论文自查表.md"
MARKER = "## 自查结论与行动清单"

CLOSING = """## 自查结论与行动清单

### 结论

**66 项检查中 62 项通过、4 项部分通过、0 项缺失。** 剩余四项全部集中在需要作者输入或流程性排版的位置，不涉及数据、统计或论证本身的正确性。

| 编号 | 未完成部分 | 完成方式 | 需谁处理 |
|---|---|---|---|
| A5 | 署名、单位、通信作者、ORCID | 按投稿系统字段填写 | 作者 |
| A6 | 基金与利益冲突声明 | 无基金则写「无」；利益冲突同样声明「无」 | 作者 |
| E6 | 母语润色 | 投稿前送一次专业润色，或逐章人工改写 | 作者（是否付费） |
| F9 | 按 JISA 官方模板排版 | 依 Guide for Authors 模板套用 | 可代办（需模板文件） |

### 已在正文声明、尚未执行的实验（属局限，不是缺陷）

下列实验均已在 §6.5 明确写为本文局限，`scripts/residual_gap_check_v5.py` 逐项确认「声明过但没做」的情况不存在：

- **严格时间外泛化**：文件级实验只覆盖部分类别，不能替代时间外测试，已在正文说明其只能作为覆盖与风险分析。
- **全量语料运行**：主实验是 2.0% 的平衡研究子集，另有 53 237 条自然先验总体作为主协议；全量 2 429 791 条未跑。
- **近重复检测**：只做精确哈希去重；已补四位有效数字分辨率的敏感性检验（另有 0.36% 近重复、104 条测试行重叠，剔除后 Macro-F1 变化 ≤ 0.00057）。
- **对抗鲁棒性**：只施加随机噪声与特征屏蔽，不构成对自适应对手的保证。
- **第四个公开数据集**：已在本节前论证其最大增量价值所在（物联网或工控场景、不同观测点、时间分离采集）。

### 第十一轮修正的辅助文档缺陷

自查表自身此前有三处陈述与实际产物不符，现已修正，并把「表内数字必须自洽」固化为自动检查：

| 位置 | 原陈述 | 实际 | 处置 |
|---|---|---|---|
| A4 / F1 | 代码已推送至 `ebb0247`、标签 `v1.1.0` | 发布标签已推进到 `v1.10.0` | 改为只引用发布标签，避免提交号漂移 |
| E7 | 英文 11 209 词、中文 31 868 字 | 英文 12 761 词、中文 35 504 字（整篇含参考文献） | 由 `refresh_selfcheck_facts_v11.py` 依据实际文件重算 |
| F4 | `补充材料_S1_S19/`：19 条目、40 文件 | 目录内实为 S01–S26，58 个材料文件 | 目录重命名为 `补充材料_S01_S26/`，条目数重算 |
| 本段 | 仍写「缺失项（仅剩 1 项）」「部分通过项（10 项）」，并列出 F6/F7 未做 | F6 容器化、F7 持续集成早已完成 | 整段重写 |

同时新增 **E9 中英数值一致** 检查项，并在 `scripts/verify_selfcheck_counts_v7.py` 中把「层级表合计 = 逐项计数 = 汇总行」写成断言：自查表此后无法再出现自相矛盾的数字。
"""


def main() -> None:
    text = SC_PATH.read_text(encoding="utf-8")
    if MARKER not in text:
        raise SystemExit("closing marker not found")
    if "### 第十一轮修正的辅助文档缺陷" in text:
        print("already rewritten")
        return
    text = text.split(MARKER)[0].rstrip() + "\n\n---\n\n" + CLOSING
    SC_PATH.write_text(text, encoding="utf-8")
    print("SELFCHECK_CLOSING_REWRITTEN")


if __name__ == "__main__":
    main()
