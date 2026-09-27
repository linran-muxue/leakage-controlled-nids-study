"""Generate publication figures from the canonical RCCF evidence package."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "results_rccf_evidence_v3b"
CIC = ROOT / "results_rccf_cic_natural_v3b"
OUT = ROOT / "results_publication_final" / "figures"


def expected_figure_names():
    return [
        "fig_rccf_model_performance.png",
        "fig_rccf_calibration.png",
        "fig_rccf_robustness.png",
        "fig_rccf_latency_percentiles.png",
        "fig_rccf_file_label_coverage.png",
        "fig_rccf_confusion_matrix.png",
    ]


def _save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=220, bbox_inches="tight")
    plt.close(fig)


def _performance():
    df = pd.read_csv(EVIDENCE / "model_metrics.csv")
    summary = df.groupby("model", sort=False).macro_f1.agg(["mean", "std"]).reset_index()
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.bar(summary.model, summary["mean"], yerr=summary["std"].fillna(0), capsize=4, color=["#2f6f9f", "#7f8c8d", "#bd6b35"])
    ax.set_ylabel("Macro-F1")
    ax.set_ylim(0.90, 0.98)
    ax.tick_params(axis="x", rotation=15)
    ax.set_title("Locked CIC-IDS2017 comparison")
    _save(fig, "fig_rccf_model_performance.png")


def _calibration():
    pred = pd.read_csv(CIC / "predictions_seed2024.csv")
    prob_cols = [c for c in pred.columns if c.startswith("prob_")]
    p = pred[prob_cols].to_numpy(float)
    y = pred.true_label.to_numpy()
    labels = [c[5:] for c in prob_cols]
    correct = p.argmax(1) == pd.Categorical(y, categories=labels).codes
    conf = p.max(1)
    bins = np.linspace(0, 1, 11)
    x, acc, count = [], [], []
    for lo, hi in zip(bins[:-1], bins[1:]):
        m = (conf >= lo) & ((conf < hi) if hi < 1 else (conf <= hi))
        if m.any():
            x.append(conf[m].mean()); acc.append(correct[m].mean()); count.append(m.sum())
    fig, ax = plt.subplots(figsize=(5.4, 4.6))
    ax.plot([0, 1], [0, 1], "k--", lw=1, label="Perfect calibration")
    ax.plot(x, acc, "o-", color="#2f6f9f", label="RCCF")
    ax.set_xlabel("Mean predicted confidence")
    ax.set_ylabel("Empirical accuracy")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.legend(); ax.set_title("Test-set reliability diagram (seed 2024)")
    _save(fig, "fig_rccf_calibration.png")


def _robustness():
    df = pd.read_csv(EVIDENCE / "robustness_shared.csv")
    s = df.groupby(["model", "condition"], sort=False).relative_drop.mean().reset_index()
    pivot = s.pivot(index="model", columns="condition", values="relative_drop")
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    pivot.plot.bar(ax=ax, color=["#bd6b35", "#2f6f9f"])
    ax.set_ylabel("Relative Macro-F1 drop")
    ax.set_title("Shared perturbation robustness")
    ax.legend(title="Condition")
    _save(fig, "fig_rccf_robustness.png")


def _latency():
    df = pd.read_csv(EVIDENCE / "latency_percentiles.csv")
    s = df.groupby(["model", "n_jobs"], sort=False)[["p50_ms", "p95_ms", "p99_ms"]].mean().reset_index()
    labels = [f"{r.model}\njobs={r.n_jobs}" for _, r in s.iterrows()]
    fig, ax = plt.subplots(figsize=(8.0, 4.5))
    x = np.arange(len(s)); w = 0.25
    for i, col in enumerate(["p50_ms", "p95_ms", "p99_ms"]):
        ax.bar(x + (i - 1) * w, s[col], w, label=col.upper())
    ax.set_xticks(x, labels, rotation=20, ha="right")
    ax.set_ylabel("Milliseconds per single-row prediction")
    ax.set_title("Offline latency percentiles")
    ax.legend()
    _save(fig, "fig_rccf_latency_percentiles.png")


def _coverage():
    df = pd.read_csv(EVIDENCE / "file_label_matrix.csv", index_col=0)
    known = [c for c in ["Normal", "DoS/DDoS", "Brute Force", "Web Attack", "Bot", "PortScan", "Infiltration", "Heartbleed", "Other"] if c in df]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    im = ax.imshow(np.log1p(df[known].to_numpy(float)), aspect="auto", cmap="viridis")
    ax.set_xticks(range(len(known)), known, rotation=35, ha="right")
    ax.set_yticks(range(len(df)), [Path(x).name for x in df.index])
    ax.set_title("Raw-file by label coverage (log(1 + count))")
    fig.colorbar(im, ax=ax, label="log(1 + count)")
    _save(fig, "fig_rccf_file_label_coverage.png")


def _confusion():
    pred = pd.read_csv(CIC / "predictions_seed2024.csv")
    labels = sorted(pred.true_label.unique())
    cm = confusion_matrix(pred.true_label, pred.predicted_label, labels=labels, normalize="true")
    fig, ax = plt.subplots(figsize=(5.8, 5.1))
    im = ax.imshow(cm, cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(range(len(labels)), labels, rotation=35, ha="right")
    ax.set_yticks(range(len(labels)), labels)
    ax.set_xlabel("Predicted label"); ax.set_ylabel("True label")
    ax.set_title("Normalized confusion matrix (seed 2024)")
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, f"{cm[i, j]:.2f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, label="Row-normalized proportion")
    _save(fig, "fig_rccf_confusion_matrix.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for func in (_performance, _calibration, _robustness, _latency, _coverage, _confusion):
        func()
    print("FIGURES_WRITTEN=" + str(OUT))


if __name__ == "__main__":
    main()
