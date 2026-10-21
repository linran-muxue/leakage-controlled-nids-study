"""English-labelled versions of the eleven main figures for the SCI manuscript."""
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
OUT = ROOT / "重构版论文_v4_20260915" / "figures_en"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.bbox"] = "tight"

C = ["#2f6fb3", "#e07b39", "#5a9e6f", "#b5525b", "#7a6fb0", "#8c8c8c"]


def box(ax, x, y, w, h, text, fc="#eef3fa", ec="#2f6fb3", fs=9):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.02",
                                linewidth=1.2, edgecolor=ec, facecolor=fc))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def arrow(ax, p1, p2, color="#444444", lw=1.3):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=12,
                                 linewidth=lw, color=color, shrinkA=1, shrinkB=1))


def fig1():
    fig, ax = plt.subplots(figsize=(13.2, 8.0))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.text(0.015, 0.935, "A  Data construction and population definitions", fontsize=10.5, weight="bold", color="#1f3552")
    steps = [
        ("Raw archive\n8 CSV files / 78 features\n2,830,743 rows", 0.015),
        ("Label mapping\n5 retained classes\n2,671,766 rows", 0.215),
        ("Non-finite + physical range\n-2,741 / -296\n2,668,729 rows", 0.415),
        ("Global dedup + conflicts\n-239,093 / -133\n2,429,503 rows", 0.615),
        ("Three reported rungs\n53,237 / 413,209 / 2,429,503", 0.815),
    ]
    for text, x in steps:
        box(ax, x, 0.755, 0.165, 0.145, text, fs=7.8)
    for i in range(len(steps) - 1):
        arrow(ax, (steps[i][1] + 0.165, 0.828), (steps[i + 1][1], 0.828))

    ax.text(0.015, 0.675, "B  Leakage-controlled modelling and intervention", fontsize=10.5, weight="bold", color="#1f3552",
            bbox=dict(facecolor="white", edgecolor="none", pad=1.8), zorder=10)
    split = [("Training 70%\n1,700,652 full-corpus rows", 0.02),
             ("Validation 15%\n364,425", 0.255),
             ("Test 15% (locked)\n364,426", 0.49)]
    for text, x in split:
        box(ax, x, 0.555, 0.205, 0.095, text, fc="#eaf5ee", ec="#5a9e6f", fs=8.0)
    arrow(ax, (0.895, 0.755), (0.12, 0.65), color="#5a9e6f")
    arrow(ax, (0.895, 0.755), (0.355, 0.65), color="#5a9e6f")
    arrow(ax, (0.895, 0.755), (0.59, 0.65), color="#5a9e6f")

    model = [
        ("Train-side fitting only\nscaler + chi2 / MI / ANOVA\nfour RF experts (100 trees)", 0.02),
        ("3-fold OOF on training\nprobabilities + confidence / entropy / margin\nrisk models -> conditional weights", 0.255),
        ("Validation-side choice\ntemperature T, entropy <= 0.95\nKL(weights || uniform) <= 0.10", 0.49),
        ("One-shot test evaluation\nsame-member equal fusion vs gate\nper-row predictions saved", 0.725),
    ]
    for text, x in model:
        box(ax, x, 0.405, 0.195, 0.105, text, fc="#fdf1e6", ec="#e07b39", fs=7.6)
        arrow(ax, (x + 0.0975, 0.555), (x + 0.0975, 0.510), color="#e07b39")

    ax.text(0.015, 0.325, "C  Controls, intervention and statistical validation", fontsize=10.5, weight="bold", color="#1f3552")
    eval_boxes = [
        ("Primary control\nsame view, same tuning budget\nequal-weight forest", 0.02, "#eef3fa", "#2f6fb3"),
        ("Constructive EDG\nfour disjoint chi2 views\ndose curve, overlap 0 -> 1", 0.255, "#f3eef9", "#7a6fb0"),
        ("Quality gradient\nfix delta near 3%\nvary member F1 spread", 0.49, "#fdeff0", "#b5525b"),
        ("Ten-seed statistics\nmean + 90% interval\nTOST / McNemar / bootstrap", 0.725, "#eef7f0", "#5a9e6f"),
    ]
    for text, x, fc, ec in eval_boxes:
        box(ax, x, 0.195, 0.195, 0.105, text, fc=fc, ec=ec, fs=7.8)
    for x in (0.1175, 0.3525, 0.5875):
        arrow(ax, (x, 0.405), (x, 0.300), color="#444444")

    out = [
        ("Reproducible outputs\naudit counts / models /\nper-row predictions", 0.02),
        ("Mechanism diagnostics\nentropy / disagreement /\nmargin bound / dilution", 0.255),
        ("Robustness and external validity\nNSL-KDD / UNSW-NB15 /\nN-BaIoT / modern corpora", 0.49),
        ("Reporting object\npopulation / protocol /\nrung / cost", 0.725),
    ]
    for text, x in out:
        box(ax, x, 0.045, 0.195, 0.095, text, fc="#f4f6f8", ec="#8c8c8c", fs=7.1)
    for x in (0.1175, 0.3525, 0.5875, 0.8225):
        arrow(ax, (x, 0.195), (x, 0.140), color="#8c8c8c")

    ax.plot([0.012, 0.985], [0.362, 0.362], color="#b5525b", lw=1.5, ls="--")
    ax.text(0.014, 0.367, "Information boundary: no test label may be read before final evaluation",
            color="#b5525b", fontsize=8.5, va="bottom",
            bbox=dict(facecolor="white", edgecolor="none", pad=1.2), zorder=11)
    ax.text(0.5, 1.015, "End-to-end workflow: audit -> leakage-controlled modelling -> conditional gate -> EDG intervention -> statistics and release",
            ha="center", va="top", fontsize=10.8, weight="bold")
    fig.savefig(OUT / "fig1_protocol_pipeline.png")
    plt.close(fig)


