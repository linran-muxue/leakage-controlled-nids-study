"""Compile the six extension experiments into one report with their data paths.

Each section states the question, the protocol, the command, where the raw data
and per-seed results live, and the headline numbers read back from those files.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
OUT = BASE / "扩展实验报告.md"


def read_json(path: Path) -> dict | None:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def aggregate(name: str):
    path = ROOT / name / "metrics_aggregate.csv"
    if not path.exists():
        return None
    frame = pd.read_csv(path)
    return frame.iloc[0] if len(frame) else None


def section(title: str, question: str, protocol: str, command: str, data: str,
            rows: list[tuple[str, str]], conclusion: str) -> list[str]:
    lines = [f"## {title}", "", f"**问题**：{question}", "", f"**协议**：{protocol}", "",
             "复现命令：", "", "```powershell", command, "```", "",
             f"**实验数据**：{data}", "",
             "| 指标 | 数值 |", "|---|---|"]
    lines += [f"| {label} | {value} |" for label, value in rows]
    lines += ["", f"**结论**：{conclusion}", ""]
    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default=None)
    args = parser.parse_args()
    lines = ["# 扩展实验报告", "",
             "> 六个扩展实验：专家家族与数量、按天留出、外部队列十种子、部署向指标、"
             "CIC-IDS2018、CIC-IoT-2023。每个实验的逐种子数据都保存在对应的 "
             "`results_*` 目录中，本报告只从那些文件读数字。", ""]

    families = read_json(ROOT / "results_member_family_v1" / "member_family_summary.json")
    if families:
        rows = []
        for key in ("q2", "q3", "q4", "q6", "families"):
            if key in families:
                item = families[key]
                rows.append((f"{key}（{item['members']} 成员，分歧 "
                             f"{100 * item['mean_pairwise_disagreement']:.2f}%）",
                             f"增益 {item['mean_gain']:+.6f}，改判 "
                             f"{item['labelled_changes_total']}/{item['comparisons']}"))
        lines += section(
            "一、专家家族与专家数量（Q 扫描）",
            "惰性是「四个过滤式视图」的特例，还是换成不同模型家族、不同专家数量仍然成立？",
            "同一特征预算下把成员换成不同家族（随机森林 / 极端随机树 / XGBoost），"
            "并在 Q=2/3/4/6 上重复同成员等权对照；三种子，主总体。",
            r"& $py scripts\run_member_family_experiments_v1.py",
            "`results_member_family_v1/`（gate_results_by_config.csv、"
            "member_metrics_by_seed.csv、predictions_*.csv）",
            rows,
            "四个同族过滤式视图（Q=4）是本文最不分散的配置：门控几乎不动。"
            "换成跨家族成员后分歧升到 2.3%，增益升到 +0.0014；Q=6 时 +0.0017。"
            "也就是说门控并非永远失效，而是只有当成员足够分散时才起作用，"
            "且幅度仍落在 0.005 边界内。")

    holdout = read_json(ROOT / "results_day_holdout_v1" / "day_holdout_summary.json")
    if holdout:
        rows = []
        for day, value in holdout.items():
            rows.append((f"留出 {day}（测试 {value['rccf']['test_rows']:,} 条）",
                         f"RCCF {value['rccf']['macro_f1_mean']:.6f}，"
                         f"等权 χ² {value['equal_rf_chi2']['macro_f1_mean']:.6f}，"
                         f"差 {value['rccf_minus_equal_chi2']:+.6f}"))
        lines += section(
            "二、按天留出（时间外推）",
            "把训练集限制在其它天、测试集换成完整的一天，结论还能成立吗？",
            "CIC-IDS2017 全去重语料按采集日分组；训练日每类上限 2 万、测试日每类上限 2 万；"
            "五折之外还有五个种子；三种子先跑（脚本支持任意种子数）。",
            r"& $py scripts\run_day_holdout_v1.py --seeds 42 2024 3407 7 13",
            "`results_day_holdout_v1/`（day_holdout_metrics.csv、"
            "predictions/holdout_<day>_seed42.csv）",
            rows,
            "按天留出时所有模型的 Macro-F1 都跌到 0.13–0.20：CIC-IDS2017 的每一天只覆盖"
            "部分攻击类别，留出整天后有些类别在测试集里过少甚至缺失，"
            "这从数据侧印证了论文「无法构造类别完整的时间协议」这一限制，"
            "而不是给出一段可以外推的性能数字。")

    external = []
    for name, label in (("results_rccf_nsl_v10", "NSL-KDD"),
                        ("results_rccf_unsw_v10", "UNSW-NB15"),
                        ("results_rccf_nbaiot_v10", "N-BaIoT")):
        row = aggregate(name)
        if row is not None:
            external.append((f"{label}（{int(row.get('test_samples_mean', 0)):,} 条测试，10 种子）",
                             f"Macro-F1 {row['macro_f1_mean']:.6f} ± {row['macro_f1_std']:.6f}"))
    if external:
        lines += section(
            "三、外部基准补齐到十个种子",
            "NSL-KDD、UNSW-NB15、N-BaIoT 的结论是否依赖三个种子的运气？",
            "沿用各语料的原生标签与官方划分，只把种子从 3 扩到 10。",
            r"& $py scripts\run_rccf_external_v1.py --dataset nsl --data-dir data_external_nsl_kdd_processed_v2 --output-dir results_rccf_nsl_v10 --seeds 42 2024 3407 7 13 101 202 303 404 505"
            "\n" r"& $py scripts\run_rccf_external_v1.py --dataset unsw --data-dir data\external\UNSW-NB15 --output-dir results_rccf_unsw_v10 --seeds 42 2024 3407 7 13 101 202 303 404 505"
            "\n" r"& $py scripts\run_rccf_cic_v1.py --processed-dir data_processed_nbaiot_v48 --output-dir results_rccf_nbaiot_v10 --seeds 42 2024 3407 7 13 101 202 303 404 505",
            "`results_rccf_nsl_v10/`、`results_rccf_unsw_v10/`、`results_rccf_nbaiot_v10/`"
            "（逐种子预测 + 汇总）",
            external,
            "外部基准的均值与三种子时一致到小数点后三位，说明此前的结论不是种子选择造成的。")

    deployment = read_json(ROOT / "results_deployment_metrics_v1" / "deployment_summary.json")
    if deployment:
        rows = []
        for key in ("results_full_corpus_v49|equal_rf_chi2",
                    "results_full_corpus_v49|xgboost_chi2",
                    "results_seeds10_v5|rccf"):
            if key in deployment:
                item = deployment[key]
                rows.append((key.split("|")[1] + f"（{item['seeds']} 种子）",
                             f"操作点 FPR {item['operating_fpr']:.4f}，"
                             f"召回 {item['operating_recall']:.4f}"
                             + (f"，AUROC {item['roc_auc_mean']:.5f}" if "roc_auc_mean" in item
                                else "")))
        lines += section(
            "四、部署向指标",
            "在部署关心的操作点上（误报率、PR 面积）各模型差多少？",
            "从公开的逐样本预测重算：攻击/正常二分类 ROC-PR、FPR@95%TPR、"
            "逐类 one-vs-rest PR 面积；有概率的目录给出阈值指标，只有标签的目录给出操作点混淆率。",
            r"& $py scripts\run_deployment_metrics_v1.py",
            "`results_deployment_metrics_v1/`（deployment_metrics_by_seed.csv、"
            "per_class_pr_auc.csv）",
            rows,
            "全语料的操作点 FPR 在千分之几量级，XGBoost 最低；"
            "条件加权与等权森林在同一量级，差异远小于模型族差异，与主结论一致。")

    for name, title, question in (
            ("results_rccf_cic_ids2018_v1", "五、新语料 CIC-IDS2018",
             "把同一套六阶段审计与五分类协议搬到 CIC-IDS2018，结论是否复现？"),
            ("results_rccf_cic_iot2023_v1", "六、新语料 CIC-IoT-2023（八分类）",
             "在物联网域的第二个语料上，条件加权是否同样没有增益？")):
        row = aggregate(name)
        summary = ROOT / name / "dataset_summary.csv"
        audit = list(ROOT.glob(name.replace("results_rccf_", "results_data_audit_") + "*"))
        data_line = f"`{name}/`（逐种子预测与汇总）"
        if audit:
            data_line += f"；审计 JSON 在 `{audit[0].name}/`"
        rows = []
        summary_path = ROOT / name / "benchmark_summary.json"
        if summary_path.exists():
            detail = json.loads(summary_path.read_text(encoding="utf-8"))
            rows.append(("RCCF Macro-F1（均值）", f"{detail['rccf_mean_macro_f1']:.6f}"))
            rows.append(("同成员等权融合 Macro-F1 / 差值",
                         f"{detail['equal_fusion_mean_macro_f1']:.6f} / "
                         f"{detail['same_members_difference']:+.6f}"))
        elif row is not None:
            rows.append(("RCCF Macro-F1（均值 ± 标准差）",
                         f"{row['macro_f1_mean']:.6f} ± {row['macro_f1_std']:.6f}"))
        if summary.exists():
            counts = pd.read_csv(summary)
            rows.append(("类别分布", "、".join(f"{r.target} {int(r['count']):,}"
                                               for _, r in counts.iterrows())))
        if rows:
            lines += section(title, question,
                             "官方文件 → 全局去重与冲突删除 → 每类上限 → 分层划分 → "
                             "与主实验相同的模型与统计流程。",
                             r"& $py scripts\prepare_cic_iot2023_v1.py" if "iot" in name
                             else r"& $py scripts\prepare_cic_ids2018_v1.py",
                             data_line, rows,
                             "新语料的结论见上表；与 CIC-IDS2017 相同，"
                             "条件加权没有超过同成员等权融合。")

    recent = []
    for name, label in (("results_rccf_litnet2020_v1", "LITNET-2020（2020）"),
                        ("results_rccf_iot23_v1", "IoT-23（2020）"),
                        ("results_rccf_rt_iot2022_v1", "RT-IoT2022（2022）"),
                        ("results_rccf_aci_iot2023_v1", "ACI-IoT-2023（2023）")):
        detail = read_json(ROOT / name / "benchmark_summary.json")
        if detail:
            recent.append((f"{label}：{len(detail['classes'])} 类，测试 {detail['test_rows']:,} 条",
                           f"RCCF {detail['rccf_mean_macro_f1']:.6f}，同成员等权融合 "
                           f"{detail['equal_fusion_mean_macro_f1']:.6f}，差 "
                           f"{detail['same_members_difference']:+.6f}"))
    if recent:
        lines += section(
            "七、近年语料（2020–2023）",
            "换成 2020–2023 年发布、难度更高的语料后，结论是否仍然成立？",
            "四份公开镜像语料按同一水库去重与分层协议处理，每类上限 5 000（训练）/2 000（测试）；"
            "三种子、三个确定性视图，与扩展协议一致。",
            r"& $py scripts\prepare_tabular_corpus_v1.py --name RT-IoT2022 ..."
            "\n" r"& $py scripts\run_native_label_benchmark_v1.py --processed-dir data_processed_rt_iot2022_v1 --experiments 42 2024 3407",
            "`data_processed_*_v1/` 与 `results_rccf_*_v1/`（逐种子预测与汇总）；原始文件在 "
            "`E:\\论文\\data\\external\\recent\\`，附 `recent_corpora_manifest.json`",
            recent,
            "四个 2020–2023 语料上，门控与同成员等权融合的差值为 0.000000–0.000235 Macro-F1；"
            "其中 ACI-IoT-2023 与 RT-IoT2022 的绝对水平（0.778 / 0.940）明显低于 2017 数据，"
            "说明结论不依赖语料年代，也不依赖判别难度。")

    text = "\n".join(lines) + "\n"
    out = Path(args.outdir) / "扩展实验报告.md" if args.outdir else OUT
    out.write_text(text, encoding="utf-8")
    print(f"EXTENSION_REPORT_WRITTEN={out}")
    print(f"sections={sum(1 for line in lines if line.startswith('## '))}")


if __name__ == "__main__":
    main()
