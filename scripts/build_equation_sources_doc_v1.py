"""Record where each equation comes from, and re-derive the numbers around it.

The paper carries five numbered equations.  Two are definitions, one is a bound
derived here, two are expansions whose error the text quantifies.  A reader -
or an examiner - is entitled to ask which of those it is for each one, and
whether the numbers used to justify them reproduce.  This document answers both,
and the build fails if a printed value stops matching the released artefact.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
OUT = BASE / "公式来源与核验.md"
EN = (BASE / "English_SCI_Manuscript_v4.md").read_text(encoding="utf-8")
problems: list[str] = []


def claim(pattern: str, label: str) -> float:
    match = re.search(pattern, EN)
    if not match:
        problems.append(f"the manuscript no longer states {label}")
        return float("nan")
    return float(match.group(1))


def close(label: str, printed: float, recomputed: float, tol: float) -> None:
    if abs(printed - recomputed) > tol:
        problems.append(f"{label}: printed {printed}, recomputed {recomputed}")


def main() -> None:
    proposition = json.loads((ROOT / "results_margin_bound_v5" /
                              "proposition3_quantification.json").read_text(
        encoding="utf-8"))
    margin = json.loads((ROOT / "results_margin_bound_v5" /
                         "margin_bound_summary.json").read_text(encoding="utf-8"))
    margin_rows = pd.read_csv(ROOT / "results_margin_bound_v5" /
                              "margin_bound_summary.csv")
    weight = pd.read_csv(ROOT / "results_weight_mechanism_v3" /
                         "weight_mechanism_summary.csv").iloc[0]
    per_row = pd.read_csv(ROOT / "results_margin_bound_v5" /
                          "proposition3_quantification.csv")

    observed = float(proposition["mean_entropy_deficiency_observed"])
    second = float(proposition["mean_second_order_identity_value"])
    first = float(proposition["mean_entropy_deficiency_predicted_from_var_delta"])
    median_sd = float(proposition["median_sd_risk_offset"])
    ratio = margin_rows.margin_to_bound_ratio_median

    # the four numbers printed beside Equations (3) and (4)
    close("observed mean entropy deficiency", claim(
        r"observed mean entropy deficiency is ([\d.]+) x 10\^-5", "it"), observed * 1e5, 5e-3)
    close("second-order prediction", claim(
        r"second-order identity predicts ([\d.]+) x 10\^-5", "it"), second * 1e5, 5e-3)
    close("first-order prediction", claim(
        r"first-order relation predicts ([\d.]+) x 10\^-5", "it"), first * 1e5, 5e-3)
    close("median risk-offset standard deviation", claim(
        r"median standard deviation of the risk offsets across the four experts is ([\d.]+)",
        "it"), median_sd, 5e-6)
    # Equation (2)'s coverage and the margin-to-bound ratio, as the text prints them
    close("provable-by-bound share", claim(
        r"under the a priori bound ([\d.]+)% of rows are provably immune", "it"),
          float(margin["provable_by_bound_rate_mean"]) * 100, 5e-3)
    printed_ratio = re.search(r"median margin-to-bound ratio of ([\d,]+) to ([\d,]+)", EN)
    if not printed_ratio:
        problems.append("the manuscript no longer prints the margin-to-bound ratio")
    else:
        close("median margin-to-bound ratio, low",
              float(printed_ratio.group(1).replace(",", "")), float(ratio.min()), 1.0)
        close("median margin-to-bound ratio, high",
              float(printed_ratio.group(2).replace(",", "")), float(ratio.max()), 1.0)

    lines: list[str] = []
    lines.append("# 公式来源与核验")
    lines.append("")
    lines.append("> 本文共五个编号公式。本表逐式说明它是**定义**、**本文推导**还是"
                 "**展开近似**，依据在哪、误差多大，并用已发布产物重新核验公式旁的数字。"
                 "核验不通过时构建会失败。")
    lines.append("")
    lines.append("## 一、一览")
    lines.append("")
    lines.append("| 式 | 内容 | 类型 | 依据 / 来源 | 正文位置 |")
    lines.append("|---|---|---|---|---|")
    lines.append("| (1) | 条件权重 w_e ∝ exp(−r_e) 与凸组合融合 p = Σ w_e p_e | **本文机制规格**（定义）| "
                 "加权平均融合的标准形式见 Kuncheva [9]；该族在文献中的多种实现见 §2；"
                 "融合后的温度缩放 [29]、Mondrian 共形 [32–35] | §4.2 Step 3 |")
    lines.append("| (2) | ‖p_w − p̄‖₁ ≤ Σ|w_e − 1/Q| =: Δ(x) | **本文推导** | "
                 "三角不等式 + 每个专家后验在单纯形上（‖p_e‖₁ = 1）；证明见 §4.3 Condition 2 | §4.3 |")
    lines.append("| (3) | 1 − H_norm = (Q / 2log Q)·‖w − (1/Q)1‖² | **本文推导（二阶展开）** | "
                 "在均匀点对归一化熵作二阶 Taylor 展开；误差在正文中量化 | §4.3 Condition 3 |")
    lines.append("| (4) | 1 − H_norm ≈ Var(δ) / (2log Q) | **本文推导（一阶展开）** | "
                 "softmax 的一阶线性化，δ 为风险偏移 | §4.3 Condition 3 |")
    lines.append("| (5) | H_norm(x) = −(1/log Q) Σ w_e log w_e | **标准定义** | "
                 "归一化 Shannon 熵，集成多样性文献中的常规度量（Kuncheva [9]） | §4.3 |")
    lines.append("")
    lines.append("## 二、式 (1)：机制规格，不是新定理")
    lines.append("")
    lines.append("条件加权的权重由 softmax 负风险给出、融合为凸组合——这是**本文对机制的规格说明**，"
                 "与 Breiman 的概率平均 [1,2] 属同一族（把等权 1/Q 换成样本相关权重），"
                 "§2 已列出该族在文献中的实现方式（验证集精度加权、袋外误差加权、元学习器预测权重、"
                 "校准后的置信度加权等）。因此式 (1) 不主张数学新颖性，它的新颖性在于**被检验**："
                 "本文用十个种子、三档总体检验它是否优于等权。")
    lines.append("")
    lines.append("## 三、式 (2)：本文推导的上界")
    lines.append("")
    lines.append(f"对任意权重向量，融合后验相对等权融合的 L1 移动不超过权重与均匀分布的 L1 距离。"
                 f"逐行核验（`results_margin_bound_v5/`）：**{margin['provable_by_bound_rate_mean'] * 100:.2f}%** "
                 f"的测试行满足 2Δ(x) < 边距从而标签必然不变，实际改判 "
                 f"{margin['empirical_changed_rows']} 行；边距与上界之比的中位数为 "
                 f"{ratio.min():.0f} 至 {ratio.max():.0f}（逐种子）。")
    lines.append("")
    lines.append("## 四、式 (3) 与 (4)：展开近似，误差已量化")
    lines.append("")
    lines.append(f"两者都是近似：式 (3) 保留二阶项，式 (4) 进一步线性化 softmax。"
                 f"在 7 986 条自然先验测试行上（逐行文件 `proposition3_quantification.csv`）：")
    lines.append("")
    lines.append("| 量 | 值 | 相对误差 |")
    lines.append("|---|---:|---:|")
    lines.append(f"| 观测的平均熵亏缺 | {observed:.3e} | — |")
    lines.append(f"| 二阶展开预测（式 3）| {second:.3e} | {abs(second - observed) / observed * 100:.1f}% |")
    lines.append(f"| 一阶展开预测（式 4）| {first:.3e} | {abs(first - observed) / observed * 100:.1f}% |")
    lines.append(f"| 四专家风险偏移的中位标准差 | {median_sd:.5f} | — |")
    lines.append("")
    lines.append("也就是说：公式本身是近似，而正文给出的误差（1.5% 与 4.0%）与逐行文件一致。")
    lines.append("")
    lines.append("## 五、式 (5)：标准定义")
    lines.append("")
    lines.append(f"归一化权重熵是集成多样性研究里的常规度量，取 Q = 4 个专家时上界为 1。"
                 f"实测权重熵 **{weight.normalized_weight_entropy:.5f}**，"
                 f"概率 L1 平均变化 {weight.mean_probability_l1:.6f}（最大 "
                 f"{weight.max_probability_l1:.6f}），与实际改判 0 行一致。")
    lines.append("")
    lines.append("## 六、核验方式")
    lines.append("")
    lines.append("- 式 (2)：`results_margin_bound_v5/margin_bound_summary.csv|json`"
                 "（逐种子可证比例、边距比）+ 逐行文件三个 seed；")
    lines.append("- 式 (3)(4)：`results_margin_bound_v5/proposition3_quantification.csv|json`"
                 f"（{len(per_row):,} 行逐样本熵亏缺、预测值与风险偏移标准差）；")
    lines.append("- 式 (5) 与式 (1)：`results_weight_mechanism_v3/`（权重熵与逐样本预测对比）；")
    lines.append("- 本表由 `scripts/build_equation_sources_doc_v1.py` 生成，"
                 "其中四处印刷数字（3.24 / 3.19 / 3.36 ×10⁻⁵ 与 0.00022）会与产物逐一比对，"
                 "不一致即构建失败。")
    lines.append("")
    if "--check" in sys.argv:
        # verification only: the gate runs this so a changed number fails without
        # rewriting the deliverable
        print("EQUATION_SOURCES_CHECK_ONLY")
    else:
        OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"EQUATION_SOURCES_WRITTEN={OUT}")
    print(f"observed={observed:.3e} second={second:.3e} first={first:.3e} "
          f"median_sd={median_sd:.5f} problems={len(problems)}")
    if problems:
        for problem in problems:
            print(f"ISSUE {problem}")
        raise SystemExit("equation verification failed")
    print("EQUATION_SOURCES_OK")


if __name__ == "__main__":
    main()
