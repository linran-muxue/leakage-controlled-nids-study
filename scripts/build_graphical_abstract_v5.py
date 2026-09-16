"""Graphical abstract for the ten-seed framing (replaces the legacy RCCF figures)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "重构版论文_v4_20260915"
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False


def box(ax, x, y, w, h, text, fc="#eef3fa", ec="#2f6fb3", fs=7.6):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.02",
                                linewidth=1.2, edgecolor=ec, facecolor=fc))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def main() -> None:
    power = pd.read_csv(ROOT / "results_seeds10_v5" / "power_analysis.csv")
    chi2 = power[power.comparison == "rccf_minus_equal_rf_chi2"].iloc[0]
    mb = json.loads((ROOT / "results_margin_bound_v5" / "margin_bound_summary.json").read_text("utf-8"))

    fig = plt.figure(figsize=(11.0, 7.6))
    gs = fig.add_gridspec(2, 2, hspace=0.34, wspace=0.24, top=0.86, bottom=0.09,
                          left=0.07, right=0.97)
    fig.suptitle("Protocol sensitivity dominates model choice in flow-based NIDS",
                 fontsize=13.5, weight="bold")

    # ---- A: protocol -------------------------------------------------------
    ax = fig.add_subplot(gs[0, 0]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.set_title("A  Leakage-controlled protocol", fontsize=10.5, weight="bold", loc="left")
    steps = ["2,830,743\nraw flows", "audit and\ndeduplicate", "70/15/15\nsplit",
             "fit on\ntraining only", "lock test\nand evaluate"]
    for i, s in enumerate(steps):
        x = 0.005 + i * 0.198
        box(ax, x, 0.45, 0.176, 0.30, s, fs=7.0)
        if i < 4:
            ax.add_patch(FancyArrowPatch((x + 0.176, 0.60), (x + 0.198, 0.60),
                                         arrowstyle="-|>", mutation_scale=9, color="#444444"))
    ax.text(0.5, 0.20, "no test label touches fitting,\nselection or calibration",
            ha="center", va="center", fontsize=8.2, color="#b5525b")

    # ---- B: main result ----------------------------------------------------
    ax = fig.add_subplot(gs[0, 1])
    ax.set_title("B  Ten seeds: no gain over equal voting", fontsize=10.5, weight="bold", loc="left")
    mean, lo, hi = float(chi2["mean_difference"]), float(chi2["ci90_low"]), float(chi2["ci90_high"])
    ax.axvspan(-0.005, 0.005, color="#eaf5ee", zorder=0)
    ax.axvline(0, color="#444444", lw=1.0, ls="--")
    ax.errorbar([mean], [0.0], xerr=[[mean - lo], [hi - mean]], fmt="o",
                color="#b5525b", capsize=5, ms=8, zorder=3)
    ax.set_ylim(-0.6, 0.6)
    ax.set_yticks([])
    ax.set_xlim(-0.0075, 0.0075)
    ax.set_xlabel("RCCF - equal-weight forest (Macro-F1)", fontsize=8.6)
    ax.text(0.5, 0.88, "equivalence margin +/-0.005", transform=ax.transAxes,
            ha="center", fontsize=8.0, color="#3d7a52")
    ax.text(0.5, 0.12, f"mean {mean:+.5f}; five seeds up, five down",
            transform=ax.transAxes, ha="center", fontsize=8.2, color="#b5525b")
    ax.tick_params(axis="x", labelsize=8)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)

    # ---- C: mechanism ------------------------------------------------------
    ax = fig.add_subplot(gs[1, 0])
    ax.set_title("C  Why the gate cannot act", fontsize=10.5, weight="bold", loc="left")
    labels = ["normalised\nweight entropy", "rows provably\ninvariant", "labels actually\nchanged"]
    values = [99.998, mb["provable_by_bound_rate_mean"] * 100, 0.0]
    bars = ax.bar(labels, values, color=["#2f6fb3", "#5a9e6f", "#b5525b"], width=0.55)
    ax.set_ylim(0, 138)
    ax.set_ylabel("percent", fontsize=8.4)
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, v + 3,
                f"{v:.2f}%" if v > 1 else "0 rows", ha="center", fontsize=8.2)
    ax.text(0.5, 0.925, "weights collapse to uniform; margins exceed\nthe perturbation bound by about 3,500x",
            transform=ax.transAxes, ha="center", va="top", fontsize=7.6, color="#444444")
    ax.tick_params(axis="x", labelsize=7.8)
    ax.grid(axis="y", alpha=0.2)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    # ---- D: protocol vs model ---------------------------------------------
    ax = fig.add_subplot(gs[1, 1])
    ax.set_title("D  Protocol effects exceed aggregation-rule differences",
                 fontsize=10.0, weight="bold", loc="left")
    items = [("class prior", 0.0725, "#b5525b"), ("tuning budget", 0.0078, "#7a6fb0"),
             ("feature view", 0.0021, "#5a9e6f"), ("aggregation", 0.0005, "#2f6fb3")]
    ax.barh([i[0] for i in items], [i[1] for i in items], color=[i[2] for i in items], height=0.6)
    for i, (_, v, _) in enumerate(items):
        ax.text(v * 1.12, i, f"{v:.4f}", va="center", fontsize=8.4, weight="bold")
    ax.set_xscale("log")
    ax.set_xlim(2e-4, 0.4)
    ax.set_xlabel("absolute Macro-F1 difference (log scale)", fontsize=8.6)
    ax.tick_params(axis="y", labelsize=8.4)
    ax.grid(axis="x", alpha=0.2)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    out = OUT / "Graphical_Abstract_v4.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"GRAPHICAL_ABSTRACT={out}")


if __name__ == "__main__":
    main()
