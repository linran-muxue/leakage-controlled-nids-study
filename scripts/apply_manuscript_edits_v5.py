"""Apply the v5 manuscript edits that depend on the S2-S6 results."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "中文SCI论文_v4_重构版.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"anchor not found: {label}")
    if text.count(old) != 1:
        raise SystemExit(f"anchor not unique: {label}")
    return text.replace(old, new)


def main() -> None:
    text = MD.read_text(encoding="utf-8")
    text = replace_once(text, "表 7 把本文的证据整理为", "表 8 把本文的证据整理为", "table7-in-text")
    text = replace_once(text, "**表 7 面向实践目标的决策矩阵**", "**表 8 面向实践目标的决策矩阵**", "table7-caption")

    abstract_anchor = "贡献在于一套可复用的泄漏受控协议、一组可辨识性边界，以及一张把协议效应与模型效应分开量化的失效地图。"
    abstract_new = (
        "进一步给出三个可辨识性命题，其中命题 2 被改写为可逐行计算的显式判据：在 23 958 条测试样本上，"
        "99.91% 的样本可被证明不受权重影响，实际改判 0 条，决策边距是权重扰动上界的 3469 至 5038 倍。"
        "对门控全部 108 种超参数配置的搜索只产生 6 个不同的验证集 Macro-F1 取值（全距 0.00117），"
        "排除了调参不足的解释；反向实验表明增益受专家多样性支配：分歧率 0.20% 至 0.36% 的两类专家集合"
        "在 6 次运行中增益恰好为零，而分歧率 1.76% 至 6.44% 的三类去相关集合在 9 次运行中增益全部为正，"
        "剂量—反应回归斜率 0.0646（Pearson r = 0.749）。"
        "贡献在于一套可复用的泄漏受控协议、一组可辨识性边界，以及一张把协议效应与模型效应分开量化的失效地图。"
    )
    text = replace_once(text, abstract_anchor, abstract_new, "abstract")

    concl_anchor = "四个专家在测试集上没有任何一条预测分歧，归一化权重熵为 0.99998。"
    concl_new = (
        "四个专家在测试集上没有任何一条预测分歧，归一化权重熵为 0.99998；命题 2 的显式上界证明 99.91% 的样本"
        "不受权重影响，门控 108 种超参数配置只产生 6 个不同的验证集取值。"
    )
    text = replace_once(text, concl_anchor, concl_new, "conclusion-1")

    second_anchor = "第二，**失效是可解释的。**"
    second_new = (
        "第二，**失效是可解释的，而且是定量的。**"
        "增益受专家多样性支配：分歧率 0.20% 至 0.36% 的两类专家集合在全部 6 次运行中增益恰好为零，"
        "分歧率 1.76% 至 6.44% 的三类去相关集合在全部 9 次运行中增益均为正，剂量—反应回归斜率 0.0646"
        "（Pearson r = 0.749）。因此条件加权的失效不是实现或调参问题，而是过滤式多视图专家彼此过于相似"
        "这一数据侧约束的直接后果。"
    )
    text = replace_once(text, second_anchor, second_new, "conclusion-2")

    MD.write_text(text, encoding="utf-8")
    print("MANUSCRIPT_EDITS_APPLIED")


def fixup_abstract_order() -> None:
    """Move the new evidence before the conclusion sentence and drop the duplicate."""
    text = MD.read_text(encoding="utf-8")
    evidence = (
        "其中命题 2 被改写为可逐行计算的显式判据：在 23 958 条测试样本上，"
        "99.91% 的样本可被证明不受权重影响，实际改判 0 条，决策边距是权重扰动上界的 3469 至 5038 倍。"
        "对门控全部 108 种超参数配置的搜索只产生 6 个不同的验证集 Macro-F1 取值（全距 0.00117），"
        "排除了调参不足的解释；反向实验表明增益受专家多样性支配：分歧率 0.20% 至 0.36% 的两类专家集合"
        "在 6 次运行中增益恰好为零，而分歧率 1.76% 至 6.44% 的三类去相关集合在 9 次运行中增益全部为正，"
        "剂量—反应回归斜率 0.0646（Pearson r = 0.749）。"
    )
    old_head = "我们进一步给出三个可辨识性命题，刻画条件加权在何种条件下必然不改变硬标签。结论是："
    new_head = "我们进一步给出三个可辨识性命题，" + evidence + "结论是："
    text = replace_once(text, old_head, new_head, "abstract-order")
    duplicate = "其可靠性增益未获证据支持。进一步给出三个可辨识性命题，" + evidence
    text = replace_once(text, duplicate, "其可靠性增益未获证据支持。", "abstract-duplicate")
    MD.write_text(text, encoding="utf-8")
    print("ABSTRACT_ORDER_FIXED")


if __name__ == "__main__":
    fixup_abstract_order()