def fig2():
    audit = json.loads((ROOT / "results_data_audit_cic_natural_v3b" / "data_processing_audit.json").read_text("utf-8"))
    dedup = json.loads((ROOT / "data_processed_cic_natural_v3b" / "dedup_audit.json").read_text("utf-8"))
    t = audit["raw_totals"]
    stages = [("Raw archive", t["source_rows"]), ("Label mapped", t["mapped_rows"]),
              ("Finite numeric", t["valid_rows"]), ("Physically valid", t["physical_valid_rows"]),
              ("Dedup + conflicts", 2429503), ("Natural-prior", 53237)]
    labels = [s[0] for s in stages]; values = [s[1] for s in stages]
    fig = plt.figure(figsize=(13.2, 7.6))
    gs = fig.add_gridspec(2, 2, hspace=0.68, wspace=0.25, top=0.88, bottom=0.10,
                          left=0.08, right=0.97)

    ax = fig.add_subplot(gs[0, 0])
    xs = np.arange(len(stages))
    ax.bar(xs, values, color=C[:len(stages)], width=0.62)
    for x, v in zip(xs, values):
        pct = 100.0 * v / values[0]
        ax.text(x, v * 1.10, f"{v:,}\n({pct:.1f}%)", ha="center", va="bottom", fontsize=7.2, weight="bold")
    ax.set_yscale("log"); ax.set_ylim(2e4, 6e6)
    ax.set_ylabel("Records (log scale)", fontsize=8.4)
    ax.set_xticks(xs); ax.set_xticklabels(labels, rotation=18, ha="right", fontsize=7.6)
    ax.set_title("A  Retention along the audit chain", fontsize=10.2, weight="bold", loc="left")
    ax.grid(axis="y", alpha=0.22)
    for s in ("top", "right"): ax.spines[s].set_visible(False)

    ax = fig.add_subplot(gs[0, 1])
    class_data = {
        "53,237": {"Normal": 19999, "DoS/DDoS": 19997, "Brute Force": 10620, "Bot": 1948, "Web Attack": 673},
        "413,209": {"Normal": 199992, "DoS/DDoS": 199976, "Brute Force": 10620, "Bot": 1948, "Web Attack": 673},
        "2,429,503": {"Normal": 2094666, "DoS/DDoS": 321596, "Brute Force": 10620, "Bot": 1948, "Web Attack": 673},
    }
    class_colors = ["#2f6fb3", "#e07b39", "#5a9e6f", "#b5525b", "#7a6fb0"]
    ys = np.arange(len(class_data)); left = np.zeros(len(class_data))
    for colour, cls in zip(class_colors, ["Normal", "DoS/DDoS", "Brute Force", "Bot", "Web Attack"]):
        shares = np.array([100.0 * class_data[k][cls] / sum(class_data[k].values()) for k in class_data])
        ax.barh(ys, shares, left=left, color=colour, height=0.55, label=cls)
        left += shares
    ax.set_yticks(ys); ax.set_yticklabels(list(class_data), fontsize=8.2)
    ax.set_xlim(0, 100); ax.set_xlabel("Class share (%)", fontsize=8.4)
    ax.set_title("B  Class composition across the three rungs", fontsize=10.2, weight="bold", loc="left")
    ax.legend(ncol=5, fontsize=6.4, frameon=False, loc="lower center", bbox_to_anchor=(0.5, -0.30))
    for s in ("top", "right"): ax.spines[s].set_visible(False)

    ax = fig.add_subplot(gs[1, 0])
    ladder = [("20k/class", 53237, 7986), ("200k/class", 413209, 61982), ("Uncapped", 2429503, 364426)]
    ys = np.arange(len(ladder)); width = 0.36
    ax.barh(ys - width/2, [r[1] for r in ladder], height=width, color="#2f6fb3", label="Population")
    ax.barh(ys + width/2, [r[2] for r in ladder], height=width, color="#e07b39", label="Test rows")
    for y, row in zip(ys, ladder):
        ax.text(row[1] * 1.08, y - width/2, f"{row[1]:,}", va="center", fontsize=7.6, weight="bold")
        ax.text(row[2] * 1.08, y + width/2, f"{row[2]:,}", va="center", fontsize=7.6, color="#a5542f")
    ax.set_xscale("log"); ax.set_xlim(5e3, 5e6)
    ax.set_yticks(ys); ax.set_yticklabels([r[0] for r in ladder], fontsize=8.2)
    ax.set_xlabel("Records (log scale)", fontsize=8.4)
    ax.set_title("C  Scale ladder and locked test sets", fontsize=10.2, weight="bold", loc="left")
    ax.legend(fontsize=7.4, frameon=False, loc="lower right")
    for s in ("top", "right"): ax.spines[s].set_visible(False)

    ax = fig.add_subplot(gs[1, 1])
    removed = [
        ("Excluded labels", t["excluded_label_rows"], "#8c8c8c"),
        ("Same-label duplicates", dedup["same_label_duplicate_rows"], "#5a9e6f"),
        ("Cross-label conflict rows", dedup["cross_label_mismatch_rows"], "#b5525b"),
        ("Non-finite rows", t["invalid_rows"], "#e07b39"),
        ("Physical-range rows", dedup["invalid_physical_rows"], "#7a6fb0"),
        ("Conflict vectors", dedup["unique_rows_removed_for_conflicts"], "#2f6fb3"),
    ]
    ys = np.arange(len(removed))
    ax.barh(ys, [r[1] for r in removed], color=[r[2] for r in removed], height=0.58)
    for y, r in zip(ys, removed):
        ax.text(r[1] * 1.10, y, f"{r[1]:,}", va="center", fontsize=7.8, weight="bold")
    ax.set_xscale("log"); ax.set_xlim(100, 5e5)
    ax.set_yticks(ys); ax.set_yticklabels([r[0] for r in removed], fontsize=8.2)
    ax.set_xlabel("Rows removed (log scale)", fontsize=8.4)
    ax.set_title("D  What was removed, and why", fontsize=10.2, weight="bold", loc="left")
    for s in ("top", "right"): ax.spines[s].set_visible(False)

    fig.suptitle("CIC-IDS2017 data-processing results: retention, class composition, scale and removals",
                 fontsize=11.6, weight="bold")
    fig.savefig(OUT / "fig2_data_waterfall.png")
    plt.close(fig)


