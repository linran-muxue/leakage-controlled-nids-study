"""Figure 10 (diversity dose-response) and Figure 11 (margin vs perturbation bound)."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "重构版论文_v4_20260915" / "figures"
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

PRETTY = {
    "rf_same_view_seeds": "同一视图、不同种子",
    "rf_views_k60": "四视图 k=60",
    "rf_views_k20": "四视图 k=20",
    "hetero_families": "异构算法族",
    "disjoint_views_k60": "互斥特征块",
}


def figure10() -> None:
    df = pd.read_csv(ROOT / "results_diversity_v5" / "diversity_suite_results.csv")
    fit = json.loads((ROOT / "results_diversity_v5" / "diversity_gain_regression.json").read_text("utf-8"))
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 4.6))
    ax = axes[0]
    for name, sub in df.groupby("expert_set"):
        ax.scatter(sub["mean_pairwise_disagreement"] * 100, sub["gate_gain"],
                   s=52, label=PRETTY.get(name, name), alpha=0.85)
    xs = np.linspace(0, df["mean_pairwise_disagreement"].max() * 100, 50)
    ax.plot(xs, fit["slope"] * xs / 100 + fit["intercept"], color="#444444", lw=1.2, ls="--")
    ax.axhline(0, color="#b5525b", lw=1.0)
    ax.set_xlabel("专家间预测分歧率（%）")
    ax.set_ylabel("门控增益（Macro-F1）")
    ax.set_title("(a) 分歧率与增益的剂量—反应", fontsize=10.5, weight="bold")
    ax.text(0.03, 0.95, f"斜率 {fit['slope']:.4f}，Pearson r = {fit['pearson_r']:.3f}（n={fit['n_points']}）",
            transform=ax.transAxes, fontsize=8.6, va="top", color="#b5525b")
    ax.legend(fontsize=7.6, loc="lower right")
    ax.grid(alpha=0.25)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    ax = axes[1]
    summary = df.groupby("expert_set").agg(
        disagreement=("mean_pairwise_disagreement", "mean"),
        entropy=("mean_weight_entropy", "mean"),
        gain=("gate_gain", "mean"),
        changed=("disagreement_gated_vs_equal", "mean"),
    ).sort_values("disagreement")
    labels = [PRETTY.get(i, i) for i in summary.index]
    colors = ["#b5525b" if g == 0 else "#5a9e6f" for g in summary["gain"]]
    ax.barh(labels, summary["gain"], color=colors)
    for i, (g, c) in enumerate(zip(summary["gain"], summary["changed"])):
        ax.text(g + 0.00012 if g >= 0 else g - 0.00012, i,
                f"{g:+.5f}（改判 {c:.1f} 条）", va="center",
                ha="left" if g >= 0 else "right", fontsize=8.2)
    ax.axvline(0, color="#444444", lw=1.0)
    ax.set_xlabel("门控增益（Macro-F1，三种子均值）")
    ax.set_xlim(-0.0006, 0.0056)
    ax.set_title("(b) 低分歧专家集合增益恰为零", fontsize=10.5, weight="bold")
    ax.grid(axis="x", alpha=0.25)
    ax.tick_params(axis="y", labelsize=8.4)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.subplots_adjust(wspace=0.45)
    fig.savefig(OUT / "fig10_diversity_dose_response.png")
    plt.close(fig)


def figure11() -> None:
    per_row = pd.concat([
        pd.read_csv(ROOT / "results_margin_bound_v5" / f"margin_bound_per_row_seed{s}.csv")
        for s in (42, 2024, 3407)
    ], ignore_index=True)
    summary = json.loads((ROOT / "results_margin_bound_v5" / "margin_bound_summary.json").read_text("utf-8"))
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.5))
    ax = axes[0]
    ax.hist(np.log10(np.clip(per_row["margin_equal_weight"], 1e-6, None)), bins=40,
            alpha=0.75, color="#2f6fb3", label="决策边距 $m(x)$")
    ax.hist(np.log10(np.clip(per_row["delta_bound_l1"], 1e-8, None)), bins=40,
            alpha=0.75, color="#b5525b", label="扰动上界 $\\Delta(x)$")
    ax.set_xlabel("$\\log_{10}$ 数值")
    ax.set_ylabel("样本数")
    ax.set_title("(a) 边距比扰动上界大约三个数量级", fontsize=10.5, weight="bold")
    ax.legend(fontsize=8.6)
    ax.grid(axis="y", alpha=0.25)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    ax = axes[1]
    items = [
        ("可证明不变\n（按上界）", summary["provable_by_bound_rate_mean"]),
        ("可证明不变\n（按实际扰动）", summary["provable_by_actual_rate_mean"]),
        ("实际改判", 1.0 - summary["empirical_changed_rows"] / summary["total_rows"]),
    ]
    labels = [i[0] for i in items]
    values = [i[1] * 100 for i in items]
    bars = ax.bar(labels, values, color=["#5a9e6f", "#2f6fb3", "#b5525b"])
    ax.set_ylim(99.5, 100.05)
    ax.set_ylabel("占 23 958 条测试样本的比例（%）")
    ax.set_title("(b) 命题 2 的可证明不变比例", fontsize=10.5, weight="bold")
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.02, f"{v:.3f}%", ha="center", fontsize=9)
    ax.grid(axis="y", alpha=0.25)
    ax.tick_params(axis="x", labelsize=8.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.savefig(OUT / "fig11_margin_bound.png")
    plt.close(fig)


def main() -> None:
    figure10()
    figure11()
    print("FIG10_OK")
    print("FIG11_OK")


if __name__ == "__main__":
    main()
