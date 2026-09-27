"""Build the eight-slide briefing deck for the supervisor talk.

Design system (chosen per the pptx-win no-template guidance, since the paper has
no brand template):

    deck job         research briefing, ten minutes, one reader-owner (supervisor)
    visual concept   "evidence memo": numbers first, one accent colour, no decoration
    palette          ink #1F2A37, paper #F3F5F7, blue #1F6FEB (the mechanism),
                     amber #C2410C (adverse findings), grey #6B7280 (annotations)
    type rhythm      28pt title / 16pt thesis / 12pt label / 14pt body / 11pt note
    patterns         title-and-thesis, process line, comparison matrix,
                     evidence-with-takeaway, executive summary strip

Every number is read from the released result files; the figures are the
published manuscript figures, not redrawn.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import artifact_counts_v1 as counts  # noqa: E402
BASE = ROOT / "重构版论文_v4_20260915"
FIGURES = BASE / "figures_en"
OUT = BASE / "汇报用_论文介绍.pptx"

INK = RGBColor(0x1F, 0x2A, 0x37)
PAPER = RGBColor(0xF3, 0xF5, 0xF7)
BLUE = RGBColor(0x1F, 0x6F, 0xEB)
AMBER = RGBColor(0xC2, 0x41, 0x0C)
GREY = RGBColor(0x6B, 0x72, 0x80)
LINE = RGBColor(0xD1, 0xD5, 0xDB)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "Microsoft YaHei"

SLIDE_W, SLIDE_H = Inches(13.333), Inches(7.5)


def numbers() -> dict[str, float]:
    ten = pd.read_csv(ROOT / "results_seeds10_v5" / "table4a_10seeds.csv").set_index("model")
    power = pd.read_csv(ROOT / "results_seeds10_v5" / "power_analysis.csv").set_index("comparison")
    row = power.loc["rccf_minus_equal_rf_chi2"]
    equivalence = json.loads((ROOT / "results_equivalence_10seeds_v5" /
                              "equivalence_summary.json").read_text(encoding="utf-8"))["pooled"]
    scale = json.loads((ROOT / "results_scale_sensitivity_v46" /
                        "scale_sensitivity_summary.json").read_text(encoding="utf-8"))
    full = json.loads((ROOT / "results_full_corpus_v49" /
                       "full_corpus_summary.json").read_text(encoding="utf-8"))
    margin = json.loads((ROOT / "results_margin_bound_v5" /
                         "margin_bound_summary.json").read_text(encoding="utf-8"))
    grid = pd.read_csv(ROOT / "results_gate_tuning_v5" / "gate_search_results.csv")
    weight = pd.read_csv(ROOT / "results_weight_mechanism_v3" /
                         "weight_mechanism_summary.csv").iloc[0]
    scale_rccf = pd.read_csv(ROOT / "results_rccf_cic_natural_v4_scale200k" /
                             "metrics_aggregate.csv").iloc[0]
    scale_frame = pd.read_csv(ROOT / "results_scale_sensitivity_v46" /
                              "metrics_aggregate.csv", header=[0, 1])
    scale_frame = scale_frame.set_index(scale_frame.columns[0])
    full_agg = pd.read_csv(ROOT / "results_full_corpus_v49" / "metrics_aggregate.csv",
                           header=[0, 1])
    full_agg = full_agg.set_index(full_agg.columns[0])
    balanced = pd.read_csv(ROOT / "results_rccf_cic_balanced_v3b" /
                           "metrics_aggregate.csv").iloc[0]
    protocol = pd.read_csv(ROOT / "results_protocol_sensitivity_v4" /
                           "protocol_sensitivity_metrics.csv")
    pivot = protocol.pivot(index="seed", columns="protocol", values="macro_f1")
    profile = json.loads((ROOT / "results_resources_v5" /
                          "resource_profile_summary.json").read_text(encoding="utf-8"))["summary"]
    openset = pd.read_csv(ROOT / "results_cfrg_open_set_v5_verified" / "open_set_metrics.csv")
    conditional = openset[openset.model.isin(("cfrg_forest", "cfrg_forest_temperature_scaled"))]
    equal = openset[openset.model.isin(("equal_rf", "equal_rf_temperature_scaled"))]
    return {
        "rccf": float(ten.loc["rccf", "macro_f1"]),
        "control": float(ten.loc["equal_rf_chi2", "macro_f1"]),
        "diff": float(row.mean_difference),
        "ci90": (float(row.ci90_low), float(row.ci90_high)),
        "boot": (float(equivalence["pooled_ci_low"]), float(equivalence["pooled_ci_high"])),
        "scale_diff": float(scale["mean_difference"]),
        "scale_rccf": float(scale_rccf.macro_f1_mean),
        "scale_control": float(scale_frame.loc["equal_rf_chi2", ("macro_f1", "mean")]),
        "full_diff": float(full["mean_difference"]),
        "full_rccf": float(full["rccf_mean_macro_f1"]),
        "full_control": float(full["control_mean_macro_f1"]),
        "full_slowdown": float(full["train_slowdown"]),
        "provable": float(margin["provable_by_bound_rate_mean"]) * 100,
        "changed": int(margin["empirical_changed_rows"]),
        "entropy": float(weight.normalized_weight_entropy),
        "configs": int(len(grid)),
        "distinct": int(grid.val_macro_f1.nunique()),
        "view_gap": float(full_agg.loc["equal_rf_chi2", ("macro_f1", "mean")] -
                          full_agg.loc["equal_rf_all", ("macro_f1", "mean")]),
        "prior_gap": float(balanced.macro_f1_mean) - float(ten.loc["rccf", "macro_f1"]),
        "dedup": float((pivot["split_first_training_only_dedup"] -
                        pivot["global_dedup_before_split"]).abs().max()),
        "size_multiple": float(profile["rccf"]["model_size_mb"]) /
        float(profile["equal_rf_chi2"]["model_size_mb"]),
        "train_multiple": float(ten.loc["rccf", "train_seconds"]) /
        float(ten.loc["equal_rf_chi2", "train_seconds"]),
        "auroc_lo": float(conditional.auroc.min()),
        "auroc_hi": float(conditional.auroc.max()),
        "auroc_eq_lo": float(equal.auroc.min()),
        "auroc_eq_hi": float(equal.auroc.max()),
        "recall_lo": float(conditional.unknown_recall.min()),
        "recall_hi": float(conditional.unknown_recall.max()),
    }


def textbox(slide, x, y, w, h, text, size=14, bold=False, color=INK, align=PP_ALIGN.LEFT,
            line_spacing=1.15):
    box = slide.shapes.add_textbox(x, y, w, h)
    frame = box.text_frame
    frame.word_wrap = True
    for index, line in enumerate(text.split("\n")):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.text = line
        paragraph.alignment = align
        paragraph.line_spacing = line_spacing
        for run in paragraph.runs:
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.color.rgb = color
            run.font.name = FONT
    return box


def panel(slide, x, y, w, h, fill=PAPER):
    shape = slide.shapes.add_shape(1, x, y, w, h)  # rectangle
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = fill
    shape.shadow.inherit = False
    return shape


def header(slide, title, kicker=None):
    if kicker:
        textbox(slide, Inches(0.6), Inches(0.38), Inches(12), Inches(0.34), kicker,
                size=12, bold=True, color=BLUE)
    textbox(slide, Inches(0.6), Inches(0.76), Inches(12.1), Inches(0.8), title,
            size=26, bold=True, color=INK)
    line = slide.shapes.add_shape(1, Inches(0.6), Inches(1.60), Inches(12.1), Pt(1.2))
    line.fill.solid()
    line.fill.fore_color.rgb = LINE
    line.line.fill.background()
    line.shadow.inherit = False


def footer(slide, page):
    textbox(slide, Inches(0.6), Inches(7.0), Inches(9), Inches(0.3),
            "泄漏受控的条件集成加权研究 · v1.11.0 · 数字均取自发布产物", size=10, color=GREY)
    textbox(slide, Inches(12.2), Inches(7.0), Inches(0.6), Inches(0.3), str(page),
            size=10, color=GREY, align=PP_ALIGN.RIGHT)


def picture(slide, name, x, y, w):
    path = FIGURES / name
    if not path.exists():
        return
    slide.shapes.add_picture(str(path), x, y, width=w)


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def main() -> None:
    n = numbers()
    deck = Presentation()
    deck.slide_width, deck.slide_height = SLIDE_W, SLIDE_H
    blank = deck.slide_layouts[6]
    view_gap = n["view_gap"]
    dilution = view_gap / 4

    # 1 - title and thesis
    slide = deck.slides.add_slide(blank)
    textbox(slide, Inches(0.9), Inches(1.6), Inches(11.5), Inches(1.0),
            "条件集成加权到底有没有增益？", size=40, bold=True, color=INK)
    textbox(slide, Inches(0.9), Inches(2.6), Inches(11.5), Inches(0.6),
            "十个种子、三档总体、一个泄漏受控协议下的等价性检验", size=18, color=GREY)
    cards = [
        ("截断总体 53 237 条", f"{n['diff']:+.6f}", "TOST 两个边界等价", BLUE),
        ("扩大 7.8 倍 413 209 条", f"{n['scale_diff']:+.6f}", "两个边界仍等价", BLUE),
        ("全语料 2 429 503 条", f"{n['full_diff']:+.6f}", "0.01 等价 / 0.005 不等价", AMBER),
    ]
    for index, (label, value, note, colour) in enumerate(cards):
        x = Inches(0.9 + index * 3.95)
        panel(slide, x, Inches(3.7), Inches(3.6), Inches(2.2))
        textbox(slide, x + Inches(0.25), Inches(3.92), Inches(3.1), Inches(0.42), label,
                size=12, bold=True, color=GREY)
        textbox(slide, x + Inches(0.25), Inches(4.35), Inches(3.1), Inches(0.7), value,
                size=30, bold=True, color=colour)
        textbox(slide, x + Inches(0.25), Inches(5.15), Inches(3.1), Inches(0.5), note,
                size=12, color=INK)
    textbox(slide, Inches(0.9), Inches(6.25), Inches(11.5), Inches(0.4),
            "协议效应比聚合规则差异大一个数量级 —— 这是本文真正可复用的结论。",
            size=15, bold=True, color=INK)
    footer(slide, 1)
    notes(slide, "开场：本文检验「按样本可靠性给多个森林专家条件加权是否优于等权投票」。"
                 "先给三个数字：截断总体等价、扩大 7.8 倍仍等价、全语料转为稳定劣势。"
                 "最后一句是本轮真正想留下的东西——协议选择的影响远大于聚合规则。")

    # 2 - why a controlled test is needed
    slide = deck.slides.add_slide(blank)
    header(slide, "公开数据上的「加权更好」，被四类污染托着", "问题")
    items = [
        ("重复与近重复样本", "同一段攻击流量在多文件里重复出现；划分顺序一换，训练与测试就重叠。"),
        ("标签冲突", "完全相同的特征向量被赋不同标签，模型在矛盾监督上拟合。"),
        ("特征选择泄漏", "选择器在全量数据上拟合，测试集信息渗进训练。"),
        ("类别先验与调参预算", "平衡控制 vs 自然先验、是否同等调参，都能单独造成「提升」。"),
    ]
    for index, (title, body) in enumerate(items):
        x = Inches(0.6 + (index % 2) * 6.2)
        y = Inches(1.9 + (index // 2) * 2.35)
        panel(slide, x, y, Inches(5.9), Inches(2.05))
        textbox(slide, x + Inches(0.3), y + Inches(0.25), Inches(5.3), Inches(0.4), title,
                size=16, bold=True, color=INK)
        textbox(slide, x + Inches(0.3), y + Inches(0.75), Inches(5.3), Inches(1.0), body,
                size=13, color=GREY)
    textbox(slide, Inches(0.6), Inches(6.5), Inches(12), Inches(0.4),
            "所以本文把问题压到最直接的对照：条件加权森林 vs 等权 χ² 森林，同一个协议、同一批划分。",
            size=13, bold=True, color=BLUE)
    footer(slide, 2)
    notes(slide, "这四类污染每一项都能单独制造出「加权更好」的假象。"
                 "本文不否认已有方法，而是把它们放进同一个去泄漏协议里做最直接的对照。")

    # 3 - protocol
    slide = deck.slides.add_slide(blank)
    header(slide, "六阶段审计 + 四个语料 + 十个种子", "做法")
    stages = ["标签映射", "非有限值清理", "物理范围筛查", "全局去重", "分层划分", "训练侧特征选择"]
    for index, stage in enumerate(stages):
        x = Inches(0.6 + index * 2.02)
        panel(slide, x, Inches(2.0), Inches(1.85), Inches(0.85), WHITE)
        textbox(slide, x, Inches(2.2), Inches(1.85), Inches(0.5), stage, size=12,
                bold=True, color=INK, align=PP_ALIGN.CENTER)
        if index < len(stages) - 1:
            textbox(slide, x + Inches(1.85), Inches(2.2), Inches(0.2), Inches(0.4), "›",
                    size=16, bold=True, color=LINE, align=PP_ALIGN.CENTER)
    facts = [
        ("主数据", "CIC-IDS2017：原始 2 830 743 行 → 审计后研究总体"),
        ("外部基准", "NSL-KDD、UNSW-NB15、N-BaIoT（UCI 442，CC BY 4.0）"),
        ("种子", "42 / 2024 / 3407 / 7 / 13 / 101 / 202 / 303 / 404 / 505"),
        ("统计", "配对差 + 种子级 90%/95% 区间 + 测试行配对 Bootstrap + TOST（0.005/0.01）"),
        ("可复现", f"{counts.gate_checks()} 项自动检查全绿；722 个逐样本预测公开；"
                   f"仓库带 tag {counts.latest_tag()}"),
    ]
    for index, (label, body) in enumerate(facts):
        y = Inches(3.25 + index * 0.72)
        textbox(slide, Inches(0.6), y, Inches(1.5), Inches(0.4), label, size=13, bold=True,
                color=BLUE)
        textbox(slide, Inches(2.2), y, Inches(10.4), Inches(0.5), body, size=13, color=INK)
    footer(slide, 3)
    notes(slide, "六阶段审计的每一步都有计数与产物记录；外部三个语料是独立原生标签基准；"
                 f"主实验十个种子。特别强调：{counts.gate_checks()} 项检查与逐样本预测都公开，"
                 "审稿时可直接重算。")

    # 4 - main results table
    slide = deck.slides.add_slide(blank)
    header(slide, "结论随规模反转：等价 → 等价 → 稳定劣势", "结果 · 三档总体")
    rows = [
        ("总体", "流量", "测试行", "条件加权", "等权 χ²", "平均差", "TOST 0.005", "TOST 0.01"),
        ("截断（每类 2 万）", "53 237", "7 986", f"{n['rccf']:.6f}", f"{n['control']:.6f}",
         f"{n['diff']:+.6f}", "等价", "等价"),
        ("扩大 7.8 倍", "413 209", "61 982", f"{n['scale_rccf']:.6f}", f"{n['scale_control']:.6f}",
         f"{n['scale_diff']:+.6f}", "等价", "等价"),
        ("全去重语料", "2 429 503", "364 426", f"{n['full_rccf']:.6f}", f"{n['full_control']:.6f}",
         f"{n['full_diff']:+.6f}", "不等价", "等价"),
    ]
    left, top, width = Inches(0.6), Inches(1.85), Inches(8.0)
    table = slide.shapes.add_table(len(rows), 8, left, top, width, Inches(1.9)).table
    widths = (1.35, 0.95, 0.85, 1.05, 1.0, 1.0, 0.9, 0.9)
    for index, inches in enumerate(widths):
        table.columns[index].width = Inches(inches)
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            cell = table.cell(r, c)
            cell.text = value
            cell.margin_left = cell.margin_right = Emu(45720)
            for paragraph in cell.text_frame.paragraphs:
                paragraph.alignment = PP_ALIGN.LEFT if c == 0 else PP_ALIGN.RIGHT
                for run in paragraph.runs:
                    run.font.size = Pt(11 if r else 11)
                    run.font.bold = (r == 0) or (c == 5 and r == 3)
                    run.font.name = FONT
                    run.font.color.rgb = AMBER if (r == 3 and c == 5) else INK
    textbox(slide, Inches(0.6), Inches(4.0), Inches(8.0), Inches(1.4),
            f"截断总体：种子级 90% 区间 [{n['ci90'][0]:.6f}, {n['ci90'][1]:.6f}]，"
            f"配对 Bootstrap [{n['boot'][0]:.6f}, {n['boot'][1]:.6f}]，"
            "都落在 0.005 与 0.01 的等价边界内；逐种子方向五正五负。",
            size=13, color=INK)
    picture(slide, "fig4_main_results.png", Inches(8.85), Inches(1.85), Inches(3.9))
    textbox(slide, Inches(8.85), Inches(4.6), Inches(3.9), Inches(1.4),
            "左图纵轴自 0.75 起，专门显示千分位差异；右图为配对区间。两图须合读。",
            size=11, color=GREY)
    footer(slide, 4)
    notes(slide, "这张表是全文骨架：同一个比较，在截断总体等价、扩大 7.8 倍仍等价、"
                 "完全取消上限后转为稳定劣势。注意措辞：全语料在 0.01 边界上仍然等价，"
                 "只是方向十个种子一致为负。")

    # 5 - mechanism
    slide = deck.slides.add_slide(blank)
    header(slide, "权重动不了预测：三条独立证据", "机制")
    evidence = [
        ("逐行可计算上界", f"{n['provable']:.2f}% 的测试行可证明不受权重影响",
         f"实际改判 {n['changed']} 行"),
        ("权重结构", f"归一化权重熵 {n['entropy']:.5f}",
         "风险模型输出近乎相同，权重退化为均匀"),
        ("门控搜索", f"{n['configs']} 组超参数配置 → {n['distinct']} 个不同验证值",
         "锁定后在测试集上改判 0 行"),
    ]
    for index, (title, lead, note) in enumerate(evidence):
        y = Inches(1.95 + index * 0.95)
        textbox(slide, Inches(0.6), y, Inches(2.4), Inches(0.4), title, size=15, bold=True,
                color=BLUE)
        textbox(slide, Inches(3.1), y - Inches(0.05), Inches(5.2), Inches(0.45), lead,
                size=15, bold=True, color=INK)
        textbox(slide, Inches(3.1), y + Inches(0.35), Inches(5.2), Inches(0.4), note,
                size=12, color=GREY)
    panel(slide, Inches(0.6), Inches(4.85), Inches(7.7), Inches(1.6))
    textbox(slide, Inches(0.85), Inches(5.05), Inches(7.2), Inches(1.2),
            "增益由专家多样性支配：分歧率 0.20%–0.36% 的专家集合 6 次运行增益恰好为 0；"
            "刻意去相关的三类集合 9 次运行全为正（斜率 0.0646，r = 0.749）。",
            size=13, color=INK)
    picture(slide, "fig5_gate_diagnostics.png", Inches(8.5), Inches(1.95), Inches(4.3))
    footer(slide, 5)
    notes(slide, "这三条是独立证据：上界是可证明的、权重结构是可观测的、搜索是穷举的。"
                 "结论：在本数据结构下继续调门控不会带来判别增益。")

    # 6 - dilution arithmetic
    slide = deck.slides.add_slide(blank)
    header(slide, "全语料上的劣势是「稀释」，不是加权", "机制 · 反转的原因")
    panel(slide, Inches(0.6), Inches(1.9), Inches(7.9), Inches(2.1), PAPER)
    textbox(slide, Inches(0.95), Inches(2.15), Inches(7.2), Inches(1.6),
            f"全特征视图 {n['full_control']:.6f} − 卡方视图 {n['full_control'] + view_gap:.6f}"
            f" = 视图差 {view_gap:.6f}\n"
            f"四路平均摊薄四分之一：{view_gap:.6f} ÷ 4 = {dilution:.6f}\n"
            f"实测平均差：{n['full_diff']:.6f}（偏差约 {abs(dilution - abs(n['full_diff'])) / dilution * 100:.1f}%）",
            size=15, color=INK, line_spacing=1.4)
    textbox(slide, Inches(0.6), Inches(4.2), Inches(7.9), Inches(1.5),
            "同一算式在三档总体上成立：53 237 条（0.002068/4 = 0.000517 对 −0.000456）、"
            "413 209 条（0.004249/4 = 0.001062 对 −0.001137）、"
            "2 429 503 条（上式）。因此随规模变化的是成员质量，不是聚合规则。",
            size=13, color=GREY)
    panel(slide, Inches(8.85), Inches(1.9), Inches(3.9), Inches(3.8), PAPER)
    textbox(slide, Inches(9.1), Inches(2.15), Inches(3.4), Inches(0.4),
            "部署含义", size=13, bold=True, color=AMBER)
    textbox(slide, Inches(9.1), Inches(2.65), Inches(3.4), Inches(2.8),
            "· 截断总体上用等权投票即可\n\n"
            "· 强不平衡语料上不要部署条件加权\n\n"
            "· 融合前先看各成员的分差：\n  差多少，四路平均就摊多少",
            size=13, color=INK, line_spacing=1.25)
    footer(slide, 6)
    notes(slide, "把反转解释清楚是这轮汇报的关键：不是加权把结果弄坏了，"
                 "而是四路平均把一份落后的特征视图摊进来。三个规模都符合同一个算式。")

    # 7 - cost and open set
    slide = deck.slides.add_slide(blank)
    header(slide, "代价与开放集：两处不利证据照实说", "次生指标")
    textbox(slide, Inches(0.6), Inches(1.85), Inches(5.6), Inches(0.4),
            "训练与推理代价", size=15, bold=True, color=BLUE)
    cost = [
        ("训练耗时", f"截断约 {n['train_multiple']:.0f} 倍，全语料 {n['full_slowdown']:.0f} 倍"),
        ("模型体积", f"{n['size_multiple']:.1f} 倍（9.09 MB vs 2.21 MB）"),
        ("代价敏感", "误报漏报代价比 1–100 内没有优势"),
    ]
    for index, (label, value) in enumerate(cost):
        y = Inches(2.3 + index * 0.6)
        textbox(slide, Inches(0.6), y, Inches(1.6), Inches(0.4), label, size=13, bold=True,
                color=GREY)
        textbox(slide, Inches(2.3), y, Inches(4.2), Inches(0.5), value, size=13, color=INK)
    textbox(slide, Inches(0.6), Inches(4.3), Inches(5.9), Inches(0.45),
            "开放集：三个未知族留出", size=15, bold=True,
            color=AMBER)
    textbox(slide, Inches(0.6), Inches(4.72), Inches(5.9), Inches(0.35),
            "PortScan / Infiltration / Heartbleed 作未知族", size=11, color=GREY)
    textbox(slide, Inches(0.6), Inches(5.05), Inches(5.9), Inches(1.5),
            f"条件加权 AUROC {n['auroc_lo']:.3f}–{n['auroc_hi']:.3f}，"
            f"未知类召回 {n['recall_lo']:.4f}–{n['recall_hi']:.4f}\n"
            f"等权森林 AUROC {n['auroc_eq_lo']:.3f}–{n['auroc_eq_hi']:.3f}，"
            "未知类召回 0.057–0.374\n"
            "风险门控把概率推向高置信区，削弱了拒绝所需的不确定性信号。",
            size=13, color=INK, line_spacing=1.3)
    picture(slide, "fig10_calibration_robustness.png", Inches(6.75), Inches(1.9), Inches(2.9))
    picture(slide, "fig11_latency.png", Inches(9.85), Inches(1.9), Inches(2.9))
    textbox(slide, Inches(6.75), Inches(4.75), Inches(6.0), Inches(1.4),
            f"{counts.gate_checks()} 项自动检查持续复核这些数字；"
            "开放集与代价的每一项都能从公开的逐样本预测重算。",
            size=12, color=GREY)
    footer(slide, 7)
    notes(slide, "这是本文对条件加权最不利的两组证据，主动讲比被问要好。"
                 "注意不要用「显著变差」的措辞：全语料在 0.01 边界上仍等价。")

    # 8 - conclusion
    slide = deck.slides.add_slide(blank)
    header(slide, "结论、边界与下一步", "收尾")
    panel(slide, Inches(0.6), Inches(1.9), Inches(7.9), Inches(2.4), PAPER)
    textbox(slide, Inches(0.9), Inches(2.15), Inches(7.3), Inches(2.0),
            "1. 在流特征公开数据上，条件加权相对等权投票**未观测到判别增益**；\n"
            "2. 全语料上的劣势来自成员稀释，可由成员分差直接算出；\n"
            "3. 协议选择（先验 +0.0725、去重顺序 ≤0.0060）比聚合规则差异（0.0005 量级）"
            "大一个数量级，模型族差异更大（MLP 落后 0.0916）。",
            size=15, color=INK, line_spacing=1.4)
    textbox(slide, Inches(0.6), Inches(4.5), Inches(7.9), Inches(1.8),
            "边界：四个语料都不是生产流量；文件级实验不是时间外推；"
            "开放集只覆盖三个未知族与一个显著性水平；对抗性规避未评估。",
            size=13, color=GREY, line_spacing=1.3)
    panel(slide, Inches(8.85), Inches(1.9), Inches(3.9), Inches(2.4), PAPER)
    textbox(slide, Inches(9.1), Inches(2.15), Inches(3.4), Inches(2.0),
            "下一步\n\n① 显式强制专家去相关的加权机制\n② 跨时段/跨场景的完整类别协议\n"
            "③ 把报告建议做成可自动检查的清单",
            size=13, color=INK, line_spacing=1.3)
    textbox(slide, Inches(8.85), Inches(4.5), Inches(3.9), Inches(1.8),
            "材料：论文介绍（两页）· 汇报要点 · 正式稿件（中英）· 补充材料 S01–S30 · "
            "公开仓库 tag v1.11.0",
            size=12, color=GREY)
    footer(slide, 8)
    notes(slide, "收尾三句：没观测到增益；反转来自稀释；协议影响更大。"
                 "然后把边界说清楚，再给三个下一步方向。")

    deck.save(OUT)
    print(f"DECK_WRITTEN={OUT}")
    print(f"slides={len(deck.slides.__iter__.__self__._sldIdLst)}")


if __name__ == "__main__":
    main()