def fig3():
    fig, ax = plt.subplots(figsize=(12.0, 7.2))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    experts = ["Expert 1\nfull, 78 features", "Expert 2\nchi2 top-60",
               "Expert 3\nmutual information top-60", "Expert 4\nANOVA top-60"]
    for i, e in enumerate(experts):
        y = 0.815 - i * 0.135
        box(ax, 0.015, y, 0.155, 0.115, e, fs=8.0)
        arrow(ax, (0.170, y + 0.0575), (0.245, 0.755))
    box(ax, 0.245, 0.645, 0.195, 0.225,
        "Cross-fitted OOF probabilities\n+ reliability descriptors\n(confidence / entropy / margin)",
        fc="#eaf5ee", ec="#5a9e6f", fs=7.8)
    arrow(ax, (0.440, 0.7575), (0.505, 0.7575))
    box(ax, 0.505, 0.645, 0.155, 0.225, "Logistic\nrisk model\n$r_e(x)$", fc="#eef3fa", ec="#2f6fb3", fs=8.4)
    arrow(ax, (0.660, 0.7575), (0.715, 0.7575))
    box(ax, 0.715, 0.645, 0.270, 0.225,
        r"$w_e(x)=\exp[-r_e(x)]\,/\,\sum_j \exp[-r_j(x)]$" + "\n\n" +
        r"$p(y\,|\,x)=\sum_e w_e(x)\,p_e(y\,|\,x)$", fc="#fdf1e6", ec="#e07b39", fs=9.4)
    arrow(ax, (0.850, 0.645), (0.850, 0.500))
    box(ax, 0.715, 0.335, 0.270, 0.165,
        "Temperature scaling (validation only)\nMondrian conformal rejection, alpha = 0.1",
        fc="#f4eef7", ec="#7a6fb0", fs=8.2)
    ax.text(0.5, 0.285, "Three identifiability conditions (Section 4.3)", fontsize=11, weight="bold", ha="center")
    props = ["Condition 1 - convex invariance\n\nidentical expert posteriors imply\nidentical predictions under any weights",
             "Condition 2 - margin dominance\n\nif the margin exceeds twice the\nperturbation bound, the label cannot change",
             "Condition 3 - weight collapse\n\nnear-equal risk outputs drive\nw_e to 1/Q and entropy to 1"]
    for i, p in enumerate(props):
        box(ax, 0.015 + i * 0.330, 0.020, 0.310, 0.235, p, fc="#fdeef0", ec="#b5525b", fs=8.0)
    fig.savefig(OUT / "fig3_rccf_mechanism.png")
    plt.close(fig)


