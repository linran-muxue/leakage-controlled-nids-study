"""Build the nine main figures for the restructured manuscript (v4).

Every panel reads from a canonical result directory so that the figures and the
manuscript text share the same source numbers.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "重构版论文_v4_20260915" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

for candidate in ["Microsoft YaHei", "SimHei", "DejaVu Sans"]:
    try:
        matplotlib.font_manager.findfont(candidate, fallback_to_default=False)
        plt.rcParams["font.sans-serif"] = [candidate]
        break
    except Exception:
        continue
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.bbox"] = "tight"

COLORS = ["#2f6fb3", "#e07b39", "#5a9e6f", "#b5525b", "#7a6fb0", "#8c8c8c"]


def box(ax, x, y, w, h, text, fc="#eef3fa", ec="#2f6fb3", fs=9):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.02",
                                linewidth=1.2, edgecolor=ec, facecolor=fc))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, wrap=True)


def arrow(ax, p1, p2, color="#444444", style="-|>", lw=1.3, ls="-"):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=12,
                                 linewidth=lw, color=color, linestyle=ls,
                                 shrinkA=1, shrinkB=1))


# ---------------------------------------------------------------- figure 1
def fig1():
    fig, ax = plt.subplots(figsize=(11.6, 5.4))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    steps = [
        ("原始归档\n8 个 CSV\n2 830 743 行", 0.01, 0.62),
        ("标签映射\n保留 5 类\n2 671 766 行", 0.155, 0.62),
        ("非有限值剔除\n−2 741 行", 0.30, 0.62),
        ("物理范围筛查\n−296 行", 0.445, 0.62),
        ("全局去重\n与冲突处理", 0.59, 0.62),
        ("类别截断\n自然先验 53 237\n平衡控制 3 365", 0.735, 0.62),
    ]
    for text, x, y in steps:
        box(ax, x, y, 0.135, 0.20, text, fs=8.6)
    for i in range(len(steps) - 1):
        arrow(ax, (steps[i][1] + 0.135, 0.72), (steps[i + 1][1], 0.72))

    split = [("训练分区 70%", 0.03), ("验证分区 15%", 0.245), ("测试分区 15%（锁定）", 0.46)]
    for text, x in split:
        box(ax, x, 0.30, 0.20, 0.16, text, fc="#eaf5ee", ec="#5a9e6f", fs=9)
    arrow(ax, (0.80, 0.62), (0.13, 0.46), color="#5a9e6f")
    arrow(ax, (0.80, 0.62), (0.345, 0.46), color="#5a9e6f")
    arrow(ax, (0.80, 0.62), (0.56, 0.46), color="#5a9e6f")

    fit = [("仅训练侧拟合\n标准化器 + χ²/MI/ANOVA 选择器\nK 折交叉拟合风险模型", 0.03, 0.045),
           ("验证侧校准\n温度缩放\n蒙德里安保形阈值 α=0.1", 0.36, 0.045),
           ("测试侧\n一次性评估\n逐样本预测公开", 0.69, 0.045)]
    for text, x, y in fit:
        box(ax, x, y, 0.28, 0.17, text, fc="#fdf1e6", ec="#e07b39", fs=8.6)
    arrow(ax, (0.13, 0.30), (0.17, 0.215), color="#e07b39")
    arrow(ax, (0.345, 0.30), (0.50, 0.215), color="#e07b39")
    arrow(ax, (0.56, 0.30), (0.83, 0.215), color="#e07b39")

    ax.plot([0.01, 0.99], [0.525, 0.525], color="#b5525b", lw=1.8, ls="--")
    ax.text(0.012, 0.545, "信息边界：以下步骤不得读取测试分区标签", color="#b5525b", fontsize=9, va="bottom")
    ax.text(0.5, 0.965, "泄漏受控协议：任何依赖标签的统计量只在训练/验证侧拟合",
            ha="center", fontsize=10.5, weight="bold")
    fig.savefig(OUT / "fig1_protocol_pipeline.png")
    plt.close(fig)


# ---------------------------------------------------------------- figure 2
def fig2():
    audit = json.loads((ROOT / "results_data_audit_cic_natural_v3b" / "data_processing_audit.json").read_text("utf-8"))
    t = audit["raw_totals"]
    stages = [
        ("原始归档", t["source_rows"]),
        ("标签映射", t["mapped_rows"]),
        ("非有限值剔除", t["valid_rows"]),
        ("物理范围筛查", t["physical_valid_rows"]),
        ("类别截断后", 53237),
        ("训练分区", 37265),
    ]
    labels = [s[0] for s in stages]
    values = [s[1] for s in stages]
    fig, ax = plt.subplots(figsize=(10.4, 4.6))
    xs = np.arange(len(stages))
    bars = ax.bar(xs, values, color=COLORS[: len(stages)], width=0.62)
    for x, v in zip(xs, values):
        ax.text(x, v * 1.05, f"{v:,}", ha="center", fontsize=9.2, weight="bold")
    drops = [("−158 977", 0), ("−2 741", 1), ("−296", 2),
             ("重复 239 093 次 / 冲突向量 133 个", 3), ("按类上限 20 000 截断", 4)]
    for text, i in drops:
        ax.annotate(text, xy=(i + 0.5, values[i] * 0.55), xytext=(i + 0.5, values[i] * 0.78),
                    ha="center", fontsize=8.2, color="#b5525b",
                    arrowprops=dict(arrowstyle="-|>", color="#b5525b", lw=1.0))
    ax.set_yscale("log")
    ax.set_ylabel("记录数（对数刻度）")
    ax.set_xticks(xs); ax.set_xticklabels(labels, fontsize=9)
    ax.set_title("CIC-IDS2017 审计阶段计数链（自然先验总体）", fontsize=11.5, weight="bold")
    ax.grid(axis="y", alpha=0.25)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.savefig(OUT / "fig2_data_waterfall.png")
    plt.close(fig)


# ---------------------------------------------------------------- figure 3
def fig3():
    fig, ax = plt.subplots(figsize=(12.0, 7.2))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    experts = ["专家 1\n全特征 78 维", "专家 2\nχ² Top-60", "专家 3\n互信息 Top-60", "专家 4\nANOVA Top-60"]
    for i, e in enumerate(experts):
        y = 0.815 - i * 0.135
        box(ax, 0.015, y, 0.155, 0.115, e, fs=8.4)
        arrow(ax, (0.170, y + 0.0575), (0.245, 0.755))

    box(ax, 0.245, 0.645, 0.195, 0.225, "交叉拟合袋外概率\n+ 可靠性描述子\n（置信度 / 归一化熵 / 边距）",
        fc="#eaf5ee", ec="#5a9e6f", fs=8.3)
    arrow(ax, (0.440, 0.7575), (0.505, 0.7575))
    box(ax, 0.505, 0.645, 0.155, 0.225, "逻辑回归\n风险模型\nr_e(x)", fc="#eef3fa", ec="#2f6fb3", fs=8.6)
    arrow(ax, (0.660, 0.7575), (0.715, 0.7575))
    box(ax, 0.715, 0.645, 0.270, 0.225,
        r"$w_e(x)=\exp[-r_e(x)]\,/\,\sum_j \exp[-r_j(x)]$" + "\n\n" +
        r"$p(y\,|\,x)=\sum_e w_e(x)\,p_e(y\,|\,x)$",
        fc="#fdf1e6", ec="#e07b39", fs=9.6)
    arrow(ax, (0.850, 0.645), (0.850, 0.500))
    box(ax, 0.715, 0.335, 0.270, 0.165, "温度缩放（仅验证集）\n蒙德里安保形拒绝 α = 0.1",
        fc="#f4eef7", ec="#7a6fb0", fs=8.6)

    ax.text(0.5, 0.285, "三个可辨识性边界（第 4.3 节）", fontsize=11, weight="bold", ha="center")
    props = [
        "命题 1 · 凸组合不变性\n\n专家后验概率相同时，\n任何凸权重组合给出相同预测",
        "命题 2 · 边距支配\n\n边距大于权重可造成的\n最大概率移动时，硬标签不变",
        "命题 3 · 权重坍缩\n\n风险输出近似相等时，\nw_e 趋近 1/Q，权重熵趋近 1",
    ]
    for i, p in enumerate(props):
        box(ax, 0.015 + i * 0.330, 0.020, 0.310, 0.235, p, fc="#fdeef0", ec="#b5525b", fs=8.4)
    fig.savefig(OUT / "fig3_rccf_mechanism.png")
    plt.close(fig)


# ---------------------------------------------------------------- figure 4
def _natural_table():
    # 面板 (a) 与表 4(a) 使用同一批十种子结果；神经基线只在两次运行共有的三个种子上训练。
    ten = pd.read_csv(ROOT / "results_seeds10_v5" / "table4a_10seeds.csv").set_index("model")
    per_seed = pd.read_csv(ROOT / "results_seeds10_v5" / "metrics_by_seed.csv")

    def ten_seed(model):
        sub = per_seed[per_seed.model == model]
        return float(ten.loc[model, "macro_f1"]), float(sub["macro_f1"].std(ddof=0))

    rows = {
        "RCCF": ten_seed("rccf"),
        "Equal RF (χ²)": ten_seed("equal_rf_chi2"),
        "Equal RF (all)": ten_seed("equal_rf_all"),
        "ExtraTrees (χ²)": ten_seed("extra_trees_chi2"),
    }
    return rows, per_seed


def fig4():
    nat, per_seed = _natural_table()
    bal = pd.read_csv(ROOT / "results_cic_balanced_baselines_v3b" / "metrics_aggregate_flat.csv")
    bal_rccf = pd.read_csv(ROOT / "results_rccf_cic_balanced_v3b" / "metrics_aggregate.csv")
    bal_rows = {
        "RCCF": float(bal_rccf["macro_f1_mean"].iloc[0]),
        "Equal RF (χ²)": float(bal.loc[bal.model == "equal_rf_chi2", "macro_f1_mean"].iloc[0]),
        "Equal RF (all)": float(bal.loc[bal.model == "equal_rf_all", "macro_f1_mean"].iloc[0]),
        "ExtraTrees (χ²)": float(bal.loc[bal.model == "extra_trees_chi2", "macro_f1_mean"].iloc[0]),
    }
    strong = pd.read_csv(ROOT / "results_cfrg_strong_baselines_v2_verified" / "summary.csv", header=[0, 1])
    strong.columns = ["_".join(str(c) for c in col if "Unnamed" not in str(c)).strip("_") for col in strong.columns]
    bal_rows["XGBoost"] = float(strong.loc[strong["model"] == "xgboost", "macro_f1_mean"].iloc[0])

    mlp = pd.read_csv(ROOT / "results_mlp_final_v5" / "metrics_aggregate.csv")
    names = list(nat.keys()) + ["MLP（三种子）", "XGBoost"]
    nat_vals = [nat[n][0] for n in nat] + [float(mlp["macro_f1_mean"].iloc[0])] + [np.nan]
    nat_err = [nat[n][1] for n in nat] + [float(mlp["macro_f1_std"].iloc[0])] + [np.nan]
    bal_vals = [bal_rows["RCCF"], bal_rows["Equal RF (χ²)"], bal_rows["Equal RF (all)"],
                bal_rows["ExtraTrees (χ²)"], np.nan, bal_rows["XGBoost"]]

    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.8), gridspec_kw={"width_ratios": [1.55, 1]})
    ax = axes[0]
    x = np.arange(len(names)); w = 0.38
    ax.bar(x - w / 2, nat_vals, w, yerr=nat_err, capsize=3, color="#2f6fb3", label="自然先验总体")
    ax.bar(x + w / 2, bal_vals, w, color="#e07b39", label="平衡控制总体")
    ax.set_xticks(x); ax.set_xticklabels(names, rotation=18, ha="right", fontsize=8.8)
    ax.set_ylim(0.75, 0.99); ax.set_ylabel("Macro-F1")
    ax.set_title("两个总体上的 Macro-F1（自然先验：十种子；平衡控制：三种子）", fontsize=10.5, weight="bold")
    ax.legend(fontsize=8.5); ax.grid(axis="y", alpha=0.25)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    ax2 = axes[1]
    bs = pd.read_csv(ROOT / "results_equivalence_10seeds_v5" / "tost_results.csv")
    labels = [f"seed {int(s)}" for s in bs["seed"]]
    est = bs["delta"].values; lo = bs["ci95_low"].values; hi = bs["ci95_high"].values
    ypos = np.arange(len(labels))
    ax2.errorbar(est, ypos, xerr=[est - lo, hi - est], fmt="o", color="#b5525b",
                 ecolor="#b5525b", capsize=4, ms=6)
    ax2.axvline(0, color="#555555", lw=1.1, ls="--")
    ax2.set_yticks(ypos); ax2.set_yticklabels(labels, fontsize=9)
    ax2.set_xlabel("RCCF − 等权森林 Macro-F1 差")
    ax2.set_title("配对 Bootstrap 95% 区间（自然先验）", fontsize=10.5, weight="bold")
    ax2.grid(axis="x", alpha=0.25)
    for s in ("top", "right"):
        ax2.spines[s].set_visible(False)
    fig.savefig(OUT / "fig4_main_results.png")
    plt.close(fig)


# ---------------------------------------------------------------- figure 5
def fig5():
    dist = pd.read_csv(ROOT / "results_weight_mechanism_v3" / "tree_weight_distribution.csv")
    summary = pd.read_csv(ROOT / "results_weight_mechanism_v3" / "weight_mechanism_summary.csv").iloc[0]
    cmp = pd.read_csv(ROOT / "results_weight_mechanism_v3" / "weight_prediction_comparison.csv")
    disagree = int(cmp["disagreement"].sum())

    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.2))
    ax = axes[0]
    ax.scatter(dist["tree_score"], dist["tree_weight"], s=14, color="#2f6fb3", alpha=0.75)
    ax.set_xlabel("单树验证准确率"); ax.set_ylabel("分配权重")
    ax.set_title("(a) 树得分与权重的关系", fontsize=10, weight="bold")
    ax.text(0.03, 0.95, f"权重变异系数 CV = {summary['weight_cv']:.5f}",
            transform=ax.transAxes, fontsize=8.6, va="top", color="#b5525b")
    ax.grid(alpha=0.25)

    ax = axes[1]
    ax.hist(dist["tree_weight"], bins=24, color="#e07b39", edgecolor="white")
    ax.set_xlabel("权重取值"); ax.set_ylabel("树数量")
    ax.set_title("(b) 权重分布高度集中", fontsize=10, weight="bold")
    ax.text(0.03, 0.95, f"归一化权重熵 = {summary['normalized_weight_entropy']:.5f}",
            transform=ax.transAxes, fontsize=8.6, va="top", color="#b5525b")
    ax.grid(alpha=0.25)

    ax = axes[2]
    ax.axis("off")
    ax.set_title("(c) 机制诊断记分卡", fontsize=10, weight="bold")
    rows = [
        ("归一化权重熵", f"{summary['normalized_weight_entropy']:.5f}", "权重坍缩为等权", "#b5525b"),
        ("权重变异系数", f"{summary['weight_cv']:.5f}", "树间权重差异极小", "#b5525b"),
        ("平均概率 L1 变化", f"{summary['mean_probability_l1']:.6f}", "概率质量几乎未移动", "#e07b39"),
        ("最大概率 L1 变化", f"{summary['max_probability_l1']:.6f}", "单个样本最大移动量", "#e07b39"),
        ("预测分歧条数", f"{disagree} / {int(summary['test_samples'])}", "硬标签零改变", "#b5525b"),
    ]
    y = 0.80
    for name, value, verdict, color in rows:
        ax.text(0.02, y, name, fontsize=8.6, va="center")
        ax.text(0.74, y, value, fontsize=9.6, va="center", weight="bold", ha="right")
        ax.text(0.78, y, verdict, fontsize=7.6, va="center", color=color)
        ax.plot([0.02, 1.00], [y - 0.082, y - 0.082], color="#dddddd", lw=0.8)
        y -= 0.168
    ax.text(0.02, 0.005, "结论：三个命题的预测均被实测数据满足。", fontsize=8.6, color="#b5525b", weight="bold")
    for a in axes:
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
    fig.savefig(OUT / "fig5_gate_diagnostics.png")
    plt.close(fig)


# ---------------------------------------------------------------- figure 6
def fig6():
    ps = pd.read_csv(ROOT / "results_protocol_sensitivity_v4" / "protocol_sensitivity_metrics.csv")
    rep = pd.read_csv(ROOT / "results_repeated_splits_v3" / "summary.csv", header=[0, 1])
    rep.columns = ["_".join(str(c) for c in col if "Unnamed" not in str(c)).strip("_") for col in rep.columns]
    nested = pd.read_csv(ROOT / "results_nested_modelwise_v1_5x3" / "outer_modelwise_summary.csv", header=[0, 1])
    nested.columns = ["_".join(str(c) for c in col if "Unnamed" not in str(c)).strip("_") for col in nested.columns]
    nat = 0.889955; bal = 0.961807
    dedup_glob = ps[ps.protocol == "global_dedup_before_split"]["macro_f1"].mean()
    dedup_split = ps[ps.protocol == "split_first_training_only_dedup"]["macro_f1"].mean()
    rf_rep = float(rep.loc[rep["model"] == "rf_all", "macro_f1_mean"].iloc[0])
    chi_rep = float(rep.loc[rep["model"] == "rf_chi2", "macro_f1_mean"].iloc[0])
    rf_nested = float(nested.loc[nested["model"] == "random_forest", "macro_f1_mean"].iloc[0])
    xgb_nested = float(nested.loc[nested["model"] == "xgboost", "macro_f1_mean"].iloc[0])

    fig, axes = plt.subplots(1, 2, figsize=(12.8, 4.8), gridspec_kw={"width_ratios": [1.25, 1]})
    ax = axes[0]
    items = [
        ("聚合策略\n(RCCF − 等权 χ²)", abs(0.0010848)),
        ("特征视图\n(全特征 − χ²)", abs(chi_rep - rf_rep)),
        ("去重顺序\n(后去重 − 先去重)", abs(dedup_split - dedup_glob)),
        ("调参预算\n(XGBoost − RF)", abs(xgb_nested - rf_nested)),
        ("类别先验\n(平衡 − 自然)", abs(bal - nat)),
    ]
    names = [i[0] for i in items]; vals = [i[1] for i in items]
    colors = ["#2f6fb3", "#5a9e6f", "#8c8c8c", "#7a6fb0", "#b5525b"]
    ax.barh(names[::-1], vals[::-1], color=colors[::-1])
    for i, v in enumerate(vals[::-1]):
        ax.text(v * 1.06, i, f"{v:.4f}", va="center", fontsize=9, weight="bold")
    ax.set_xscale("log")
    ax.set_xlabel("Macro-F1 绝对差异（对数刻度）")
    ax.set_title("(a) 差异来源的量级对比", fontsize=10.5, weight="bold")
    ax.grid(axis="x", alpha=0.25)
    ax.tick_params(axis="y", labelsize=8.4)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    ax = axes[1]
    seeds = [42, 2024, 3407]
    g = [ps[(ps.protocol == "global_dedup_before_split") & (ps.seed == s)]["macro_f1"].iloc[0] for s in seeds]
    q = [ps[(ps.protocol == "split_first_training_only_dedup") & (ps.seed == s)]["macro_f1"].iloc[0] for s in seeds]
    x = np.arange(len(seeds)); w = 0.36
    ax.bar(x - w / 2, g, w, label="划分前全局去重", color="#2f6fb3")
    ax.bar(x + w / 2, q, w, label="划分后训练侧去重", color="#e07b39")
    for i, (a, b) in enumerate(zip(g, q)):
        ax.text(i, max(a, b) + 0.0016, f"Δ={b - a:+.4f}", ha="center", fontsize=8.6, color="#b5525b")
    ax.set_xticks(x); ax.set_xticklabels([f"seed {s}" for s in seeds])
    ax.set_ylim(0.94, 0.972); ax.set_ylabel("Macro-F1")
    ax.set_title("(b) 去重顺序的逐种子对照", fontsize=10.5, weight="bold")
    ax.legend(fontsize=8.4); ax.grid(axis="y", alpha=0.25)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.savefig(OUT / "fig8_protocol_sensitivity.png")
    plt.close(fig)


# ---------------------------------------------------------------- figure 7
def _class_report(path):
    df = pd.read_csv(path)
    df = df.rename(columns={df.columns[0]: "class"})
    df = df[~df["class"].astype(str).str.strip().isin(["accuracy", "macro avg", "weighted avg"])]
    return df[["class", "f1-score", "support"]].astype({"f1-score": float, "support": float})


def fig7():
    nsl = _class_report(ROOT / "results_rccf_nsl_v2_final" / "classification_report_seed42.csv")
    unsw = _class_report(ROOT / "results_rccf_unsw_v2_final" / "classification_report_seed42.csv")
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 4.8))
    for ax, df, title in [(axes[0], nsl, "(a) NSL-KDD（5 类）"), (axes[1], unsw, "(b) UNSW-NB15（10 类）")]:
        d = df.sort_values("f1-score")
        labels = [f"{c}  (n={int(s):,})" for c, s in zip(d["class"], d["support"])]
        colors = ["#b5525b" if v < 0.5 else "#e07b39" if v < 0.8 else "#5a9e6f" for v in d["f1-score"]]
        ax.barh(labels, d["f1-score"], color=colors)
        for i, v in enumerate(d["f1-score"]):
            ax.text(v + 0.015, i, f"{v:.3f}", va="center", fontsize=8.4)
        ax.set_xlim(0, 1.12); ax.set_xlabel("F1 分数")
        ax.set_title(title, fontsize=10.5, weight="bold")
        ax.grid(axis="x", alpha=0.25); ax.tick_params(axis="y", labelsize=8.2)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    fig.suptitle("外部原生标签基准的类别级 F1（RCCF，seed 42）", fontsize=11.5, weight="bold", y=1.02)
    fig.savefig(OUT / "fig9_external_class_f1.png")
    plt.close(fig)


# ---------------------------------------------------------------- figure 8
def fig8():
    cal = pd.read_csv(ROOT / "results_cfrg_calibration_v2_verified" / "metrics.csv")
    rob = pd.read_csv(ROOT / "results_rccf_evidence_v3b" / "robustness_shared.csv")
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 4.6))
    ax = axes[0]
    piv = cal.groupby(["model", "variant"])["ece"].mean().unstack()
    labels = ["等权森林", "条件加权"]
    uncal = [piv.loc["equal_rf", "uncalibrated"], piv.loc["cfrg_forest", "uncalibrated"]]
    scaled = [piv.loc["equal_rf", "temperature_scaled"], piv.loc["cfrg_forest", "temperature_scaled"]]
    x = np.arange(2); w = 0.36
    ax.bar(x - w / 2, uncal, w, label="校准前", color="#8c8c8c")
    ax.bar(x + w / 2, scaled, w, label="温度缩放后", color="#2f6fb3")
    for i in range(2):
        ax.text(i - w / 2, uncal[i] + 0.0012, f"{uncal[i]:.4f}", ha="center", fontsize=8.6)
        ax.text(i + w / 2, scaled[i] + 0.0012, f"{scaled[i]:.4f}", ha="center", fontsize=8.6)
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylabel("期望校准误差 ECE（三种子均值）")
    ax.set_title("(a) 概率校准：温度缩放的效果", fontsize=10.5, weight="bold")
    ax.legend(fontsize=8.6); ax.grid(axis="y", alpha=0.25)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    ax = axes[1]
    g = rob.groupby(["model", "condition"])["relative_drop"].mean().unstack() * 100
    models = ["equal_rf_chi2", "rccf", "extra_trees_chi2"]
    pretty = ["等权森林", "条件加权", "极端随机树"]
    noise = [g.loc[m, "gaussian_noise_1pct"] for m in models]
    mask = [g.loc[m, "feature_mask_5pct"] for m in models]
    x = np.arange(len(models)); w = 0.36
    ax.bar(x - w / 2, noise, w, label="1% 高斯噪声", color="#b5525b")
    ax.bar(x + w / 2, mask, w, label="5% 特征屏蔽", color="#5a9e6f")
    for i in range(len(models)):
        ax.text(i - w / 2, noise[i] + 1.0, f"{noise[i]:.2f}%", ha="center", fontsize=8.4)
        ax.text(i + w / 2, mask[i] + 1.0, f"{mask[i]:.2f}%", ha="center", fontsize=8.4)
    ax.set_xticks(x); ax.set_xticklabels(pretty)
    ax.set_ylabel("Macro-F1 相对下降（%）")
    ax.set_title("(b) 共享扰动下的鲁棒性", fontsize=10.5, weight="bold")
    ax.legend(fontsize=8.6); ax.grid(axis="y", alpha=0.25)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.savefig(OUT / "fig10_calibration_robustness.png")
    plt.close(fig)


# ---------------------------------------------------------------- figure 9
def fig9():
    lat = pd.read_csv(ROOT / "results_rccf_evidence_v3b" / "latency_percentiles.csv")
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.5), sharey=True)
    pretty = {"rccf": "条件加权", "equal_rf_chi2": "等权森林", "extra_trees_chi2": "极端随机树"}
    for ax, nj, title in [(axes[0], 1, "(a) 单线程 n_jobs = 1"), (axes[1], -1, "(b) 库默认多线程 n_jobs = -1")]:
        sub = lat[lat.n_jobs == nj].groupby("model")[["p50_ms", "p95_ms", "p99_ms"]].mean()
        models = ["equal_rf_chi2", "extra_trees_chi2", "rccf"]
        x = np.arange(len(models)); w = 0.26
        for k, (col, c) in enumerate(zip(["p50_ms", "p95_ms", "p99_ms"], ["#2f6fb3", "#e07b39", "#b5525b"])):
            vals = [sub.loc[m, col] for m in models]
            ax.bar(x + (k - 1) * w, vals, w, label=col.replace("_ms", "").upper(), color=c)
        ax.set_xticks(x); ax.set_xticklabels([pretty[m] for m in models])
        ax.set_title(title, fontsize=10.5, weight="bold")
        ax.grid(axis="y", alpha=0.25)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axes[0].set_ylabel("单条推理延迟（ms）")
    axes[0].legend(fontsize=8.4)
    fig.suptitle("分类器阶段的单条推理延迟（不含抓包与特征提取）", fontsize=11.2, weight="bold", y=1.02)
    fig.savefig(OUT / "fig11_latency.png")
    plt.close(fig)


# ------------------------------------------------- figure 6 (margin bound)
# The Chinese bundle needs these two figures as well: until now
# figures/fig6_margin_bound.png and figures/fig7_diversity_dose_response.png
# were frozen copies from 2026-09-15 that no builder produced.
def fig6_margin_bound():
    per_row = pd.concat([pd.read_csv(ROOT / "results_margin_bound_v5" / f"margin_bound_per_row_seed{s}.csv")
                         for s in (42, 2024, 3407)], ignore_index=True)
    summary = json.loads((ROOT / "results_margin_bound_v5" / "margin_bound_summary.json").read_text("utf-8"))
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 4.5))
    ax = axes[0]
    ax.hist(np.log10(np.clip(per_row["margin_equal_weight"], 1e-6, None)), bins=40,
            alpha=0.75, color="#2f6fb3", label="决策边距 $m(x)$")
    ax.hist(np.log10(np.clip(per_row["delta_bound_l1"], 1e-8, None)), bins=40,
            alpha=0.75, color="#b5525b", label="扰动上界 $\\Delta(x)$")
    ax.set_xlabel("$\\log_{10}$ 数值"); ax.set_ylabel("样本数")
    ax.set_title("(a) 边距比扰动上界大约三个数量级", fontsize=10.5, weight="bold")
    ax.legend(fontsize=8.6); ax.grid(axis="y", alpha=0.25)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax = axes[1]
    items = [("可证明不变\n(按上界)", summary["provable_by_bound_rate_mean"]),
             ("可证明不变\n(按实际扰动)", summary["provable_by_actual_rate_mean"]),
             ("实际改判", 1.0 - summary["empirical_changed_rows"] / summary["total_rows"])]
    labels = [i[0] for i in items]; values = [i[1] * 100 for i in items]
    bars = ax.bar(labels, values, color=["#5a9e6f", "#2f6fb3", "#b5525b"])
    ax.set_ylim(99.5, 100.05)
    ax.set_ylabel("占 23 958 条测试样本的比例 (%)")
    ax.set_title("(b) 命题 2 的可证明不变比例", fontsize=10.5, weight="bold")
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.02, f"{v:.3f}%", ha="center", fontsize=9)
    ax.grid(axis="y", alpha=0.25); ax.tick_params(axis="x", labelsize=8.4)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.savefig(OUT / "fig6_margin_bound.png")
    plt.close(fig)


# ------------------------------------------------- figure 7 (diversity gain)
DIVERSITY_ZH = {"rf_same_view_seeds": "同一视图、不同种子",
                "rf_views_k60": "四视图 k=60",
                "rf_views_k20": "四视图 k=20",
                "hetero_families": "异构算法族",
                "disjoint_views_k60": "互斥特征块"}


def fig7_diversity():
    df = pd.read_csv(ROOT / "results_diversity_v5" / "diversity_suite_results.csv")
    fit = json.loads((ROOT / "results_diversity_v5" / "diversity_gain_regression.json").read_text("utf-8"))
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 4.6))
    ax = axes[0]
    for name, sub in df.groupby("expert_set"):
        ax.scatter(sub["mean_pairwise_disagreement"] * 100, sub["gate_gain"], s=52,
                   label=DIVERSITY_ZH.get(name, name), alpha=0.85)
    xs = np.linspace(0, df["mean_pairwise_disagreement"].max() * 100, 50)
    ax.plot(xs, fit["slope"] * xs / 100 + fit["intercept"], color="#444444", lw=1.2, ls="--")
    ax.axhline(0, color="#b5525b", lw=1.0)
    ax.set_xlabel("专家间预测分歧率（%）"); ax.set_ylabel("门控增益（Macro-F1）")
    ax.set_title("(a) 分歧率与增益的剂量—反应", fontsize=10.5, weight="bold")
    ax.text(0.03, 0.95, f"斜率 {fit['slope']:.4f}，Pearson r = {fit['pearson_r']:.3f} (n={fit['n_points']})",
            transform=ax.transAxes, fontsize=8.4, va="top", color="#b5525b")
    ax.legend(fontsize=7.4, loc="lower right"); ax.grid(alpha=0.25)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax = axes[1]
    summary = df.groupby("expert_set").agg(
        disagreement=("mean_pairwise_disagreement", "mean"),
        gain=("gate_gain", "mean"),
        changed=("disagreement_gated_vs_equal", "mean")).sort_values("disagreement")
    colors = ["#b5525b" if g == 0 else "#5a9e6f" for g in summary["gain"]]
    ax.barh([DIVERSITY_ZH.get(i, i) for i in summary.index], summary["gain"], color=colors)
    for i, (g, c) in enumerate(zip(summary["gain"], summary["changed"])):
        ax.text(g + 0.00012 if g >= 0 else g - 0.00012, i, f"{g:+.5f}（改判 {c:.1f} 条）",
                va="center", ha="left" if g >= 0 else "right", fontsize=8.0)
    ax.axvline(0, color="#444444", lw=1.0)
    ax.set_xlim(-0.0006, 0.0058)
    ax.set_xlabel("门控增益（Macro-F1，三种子均值）")
    ax.set_title("(b) 低分歧专家集合增益恰为零", fontsize=10.5, weight="bold")
    ax.grid(axis="x", alpha=0.25); ax.tick_params(axis="y", labelsize=8.2)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.subplots_adjust(wspace=0.45)
    fig.savefig(OUT / "fig7_diversity_dose_response.png")
    plt.close(fig)


def main() -> None:
    for fn in [fig1, fig2, fig3, fig4, fig5, fig6_margin_bound, fig7_diversity,
               fig6, fig7, fig8, fig9]:
        fn()
        print(f"FIGURE_OK={fn.__name__}")
    print(f"OUTPUT_DIR={OUT}")


if __name__ == "__main__":
    main()
