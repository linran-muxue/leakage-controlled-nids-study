"""Update the Chinese manuscript with the ten-seed primary results."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "中文SCI论文_v4_重构版.md"
RUN = ROOT / "results_seeds10_v5"


def fix(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"anchor missing: {label}")
    return text.replace(old, new, 1)


def main() -> None:
    text = MD.read_text(encoding="utf-8")
    table = pd.read_csv(RUN / "table4a_10seeds.csv")
    pretty = {"rccf": "RCCF", "equal_rf_chi2": "等权森林（χ²，k = 60）",
              "equal_rf_all": "等权森林（全特征）", "extra_trees_chi2": "极端随机树（χ²）"}
    rows = ["| 模型 | 准确率 | 平衡准确率 | Macro-F1 | Log Loss | Brier | ECE | 训练 (s) | 推理 (s) |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for _, r in table.iterrows():
        rows.append(f"| {pretty[r['model']]} | {r['accuracy']:.5f} | {r['balanced_accuracy']:.5f} | "
                    f"**{r['macro_f1']:.6f}** | {r['log_loss']:.5f} | {r['brier']:.6f} | "
                    f"{r['ece']:.6f} | {r['train_seconds']:.3f} | {r['predict_seconds']:.4f} |")

    # contribution 3
    text = fix(text, "聚合策略（+0.0011）、特征视图（−0.0009）、类别先验（+0.072）",
               "聚合策略（0.0005）、特征视图（+0.0021）、类别先验（+0.0725）", "contrib")

    # estimand seeds
    text = fix(text, "在一组预先固定的随机种子（42、2024、3407）上取平均。",
               "在一组预先固定的十个随机种子（42、2024、3407、7、13、101、202、303、404、505）上取平均。",
               "seeds")

    # 5.1 feature-selection row
    text = fix(text, "| 自然先验总体（3 种子均值） | 0.887960 | 0.888870 | **+0.00091** |",
               "| 自然先验总体（10 种子均值） | 0.887666 | 0.889734 | **+0.00207** |", "feature-row")

    # table 4 lead-in / caption / panel head
    text = fix(text, "表 4 给出在自然先验总体与平衡控制总体上的主结果。所有数字为三个固定随机种子的均值。",
               "表 4 给出在自然先验总体与平衡控制总体上的主结果。其中 (a) 为十个种子的均值，(b) 仍为三个种子的平衡控制。",
               "table4-lead")
    text = fix(text, "**表 4 主结果：两个总体上的模型对比（三种子均值）**",
               "**表 4 主结果：两个总体上的模型对比**", "table4-caption")
    text = fix(text, "（a）自然先验总体 P_nat，测试集 7 986 条",
               "（a）自然先验总体 P_nat，测试集 7 986 条，十种子均值", "table4a-head")

    old_rows = "\n".join([
        "| RCCF | 0.97792 | 0.94920 | **0.889955** | **0.05148** | **0.006312** | 0.006605 | 61.00 | 0.173 |",
        "| 等权森林（χ²，k = 60） | 0.97759 | 0.94948 | 0.888870 | 0.05283 | 0.006334 | **0.004442** | 0.784 | 0.0295 |",
        "| 等权森林（全特征） | 0.97696 | 0.95085 | 0.887960 | 0.05424 | 0.006624 | 0.005126 | 0.816 | 0.0367 |",
        "| 极端随机树（χ²） | 0.96369 | **0.96173** | 0.857713 | 0.08903 | 0.010849 | 0.015791 | 0.442 | 0.0368 |",
    ])
    text = fix(text, old_rows, "\n".join(rows), "panel-a")

    # first reading
    text = fix(text,
               "**第一，相对最直接的等权对照，差异落在等价边界内。** 在自然先验总体下，RCCF 的 Macro-F1 为 0.889955，"
               "等权卡方森林为 0.888870，平均差 **+0.001085**；在平衡控制总体下，RCCF 为 0.961807，等权卡方森林为 "
               "0.963215，RCCF 反而落后 **−0.001408**。两个总体的符号相反，量级都在千分之一量级。另有一个基线在"
               "另一项指标上更强：极端随机树的平衡准确率为 0.96173，高于 RCCF 的 0.94920，为全场最高，但其 Macro-F1 "
               "最低（0.857713），原因在于它把预测更均匀地分摊到稀有类上。",
               "**第一，相对最直接的等权对照，差异落在等价边界内。** 在自然先验总体上取十个种子的平均，RCCF 的 "
               "Macro-F1 为 0.889278，等权卡方森林为 0.889734，平均差 **−0.000456**，逐种子方向为五正五负。"
               "在三 seed 的平衡控制总体下，RCCF 为 0.961807，等权卡方森林为 0.963215，RCCF 反而落后 **−0.001408**。"
               "两个总体的量级都在千分之一以下，且符号不稳定。另有一个基线在另一项指标上更强：极端随机树的平衡准确率"
               "为 0.96215，高于 RCCF 的 0.94820，为全场最高，但其 Macro-F1 最低（0.857490），原因在于它把预测"
               "更均匀地分摊到稀有类上。",
               "first-reading")

    # second reading
    text = fix(text,
               "**第二，配对统计给出明确的等价边界。** 表 5 给出逐种子配对结果。三个种子的差分别为 −0.00149、+0.00314、"
               "+0.00160。以测试行为重采样单元的配对 Bootstrap 给出合并 90% 区间 [−0.00290, +0.00550]，在预先设定的"
               "等价边界 SESOI = 0.01 Macro-F1 下完全落入边界内，因此可在 α = 0.05 水平主张两者等价；但在 SESOI = 0.005 "
               "下不成立，因为上界 0.0055 越界。逐种子精确 McNemar 检验的 p 值为 0.508、0.092、0.344，合并 23 958 条"
               "测试行的 p 值为 0.215，均不显著。",
               "**第二，配对统计在严格边界上也给出等价结论。** 十个种子的平均配对差为 −0.000456，标准差 0.001152。"
               "这里报告两个区间，因为它们回答不同的问题：种子级 90% 区间 [−0.001124, +0.000212] 反映模型间的波动，"
               "测试行级配对 Bootstrap 区间 [−0.004251, +0.003382] 反映锁定测试集上的重采样不确定性。两者都落在 "
               "SESOI = 0.005 与 0.01 Macro-F1 的边界之内，因此可在 α = 0.05 水平对两个边界分别主张等价。"
               "相比三种子分析，这是实质加强——当时 0.005 边界无法达到。逐种子符号为五正五负，测试行上的精确 McNemar "
               "检验不显著。",
               "second-reading")

    MD.write_text(text, encoding="utf-8")
    print("ZH_10SEED_PART1_APPLIED")


if __name__ == "__main__":
    main()