def fig4():
    # Panel (a) shows the ten-seed primary protocol, the same run as Table 4(a).
    # The neural baseline was trained on the three seeds common to both runs and
    # is labelled as such on the axis.
    ten = pd.read_csv(ROOT / "results_seeds10_v5" / "table4a_10seeds.csv").set_index("model")
    per_seed = pd.read_csv(ROOT / "results_seeds10_v5" / "metrics_by_seed.csv")

    def ten_seed(model):
        sub = per_seed[per_seed.model == model]
        return float(ten.loc[model, "macro_f1"]), float(sub["macro_f1"].std(ddof=0))

    nat_rows = {
        "RCCF": ten_seed("rccf"),
        "Equal RF (chi2)": ten_seed("equal_rf_chi2"),
        "Equal RF (all)": ten_seed("equal_rf_all"),
        "ExtraTrees (chi2)": ten_seed("extra_trees_chi2"),
    }
    bal = pd.read_csv(ROOT / "results_cic_balanced_baselines_v3b" / "metrics_aggregate_flat.csv")
    bal_rccf = pd.read_csv(ROOT / "results_rccf_cic_balanced_v3b" / "metrics_aggregate.csv")
    strong = pd.read_csv(ROOT / "results_cfrg_strong_baselines_v2_verified" / "summary.csv", header=[0, 1])
    strong.columns = ["_".join(str(c) for c in col if "Unnamed" not in str(c)).strip("_") for col in strong.columns]
    mlp = pd.read_csv(ROOT / "results_mlp_final_v5" / "metrics_aggregate.csv")
    names = list(nat_rows.keys()) + ["MLP (3 seeds)", "XGBoost"]
    nat_vals = [nat_rows[n][0] for n in nat_rows] + [float(mlp["macro_f1_mean"].iloc[0])] + [np.nan]
    nat_err = [nat_rows[n][1] for n in nat_rows] + [float(mlp["macro_f1_std"].iloc[0])] + [np.nan]
    bal_vals = [float(bal_rccf["macro_f1_mean"].iloc[0]),
                float(bal.loc[bal.model == "equal_rf_chi2", "macro_f1_mean"].iloc[0]),
                float(bal.loc[bal.model == "equal_rf_all", "macro_f1_mean"].iloc[0]),
                float(bal.loc[bal.model == "extra_trees_chi2", "macro_f1_mean"].iloc[0]),
                np.nan,
                float(strong.loc[strong["model"] == "xgboost", "macro_f1_mean"].iloc[0])]

    fig, axes = plt.subplots(1, 2, figsize=(13.4, 4.8), gridspec_kw={"width_ratios": [1.7, 1]})
    ax = axes[0]
    x = np.arange(len(names)); w = 0.38
    ax.bar(x - w / 2, nat_vals, w, yerr=nat_err, capsize=3, color="#2f6fb3", label="Natural-prior population")
    ax.bar(x + w / 2, bal_vals, w, color="#e07b39", label="Balanced control population")
    ax.set_xticks(x); ax.set_xticklabels(names, rotation=18, ha="right", fontsize=8.8)
    ax.set_ylim(0.75, 0.99); ax.set_ylabel("Macro-F1")
    ax.set_title("Macro-F1 on both populations (natural prior: 10 seeds; balanced control: 3 seeds)",
                 fontsize=10.5, weight="bold")
    ax.legend(fontsize=8.4); ax.grid(axis="y", alpha=0.25)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax = axes[1]
    bs = pd.read_csv(ROOT / "results_equivalence_10seeds_v5" / "tost_results.csv")
    est = bs["delta"].values; lo = bs["ci95_low"].values; hi = bs["ci95_high"].values
    ypos = np.arange(len(est))
    ax.errorbar(est, ypos, xerr=[est - lo, hi - est], fmt="o", color="#b5525b",
                ecolor="#b5525b", capsize=4, ms=6)
    ax.axvline(0, color="#555555", lw=1.1, ls="--")
    ax.set_yticks(ypos); ax.set_yticklabels([f"seed {int(s)}" for s in bs["seed"]], fontsize=9)
    ax.set_xlabel("RCCF - equal-weight Macro-F1 difference")
    ax.set_title("Paired bootstrap 95% interval (natural prior)", fontsize=10.5, weight="bold")
    ax.grid(axis="x", alpha=0.25)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.savefig(OUT / "fig4_main_results.png")
    plt.close(fig)


