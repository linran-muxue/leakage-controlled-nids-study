"""Chinese side of the v6 content fixes."""
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
    t = MD.read_text(encoding="utf-8")

    t = fix(t, "# 协议敏感性主导模型选择：面向条件集成加权的泄漏受控网络入侵检测研究",
            "# 协议敏感性主导聚合规则差异：面向条件集成加权的泄漏受控网络入侵检测研究", "title")
    t = fix(t, "### 5.4 RQ3：协议效应比模型效应大一个数量级",
            "### 5.4 RQ3：协议效应比聚合策略差异大一个数量级", "head")
    t = fix(t, "3. **一张把协议效应与模型效应分离的定量地图**。",
            "3. **一张把协议效应与聚合策略差异分离的定量地图**。", "contrib")
    t = fix(t, "该判据只需逐行计算，因此命题 2 是可验证的，而不是存在性陈述。",
            "该判据只需逐行计算，因此命题 2 是可验证的，而不是存在性陈述。该上界在温度缩放之前的融合概率上计算；"
            "温度缩放是 log 概率的单调变换，保持 argmax 不变，因此不变性结论同样适用于最终报告的预测。", "bound")
    t = fix(t, "共 15 个观测（表 6）。",
            "共 15 个观测（表 6）。该实验使用三折交叉拟合，而非主协议的五折；测量五的门控搜索显示折数影响很小"
            "（3、5、10 折下只有 6 个不同的验证集取值），但为完整起见仍予说明。", "folds")
    t = fix(t, "因此条件门控在代价敏感维度上同样没有优势。",
            "因此条件门控在代价敏感维度上同样没有优势。需要注意的是，工作点是在测试分区上选出的，"
            "因此上述归一化期望代价是偏乐观的下界；若改在验证分区选择阈值，三条曲线都会整体上移，但相对次序不变。",
            "cost")
    t = fix(t, "**H3 假设被证伪：协议不可交换，而且协议效应的量级压过模型效应。**",
            "**H3 假设被证伪：协议不可交换，而且协议效应远大于聚合策略之间的差异。** 需要强调的是，这一排序针对的是"
            "聚合策略本身。模型族之间的差异更大：多层感知机比森林低 0.0916 Macro-F1，极端随机树低 0.0318，前者甚至"
            "超过类别先验的 0.0725。因此准确的表述是：聚合策略差异被协议选择压过，而模型族差异不会。", "claim")
    t = fix(t, "第三，**协议效应主导模型效应。**", "第三，**协议效应主导聚合策略差异。**", "concl-head")
    t = fix(t, "因此，在公开入侵检测数据集上，**报告什么协议比报告什么模型更能决定结论**。",
            "因此，在公开入侵检测数据集上，**报告什么协议比报告什么聚合策略更能决定结论**——不过模型族的选择"
            "可能比两者都更重要。", "concl-tail")

    MD.write_text(t, encoding="utf-8")
    print("ZH_CONTENT_FIXES_APPLIED")


if __name__ == "__main__":
    main()
