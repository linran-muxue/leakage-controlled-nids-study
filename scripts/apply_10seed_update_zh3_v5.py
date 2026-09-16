"""Chinese abstract and conclusion for the ten-seed results."""
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

    # abstract
    text = fix(text,
               "RCCF 与等权卡方随机森林的 Macro-F1 平均差仅 +0.0011，配对 Bootstrap 的合并 90% 区间为 "
               "[−0.00290, +0.00550]，在 SESOI = 0.01 Macro-F1 下给出等价结论，逐种子精确 McNemar 检验均不显著"
               "（p = 0.508 / 0.092 / 0.344）",
               "在十个种子上，RCCF 与等权卡方随机森林的 Macro-F1 平均差为 −0.00046，逐种子方向五正五负；"
               "种子级 90% 区间 [−0.00112, +0.00021] 与测试行级配对 Bootstrap 区间 [−0.00425, +0.00338] "
               "都落在 SESOI = 0.005 与 0.01 Macro-F1 的等价边界之内",
               "abstract")

    # conclusion first
    text = fix(text,
               "在 CIC-IDS2017 的自然先验总体上，条件加权森林与等权卡方森林的 Macro-F1 平均差为 +0.0011，"
               "配对 Bootstrap 合并 90% 区间 [−0.00290, +0.00550]，在 SESOI = 0.01 下等价，逐种子 McNemar 检验"
               "不显著（p = 0.508 / 0.092 / 0.344）；四个专家在测试集上没有任何一条预测分歧，归一化权重熵为 "
               "0.99998；命题 2 的显式上界证明 99.91% 的样本不受权重影响，门控 108 种超参数配置只产生 6 个"
               "不同的验证集取值。代价则是训练时间增加约 78 倍、推理时间增加约 5.9 倍。",
               "在 CIC-IDS2017 的自然先验总体上取十个种子的平均，条件加权森林与等权卡方森林的 Macro-F1 平均差为 "
               "−0.000456，逐种子方向五正五负；种子级 90% 区间 [−0.00112, +0.00021] 与测试行级配对 Bootstrap "
               "区间 [−0.00425, +0.00338] 都落在 SESOI = 0.005 与 0.01 的等价边界之内。四个专家在测试集上"
               "没有任何一条预测分歧，归一化权重熵为 0.99998；命题 2 的显式上界证明 99.91% 的样本不受权重影响，"
               "门控 108 种超参数配置只产生 6 个不同的验证集取值。代价则是训练时间增加约 80 倍、整批推理时间"
               "增加约 5.3 倍。",
               "conclusion-first")

    # conclusion third
    text = fix(text,
               "类别先验变化带来 +0.0719 的 Macro-F1 差异，去重顺序至多 +0.0060，而聚合策略仅 +0.0011。",
               "类别先验变化带来 +0.0725 的 Macro-F1 差异，去重顺序至多 +0.0060，而聚合策略仅 0.0005。",
               "conclusion-third")

    MD.write_text(text, encoding="utf-8")
    print("ZH_10SEED_PART3_APPLIED")


if __name__ == "__main__":
    main()
