"""Fixes from the full read-through review (Chinese side)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "中文SCI论文_v4_重构版.md"

EDITS = [
    ("我们在同一批数据上测量四类差异来源", "我们在同一批数据上测量五类差异来源", "contrib-five"),
    ("结论是协议效应比模型效应高出一个数量级。",
     "结论是协议效应比聚合策略差异高出一个数量级。", "contrib-claim"),
    ("（iii）协议效应与模型效应的相对量级", "（iii）协议效应与聚合规则差异的相对量级", "2.5-effects"),
    ("此前的纯定义式表述使用归一化权重熵", "对应的可观测判据是归一化权重熵", "cond3-dangling"),
    ("这是本文观察到的最大单项协议效应，比任何模型间差异（最大 +0.0078）高出一个数量级。",
     "这是本文观察到的最大单项协议效应，大于任何聚合策略差异与调参预算差异（最大 +0.0078），"
     "但小于模型族之间的差异（0.0318 与 0.0916）。", "5.4-overclaim"),
    ("把类别先验从平衡改为自然，Macro-F1 变化 +0.0719；",
     "把类别先验从平衡改为自然，Macro-F1 变化 +0.0725；", "6.2-prior"),
    ("以及一张把协议效应与模型效应分离的定量地图。",
     "以及一张把协议效应与聚合策略差异分离的定量地图。", "concl-map"),
    ("H3 尤其关键：", "H3 尤其关键，因为在文献中它从未被显式声明：", "1.2-h3"),
]

DUP_HEADER = ("| 模型 | 准确率 | 平衡准确率 | Macro-F1 | Log Loss | Brier | ECE | 训练 (s) | 推理 (s) |\n"
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|\n"
              "| 模型 | 准确率 | 平衡准确率 | Macro-F1 | Log Loss | Brier | ECE | 训练 (s) | 推理 (s) |\n"
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|")
SINGLE_HEADER = ("| 模型 | 准确率 | 平衡准确率 | Macro-F1 | Log Loss | Brier | ECE | 训练 (s) | 推理 (s) |\n"
                 "|---|---:|---:|---:|---:|---:|---:|---:|---:|")


def main() -> None:
    t = MD.read_text(encoding="utf-8")
    if DUP_HEADER in t:
        t = t.replace(DUP_HEADER, SINGLE_HEADER, 1)
        print("table4a duplicate header removed")
    for old, new, label in EDITS:
        if old in t:
            t = t.replace(old, new, 1)
        else:
            print(f"  note: '{label}' already applied or anchor absent")
    before = len(re.findall(r"[\u4e00-\u9fff）)]。 ?\[\d", t))
    t = re.sub(r"([\u4e00-\u9fff）)])。 ?\[(\d[\d,\- ]*)\]", r"\1 [\2]。", t)
    after = len(re.findall(r"[\u4e00-\u9fff）)]。 ?\[\d", t))
    print(f"citations moved before the full stop: {before} -> {after}")
    residuals = t.count("。.。")
    t = t.replace("。.。", "。")
    t = re.sub(r"ISBN (978-0-412-04231-7)。\. ISBN \1。", r"ISBN \1。", t)
    t = re.sub(r"ISBN (978-0-412-04231-7)。 ISBN \1。", r"ISBN \1。", t)
    print(f"residual artefacts repaired: {residuals}")
    MD.write_text(t, encoding="utf-8")
    print("ZH_READTHROUGH_FIXES_APPLIED")


if __name__ == "__main__":
    main()