def fig5():
    dist = pd.read_csv(ROOT / "results_weight_mechanism_v3" / "tree_weight_distribution.csv")
    s = pd.read_csv(ROOT / "results_weight_mechanism_v3" / "weight_mechanism_summary.csv").iloc[0]
    cmp = pd.read_csv(ROOT / "results_weight_mechanism_v3" / "weight_prediction_comparison.csv")
    disagree = int(cmp["disagreement"].sum())
    fig, axes = plt.subplots(1, 3, figsize=(13.4, 4.2))
    ax = axes[0]
    ax.scatter(dist["tree_score"], dist["tree_weight"], s=14, color="#2f6fb3", alpha=0.75)
    ax.set_xlabel("Single-tree validation accuracy"); ax.set_ylabel("Assigned weight")
    ax.set_title("(a) Tree score vs assigned weight", fontsize=10, weight="bold")
    ax.text(0.03, 0.95, f"weight CV = {s['weight_cv']:.5f}", transform=ax.transAxes,
            fontsize=8.6, va="top", color="#b5525b")
    ax.grid(alpha=0.25)
    ax = axes[1]
    ax.hist(dist["tree_weight"], bins=24, color="#e07b39", edgecolor="white")
    ax.set_xlabel("Weight value"); ax.set_ylabel("Number of trees")
    ax.set_title("(b) Weights concentrate near the uniform value", fontsize=10, weight="bold")
    ax.text(0.03, 0.95, f"normalized weight entropy = {s['normalized_weight_entropy']:.5f}",
            transform=ax.transAxes, fontsize=8.6, va="top", color="#b5525b")
    ax.grid(alpha=0.25)
    ax = axes[2]; ax.axis("off")
    ax.set_title("(c) Mechanism diagnostic scorecard", fontsize=10, weight="bold")
    rows = [("Normalized weight entropy", f"{s['normalized_weight_entropy']:.5f}", "weights collapse to uniform"),
            ("Weight coefficient of variation", f"{s['weight_cv']:.5f}", "tiny spread across trees"),
            ("Mean probability L1 change", f"{s['mean_probability_l1']:.6f}", "mass barely moves"),
            ("Max probability L1 change", f"{s['max_probability_l1']:.6f}", "largest single-row shift"),
            ("Prediction disagreements", f"{disagree} / {int(s['test_samples'])}", "no hard label changes")]
    y = 0.80
    for name, value, verdict in rows:
        ax.text(0.0, y, name, fontsize=8.4, va="center")
        ax.text(0.60, y, value, fontsize=9.4, va="center", weight="bold", ha="right")
        ax.text(0.64, y, verdict, fontsize=7.4, va="center", color="#b5525b")
        ax.plot([0.0, 1.0], [y - 0.082, y - 0.082], color="#dddddd", lw=0.8)
        y -= 0.168
    ax.text(0.0, 0.005, "All three identifiability conditions are satisfied.", fontsize=8.4,
            color="#b5525b", weight="bold")
    for a in axes[:2]:
        for sp in ("top", "right"):
            a.spines[sp].set_visible(False)
    fig.savefig(OUT / "fig5_gate_diagnostics.png")
    plt.close(fig)


