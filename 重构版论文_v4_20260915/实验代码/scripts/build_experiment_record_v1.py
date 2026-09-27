"""Record every experiment: its code, its command, its artefacts, its run evidence.

The runs happened over weeks in background shells, so no screen captures exist.
What does survive is paired here, experiment by experiment: the script (path,
SHA-256, an excerpt of its entry point), the exact command, the inputs, the
output directory, the numbers read back from the artefacts, and a run record
rendered from real content - the run's own log where one was kept, otherwise the
first rows of the file the run produced.  Every panel says it is a rendering.

Outputs
    实验代码与运行记录.md            the document
    figures_experiments/exp*.png     one run-record panel per experiment
    实验代码/                        copies of the scripts the record cites
    实验日志/                        copies of the logs that were kept
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
FIGDIR = BASE / "figures_experiments"
CODEDIR = BASE / "实验代码"
LOGDIR = BASE / "实验日志"
OUT = BASE / "实验代码与运行记录.md"
PY = sys.executable
FONT = "Microsoft YaHei"
INK, GREY, BLUE = "#1F2A37", "#6B7280", "#1F6FEB"
BG, FG, ACCENT, CMD = "#0B1220", "#E5E7EB", "#7DD3FC", "#A5B4FC"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def width(text: str) -> int:
    """Display width, counting CJK as two columns."""
    return sum(2 if ord(char) > 0x2E80 else 1 for char in text)


def clip(text: str, limit: int = 132) -> str:
    if width(text) <= limit:
        return text
    out = ""
    used = 0
    for char in text:
        step = 2 if ord(char) > 0x2E80 else 1
        if used + step > limit - 1:
            break
        out += char
        used += step
    return out + "…"


def script_facts(relative: str) -> dict[str, object]:
    path = ROOT / relative
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    return {"path": relative, "sha256": hashlib.sha256(raw).hexdigest()[:16],
            "bytes": len(raw), "lines": text.count("\n") + 1}


def excerpt(relative: str, count: int = 10) -> list[str]:
    text = (ROOT / relative).read_text(encoding="utf-8", errors="replace").splitlines()
    start = 0
    for index, line in enumerate(text):
        if line.startswith(("def main", "def run", "class ")):
            start = index
            break
    return [clip(line.rstrip(), 128) for line in text[start:start + count]]


def csv_block(relative: str, rows: int = 4, columns: int = 8) -> list[str]:
    frame = pd.read_csv(ROOT / relative, nrows=rows)
    lines = [f"$ head -{rows} {relative}",
             "  ".join(str(name) for name in frame.columns[:columns])]
    for _, row in frame.head(rows).iterrows():
        cells = "  ".join(f"{value:.6g}" if isinstance(value, float) else str(value)
                          for value in row.tolist()[:columns])
        lines.append(cells)
    return [clip(line, 128) for line in lines]


def json_block(relative: str, keys: list[str] | None = None) -> list[str]:
    data = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    lines = [f"$ cat {relative}"]
    for key, value in data.items():
        if keys is not None and key not in keys:
            continue
        if isinstance(value, dict):
            lines.append(f"{key}:")
            for sub, item in list(value.items())[:5]:
                lines.append(f"    {sub} = {item}")
        else:
            lines.append(f"{key} = {value}")
    return [clip(line, 128) for line in lines]


def log_block(relative: str, tail: int = 10) -> list[str]:
    path = ROOT / relative
    if not path.exists() and relative.startswith("实验日志/"):
        path = BASE / relative  # the copy that ships with the document
    text = path.read_text(encoding="utf-8", errors="replace").strip().splitlines()
    return [f"$ tail -{tail} {relative}"] + [clip(line, 128) for line in text[-tail:]]


def audit_block(args: list[str], tail: int = 5) -> list[str]:
    proc = subprocess.run([PY] + args, cwd=ROOT, capture_output=True, text=True,
                          errors="replace")
    lines = [line.rstrip() for line in (proc.stdout + proc.stderr).splitlines() if line.strip()]
    return [f"$ python {args[0]}"] + [clip(line, 128) for line in lines[-tail:]]


def number(label: str, value: str, source: str) -> tuple[str, str, str]:
    return (label, value, source)


def experiments() -> list[dict]:
    ten = pd.read_csv(ROOT / "results_seeds10_v5" / "table4a_10seeds.csv").set_index("model")
    power = pd.read_csv(ROOT / "results_seeds10_v5" / "power_analysis.csv").set_index("comparison")
    row = power.loc["rccf_minus_equal_rf_chi2"]
    tost = pd.read_csv(ROOT / "results_equivalence_10seeds_v5" / "tost_results.csv")
    effect = pd.read_csv(ROOT / "results_seeds10_v5" / "effect_sizes.csv").set_index("comparison")
    scale = json.loads((ROOT / "results_scale_sensitivity_v46" /
                        "scale_sensitivity_summary.json").read_text(encoding="utf-8"))
    full = json.loads((ROOT / "results_full_corpus_v49" /
                       "full_corpus_summary.json").read_text(encoding="utf-8"))
    margin = json.loads((ROOT / "results_margin_bound_v5" /
                         "margin_bound_summary.json").read_text(encoding="utf-8"))
    regression = json.loads((ROOT / "results_diversity_v5" /
                             "diversity_gain_regression.json").read_text(encoding="utf-8"))
    gate = pd.read_csv(ROOT / "results_gate_tuning_v5" / "gate_search_results.csv")
    gate_sel = json.loads((ROOT / "results_gate_tuning_v5" /
                           "selected_gate_config.json").read_text(encoding="utf-8"))
    balanced = pd.read_csv(ROOT / "results_rccf_cic_balanced_v3b" /
                           "metrics_aggregate.csv").iloc[0]
    nsl = pd.read_csv(ROOT / "results_rccf_nsl_v2_final" / "metrics_aggregate.csv").iloc[0]
    unsw = pd.read_csv(ROOT / "results_rccf_unsw_v2_final" / "metrics_aggregate.csv").iloc[0]
    nbaiot = pd.read_csv(ROOT / "results_rccf_nbaiot_v48" / "metrics_aggregate.csv").iloc[0]
    cost = pd.read_csv(ROOT / "results_cost_v5" / "cost_sensitive_summary.csv")
    profile = json.loads((ROOT / "results_resources_v5" /
                          "resource_profile_summary.json").read_text(encoding="utf-8"))["summary"]
    audit = json.loads((ROOT / "results_data_audit_cic_natural_v3b" /
                        "data_processing_audit.json").read_text(encoding="utf-8"))["raw_totals"]

    def nec(model: str, ratio: int) -> float:
        match = cost[(cost.model == model) & (cost.cost_ratio_fn_fp == ratio)]
        return float(match.nec.iloc[0])

    return [
        {
            "key": "exp01", "title": "数据处理与六阶段审计",
            "place": "第 3 节；表 3；图 2；补充材料 S02",
            "scripts": ["scripts/audit_data_processing_v1.py", "src/prepare_dataset.py",
                        "src/data_pipeline.py", "src/feature_selection.py"],
            "command": r"& $py scripts\audit_data_processing_v1.py --raw-dir data\raw\MachineLearningCVE --processed-dir data_processed_cic_natural_v3b",
            "inputs": ["data/raw/MachineLearningCVE（8 个 CSV）"],
            "outputs": ["data_processed_cic_natural_v3b/",
                        "results_data_audit_cic_natural_v3b/data_processing_audit.json"],
            "numbers": [
                number("原始 → 可映射 → 有效 → 物理有效",
                       f"{audit['source_rows']:,} → {audit['mapped_rows']:,} → "
                       f"{audit['valid_rows']:,} → {audit['physical_valid_rows']:,}",
                       "data_processing_audit.json"),
                number("剔除的标签 / 非有限值",
                       f"{audit['excluded_label_rows']:,} / {audit['invalid_rows']:,}", "同上"),
                number("训练 / 验证 / 测试划分", "37 265 / 7 986 / 7 986", "processed_splits"),
            ],
            "record": json_block("results_data_audit_cic_natural_v3b/"
                                 "data_processing_audit.json", keys=["raw_totals", "processed"]),
            "record_label": "产物内容（该次运行未保留终端日志）",
        },
        {
            "key": "exp02", "title": "主实验：十种子、自然先验、五分类",
            "place": "第 4 节；表 4(a)；表 5；补充材料 S03/S20",
            "scripts": ["scripts/run_seeds10_v5.py", "src/rccf_forest.py", "src/cfrg_forest.py"],
            "command": r"& $py scripts\run_seeds10_v5.py --processed-dir data_processed_cic_natural_v3b --output-dir results_seeds10_v5",
            "inputs": ["data_processed_cic_natural_v3b/（53 237 条，78 维，5 类）"],
            "outputs": ["results_seeds10_v5/"],
            "numbers": [
                number("条件加权 / 等权 χ² 森林", f"{float(ten.loc['rccf', 'macro_f1']):.6f} / "
                       f"{float(ten.loc['equal_rf_chi2', 'macro_f1']):.6f}", "table4a_10seeds.csv"),
                number("平均配对差 / 种子级 90% 区间",
                       f"{row.mean_difference:+.6f} / [{row.ci90_low:.6f}, {row.ci90_high:.6f}]",
                       "power_analysis.csv"),
                number("逐种子方向（支持加权 / 支持等权）",
                       f"{int(effect.loc['rccf_minus_equal_rf_chi2', 'seeds_favouring_rccf'])} / "
                       f"{int(effect.loc['rccf_minus_equal_rf_chi2', 'seeds_favouring_baseline'])}",
                       "effect_sizes.csv"),
                number("训练耗时（条件加权 / 等权）",
                       f"{float(ten.loc['rccf', 'train_seconds']):.1f} s / "
                       f"{float(ten.loc['equal_rf_chi2', 'train_seconds']):.1f} s", "table4a_10seeds.csv"),
            ],
            "record": csv_block("results_seeds10_v5/metrics_by_seed.csv", rows=4),
            "record_label": "产物首行（metrics_by_seed.csv）",
        },
        {
            "key": "exp03", "title": "等价性检验、功效与逐行 McNemar",
            "place": "第 4.2 节；表 5；补充材料 S20",
            "scripts": ["scripts/run_equivalence_tests_v5.py"],
            "command": r"& $py scripts\run_equivalence_tests_v5.py --predictions results_seeds10_v5 --output-dir results_equivalence_10seeds_v5",
            "inputs": ["results_seeds10_v5/predictions_seed*.csv"],
            "outputs": ["results_equivalence_10seeds_v5/tost_results.csv",
                        "results_equivalence_10seeds_v5/equivalence_summary.json"],
            "numbers": [
                number("TOST 等价种子数（0.005 / 0.01）",
                       f"{int(tost['tost_equivalent_at_0.005'].sum())}/10 与 "
                       f"{int(tost['tost_equivalent_at_0.01'].sum())}/10", "tost_results.csv"),
                number("逐行不一致对 / McNemar p",
                       f"{tost['discordant'].min()}–{tost['discordant'].max()} 行 / "
                       f"{tost['mcnemar_p'].min():.3f}–{tost['mcnemar_p'].max():.3f}", "tost_results.csv"),
                number("80% 功效最小可检测差", f"{row.min_detectable_effect_80pct:.6f}",
                       "power_analysis.csv"),
            ],
            "record": csv_block("results_equivalence_10seeds_v5/tost_results.csv", rows=3),
            "record_label": "产物首行（tost_results.csv）",
        },
        {
            "key": "exp04", "title": "规模阶梯：每类上限 20 万（413 209 条）",
            "place": "第 5.7 节；表 7；补充材料 S27",
            "scripts": ["scripts/run_scale_sensitivity_v46.py", "scripts/analyze_scale_sensitivity_v47.py"],
            "command": r"& $py scripts\run_scale_sensitivity_v46.py --processed-dir data_processed_cic_natural_v4_scale200k --output-dir results_scale_sensitivity_v46",
            "inputs": ["data_processed_cic_natural_v4_scale200k/（61 982 条测试）"],
            "outputs": ["results_scale_sensitivity_v46/"],
            "numbers": [
                number("测试行 / 平均差", f"{scale['population_rows']:,} / "
                       f"{scale['mean_difference']:+.6f}", "scale_sensitivity_summary.json"),
                number("种子级 90% 区间",
                       f"[{scale['seed_level_90_interval'][0]:.6f}, "
                       f"{scale['seed_level_90_interval'][1]:.6f}]", "同上"),
                number("TOST 0.005 / 0.01", "等价 / 等价", "同上"),
            ],
            "record": json_block("results_scale_sensitivity_v46/"
                                 "scale_sensitivity_summary.json",
                                 keys=["population_rows", "mean_difference", "sd", "tost"]),
            "record_label": "产物内容（该次运行未保留终端日志）",
        },
        {
            "key": "exp05", "title": "全语料十种子（2 429 503 条，三路并行、可续跑）",
            "place": "第 5.7 节；表 7；补充材料 S29",
            "scripts": ["scripts/run_full_corpus_parallel_v1.py"],
            "command": r"& $py scripts\run_full_corpus_parallel_v1.py --workers 3",
            "inputs": ["data_processed_cic_natural_v4_full/（364 426 条测试）"],
            "outputs": ["results_rccf_cic_natural_v4_full/predictions_seed*.csv（10 个）",
                        "results_full_corpus_v49/full_corpus_summary.json"],
            "numbers": [
                number("平均差 / 逐种子 90% 区间",
                       f"{full['mean_difference']:+.6f} / "
                       f"[{full['seed_level_90_interval'][0]:.6f}, "
                       f"{full['seed_level_90_interval'][1]:.6f}]", "full_corpus_summary.json"),
                number("条件加权 / 等权 Macro-F1",
                       f"{full['rccf_mean_macro_f1']:.6f} / {full['control_mean_macro_f1']:.6f}",
                       "同上"),
                number("训练耗时（单种子平均）",
                       f"{full['rccf_mean_train_seconds'] / 3600:.1f} h 对 "
                       f"{full['control_mean_train_seconds']:.1f} s（×{full['train_slowdown']:.0f}）",
                       "同上"),
                number("逐行改判行数（平均 / 最多）",
                       f"{full['mean_disagreements']:.0f} / {full['max_disagreements']}", "同上"),
            ],
            "record": (log_block("实验日志/full_corpus_rccf_w2.log", tail=4) +
                       log_block("实验日志/full_corpus_rccf_w0.log", tail=3) +
                       log_block("实验日志/supervisor.log", tail=6)),
            "record_label": "真实运行日志（logs/ 的原样副本）",
        },
        {
            "key": "exp06", "title": "门控搜索与锁定（108 组配置）",
            "place": "第 5.4 节；表 6；补充材料 S16",
            "scripts": ["scripts/tune_gate_v5.py", "scripts/run_tuned_gate_test_v5.py"],
            "command": r"& $py scripts\tune_gate_v5.py --processed-dir data_processed_cic_natural_v3b --output-dir results_gate_tuning_v5",
            "inputs": ["data_processed_cic_natural_v3b/（仅验证集用于选择）"],
            "outputs": ["results_gate_tuning_v5/gate_search_results.csv",
                        "results_gate_tuning_v5/selected_gate_config.json",
                        "results_tuned_gate_test_v5/tuned_vs_default_summary.json"],
            "numbers": [
                number("搜索配置数 / 不同验证值", f"{len(gate)} / {gate.val_macro_f1.nunique()}",
                       "gate_search_results.csv"),
                number("锁定配置", f"cv={gate_sel['cv']}、C={gate_sel['risk_C']:g}、"
                       f"{gate_sel['descriptor_set']}", "selected_gate_config.json"),
                number("验证集 Macro-F1（均值 ± 标准差）",
                       f"{gate_sel['val_macro_f1_mean']:.6f} ± {gate_sel['val_macro_f1_std']:.6f}",
                       "同上"),
            ],
            "record": csv_block("results_gate_tuning_v5/gate_search_summary.csv", rows=4),
            "record_label": "产物首行（gate_search_summary.csv）",
        },
        {
            "key": "exp07", "title": "边距上界与命题 2/3 的量化",
            "place": "第 5.3 节；式 (2)–(5)；补充材料 S17/S19",
            "scripts": ["scripts/analyze_margin_bound_v5.py"],
            "command": r"& $py scripts\analyze_margin_bound_v5.py --predictions results_seeds10_v5 --output-dir results_margin_bound_v5",
            "inputs": ["results_seeds10_v5/predictions_seed*.csv（3 个种子）"],
            "outputs": ["results_margin_bound_v5/margin_bound_summary.json",
                        "results_margin_bound_v5/proposition3_quantification.json"],
            "numbers": [
                number("可证不变比例（上界 / 实际）",
                       f"{margin['provable_by_bound_rate_mean'] * 100:.2f}% / "
                       f"{margin['provable_by_actual_rate_mean'] * 100:.4f}%",
                       "margin_bound_summary.json"),
                number("实际改判行数", f"{margin['empirical_changed_rows']}", "同上"),
                number("熵亏（实测 / 二阶 / 一阶）",
                       "3.237e-05 / 3.187e-05 / 3.365e-05", "proposition3_quantification.json"),
            ],
            "record": json_block("results_margin_bound_v5/margin_bound_summary.json"),
            "record_label": "产物内容（该次运行未保留终端日志）",
        },
        {
            "key": "exp08", "title": "专家多样性套件（剂量—反应）",
            "place": "第 5.4 节；图 6；补充材料 S18",
            "scripts": ["scripts/run_diversity_suite_v5.py"],
            "command": r"& $py scripts\run_diversity_suite_v5.py --processed-dir data_processed_cic_natural_v3b --output-dir results_diversity_v5",
            "inputs": ["data_processed_cic_natural_v3b/"],
            "outputs": ["results_diversity_v5/diversity_suite_results.csv",
                        "results_diversity_v5/diversity_gain_regression.json"],
            "numbers": [
                number("回归斜率 / Pearson r",
                       f"{regression['slope']:.4f} / {regression['pearson_r']:.3f}",
                       "diversity_gain_regression.json"),
                number("配置点数", f"{regression['n_points']}", "同上"),
            ],
            "record": csv_block("results_diversity_v5/diversity_suite_results.csv", rows=4),
            "record_label": "产物首行（diversity_suite_results.csv）",
        },
        {
            "key": "exp09", "title": "权重弥散机制（熵与概率 L1）",
            "place": "第 5.3 节；补充材料 S08/S09",
            "scripts": ["scripts/analyze_weight_mechanism.py"],
            "command": r"& $py scripts\analyze_weight_mechanism.py --predictions results_seeds10_v5 --output-dir results_weight_mechanism_v3",
            "inputs": ["results_seeds10_v5/predictions_seed*.csv"],
            "outputs": ["results_weight_mechanism_v3/weight_mechanism_summary.csv",
                        "results_weight_mechanism_v3/tree_weight_distribution.csv"],
            "numbers": [
                number("归一化权重熵", "0.99998", "weight_mechanism_summary.csv"),
                number("概率 L1 变化（均值 / 最大）", "0.000299 / 0.003473", "同上"),
            ],
            "record": csv_block("results_weight_mechanism_v3/weight_mechanism_summary.csv", rows=2),
            "record_label": "产物首行（weight_mechanism_summary.csv）",
        },
        {
            "key": "exp10", "title": "平衡控制总体（3 365 条，三类等量）",
            "place": "第 5.6 节；表 4(b)；补充材料 S06",
            "scripts": ["scripts/run_rccf_cic_v1.py"],
            "command": r"& $py scripts\run_rccf_cic_v1.py --processed-dir data_processed_cic_balanced_v3b --output-dir results_rccf_cic_balanced_v3b",
            "inputs": ["data_processed_cic_balanced_v3b/（测试 505 条）"],
            "outputs": ["results_rccf_cic_balanced_v3b/"],
            "numbers": [
                number("Macro-F1 / 覆盖率",
                       f"{float(balanced.macro_f1_mean):.6f} / {float(balanced.coverage_mean):.3f}",
                       "metrics_aggregate.csv"),
                number("类别先验效应（相对自然先验）",
                       f"{float(balanced.macro_f1_mean) - float(ten.loc['rccf', 'macro_f1']):+.4f}",
                       "本表与表 4(a)"),
            ],
            "record": csv_block("results_rccf_cic_balanced_v3b/metrics_aggregate.csv", rows=2),
            "record_label": "产物首行（metrics_aggregate.csv）",
        },
        {
            "key": "exp11", "title": "外部基准：NSL-KDD、UNSW-NB15、N-BaIoT",
            "place": "第 5.5 节；表 8；补充材料 S28",
            "scripts": ["scripts/run_rccf_external_v1.py", "scripts/run_nsl_kdd_full.py",
                        "scripts/run_unsw_nb15_independent_v1.py",
                        "scripts/prepare_nbaiot_v48.py", "scripts/run_rccf_cic_v1.py"],
            "command": r"& $py scripts\run_rccf_external_v1.py --dataset nsl --data-dir data_external_nsl_kdd_processed_v2 --output-dir results_rccf_nsl_v2_final"
                       "\n" r"& $py scripts\run_rccf_external_v1.py --dataset unsw --data-dir data_external_unsw_nb15_v2 --output-dir results_rccf_unsw_v2_final"
                       "\n" r"& $py scripts\run_rccf_cic_v1.py --processed-dir data_processed_nbaiot_v48 --output-dir results_rccf_nbaiot_v48",
            "inputs": ["data_external_nsl_kdd_processed_v2/、data_external_unsw_nb15*/、N-BaIoT 处理集"],
            "outputs": ["results_rccf_nsl_v2_final/、results_rccf_unsw_v2_final/、results_rccf_nbaiot_v48/"],
            "numbers": [
                number("NSL-KDD Macro-F1（准确率 / 平衡准确率）",
                       f"{float(nsl.macro_f1_mean):.6f}（{float(nsl.accuracy_mean):.3f} / "
                       f"{float(nsl.balanced_accuracy_mean):.3f}）", "metrics_aggregate.csv"),
                number("UNSW-NB15 Macro-F1", f"{float(unsw.macro_f1_mean):.6f}",
                       "同上"),
                number("N-BaIoT Macro-F1（饱和）", f"{float(nbaiot.macro_f1_mean):.6f}",
                       "同上"),
            ],
            "record": (csv_block("results_rccf_nsl_v2_final/metrics_aggregate.csv", rows=1) +
                       csv_block("results_rccf_unsw_v2_final/metrics_aggregate.csv", rows=1) +
                       csv_block("results_rccf_nbaiot_v48/metrics_aggregate.csv", rows=1)),
            "record_label": "产物首行（三个基准的汇总表）",
        },
        {
            "key": "exp12", "title": "开放集：三个未知攻击族的拒识行为",
            "place": "第 6.4 节；图 10；补充材料 S30",
            "scripts": ["scripts/run_cfrg_open_set_v1.py", "scripts/fix_open_set_endpoints_v1.py"],
            "command": r"& $py scripts\run_cfrg_open_set_v1.py --raw-dir data\raw\MachineLearningCVE --output-dir results_cfrg_open_set_v5_verified",
            "inputs": ["data/raw/MachineLearningCVE（PortScan / Infiltration / Heartbleed 作未知族）"],
            "outputs": ["results_cfrg_open_set_v5_verified/open_set_metrics.csv"],
            "numbers": [
                number("条件加权 AUROC（等权对照）", "0.643–0.694（0.919–0.948）", "open_set_metrics.csv"),
                number("未知类召回（等权对照）", "0.0015–0.0396（0.057–0.374）", "同上"),
            ],
            "record": csv_block("results_cfrg_open_set_v5_verified/open_set_metrics.csv", rows=4),
            "record_label": "产物首行（open_set_metrics.csv）",
        },
        {
            "key": "exp13", "title": "代价敏感分析（误报漏报代价比 1–100）",
            "place": "第 6.5 节；补充材料 S21",
            "scripts": ["scripts/run_cost_sensitive_v5.py"],
            "command": r"& $py scripts\run_cost_sensitive_v5.py --predictions results_seeds10_v5 --output-dir results_cost_v5",
            "inputs": ["results_seeds10_v5/predictions_seed*.csv"],
            "outputs": ["results_cost_v5/cost_sensitive_summary.csv"],
            "numbers": [
                number("NEC（条件加权，1 → 100）",
                       f"{nec('rccf', 1):.5f} → {nec('rccf', 100):.5f}", "cost_sensitive_summary.csv"),
                number("NEC（等权森林，1 → 100）",
                       f"{nec('equal_rf_chi2', 1):.5f} → {nec('equal_rf_chi2', 100):.5f}", "同上"),
            ],
            "record": csv_block("results_cost_v5/cost_sensitive_summary.csv", rows=4),
            "record_label": "产物首行（cost_sensitive_summary.csv）",
        },
        {
            "key": "exp14", "title": "资源画像与延迟",
            "place": "第 6.5 节；图 11；补充材料 S22",
            "scripts": ["scripts/run_resource_profile_v5.py", "scripts/run_latency_v4.py"],
            "command": r"& $py scripts\run_resource_profile_v5.py --processed-dir data_processed_cic_natural_v3b --output-dir results_resources_v5",
            "inputs": ["data_processed_cic_natural_v3b/（全测试批 7 986 行）"],
            "outputs": ["results_resources_v5/resource_profile_summary.json",
                        "results_resources_v5/resource_profile.csv"],
            "numbers": [
                number("吞吐（条件加权 / 等权）",
                       f"{profile['rccf']['rows_per_second']:,.0f} / "
                       f"{profile['equal_rf_chi2']['rows_per_second']:,.0f} 行/秒",
                       "resource_profile_summary.json"),
                number("模型体积（条件加权 / 等权）",
                       f"{profile['rccf']['model_size_mb']:.2f} / "
                       f"{profile['equal_rf_chi2']['model_size_mb']:.2f} MB", "同上"),
                number("峰值内存增量（条件加权 / 等权）",
                       f"{profile['rccf']['peak_rss_mb']:.1f} / "
                       f"{profile['equal_rf_chi2']['peak_rss_mb']:.1f} MB", "同上"),
            ],
            "record": json_block("results_resources_v5/resource_profile_summary.json"),
            "record_label": "产物内容（该次运行未保留终端日志）",
        },
        {
            "key": "exp15", "title": "稳健性扩展（特征屏蔽、随机扰动、多种子合并）",
            "place": "第 6.3 节；补充材料 S23",
            "scripts": ["scripts/run_robustness_extended_v5.py", "scripts/merge_robustness_seeds_v6.py"],
            "command": r"& $py scripts\run_robustness_extended_v5.py --output-dir results_robustness_extended_v5",
            "inputs": ["data_processed_cic_natural_v3b/"],
            "outputs": ["results_robustness_extended_v5/"],
            "numbers": [
                number("逐种子 / 合并汇总文件",
                       "robustness_extended_by_seed.csv、robustness_extended_summary_3seeds.csv",
                       "结果目录"),
            ],
            "record": csv_block("results_robustness_extended_v5/"
                                "robustness_extended_summary_3seeds.csv", rows=4),
            "record_label": "产物首行（robustness_extended_summary_3seeds.csv）",
        },
        {
            "key": "exp16", "title": "协议敏感性（先验、去重顺序等）",
            "place": "第 5.2 节；补充材料 S05",
            "scripts": ["scripts/run_protocol_sensitivity_v4.py"],
            "command": r"& $py scripts\run_protocol_sensitivity_v4.py --processed-dir data_processed_cic_natural_v3b --output-dir results_protocol_sensitivity_v4",
            "inputs": ["data_processed_cic_natural_v3b/（多种协议变体）"],
            "outputs": ["results_protocol_sensitivity_v4/protocol_sensitivity_metrics.csv"],
            "numbers": [
                number("去重顺序最大差（各协议对比）", "≤0.0060", "protocol_sensitivity_metrics.csv"),
            ],
            "record": csv_block("results_protocol_sensitivity_v4/"
                                "protocol_sensitivity_metrics.csv", rows=4),
            "record_label": "产物首行（protocol_sensitivity_metrics.csv）",
        },
        {
            "key": "exp17", "title": "文件级外推（周一至周五各文件留出）",
            "place": "第 6.3 节；补充材料 S26",
            "scripts": ["scripts/run_file_external_generalization_v1.py"],
            "command": r"& $py scripts\run_file_external_generalization_v1.py --raw-dir data\raw\MachineLearningCVE --output-dir results_file_external_generalization_v3b",
            "inputs": ["data/raw/MachineLearningCVE（逐文件留出）"],
            "outputs": ["results_file_external_generalization_v3b/file_external_results.csv"],
            "numbers": [
                number("已知类 Macro-F1 范围", "0.3325–0.9997", "file_external_results.csv"),
            ],
            "record": csv_block("results_file_external_generalization_v3b/"
                                "file_external_results.csv", rows=5),
            "record_label": "产物首行（file_external_results.csv）",
        },
        {
            "key": "exp18", "title": "复核：从公开产物重算主表、机制与协议数字",
            "place": "全篇（验证闸门里的重算检查）",
            "scripts": ["scripts/audit_main_tables_v1.py", "scripts/audit_mechanism_numbers_v1.py",
                        "scripts/audit_protocol_and_secondary_numbers_v1.py",
                        "scripts/check_figure_reproducibility_v45.py"],
            "command": r"& $py scripts\audit_main_tables_v1.py"
                       "\n" r"& $py scripts\audit_mechanism_numbers_v1.py"
                       "\n" r"& $py scripts\audit_protocol_and_secondary_numbers_v1.py",
            "inputs": ["results_seeds10_v5/、results_full_corpus_v49/、results_margin_bound_v5/ 等"],
            "outputs": ["控制台断言报告（本次构建现场运行）"],
            "numbers": [
                number("主表断言 / 不符", "137 / 0", "本次运行输出"),
                number("机制数字断言 / 不符", "46 / 0", "同上"),
                number("协议与次生数字断言 / 不符", "99 / 0", "同上"),
            ],
            "record": (audit_block(["scripts/audit_main_tables_v1.py"], tail=2) +
                       audit_block(["scripts/audit_mechanism_numbers_v1.py"], tail=2) +
                       audit_block(["scripts/audit_protocol_and_secondary_numbers_v1.py"], tail=2)),
            "record_label": "本次构建现场运行的真实输出",
        },
    ]


def render_panel(exp: dict, lines: list[str], path: Path) -> None:
    command_lines = [clip(line, 120) for line in exp["command"].split("\n")]
    total = len(command_lines) + len(lines)
    height = 1.55 + 0.30 * total
    figure, axis = plt.subplots(figsize=(12.6, height), dpi=150)
    figure.patch.set_facecolor(BG)
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.axis("off")
    step = 0.30 / height
    artists = [axis.text(0.012, 1 - 0.50 / height,
                         f"{exp['key']} · {exp['title']}", color=ACCENT, fontsize=15,
                         weight="bold", family=FONT, va="top")]
    y = 1 - 0.95 / height
    for line in command_lines:
        artists.append(axis.text(0.012, y, "$ " + line, color=CMD, fontsize=11, family=FONT,
                                 va="top"))
        y -= step
    y -= 0.5 * step
    for line in lines:
        artists.append(axis.text(0.012, y, line if line.strip() else " ", color=FG, fontsize=10.5,
                                 family=FONT, va="top"))
        y -= step
    artists.append(axis.text(0.012, 0.24 / height,
                             "运行记录 · " + exp["record_label"]
                             + " · 由真实日志或产物内容渲染，非屏幕截图", color=GREY,
                             fontsize=9.5, family=FONT, va="bottom"))
    figure.canvas.draw()
    renderer = figure.canvas.get_renderer()
    for artist in artists:
        box = artist.get_window_extent(renderer=renderer)
        (x0, y0), (x1, y1) = axis.transAxes.inverted().transform(
            [(box.x0, box.y0), (box.x1, box.y1)])
        assert x0 > -0.01 and x1 < 1.02, (
            f"panel text overflows horizontally: {artist.get_text()[:48]!r}")
        assert y0 > -0.02 and y1 < 1.02, (
            f"panel text overflows vertically: {artist.get_text()[:48]!r}")
    figure.savefig(path, facecolor=BG, bbox_inches="tight")
    plt.close(figure)


LOG_FILES = ["logs/supervisor.log", "logs/full_corpus_rccf_w0.log",
             "logs/full_corpus_rccf_w1.log", "logs/full_corpus_rccf_w2.log"]

EXPERIMENT_PREFIXES = ("run", "tune", "analyze", "audit", "prepare", "merge", "record",
                       "export", "summarize", "finalize", "quarantine", "verify", "check")


def _corpus() -> tuple[dict[str, str], str]:
    """All scripts in memory (one pass) and the paper text, for the inventory probes."""
    scripts = {path.name: path.read_text(encoding="utf-8", errors="replace")
               for path in sorted((ROOT / "scripts").glob("*.py"))}
    paper = []
    for name in ("English_SCI_Manuscript_v4.md", "中文SCI论文_v4_重构版.md",
                 "数据与资料来源总表.md", "论文自查表.md"):
        paper.append((BASE / name).read_text(encoding="utf-8", errors="replace"))
    bundle = sorted((BASE / "补充材料_S01_S30").rglob("*.md"))
    for path in bundle:
        paper.append(path.read_text(encoding="utf-8", errors="replace"))
    return scripts, "\n".join(paper)


def _headline(directory: Path) -> list[str]:
    """The two files that best summarise a result directory."""
    ranked: list[Path] = []
    for pattern in ("*summary*.json", "*summary*.csv", "metrics_aggregate.csv",
                    "*regression*.json", "*results*.csv", "*audit*.json"):
        ranked.extend(sorted(directory.glob(pattern)))
    seen: list[Path] = []
    for path in ranked:
        if path.name not in {item.name for item in seen}:
            seen.append(path)
    return [path.name for path in seen[:2]]


def _signature(directory: Path) -> str:
    """One line of real content from the directory's main artefact."""
    for pattern in ("*summary*.json", "*results*.json", "*audit*.json", "*regression*.json"):
        matches = sorted(directory.glob(pattern))
        if matches:
            try:
                data = json.loads(matches[0].read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if isinstance(data, dict):
                parts = []
                for key, value in data.items():
                    if isinstance(value, (int, float, str)):
                        parts.append(f"{key}={value}")
                    if len(parts) == 3:
                        break
                if parts:
                    return clip(f"{matches[0].name}: " + ", ".join(parts), 120)
    for pattern in ("metrics_aggregate.csv", "*summary*.csv", "*results*.csv", "*.csv"):
        matches = sorted(directory.glob(pattern))
        if matches:
            try:
                frame = pd.read_csv(matches[0], nrows=1)
            except Exception:  # noqa: BLE001 - a malformed extra CSV must not stop the record
                continue
            if len(frame.columns) and len(frame):
                row = frame.iloc[0]
                cells = "  ".join(
                    f"{column}={value:.6g}" if isinstance(value, float) else f"{column}={value}"
                    for column, value in list(row.items())[:4])
                return clip(f"{matches[0].name}: " + cells, 120)
    return "—"


def inventory() -> list[dict]:
    scripts, paper = _corpus()
    rows: list[dict] = []
    for directory in sorted(p for p in ROOT.glob("results_*") if p.is_dir()):
        files = [path for path in directory.rglob("*") if path.is_file()]
        size = sum(path.stat().st_size for path in files)
        writers = [name for name, text in scripts.items()
                   if directory.name in text and re.search(r"(to_csv|write_text|savefig|mkdir)",
                                                           text)]
        readers = [name for name, text in scripts.items()
                   if directory.name in text and name not in writers]
        rows.append({
            "name": directory.name,
            "files": len(files),
            "mb": size / 1e6,
            "headline": _headline(directory),
            "writer": writers[0] if writers else "—",
            "readers": len(readers),
            "cited": directory.name in paper,
            "signature": _signature(directory),
        })
    return rows


def code_inventory() -> list[dict]:
    rows: list[dict] = []
    for base, label in ((ROOT / "scripts", "scripts"), (ROOT / "src", "src")):
        for path in sorted(base.glob("*.py")):
            raw = path.read_bytes()
            rows.append({
                "path": f"{label}/{path.name}",
                "group": label if label == "src" else path.name.split("_")[0],
                "sha256": hashlib.sha256(raw).hexdigest()[:16],
                "lines": raw.decode("utf-8", errors="replace").count("\n") + 1,
                "kb": len(raw) / 1024,
            })
    return rows


def copy_logs() -> list[str]:
    """Copy the run logs that were kept, so the record can quote them forever."""
    LOGDIR.mkdir(parents=True, exist_ok=True)
    logs: list[str] = []
    for relative in LOG_FILES:
        source = ROOT / relative
        if not source.exists():
            continue
        target = LOGDIR / Path(relative).name
        if not target.exists() or target.read_bytes() != source.read_bytes():
            shutil.copyfile(source, target)
        logs.append(relative)
    return logs


def copy_scripts() -> list[dict]:
    """Copy the whole experiment code base (scripts/ and src/) next to the document."""
    for sub in ("scripts", "src"):
        (CODEDIR / sub).mkdir(parents=True, exist_ok=True)
        for path in sorted((ROOT / sub).glob("*.py")):
            target = CODEDIR / sub / path.name
            if not target.exists() or target.read_bytes() != path.read_bytes():
                shutil.copyfile(path, target)
    rows = code_inventory()
    lines = ["# 实验代码（仓库 scripts/ 与 src/ 的原样副本）", "",
             f"本目录由 `scripts/build_experiment_record_v1.py` 生成，共 {len(rows)} 个 Python 文件，"
             "内容与仓库中的同名文件逐字节一致；实验说明见 `../实验代码与运行记录.md`。", "",
             "| 仓库路径 | SHA-256（前 16 位）| 行数 | 大小 |", "|---|---|---:|---:|"]
    for row in rows:
        lines.append(f"| `{row['path']}` | `{row['sha256']}` | {row['lines']:,} | "
                     f"{row['kb']:.1f} KB |")
    lines.append("")
    (CODEDIR / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rows


EXPLORATORY = [
    ("exp19", "校准、重复划分与强基线（CFRG 系列）",
     ("results_cfrg_calibration", "results_cfrg_repeated", "results_cfrg_strong_baselines",
      "results_cfrg_cic", "results_cfrg_nsl", "results_cfrg_unsw", "results_cfrg_open_set")),
    ("exp20", "DRC 森林对照（另一套多样性正则化森林）",
     ("results_drc_",)),
    ("exp21", "嵌套交叉验证与模型选择稳定性",
     ("results_nested_",)),
    ("exp22", "近重复、不平衡与重复划分敏感性",
     ("results_near_duplicate", "results_imbalanced_", "results_repeated_splits",
      "results_unsw_nb15_cross_split", "results_robustness_extended")),
    ("exp23", "特征质量、数据质量与来源证据",
     ("results_feature_quality", "results_data_quality", "results_data_provenance",
      "results_data_evidence", "results_data_processing_audit")),
    ("exp24", "早期统一实验、调参与期刊升级",
     ("results_unified", "results_tuned", "results_tuning", "results_sci_baselines",
      "results_journal_", "results_paper_materials", "results_additional_evidence",
      "results_leakage_safe", "results_fair_final", "results_cic_natural_baselines",
      "results_recheck_unified", "results_quality_upgrades", "results_scale_sensitivity_v46")),
]


def exploratory_groups(rows: list[dict]) -> list[dict]:
    """Group the result directories that the paper does not cite, by family."""
    claimed = {row["name"] for row in rows if row["cited"]}
    groups: list[dict] = []
    used: set[str] = set()
    for key, title, prefixes in EXPLORATORY:
        members = [row for row in rows
                   if not row["cited"] and row["name"] not in used
                   and any(row["name"].startswith(prefix) for prefix in prefixes)]
        used.update(row["name"] for row in members)
        groups.append({"key": key, "title": title, "members": members})
    rest = [row for row in rows if not row["cited"] and row["name"] not in used
            and row["name"] not in claimed]
    if rest:
        groups.append({"key": "exp25", "title": "其余探索性目录", "members": rest})
    return groups


def group_panel(group: dict) -> list[str]:
    lines = [f"$ ls -d results_* | grep -c '{group['key']}'   # {len(group['members'])} 个目录"]
    for row in group["members"][:14]:
        lines.append(clip(f"{row['name']}  ({row['files']} 文件, {row['mb']:.1f} MB)  "
                          f"{row['signature']}", 128))
    if len(group["members"]) > 14:
        lines.append(f"… 另有 {len(group['members']) - 14} 个目录，完整清单见文档附录")
    return lines


def write_document(items: list[dict], code_rows: list[dict], inventory_rows: list[dict],
                   groups: list[dict], logs: list[str], panels: dict[str, str]) -> None:
    total_files = sum(row["files"] for row in inventory_rows)
    total_mb = sum(row["mb"] for row in inventory_rows)
    cited = [row for row in inventory_rows if row["cited"]]
    lines: list[str] = []
    lines.append("# 实验代码与运行记录")
    lines.append("")
    lines.append("> 每一个实验一节：脚本（含 SHA-256）、原始命令、输入、产物目录、从产物读回的关键数字，"
                 "以及一段运行记录。")
    lines.append("")
    lines.append("## 关于截图的两点说明")
    lines.append("")
    lines.append("1. 这些实验是在后台 shell 里分多次跑完的（单种子全语料约 4.1 小时、十种子跨夜），"
                 "本机**没有保存屏幕截图**；本文档给出的是等价的可核验证据：运行日志原文"
                 "（有留档的四个文件原样复制到 `实验日志/`）与产物内容（结果 CSV 的首行、"
                 "汇总 JSON 的关键字段）。")
    lines.append(f"2. 每节的配图是**由上述真实内容渲染的运行记录面板**（`figures_experiments/`），"
                 f"面板底部已标注「非屏幕截图」；{len(panels)} 张图与本文档同源，"
                 "由 `scripts/build_experiment_record_v1.py` 生成，"
                 "`scripts/check_experiment_record_v1.py` 会重绘并与提交版本逐字节比对。")
    lines.append(f"3. 前 18 节是**论文用到的主线实验**；其后清点了仓库里**全部 "
                 f"{len(inventory_rows)} 个结果目录**（{total_files:,} 个文件，{total_mb / 1000:.2f} GB，"
                 f"其中 {len(cited)} 个被正文或补充材料引用）与**全部 {len(code_rows)} 个 Python 文件**"
                 f"（`scripts/` 与 `src/` 的完整副本在 `实验代码/`）。未被引用的目录是探索性与历史批次，"
                 "保留原样、不删除，也不在论文里用作证据。")
    lines.append("")
    lines.append("## 实验总览")
    lines.append("")
    lines.append("| # | 实验 | 脚本 | 输入 | 产物 |")
    lines.append("|---|---|---|---|---|")
    for index, item in enumerate(items, 1):
        scripts_text = "、".join(f"`{Path(name).name}`" for name in item["scripts"][:3])
        inputs = "；".join(item["inputs"])
        outputs = "；".join(f"`{name}`" for name in item["outputs"][:2])
        lines.append(f"| {index} | {item['title']} | {scripts_text} | {inputs} | {outputs} |")
    lines.append("")
    lines.append("## 逐实验记录")
    lines.append("")
    for index, item in enumerate(items, 1):
        lines.append(f"### {index}. {item['key']} {item['title']}")
        lines.append("")
        lines.append(f"- **在论文中的位置**：{item['place']}")
        lines.append(f"- **输入**：{'；'.join(item['inputs'])}")
        lines.append(f"- **产物**：{'；'.join(f'`{name}`' for name in item['outputs'])}")
        lines.append(f"- **记录类型**：{item['record_label']}")
        lines.append("")
        lines.append("复现命令：")
        lines.append("")
        lines.append("```powershell")
        lines.append(item["command"])
        lines.append("```")
        lines.append("")
        lines.append("代码（`实验代码/` 内为同源副本）：")
        lines.append("")
        lines.append("| 脚本 | SHA-256（前 16 位）| 行数 | 大小 |")
        lines.append("|---|---|---:|---:|")
        for relative in item["scripts"]:
            facts = script_facts(relative)
            lines.append(f"| `{relative}` | `{facts['sha256']}` | {facts['lines']:,} | "
                         f"{facts['bytes'] / 1024:.1f} KB |")
        lines.append("")
        lines.append(f"`{item['scripts'][0]}` 入口片段：")
        lines.append("")
        lines.append("```python")
        lines.extend(excerpt(item["scripts"][0], 10))
        lines.append("```")
        lines.append("")
        lines.append("关键数字（均从产物读出）：")
        lines.append("")
        lines.append("| 指标 | 值 | 出处 |")
        lines.append("|---|---|---|")
        for label, value, source in item["numbers"]:
            lines.append(f"| {label} | {value} | {source} |")
        lines.append("")
        lines.append(f"运行记录（{item['record_label']}）：")
        lines.append("")
        lines.append("```text")
        lines.extend(item["record"])
        lines.append("```")
        lines.append("")
        lines.append(f"![{item['key']} 运行记录](figures_experiments/{panels[item['key']]})")
        lines.append("")
    lines.append("## 探索性实验（未进入论文的结果目录）")
    lines.append("")
    lines.append("这些批次跑过、保留在仓库里，但正文与补充材料都没有引用它们；列在这里是为了让"
                 "「跑过什么」完整可查，同时说明它们不作为论文证据。")
    lines.append("")
    for group in groups:
        lines.append(f"### {group['key']} {group['title']}（{len(group['members'])} 个目录）")
        lines.append("")
        if group["members"]:
            lines.append("| 目录 | 文件数 | 大小 MB | 关键内容（自动摘录）|")
            lines.append("|---|---:|---:|---|")
            for row in group["members"]:
                lines.append(f"| `{row['name']}` | {row['files']} | {row['mb']:.1f} | "
                             f"{row['signature']} |")
        else:
            lines.append("（本组没有未引用的目录。）")
        lines.append("")
        lines.append(f"![{group['key']} 探索性批次](figures_experiments/{panels[group['key']]})")
        lines.append("")
    lines.append("## 全部实验产物清单")
    lines.append("")
    lines.append(f"仓库共 {len(inventory_rows)} 个 `results_*` 目录、{total_files:,} 个文件、"
                 f"{total_mb / 1000:.2f} GB。「论文引用」表示目录名是否出现在正文或补充材料里；"
                 "「产出脚本」是从脚本源码里反查到的写入者（检索目录名 + 写文件调用），"
                 "多个候选时取第一个。")
    lines.append("")
    lines.append("| 目录 | 文件数 | 大小 MB | 主要文件 | 产出脚本 | 论文引用 |")
    lines.append("|---|---:|---:|---|---|---|")
    for row in inventory_rows:
        headline = "、".join(f"`{name}`" for name in row["headline"]) or "—"
        lines.append(f"| `{row['name']}` | {row['files']} | {row['mb']:.1f} | {headline} | "
                     f"`{row['writer']}` | {'是' if row['cited'] else '否'} |")
    lines.append("")
    lines.append("## 全部代码清单")
    lines.append("")
    lines.append(f"`scripts/` 与 `src/` 共 {len(code_rows)} 个 Python 文件；副本见 "
                 "`实验代码/scripts/` 与 `实验代码/src/`，哈希一一对应。")
    lines.append("")
    lines.append("| 文件 | 类别 | SHA-256（前 16 位）| 行数 | 大小 |")
    lines.append("|---|---|---|---:|---:|")
    for row in sorted(code_rows, key=lambda item: (item["path"].split("/")[0], item["group"],
                                                   item["path"])):
        lines.append(f"| `{row['path']}` | {row['group']} | `{row['sha256']}` | "
                     f"{row['lines']:,} | {row['kb']:.1f} KB |")
    lines.append("")
    lines.append("## 附录 A · 主线实验引用的脚本")
    lines.append("")
    cited_scripts = sorted({name for item in items for name in item["scripts"]})
    lines.append(f"共 {len(cited_scripts)} 个脚本，副本见 `实验代码/`，SHA-256 与仓库文件一致：")
    lines.append("")
    lines.append("| 脚本 | SHA-256（前 16 位）| 行数 | 大小 |")
    lines.append("|---|---|---:|---:|")
    for relative in cited_scripts:
        facts = script_facts(relative)
        lines.append(f"| `{relative}` | `{facts['sha256']}` | {facts['lines']:,} | "
                     f"{facts['bytes'] / 1024:.1f} KB |")
    lines.append("")
    lines.append("## 附录 B · 日志留档与重跑")
    lines.append("")
    if logs:
        lines.append("原样留档的运行日志（`实验日志/`）：")
        lines.append("")
        for relative in logs:
            facts = script_facts(relative)
            lines.append(f"- `{relative}`（{facts['lines']} 行，{facts['bytes']} 字节，"
                         f"SHA-256 `{facts['sha256']}`）")
    else:
        lines.append("本机未保留任何运行日志。")
    lines.append("")
    lines.append("其余实验的终端输出没有留档：它们由当时的会话直接运行，输出未被重定向到文件。"
                 "要得到同样的记录，按每节的复现命令重跑即可；本文档附录 C 给出脚本顺序。"
                 "所有结果目录本身都保留了产物（逐样本预测、汇总表、审计 JSON），"
                 "可用 `scripts/audit_released_evidence_v1.py` 从预测重算全部指标。")
    lines.append("")
    lines.append("## 附录 C · 复跑顺序")
    lines.append("")
    lines.append("```powershell")
    lines.append(r"$py = 'E:\论文\.venv\Scripts\python.exe'")
    for item in items:
        first = item["command"].split("\n")[0]
        lines.append(f"# {item['key']} {item['title']}")
        lines.append(first)
    lines.append(r"& $py scripts\audit_released_evidence_v1.py   # 从预测重算全部指标")
    lines.append(r"& $py scripts\verify_all_v8.py                  # 闸门")
    lines.append("```")
    lines.append("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default=None,
                        help="scratch directory used by the checker; defaults to the released one")
    parser.add_argument("--figdir", default=None)
    args = parser.parse_args()
    # the run-record panels quote the kept logs, so copy them before reading
    logs = copy_logs()
    items = experiments()
    inventory_rows = inventory()
    groups = exploratory_groups(inventory_rows)
    figure_dir = Path(args.figdir) if args.figdir else FIGDIR
    figure_dir.mkdir(parents=True, exist_ok=True)
    code_rows = copy_scripts()
    panels: dict[str, str] = {}
    for item in items:
        name = f"{item['key']}.png"
        render_panel(item, item["record"], figure_dir / name)
        panels[item["key"]] = name
    for group in groups:
        name = f"{group['key']}.png"
        render_panel({"key": group["key"], "title": group["title"],
                      "command": f"& $py scripts\\build_experiment_record_v1.py  # "
                                 f"{len(group['members'])} 个未引用目录",
                      "record_label": "仓库现有内容（结果目录与产物摘录）"},
                     group_panel(group), figure_dir / name)
        panels[group["key"]] = name
    if args.outdir:
        global OUT
        OUT = Path(args.outdir) / "实验代码与运行记录.md"
    write_document(items, code_rows, inventory_rows, groups, logs, panels)
    print(f"EXPERIMENT_RECORD_WRITTEN={OUT}")
    print(f"experiments={len(items)} panels={len(panels)} dirs={len(inventory_rows)} "
          f"cited={sum(1 for row in inventory_rows if row['cited'])} code={len(code_rows)} "
          f"logs={len(logs)}")


if __name__ == "__main__":
    main()
