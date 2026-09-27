"""Bring the Chinese manuscript into line with the English read-through fixes."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

EDITS = [
    # 1. Fourth reading: align the training times and the ratio explanation
    ("**第四，代价是确定的，增益不是。** 自然先验下 RCCF 训练耗时 61.0 秒，等权森林为 0.78 秒；"
     "整批推理耗时 0.244 秒对 0.046 秒（约 5.3 倍）；5.6 节报告的单条 P50 延迟之比为 4.9 倍（14.62 ms 对 2.96 ms）。"
     "两类口径不同，不应混用。",
     "**第四，代价是确定的，增益不是。** 在自然先验协议上按表 4(a) 的十个种子取平均，RCCF 训练耗时 93.3 秒，"
     "等权森林为 1.16 秒；整批推理耗时 0.244 秒对 0.046 秒，约慢 5.3 倍。该整批比值不应与 5.6 节的单条延迟之比 4.9 "
     "混用（14.62 ms 对 2.96 ms）：前者衡量 7 986 行的吞吐，后者衡量单次调用。差距在平衡控制协议上更大："
     "训练 9.13 秒对 0.45 秒。这些代价换来的最好说法是 Macro-F1 变化在 ±0.01 以内。"),
    # 2. Figure 4 axis note
    ("注：图 4(a) 纵轴从 0.84 起，目的是显示千分位量级的差异；图 4(b) 的配对区间表明这些差异在统计上不可区分。"
     "两个面板应合起来阅读，不能只看柱高。",
     "注：图 4(a) 纵轴从 0.75 起，目的是显示千分位量级的差异；图 4(b) 的配对区间表明这些差异在统计上不可区分。"
     "两个面板应合起来阅读，不能只看柱高。"),
    # 3. Table 5 commentary
    ("**相对极端随机树**：差异大且无歧义（d_z = 19.68，十个种子全部支持），是本研究唯一一处实质性的模型间差距。",
     "**相对极端随机树**：差异大且无歧义（d_z = 19.68，十个种子全部支持）。它与第五条的神经基线一起，"
     "构成本研究仅有的两处实质性模型间差距，而且都来自模型族而非聚合策略。"),
    # 4. Section 6.2 item 1
    ("1. **划分噪声**：十次重复划分的标准差约为 0.011，足以掩盖本文观察到的全部模型间差异（最大 0.0078）。",
     "1. **划分噪声**：十次重复划分的标准差约为 0.011，大于本文观察到的全部聚合策略差异与调参预算差异"
     "（最大 0.0078），但小于模型族差距 0.0318 与 0.0916。"),
    # 5. Merge the redundant label-space paragraph in 3.3
    ("三者使用不同的标签体系，其分数因此**不得合并、不得平均、不得解释为迁移成功**。",
     "由于标签体系互不相容，三者的分数在本文中从不合并或平均，也从不被解释为迁移成功的证据。"),
]


def main() -> None:
    path = BASE / "中文SCI论文_v4_重构版.md"
    t = path.read_text(encoding="utf-8")
    applied = 0
    for old, new in EDITS:
        if old in t:
            t = t.replace(old, new, 1)
            applied += 1
        else:
            print(f"  anchor absent (already applied?): {old[:48]}...")
    path.write_text(t, encoding="utf-8")
    print(f"ZH_ALIGNMENT_APPLIED={applied}/{len(EDITS)}")


if __name__ == "__main__":
    main()