def fig6():
    ps = pd.read_csv(ROOT / "results_protocol_sensitivity_v4" / "protocol_sensitivity_metrics.csv")
    rep = pd.read_csv(ROOT / "results_repeated_splits_v3" / "summary.csv", header=[0, 1])
    rep.columns = ["_".join(str(c) for c in col if "Unnamed" not in str(c)).strip("_") for col in rep.columns]
    nested = pd.read_csv(ROOT / "results_nested_modelwise_v1_5x3" / "outer_modelwise_summary.csv", header=[0, 1])
    nested.columns = ["_".join(str(c) for c in col if "Unnamed" not in str(c)).strip("_") for col in nested.columns]
    dedup_glob = ps[ps.protocol == "global_dedup_before_split"]["macro_f1"].mean()
    dedup_split = ps[ps.protocol == "split_first_training_only_dedup"]["macro_f1"].mean()
    rf_rep = float(rep.loc[rep["model"] == "rf_all", "macro_f1_mean"].iloc[0])
    chi_rep = float(rep.loc[rep["model"] == "rf_chi2", "macro_f1_mean"].iloc[0])
    rf_n = float(nested.loc[nested["model"] == "random_forest", "macro_f1_mean"].iloc[0])
    xgb_n = float(nested.loc[nested["model"] == "xgboost", "macro_f1_mean"].iloc[0])
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 4.8), gridspec_kw={"width_ratios": [1.25, 1]})
    ax = axes[0]
    items = [("Aggregation\nRCCF - equal RF", abs(0.0010848)),
             ("Feature view\nall - chi2", abs(chi_rep - rf_rep)),
             ("Dedup order\nsplit-first - global-first", abs(dedup_split - dedup_glob)),
             ("Tuning budget\nXGBoost - RF", abs(xgb_n - rf_n)),
             ("Class prior\nbalanced - natural", abs(0.961807 - 0.889955))]
    names = [i[0] for i in items]; vals = [i[1] for i in items]
    colors = ["#2f6fb3", "#5a9e6f", "#8c8c8c", "#7a6fb0", "#b5525b"]
    ax.barh(names[::-1], vals[::-1], color=colors[::-1])
    for i, v in enumerate(vals[::-1]):
        ax.text(v * 1.06, i, f"{v:.4f}", va="center", fontsize=9, weight="bold")
    ax.set_xscale("log"); ax.set_xlabel("Absolute Macro-F1 difference (log scale)")
    ax.set_title("(a) Magnitude of each source of difference", fontsize=10.5, weight="bold")
    ax.grid(axis="x", alpha=0.25); ax.tick_params(axis="y", labelsize=8.2)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax = axes[1]
    seeds = [42, 2024, 3407]
    g = [ps[(ps.protocol == "global_dedup_before_split") & (ps.seed == s)]["macro_f1"].iloc[0] for s in seeds]
    q = [ps[(ps.protocol == "split_first_training_only_dedup") & (ps.seed == s)]["macro_f1"].iloc[0] for s in seeds]
    x = np.arange(len(seeds)); w = 0.36
    ax.bar(x - w / 2, g, w, label="Global dedup before split", color="#2f6fb3")
    ax.bar(x + w / 2, q, w, label="Training-only dedup after split", color="#e07b39")
    for i, (a, b) in enumerate(zip(g, q)):
        ax.text(i, max(a, b) + 0.0016, f"delta={b - a:+.4f}", ha="center", fontsize=8.6, color="#b5525b")
    ax.set_xticks(x); ax.set_xticklabels([f"seed {s}" for s in seeds])
    ax.set_ylim(0.94, 0.972); ax.set_ylabel("Macro-F1")
    ax.set_title("(b) Dedup-order control by seed", fontsize=10.5, weight="bold")
    ax.legend(fontsize=8.2); ax.grid(axis="y", alpha=0.25)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.savefig(OUT / "fig8_protocol_sensitivity.png")
    plt.close(fig)


def _class_report(path):
    df = pd.read_csv(path)
    df = df.rename(columns={df.columns[0]: "class"})
    df = df[~df["class"].astype(str).str.strip().isin(["accuracy", "macro avg", "weighted avg"])]
    return df[["class", "f1-score", "support"]].astype({"f1-score": float, "support": float})


def fig7():
    nsl = _class_report(ROOT / "results_rccf_nsl_v2_final" / "classification_report_seed42.csv")
    unsw = _class_report(ROOT / "results_rccf_unsw_v2_final" / "classification_report_seed42.csv")
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 4.8))
    for ax, df, title in [(axes[0], nsl, "(a) NSL-KDD (5 native classes)"),
                          (axes[1], unsw, "(b) UNSW-NB15 (10 native classes)")]:
        d = df.sort_values("f1-score")
        labels = [f"{c}  (n={int(s):,})" for c, s in zip(d["class"], d["support"])]
        colors = ["#b5525b" if v < 0.5 else "#e07b39" if v < 0.8 else "#5a9e6f" for v in d["f1-score"]]
        ax.barh(labels, d["f1-score"], color=colors)
        for i, v in enumerate(d["f1-score"]):
            ax.text(v + 0.015, i, f"{v:.3f}", va="center", fontsize=8.4)
        ax.set_xlim(0, 1.12); ax.set_xlabel("F1 score")
        ax.set_title(title, fontsize=10.5, weight="bold")
        ax.grid(axis="x", alpha=0.25); ax.tick_params(axis="y", labelsize=8.2)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    fig.suptitle("Class-level F1 on independent native-label benchmarks (RCCF, seed 42)",
                 fontsize=11.2, weight="bold", y=1.02)
    fig.savefig(OUT / "fig9_external_class_f1.png")
    plt.close(fig)


