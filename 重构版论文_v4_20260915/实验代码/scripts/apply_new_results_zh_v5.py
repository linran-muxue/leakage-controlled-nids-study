"""Add resource profile, cost-sensitive analysis and near-duplicate disclosure (Chinese)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "中文SCI论文_v4_重构版.md"


def fix(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"anchor missing: {label}")
    return text.replace(old, new, 1)


def main() -> None:
    text = MD.read_text(encoding="utf-8")

    anchor = "**开放集。** 以 PortScan、Infiltration 与 Heartbleed 为保留未知族时"
    addition = (
        "**资源占用。** 模型体积与吞吐率比墙钟时间更能区分两种设计。条件加权机制保存四个森林，序列化后占 "
        "9.09 MB，而单个等权森林占 2.21 MB，相差 4.1 倍；在完整测试批次上，前者每秒约处理 43 100 行，"
        "后者约 200 300 行，相差 4.6 倍。拟合期间峰值常驻内存增量为 37.0 MB 对 78.3 MB，但两个模型在同一"
        "进程内先后测量，该数字受执行顺序影响，仅供参考。\n\n"
        "**代价敏感表现。** 把任务视为「攻击 vs 正常」并扫描决策阈值，在误报漏报代价比 C_FN / C_FP 从 1 到 "
        "100 的整个区间内，条件加权机制的归一化期望代价与等权卡方森林的差距始终在 0.0005 以内——例如代价比 "
        "为 1 时是 0.00913 对 0.00867，为 100 时是 0.07260 对 0.06753。极端随机树在低代价比下代价约为两者"
        "的两倍（代价比 1 时为 0.01917），但当漏报主导时反而更便宜（代价比 100 时为 0.06180）。因此条件门控"
        "在代价敏感维度上同样没有优势。\n\n"
    )
    text = fix(text, anchor, addition + anchor, "5.6-resources")

    limit_anchor = "**未知族支持量不均衡。**"
    limits = (
        "**近重复只按精确形式剔除。** 引言把「重复与近重复样本」列为公开数据集的危害之一，而审计只删除了"
        "完全相同的特征向量。把所有特征四舍五入到四位有效数字后做哈希，发现研究总体中另有 0.36% 的行在该"
        "分辨率下构成近重复组，其中 104 条测试行（占测试集 0.21%）与训练行共享同一个舍入后特征向量。"
        "剔除这些行后，三个模型的 Macro-F1 变化均不超过 0.00057，因此该重叠不足以解释本文报告的差异；"
        "更粗分辨率的结果见补充材料。\n\n"
        "**未评估对抗鲁棒性。** 本文只施加了随机扰动与特征屏蔽，没有构造规避攻击或基于梯度的攻击，"
        "报告的退化数字不构成对自适应对手的鲁棒性保证。\n\n"
    )
    text = fix(text, limit_anchor, limits + limit_anchor, "6.5-limits")

    abs_anchor = "贡献在于一套可复用的泄漏受控协议、一组可辨识性边界，以及一张把协议效应与模型效应分开量化的失效地图。"
    text = fix(text, abs_anchor,
               "条件加权机制的模型体积是单个等权森林的 4.1 倍、单行吞吐约为其五分之一，而在误报漏报代价比 "
               "1 至 100 的区间内其代价敏感表现与等权森林相同。" + abs_anchor, "abstract-cost")

    MD.write_text(text, encoding="utf-8")
    print("ZH_NEW_RESULTS_APPLIED")


if __name__ == "__main__":
    main()
