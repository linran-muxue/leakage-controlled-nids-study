"""Draw the whole project as one flow chart, for print and for slides.

Six stages, left to right in two rows: data acquisition, the six-stage audit,
modelling and controls, evaluation, mechanism analysis, and the paper plus its
release.  Numbers come from the artefacts, and the diagram is exported as a
300-dpi PNG for slides and a vector PDF for print.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
OUTDIR = BASE / "figures_project"
OUT = BASE / "项目流程图.md"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import artifact_counts_v1 as counts  # noqa: E402

INK = "#1F2A37"
PAPER = "#F3F5F7"
BLUE = "#1F6FEB"
AMBER = "#C2410C"
GREY = "#6B7280"
WHITE = "#FFFFFF"


def numbers() -> dict[str, str]:
    audit = json.loads((ROOT / "results_data_audit_cic_natural_v3b" /
                        "data_processing_audit.json").read_text(encoding="utf-8"))
    full = json.loads((ROOT / "results_full_corpus_v49" /
                       "full_corpus_summary.json").read_text(encoding="utf-8"))
    margin = json.loads((ROOT / "results_margin_bound_v5" /
                         "margin_bound_summary.json").read_text(encoding="utf-8"))
    return {
        "raw": f"{audit['raw_totals']['source_rows']:,}",
        "capped": "53 237",
        "full": f"{full['test_rows'] + 1700652 + 364425:,}".replace(",", " "),
        "provable": f"{margin['provable_by_bound_rate_mean'] * 100:.2f}%",
        # the counts below describe the repository itself, so they are measured
        # rather than typed in - the gate grows and the archive gains files
        "gate": str(counts.gate_checks()),
        "bundle": str(counts.bundle_files()),
        "figures": str(counts.figures()),
        "tables": str(counts.tables()),
        "tag": counts.latest_tag(),
    }


FIT_CHECKS: list[tuple[str, object, tuple[float, float, float, float]]] = []


def stage(axis, x, y, w, h, title, kind, bullets):
    accent = {"data": BLUE, "model": BLUE, "evidence": INK, "limit": AMBER}.get(kind, INK)
    axis.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.006,rounding_size=0.012",
                                  linewidth=0, facecolor=PAPER, zorder=1))
    axis.add_patch(FancyBboxPatch((x, y + h - 0.075), w, 0.075,
                                  boxstyle="round,pad=0.006,rounding_size=0.012",
                                  linewidth=0, facecolor=accent, zorder=2))
    FIT_CHECKS.append((title, axis.text(x + 0.018, y + h - 0.038, title, color=WHITE,
                                        fontsize=13.5, weight="bold", family="Microsoft YaHei",
                                        va="center", zorder=3), (x, y, w, h)))
    for index, line in enumerate(bullets):
        artist = axis.text(x + 0.018, y + h - 0.105 - index * 0.055, line, color=INK,
                           fontsize=10.8, family="Microsoft YaHei", va="top", zorder=3,
                           linespacing=1.35)
        FIT_CHECKS.append((title + " 第" + str(index + 1) + "行", artist, (x, y, w, h)))


def assert_text_fits(axis, figure) -> int:
    """Every string must sit inside the panel it belongs to.

    Earlier drafts pushed the closing lines past their panel and the overflow
    was only visible on inspection, so the fit is now measured instead of
    eyeballed.
    """
    figure.canvas.draw()
    renderer = figure.canvas.get_renderer()
    failures: list[str] = []
    for label, artist, (x, y, w, h) in FIT_CHECKS:
        box = artist.get_window_extent(renderer=renderer)
        (x0, y0), (x1, y1) = axis.transAxes.inverted().transform(
            [(box.x0, box.y0), (box.x1, box.y1)])
        if not (x - 0.002 <= x0 and x1 <= x + w + 0.002):
            failures.append(f"TEXT_OVERFLOW_X: {label} 实际 {x0:.3f}-{x1:.3f}，"
                            f"方框 {x:.3f}-{x + w:.3f}")
        if not (y - 0.002 <= y0 and y1 <= y + h + 0.002):
            failures.append(f"TEXT_OVERFLOW_Y: {label} 实际 {y0:.3f}-{y1:.3f}，"
                            f"方框 {y:.3f}-{y + h:.3f}")
    assert not failures, "；".join(failures)
    return len(FIT_CHECKS)


def arrow(axis, start, end):
    axis.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=16,
                                   linewidth=1.8, color=GREY, zorder=4,
                                   shrinkA=2, shrinkB=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default=None,
                        help="scratch directory used by the checker; defaults to the released one")
    args = parser.parse_args()
    n = numbers()
    outdir = Path(args.outdir) if args.outdir else OUTDIR
    doc = (outdir / "项目流程图.md") if args.outdir else OUT
    outdir.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(16, 9), dpi=200)
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.axis("off")
    figure.patch.set_facecolor(WHITE)

    axis.text(0.5, 0.985, "泄漏受控的条件集成加权研究：项目全流程", ha="center", va="top",
              fontsize=22, weight="bold", color=INK, family="Microsoft YaHei")
    axis.text(0.5, 0.935, "从四个公开语料到可复现投稿包；每个方框都对应可核验的产物或脚本",
              ha="center", va="top", fontsize=12.5, color=GREY, family="Microsoft YaHei")

    w, h = 0.29, 0.30
    y_top, y_bottom = 0.575, 0.185
    x1, x2, x3 = 0.035, 0.355, 0.675

    stage(axis, x1, y_top, w, h, "① 数据获取", "data", [
        "CIC-IDS2017：8 个 CSV，原始 " + n["raw"] + " 行",
        "NSL-KDD、UNSW-NB15、N-BaIoT（UCI 442）",
        "URL／检索日期／许可／SHA-256 → S01",
        "13 项摘要逐字节核验（audit_data_authenticity）",
    ])
    stage(axis, x2, y_top, w, h, "② 数据处理（六阶段审计）", "data", [
        "标签映射 → 非有限值 → 物理范围",
        "全局去重（前向/反向双哈希）→ 分层划分",
        "训练侧特征选择：卡方／互信息／ANOVA",
        "2 668 729 → 研究总体；跨划分精确重叠 0",
    ])
    stage(axis, x3, y_top, w, h, "③ 建模与对照", "model", [
        "条件加权 RCCF：softmax(−风险) 权重 + 凸组合",
        "对照：等权 χ² 森林、全特征等权、ExtraTrees",
        "XGBoost、MLP（同等预算）",
        "门控 108 组配置搜索与锁定",
    ])
    stage(axis, x1, y_bottom, w, h, "④ 评估", "evidence", [
        "主实验：十种子；截断 53 237 条",
        "规模阶梯 413 209 条；全语料 2 429 503 条",
        "配对差 + 90%/95% 区间 + Bootstrap + TOST",
        "逐类别、开放集、鲁棒性、延迟、代价敏感",
    ])
    stage(axis, x2, y_bottom, w, h, "⑤ 机制分析", "evidence", [
        "三个可辨识性条件；边距上界 " + n["provable"] + " 可证",
        "门控搜索只产生 6 个不同验证值",
        "专家多样性剂量—反应（斜率 0.0646，r=0.749）",
        "稀释诊断：视图差 ÷ 4 ≈ 实测差（三档成立）",
    ])
    stage(axis, x3, y_bottom, w, h, "⑥ 论文与交付", "evidence", [
        f"中英正式稿件、{n['figures']} 图 {n['tables']} 表、补充材料 S01–S30",
        f"验证闸门 {n['gate']} 项（数字、结构、可复现、真实性）",
        f"公开仓库 tag {n['tag']}；722 个逐样本预测",
        # deliberately no file count here: the archive gains and loses files
        # every round, and a count in a printed figure would age immediately.
        # The current figures live in 材料完整性清单 and 数据与资料来源总表.
        "投稿包与逐文件校验清单；工作日志与来源总表",
    ])

    # top row runs left to right, then an elbow connector drops into the bottom
    # row, which also runs left to right so the numbering matches the flow
    arrow(axis, (x1 + w + 0.004, y_top + h / 2), (x2 - 0.004, y_top + h / 2))
    arrow(axis, (x2 + w + 0.004, y_top + h / 2), (x3 - 0.004, y_top + h / 2))
    gap = (y_top + y_bottom + h) / 2 - 0.015
    axis.plot([x3 + w / 2, x3 + w / 2], [y_top - 0.004, gap], color=GREY, linewidth=1.8, zorder=4)
    axis.plot([x3 + w / 2, x1 + w / 2], [gap, gap], color=GREY, linewidth=1.8, zorder=4)
    arrow(axis, (x1 + w / 2, gap), (x1 + w / 2, y_bottom + h + 0.004))
    arrow(axis, (x1 + w + 0.004, y_bottom + h / 2), (x2 - 0.004, y_bottom + h / 2))
    arrow(axis, (x2 + w + 0.004, y_bottom + h / 2), (x3 - 0.004, y_bottom + h / 2))

    summary = (0.035, 0.012, 0.93, 0.150)
    axis.add_patch(FancyBboxPatch(summary[:2], summary[2], summary[3],
                                  boxstyle="round,pad=0.004,rounding_size=0.01",
                                  linewidth=0, facecolor="#EEF3FB", zorder=1))
    FIT_CHECKS.append(("核心结论", axis.text(
        0.05, 0.136,
        "核心结论：截断总体上条件加权与等权投票等价（−0.000456，TOST 两边界成立）；\n"
        "全语料上转为稳定劣势（−0.005533，十种子方向一致，0.01 边界仍等价）；"
        "协议效应比聚合规则差异大一个数量级。",
        fontsize=12, color=INK, family="Microsoft YaHei", va="top", linespacing=1.6),
        summary))
    FIT_CHECKS.append(("证据与复现", axis.text(
        0.05, 0.038,
        "证据与复现：数据来源总表 · 公式来源与核验 · 数据处理代码与流程 · 补充材料 S01–S30 · "
        f"scripts/verify_all_v8.py（{n['gate']} 项闸门）",
        fontsize=10.5, color=GREY, family="Microsoft YaHei", va="center"), summary))

    print(f"TEXT_FIT_CHECKS={assert_text_fits(axis, figure)}")

    png = outdir / "flow_project.png"
    pdf = outdir / "flow_project.pdf"
    figure.savefig(png, facecolor=WHITE, bbox_inches="tight")
    figure.savefig(pdf, facecolor=WHITE, bbox_inches="tight")
    plt.close(figure)

    lines = [
        "# 项目流程图",
        "",
        "> 一张图概括从数据到投稿包的全过程；每个方框都对应可核验的脚本或产物。",
        "",
        "![项目全流程](figures_project/flow_project.png)",
        "",
        "## 各阶段的入口",
        "",
        "| 阶段 | 入口 | 产物 |",
        "|---|---|---|",
        "| ① 数据获取 | S01、`docs/source_records/` | 四项语料的摘要与来源记录 |",
        "| ② 数据处理 | `src/prepare_dataset.py`、`src/data_pipeline.py`、"
        "`scripts/audit_data_processing_v1.py` | `data_processed_*`、审计 JSON |",
        "| ③ 建模与对照 | `src/rccf_forest.py`、`scripts/run_seeds10_v5.py`、`scripts/tune_gate_v5.py` | "
        "逐种子预测、门控搜索记录 |",
        "| ④ 评估 | `scripts/run_full_corpus_parallel_v1.py`、`scripts/audit_released_evidence_v1.py` | "
        "汇总指标、TOST、开放集与代价结果 |",
        "| ⑤ 机制分析 | `scripts/analyze_margin_bound_v5.py`、`scripts/run_diversity_suite_v5.py` | "
        "边距上界、多样性回归、稀释诊断 |",
        "| ⑥ 论文与交付 | `scripts/build_restructured_manuscript_v4.py`、"
        "`scripts/package_submission_bundle_v18.py` | 正式稿件、补充材料、投稿包 |",
        "",
        "矢量版（印刷用）：`figures_project/flow_project.pdf`。",
        "",
    ]
    doc.write_text("\n".join(lines), encoding="utf-8")
    print(f"FLOWCHART_WRITTEN={png}")
    print(f"pdf={pdf} doc={doc}")


if __name__ == "__main__":
    main()