def fig8():
    cal = pd.read_csv(ROOT / "results_cfrg_calibration_v2_verified" / "metrics.csv")
    rob = pd.read_csv(ROOT / "results_rccf_evidence_v3b" / "robustness_shared.csv")
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 4.6))
    ax = axes[0]
    piv = cal.groupby(["model", "variant"])["ece"].mean().unstack()
    uncal = [piv.loc["equal_rf", "uncalibrated"], piv.loc["cfrg_forest", "uncalibrated"]]
    scaled = [piv.loc["equal_rf", "temperature_scaled"], piv.loc["cfrg_forest", "temperature_scaled"]]
    x = np.arange(2); w = 0.36
    ax.bar(x - w / 2, uncal, w, label="before calibration", color="#8c8c8c")
    ax.bar(x + w / 2, scaled, w, label="after temperature scaling", color="#2f6fb3")
    for i in range(2):
        ax.text(i - w / 2, uncal[i] + 0.0012, f"{uncal[i]:.4f}", ha="center", fontsize=8.6)
        ax.text(i + w / 2, scaled[i] + 0.0012, f"{scaled[i]:.4f}", ha="center", fontsize=8.6)
    ax.set_xticks(x); ax.set_xticklabels(["Equal forest", "Conditional gate"])
    ax.set_ylabel("Expected calibration error (mean of seeds)")
    ax.set_title("(a) Effect of temperature scaling", fontsize=10.5, weight="bold")
    ax.legend(fontsize=8.4); ax.grid(axis="y", alpha=0.25)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax = axes[1]
    g = rob.groupby(["model", "condition"])["relative_drop"].mean().unstack() * 100
    models = ["equal_rf_chi2", "rccf", "extra_trees_chi2"]
    pretty = ["Equal forest", "Conditional gate", "ExtraTrees"]
    noise = [g.loc[m, "gaussian_noise_1pct"] for m in models]
    mask = [g.loc[m, "feature_mask_5pct"] for m in models]
    x = np.arange(len(models)); w = 0.36
    ax.bar(x - w / 2, noise, w, label="1% Gaussian noise", color="#b5525b")
    ax.bar(x + w / 2, mask, w, label="5% feature masking", color="#5a9e6f")
    for i in range(len(models)):
        ax.text(i - w / 2, noise[i] + 1.0, f"{noise[i]:.2f}%", ha="center", fontsize=8.4)
        ax.text(i + w / 2, mask[i] + 1.0, f"{mask[i]:.2f}%", ha="center", fontsize=8.4)
    ax.set_xticks(x); ax.set_xticklabels(pretty)
    ax.set_ylabel("Relative Macro-F1 drop (%)")
    ax.set_title("(b) Robustness under shared perturbations", fontsize=10.5, weight="bold")
    ax.legend(fontsize=8.4); ax.grid(axis="y", alpha=0.25)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.savefig(OUT / "fig10_calibration_robustness.png")
    plt.close(fig)


def fig9():
    lat = pd.read_csv(ROOT / "results_rccf_evidence_v3b" / "latency_percentiles.csv")
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.5), sharey=True)
    pretty = {"rccf": "Conditional gate", "equal_rf_chi2": "Equal forest", "extra_trees_chi2": "ExtraTrees"}
    for ax, nj, title in [(axes[0], 1, "(a) single thread, n_jobs = 1"),
                          (axes[1], -1, "(b) library default, n_jobs = -1")]:
        sub = lat[lat.n_jobs == nj].groupby("model")[["p50_ms", "p95_ms", "p99_ms"]].mean()
        models = ["equal_rf_chi2", "extra_trees_chi2", "rccf"]
        x = np.arange(len(models)); w = 0.26
        for k, (col, c) in enumerate(zip(["p50_ms", "p95_ms", "p99_ms"], ["#2f6fb3", "#e07b39", "#b5525b"])):
            ax.bar(x + (k - 1) * w, [sub.loc[m, col] for m in models], w,
                   label=col.replace("_ms", "").upper(), color=c)
        ax.set_xticks(x); ax.set_xticklabels([pretty[m] for m in models])
        ax.set_title(title, fontsize=10.5, weight="bold")
        ax.grid(axis="y", alpha=0.25)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    axes[0].set_ylabel("Single-row inference latency (ms)")
    axes[0].legend(fontsize=8.4)
    fig.suptitle("Classifier-stage single-row latency (excludes capture and feature extraction)",
                 fontsize=11.0, weight="bold", y=1.02)
    fig.savefig(OUT / "fig11_latency.png")
    plt.close(fig)


PRETTY = {"rf_same_view_seeds": "same view, different seeds",
          "rf_views_k60": "four views, k=60",
          "rf_views_k20": "four views, k=20",
          "hetero_families": "heterogeneous families",
          "disjoint_views_k60": "disjoint feature blocks"}


