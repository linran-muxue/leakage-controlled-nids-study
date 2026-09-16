"""Apply the audit fixes to the Chinese manuscript (rounds 1-3)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "中文SCI论文_v4_重构版.md"

TABLE_MAP = {1: 1, 2: 2, 3: 3, 5: 4, 6: 5, 7: 6, 8: 7}


def fix(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"anchor missing: {label}")
    if text.count(old) != 1:
        print(f"  note: '{label}' occurs {text.count(old)} times; replacing first only")
    return text.replace(old, new, 1)


def renumber_tables(text: str) -> str:
    pattern = re.compile(r"表\s*(\d+)")

    def to_token(m: re.Match) -> str:
        return f"@@T{m.group(1)}@@"

    text = pattern.sub(to_token, text)
    for old, new in TABLE_MAP.items():
        text = text.replace(f"@@T{old}@@", f"表 {new}")
    if "@@T" in text:
        raise SystemExit("unresolved table token")
    return text


def main() -> None:
    text = MD.read_text(encoding="utf-8")
    n0 = len(text)

    # A1 table numbering: 1,2,3,5,6,7,8 -> 1..7
    text = renumber_tables(text)

    # A2 measurement count
    text = fix(text, "本节用三组独立测量检验它。", "本节用六组独立测量检验它。", "A2")

    # A3 stale section title
    text = fix(text, "### 5.3 机制诊断：门控为何不改变任何一条预测",
               "### 5.3 机制诊断：门控为何不改变预测，以及在什么条件下会改变", "A3")

    # A4 latency ratio clarity
    text = fix(text, "推理耗时 0.173 秒对 0.0295 秒，约 5.9 倍。",
               "整批推理耗时 0.173 秒对 0.0295 秒（约 5.9 倍）；5.6 节报告的单条 P50 延迟之比为 4.9 倍（14.62 ms 对 2.96 ms）。两类口径不同，不应混用。",
               "A4")

    # B1 declare the SESOI values in the methods
    text = fix(text,
               "任何 p 值都必须与效应量同时报告；小而不稳定的点估计不被解释为算法优势。",
               "任何 p 值都必须与效应量同时报告；小而不稳定的点估计不被解释为算法优势。"
               "本文的等价边界在查看主结果之前确定：主要边界为 Macro-F1 = 0.01，严格边界为 0.005。"
               "主要边界约相当于自然先验总体 Macro-F1 的 1.1%，取为在工程上足以否定该机制成本的最小差异。",
               "B1")

    # B2 declare the experimental environment
    text = fix(text,
               "因此 RCCF 在训练与推理两端都显著贵于单个等权森林，这一代价在 5.6 节被定量报告。",
               "因此 RCCF 在训练与推理两端都显著贵于单个等权森林，这一代价在 5.6 节被定量报告。"
               "全部实验在单台工作站上完成：8 个物理核心（16 逻辑核心）、35.8 GB 内存、Windows 10（内部版本 10.0.26200），"
               "软件为 Python 3.11.4、scikit-learn 1.9.0、XGBoost 3.2.0、NumPy 2.4.6、pandas 3.0.5 与 Matplotlib 3.11.1。"
               "报告的时间为单机测量值，不构成跨平台可移植性主张。",
               "B2")

    # G1a ExtraTrees balanced accuracy
    text = fix(text,
               "两个总体的符号相反，量级都在千分之一量级。",
               "两个总体的符号相反，量级都在千分之一量级。另有一个基线在另一项指标上更强：极端随机树的平衡准确率为 0.96173，"
               "高于 RCCF 的 0.94920，为全场最高，但其 Macro-F1 最低（0.857713），原因在于它把预测更均匀地分摊到稀有类上。",
               "G1a")

    # G1b ExtraTrees robustness
    text = fix(text,
               "因此可以说\"在本扰动协议下两者鲁棒性相当，且都不耐受 1% 量级的连续噪声\"。",
               "因此可以说“在本扰动协议下两者鲁棒性相当，且都不耐受 1% 量级的连续噪声”。"
               "需要指出的是，极端随机树在同一扰动下明显更稳健：其相对下降仅 11.57%，约为条件加权分支 43.30% 的四分之一（图 10b）。"
               "正确的读法不是“门控提升了鲁棒性”（它没有），而是“另一个基线族提升了鲁棒性”，且这一差异大于门控在两个森林变体之间造成的任何差异。",
               "G1b")

    # F3a expand RCCF in the abstract
    text = fix(text, "以及条件加权森林（RCCF）、等权随机森林",
               "以及风险校准保形森林（Risk-Calibrated Conformal Forest，RCCF）、等权随机森林", "F3a")

    # F3b mention the neural baseline in the methods
    text = fix(text, "作为外部对照，本文还比较了等权随机森林（全特征与卡方两个版本）、极端随机树与 XGBoost。",
               "作为外部对照，本文还比较了等权随机森林（全特征与卡方两个版本）、极端随机树、XGBoost 与多层感知机（MLP）。", "F3b")

    # F5 unify the Demsar spelling
    text = fix(text, "37. Demšar J.", "37. Demsar J.", "F5")

    # A5 extend the supplementary list to match the English version
    tail = "| S15 | 校准曲线、扰动鲁棒性与延迟百分位的原始数值 |"
    extra = tail + "\n" + "\n".join([
        "| S16 | 门控 108 种超参数配置的搜索记录 |",
        "| S17 | 逐测试行的边距—扰动上界分析 |",
        "| S18 | 专家多样性实验（五类专家集合 × 三个种子） |",
        "| S19 | 神经基线结果及其与 RCCF 的配对比较 |",
    ])
    text = fix(text, tail, extra, "A5")

    MD.write_text(text, encoding="utf-8")
    print(f"ZH_FIXES_APPLIED  chars {n0} -> {len(text)}")


if __name__ == "__main__":
    main()
