"""Draw Figure 12: the modern-corpus ladder (scale rungs, holdouts, mechanism).

Three panels, all values read from the released summaries at build time so the
figure cannot drift:

  (a) the feature-budget sweep on CIC-IoT-2023 (k = 8, 16, 32, 60);
  (b) the scale ladder - the gate-minus-equal gap for each modern rung;
  (c) the mechanism - relabelled rows and the tree-weight spread.

Both language editions are produced (``figures/`` and ``figures_en/``).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

for candidate in ["Microsoft YaHei", "SimHei", "DejaVu Sans"]:
    try:
        matplotlib.font_manager.findfont(candidate, fallback_to_default=False)
    except Exception:
        continue
    plt.rcParams["font.sans-serif"] = [candidate]
    break
plt.rcParams["axes.unicode_minus"] = False

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"


def summary(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def collect() -> dict:
    rungs = [
        ("results_rccf_cic_iot2023_cap200k/benchmark_summary.json", "CIC-IoT-2023 20万"),
        ("results_rccf_cic_iot2023_cap500k/benchmark_summary.json", "CIC-IoT-2023 50万"),
        ("results_rccf_gotham2025_cap200k/benchmark_summary.json", "Gotham-2025 20万"),
        ("results_rccf_gotham2025_full/benchmark_summary.json", "Gotham-2025 全档"),
        ("results_rccf_6tisch2026_uncapped/benchmark_summary.json", "6TiSCHSet 全档"),
        ("results_rccf_ctu_idseval6_uncapped/benchmark_summary.json", "CTU-IDSEVAL-6 全档"),
    ]
    rung_rows = [(label, summary(path)["same_members_difference"]) for path, label in rungs]
    budget = {k: summary(f"results_rccf_cic_iot2023_k{k}/benchmark_summary.json")
              ["same_members_difference"] for k in (8, 16, 32, 60)}
    margin_c = summary("results_margin_bound_cic-iot2023_v1/margin_bound_summary.json")
    margin_g = summary("results_margin_bound_gotham2025_v1/margin_bound_summary.json")
    weight = (ROOT / "results_weight_mechanism_gotham2025_v1" /
              "weight_mechanism_summary.csv").read_text(encoding="utf-8").splitlines()
    header, values = weight[0].split(","), weight[1].split(",")
    row = dict(zip(header, values))
    assert margin_g["empirical_changed_rows"] == 0
    assert float(row["weight_min"]) < 0.01 < float(row["weight_max"])
    return dict(rungs=rung_rows, budget=budget, margin_c=margin_c, margin_g=margin_g,
                weight_min=float(row["weight_min"]), weight_max=float(row["weight_max"]),
                disagree=int(row["prediction_disagreement_count"]),
                samples=int(float(row["test_samples"])))


def draw(data: dict, lang: str, out: Path) -> None:
    zh = lang == "zh"
    fig, axes = plt.subplots(1, 3, figsize=(13.6, 4.1), dpi=200)
    fig.subplots_adjust(left=0.06, right=0.985, top=0.86, bottom=0.22, wspace=0.35)

    ax = axes[0]
    ks = sorted(data["budget"])
    gains = [data["budget"][k] for k in ks]
    colours = ["#2E6F9E" if g > 0 else "#8C8C8C" for g in gains]
    ax.bar([str(k) for k in ks], gains, color=colours, width=0.62)
    ax.axhline(0, color="#444444", linewidth=0.8)
    for x, g in zip(range(len(ks)), gains):
        ax.text(x, g + (0.00006 if g >= 0 else -0.00014), f"{g:+.6f}",
                ha="center", fontsize=8.5, color="#222222")
    ax.set_ylim(min(gains) - 0.0006, max(gains) + 0.0005)
    ax.set_xlabel("k" if zh else "feature budget k", fontsize=10)
    ax.set_ylabel("RCCF − equal fusion (Macro-F1)" if not zh else "门控 − 等权（Macro-F1）",
                  fontsize=10)
    ax.set_title("(a) " + ("特征预算扫描（CIC-IoT-2023）" if zh else
                           "Feature-budget sweep (CIC-IoT-2023)"), fontsize=11)

    ax = axes[1]
    labels = [label for label, _ in data["rungs"]]
    values = [value for _, value in data["rungs"]]
    ax.barh(range(len(values)), values,
            color=["#2E6F9E" if v > 0 else "#B4553C" for v in values], height=0.6)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels if zh else [label.replace("全档", " uncapped") for label in labels],
                       fontsize=9)
    ax.axvline(0, color="#444444", linewidth=0.8)
    for y, v in enumerate(values):
        ax.text(v + (0.00008 if v >= 0 else -0.00008), y, f"{v:+.6f}",
                va="center", ha="left" if v >= 0 else "right", fontsize=8.5)
    ax.set_xlim(min(values) - 0.0006, max(values) + 0.0006)
    ax.set_xlabel("RCCF − equal fusion (Macro-F1)" if not zh else "门控 − 等权（Macro-F1）",
                  fontsize=10)
    ax.set_title("(b) " + ("规模档位" if zh else "Scale rungs"), fontsize=11)

    ax = axes[2]
    names = ["Gotham 全档" if zh else "Gotham uncapped",
             "CIC-IoT-2023" if zh else "CIC-IoT-2023"]
    changed = [data["margin_g"]["empirical_changed_rows"], data["margin_c"]["empirical_changed_rows"]]
    rows = [data["margin_g"]["total_rows"], data["margin_c"]["total_rows"]]
    ax.bar(names, [c / r * 1e6 for c, r in zip(changed, rows)], color="#2E6F9E", width=0.5)
    for x, (c, r) in enumerate(zip(changed, rows)):
        ax.text(x, c / r * 1e6 + 0.06, f"{c} / {r:,}", ha="center", fontsize=9)
    ax.set_ylabel("relabelled rows per million" if not zh else "每百万行改判数", fontsize=10)
    ax.set_ylim(0, max(c / r * 1e6 for c, r in zip(changed, rows)) * 1.6 + 0.2)
    ax.set_title("(c) " + ("机制：改判行数与树权重" if zh else
                           "Mechanism: relabelled rows and tree weights"), fontsize=11)
    spread = (data["weight_max"] - data["weight_min"]) / 0.01 * 100
    ax.text(0.5, 0.62, ("Gotham 树权重 " + f"{data['weight_min']:.4f}–{data['weight_max']:.4f}"
                        + f"\n（偏离均匀值 {spread:.1f}%）") if zh else
            (f"Gotham tree weights {data['weight_min']:.4f}-{data['weight_max']:.4f}"
             f"\n({spread:.1f}% around uniform)"),
            transform=ax.transAxes, ha="center", fontsize=9, color="#333333")

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"FIGURE_WRITTEN={out}")


def main() -> int:
    data = collect()
    draw(data, "zh", BASE / "figures" / "fig12_ladder_modern.png")
    draw(data, "en", BASE / "figures_en" / "fig12_ladder_modern.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