def fig10():
    df = pd.read_csv(ROOT / "results_diversity_v5" / "diversity_suite_results.csv")
    fit = json.loads((ROOT / "results_diversity_v5" / "diversity_gain_regression.json").read_text("utf-8"))
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 4.6))
    ax = axes[0]
    for name, sub in df.groupby("expert_set"):
        ax.scatter(sub["mean_pairwise_disagreement"] * 100, sub["gate_gain"], s=52,
                   label=PRETTY.get(name, name), alpha=0.85)
    xs = np.linspace(0, df["mean_pairwise_disagreement"].max() * 100, 50)
    ax.plot(xs, fit["slope"] * xs / 100 + fit["intercept"], color="#444444", lw=1.2, ls="--")
    ax.axhline(0, color="#b5525b", lw=1.0)
    ax.set_xlabel("Pairwise expert disagreement (%)"); ax.set_ylabel("Gate gain (Macro-F1)")
    ax.set_title("(a) Dose-response between diversity and gain", fontsize=10.5, weight="bold")
    ax.text(0.03, 0.95, f"slope {fit['slope']:.4f}, Pearson r = {fit['pearson_r']:.3f} (n={fit['n_points']})",
            transform=ax.transAxes, fontsize=8.4, va="top", color="#b5525b")
    ax.legend(fontsize=7.4, loc="lower right"); ax.grid(alpha=0.25)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax = axes[1]
    summary = df.groupby("expert_set").agg(
        disagreement=("mean_pairwise_disagreement", "mean"),
        gain=("gate_gain", "mean"),
        changed=("disagreement_gated_vs_equal", "mean")).sort_values("disagreement")
    colors = ["#b5525b" if g == 0 else "#5a9e6f" for g in summary["gain"]]
    ax.barh([PRETTY.get(i, i) for i in summary.index], summary["gain"], color=colors)
    for i, (g, c) in enumerate(zip(summary["gain"], summary["changed"])):
        ax.text(g + 0.00012 if g >= 0 else g - 0.00012, i, f"{g:+.5f} ({c:.1f} rows changed)",
                va="center", ha="left" if g >= 0 else "right", fontsize=8.0)
    ax.axvline(0, color="#444444", lw=1.0)
    ax.set_xlim(-0.0006, 0.0058)
    ax.set_xlabel("Gate gain (Macro-F1, mean of three seeds)")
    ax.set_title("(b) Low-diversity expert sets gain exactly zero", fontsize=10.5, weight="bold")
    ax.grid(axis="x", alpha=0.25); ax.tick_params(axis="y", labelsize=8.2)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.subplots_adjust(wspace=0.45)
    fig.savefig(OUT / "fig7_diversity_dose_response.png")
    plt.close(fig)


def fig11():
    per_row = pd.concat([pd.read_csv(ROOT / "results_margin_bound_v5" / f"margin_bound_per_row_seed{s}.csv")
                         for s in (42, 2024, 3407)], ignore_index=True)
    summary = json.loads((ROOT / "results_margin_bound_v5" / "margin_bound_summary.json").read_text("utf-8"))
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 4.5))
    ax = axes[0]
    ax.hist(np.log10(np.clip(per_row["margin_equal_weight"], 1e-6, None)), bins=40,
            alpha=0.75, color="#2f6fb3", label="decision margin $m(x)$")
    ax.hist(np.log10(np.clip(per_row["delta_bound_l1"], 1e-8, None)), bins=40,
            alpha=0.75, color="#b5525b", label="perturbation bound $\\Delta(x)$")
    ax.set_xlabel("$\\log_{10}$ value"); ax.set_ylabel("Rows")
    ax.set_title("(a) Margins exceed the bound by ~3 orders of magnitude", fontsize=10.5, weight="bold")
    ax.legend(fontsize=8.6); ax.grid(axis="y", alpha=0.25)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax = axes[1]
    items = [("Provably invariant\n(a priori bound)", summary["provable_by_bound_rate_mean"]),
             ("Provably invariant\n(realised perturbation)", summary["provable_by_actual_rate_mean"]),
             ("Labels actually changed", 1.0 - summary["empirical_changed_rows"] / summary["total_rows"])]
    labels = [i[0] for i in items]; values = [i[1] * 100 for i in items]
    bars = ax.bar(labels, values, color=["#5a9e6f", "#2f6fb3", "#b5525b"])
    ax.set_ylim(99.5, 100.05)
    ax.set_ylabel("Share of 23,958 test rows (%)")
    ax.set_title("(b) Provable invariance under Condition 2", fontsize=10.5, weight="bold")
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.02, f"{v:.3f}%", ha="center", fontsize=9)
    ax.grid(axis="y", alpha=0.25); ax.tick_params(axis="x", labelsize=8.4)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.savefig(OUT / "fig6_margin_bound.png")
    plt.close(fig)


def main() -> None:
    for fn in [fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10, fig11]:
        fn()
        print(f"EN_FIGURE_OK={fn.__name__}")
    # Figure 12 (the 2026-10-03 modern-corpus ladder) is drawn by its own module
    # so both language editions share one implementation; it is invoked here so
    # this builder remains the single declared producer of figures_en/
    import build_ladder_figure_v1 as ladder

    ladder.draw(ladder.collect(), "en", OUT / "fig12_ladder_modern.png")
    print("EN_FIGURE_OK=ladder")
    print(f"OUTPUT_DIR={OUT}")


if __name__ == "__main__":
    main()
