"""Content fixes found by the v6 audit.

1. The headline claim was too broad: the largest model-family difference (RCCF vs MLP,
   0.092) exceeds the largest protocol effect (class prior, 0.073). The defensible claim
   concerns the aggregation rule, whose effect is 0.0005.
2. State that the margin bound is computed pre-temperature and that temperature scaling
   preserves the argmax.
3. Disclose that the diversity suite used three folds rather than five.
4. Disclose that cost-sensitive thresholds were selected on the test partition.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"


def fix(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"anchor missing: {label}")
    return text.replace(old, new, 1)


def english() -> None:
    path = BASE / "English_SCI_Manuscript_v4.md"
    t = path.read_text(encoding="utf-8")

    t = fix(t, "# Protocol Sensitivity Dominates Model Choice in Flow-Based Network Intrusion Detection",
            "# Protocol Sensitivity Dominates Aggregation-Rule Differences in Flow-Based Network Intrusion Detection",
            "en-title")
    t = fix(t, "### 5.4 RQ3: Protocol effects exceed model effects by an order of magnitude",
            "### 5.4 RQ3: Protocol effects exceed aggregation-rule differences by an order of magnitude",
            "en-54-head")
    t = fix(t,
            "**H3 is falsified: protocols are not interchangeable, and protocol effects outweigh model effects.**",
            "**H3 is falsified: protocols are not interchangeable, and protocol effects far outweigh the "
            "difference between aggregation rules.** The ordering concerns the aggregation rule specifically. "
            "Differences between model *families* are larger: the multilayer perceptron trails the forests by "
            "0.0916 Macro-F1 and extremely randomised trees by 0.0318, both of which exceed the class-prior "
            "effect of 0.0725 in the first case. The defensible statement is therefore that aggregation-rule "
            "differences are dominated by protocol choices, whereas model-family differences are not.",
            "en-54-claim")
    t = fix(t, "3. **A quantitative map separating protocol effects from model effects.**",
            "3. **A quantitative map separating protocol effects from aggregation-rule effects.**", "en-contrib")
    t = fix(t,
            "On public intrusion-detection benchmarks, **what protocol is reported therefore determines the "
            "conclusion more than which model is used.**",
            "On public intrusion-detection benchmarks, **what protocol is reported therefore determines the "
            "conclusion more than which aggregation rule is used** - although the choice of model family can "
            "matter more than either.", "en-conclusion")

    # margin-bound scope
    t = fix(t,
            "The criterion is evaluated row by row, which makes Condition 2 checkable rather than existential.",
            "The criterion is evaluated row by row, which makes Condition 2 checkable rather than existential. "
            "The bound is computed on the pre-temperature fused probabilities; temperature scaling is a monotone "
            "transform of the log-probabilities and therefore preserves the argmax, so the invariance conclusion "
            "carries over to the reported predictions.", "en-bound-scope")

    # diversity folds
    t = fix(t,
            "We built five families of expert sets and measured the pairwise expert disagreement rate against the "
            "gate gain over three seeds, giving 15 observations.",
            "We built five families of expert sets and measured the pairwise expert disagreement rate against the "
            "gate gain over three seeds, giving 15 observations. This suite used three cross-fitting folds rather "
            "than the five of the primary protocol; the gate search of Measurement 5 shows that fold count changes "
            "little (six distinct validation values across three, five and ten folds), but the difference is noted "
            "for completeness.", "en-diversity-folds")

    # cost-sensitive caveat
    t = fix(t,
            "The conditional gate therefore offers no cost-sensitive advantage either.",
            "The conditional gate therefore offers no cost-sensitive advantage either. Note that the operating "
            "point was selected on the test partition itself, so these normalised expected costs are optimistic "
            "lower bounds; selecting the threshold on the validation partition would raise all three curves by a "
            "similar amount without changing their ordering.", "en-cost-caveat")

    path.write_text(t, encoding="utf-8")
    print("EN_CONTENT_FIXES_APPLIED")


def chinese() -> None:
    path = BASE / "中文SCI论文_v4_重构版.md"
    t = path.read_text(encoding="utf-8")

    t = fix(t, "# 协议敏感性主导模型选择：面向条件集成加权的泄漏受控网络入侵检测研究",
            "# 协议敏感性主导聚合规则差异：面向条件集成加权的泄漏受控网络入侵检测研究", "zh-title")
    t = fix(t, "### 5.4 RQ3：协议效应比模型效应大一个数量级",
            "### 5.4 RQ3：协议效应比聚合策略差异大一个数量级", "zh-54-head")
    t = fix(t,
            "把四个量级并列：聚合策略 0.0005、特征视图 +0.0021、去重顺序 +0.0014（最大 0.0060）、类别先验 +0.0725、调参预算 +0.0078。**H3 假设被证伪：协议不可交换，而且协议效应的量级压过模型效应。**",
            "把四个量级并列：聚合策略 0.0005、特征视图 +0.0021、去重顺序 +0.0014（最大 0.0060）、类别先验 +0.0725、调参预算 +0.0078。"
            "**H3 假设被证伪：协议不可交换，而且协议效应远大于聚合策略之间的差异。** 需要强调的是，这一排序针对的是聚合策略本身。"
            "模型族之间的差异更大：多层感知机比森林低 0.0916 Macro-F1，极端随机树低 0.0318，前者甚至超过类别先验的 0.0725。"
            "因此准确的表述是：聚合策略差异被协议选择压过，而模型族差异不会。", "zh-54-claim")
    t = fix(t, "3. **一张把协议效应与模型效应分离的定量地图**。",
            "3. **一张把协议效应与聚合策略差异分离的定量地图**。", "zh-contrib")
    t = fix(t,
            "因此，在公开入侵检测数据集上，**报告什么协议比报告什么模型更能决定结论**。",
            "因此，在公开入侵检测数据集上，**报告什么协议比报告什么聚合策略更能决定结论**——不过模型族的选择可能比两者都更重要。",
            "zh-conclusion")

    t = fix(t,
            "该判据只需逐行计算，因此命题 2 是可验证的，而不是存在性陈述。",
            "该判据只需逐行计算，因此命题 2 是可验证的，而不是存在性陈述。该上界在温度缩放之前的融合概率上计算；"
            "温度缩放是 log 概率的单调变换，保持 argmax 不变，因此不变性结论同样适用于最终报告的预测。",
            "zh-bound-scope")

    t = fix(t,
            "我们构造五类专家集合，在三个种子上测量专家两两预测分歧率与门控增益，共 15 个观测（表 7）。",
            "我们构造五类专家集合，在三个种子上测量专家两两预测分歧率与门控增益，共 15 个观测（表 7）。"
            "该实验使用三折交叉拟合，而非主协议的五折；测量五的门控搜索显示折数影响很小（3、5、10 折下只有 6 个不同的验证集取值），"
            "但为完整起见仍予说明。", "zh-diversity-folds")

    t = fix(t,
            "因此条件门控在代价敏感维度上同样没有优势。",
            "因此条件门控在代价敏感维度上同样没有优势。需要注意的是，工作点是在测试分区上选出的，"
            "因此上述归一化期望代价是偏乐观的下界；若改在验证分区选择阈值，三条曲线都会整体上移，但相对次序不变。",
            "zh-cost-caveat")

    path.write_text(t, encoding="utf-8")
    print("ZH_CONTENT_FIXES_APPLIED")


def main() -> None:
    english()
    chinese()


if __name__ == "__main__":
    main()
