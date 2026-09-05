"""Build a machine-readable data evidence pack for publication.

The pack is descriptive only: it does not alter any training data or model
results. It records retention rates, class support, source-file coverage,
feature-quality findings, and external-dataset split properties.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results_data_evidence_v1"


def write(df: pd.DataFrame, name: str) -> None:
    df.to_csv(OUT / name, index=False, encoding="utf-8-sig")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    cic_audit = json.loads((ROOT / "results_data_processing_audit_v3" / "data_processing_audit.json").read_text(encoding="utf-8"))
    totals = cic_audit["raw_totals"]
    stages = [
        ("raw source", totals["source_rows"]),
        ("label mapped", totals["mapped_rows"]),
        ("valid numeric", totals["valid_rows"]),
        ("unique before conflict", 2429924),
        ("unique after conflict", 2429791),
        ("capped before balance", 53237),
        ("balanced research subset", 3365),
    ]
    stage_rows = []
    first = stages[0][1]
    previous = first
    for name, rows in stages:
        stage_rows.append({
            "stage": name,
            "rows": rows,
            "retention_vs_raw": rows / first,
            "drop_vs_previous": 0.0 if name == "raw source" else (previous - rows) / previous,
        })
        previous = rows
    write(pd.DataFrame(stage_rows), "cic_processing_retention.csv")

    cic_counts = pd.read_csv(ROOT / "results_file_label_coverage_v5" / "file_label_counts.csv")
    label_cols = ["Normal", "DoS/DDoS", "Brute Force", "Web Attack", "Bot", "PortScan", "Infiltration", "Heartbleed", "Other"]
    coverage = cic_counts[["file", "raw_rows", *label_cols]].copy()
    for col in label_cols:
        coverage[f"{col}_fraction"] = coverage[col] / coverage["raw_rows"]
    coverage["main_class_count"] = (coverage[label_cols[:5]] > 0).sum(axis=1)
    write(coverage, "cic_file_label_coverage_with_fractions.csv")

    raw_labels = pd.read_csv(ROOT / "results_publication_final" / ".." / "results_paper_materials_v2" / "tables" / "table_split_class_counts.csv")
    raw_label_path = ROOT / "results_paper_materials_v3" / "tables" / "table_data_source_provenance_v1.csv"
    # Canonical balanced support is taken from the processed summary.
    balanced = pd.read_csv(ROOT / "data_processed_audit_v4" / "dataset_summary.csv")
    balanced["fraction"] = balanced["count"] / balanced["count"].sum()
    balanced.insert(0, "dataset", "CIC-IDS2017 balanced research subset")
    write(balanced, "cic_balanced_class_support.csv")

    nsl = pd.read_csv(ROOT / "results_nsl_kdd_fair_v2" / "class_counts.csv")
    nsl["fraction"] = nsl["count"] / nsl.groupby("split")["count"].transform("sum")
    nsl["dataset"] = "NSL-KDD"
    write(nsl[["dataset", "split", "class", "count", "fraction"]], "nsl_kdd_class_support.csv")

    # UNSW support is available in the audited JSON and is independent of the
    # prediction results.
    unsw_audit = json.loads((ROOT / "results_unsw_nb15_audit" / "audit_v2.json").read_text(encoding="utf-8"))
    unsw_rows = []
    for file_name, info in unsw_audit["files"].items():
        split = "test" if "testing" in file_name else "train"
        total = info["audit"]["rows"]
        for item in info["audit"]["labels"]:
            unsw_rows.append({"dataset": "UNSW-NB15", "split": split, "class": item["label"], "count": item["count"], "fraction": item["count"] / total})
    write(pd.DataFrame(unsw_rows), "unsw_nb15_class_support.csv")

    quality = json.loads((ROOT / "results_feature_quality_v5" / "feature_quality_audit.json").read_text(encoding="utf-8"))
    unsw_overlap = json.loads((ROOT / "results_unsw_nb15_audit" / "cross_split_overlap_audit.json").read_text(encoding="utf-8"))
    evidence = {
        "generated_from": {
            "cic_processing_audit": "results_data_processing_audit_v3/data_processing_audit.json",
            "cic_coverage": "results_file_label_coverage_v5/file_label_counts.csv",
            "nsl_support": "results_nsl_kdd_fair_v2/class_counts.csv",
            "unsw_audit": "results_unsw_nb15_audit/audit_v2.json",
            "feature_quality": "results_feature_quality_v5/feature_quality_audit.json",
        },
        "cic": {
            "raw_rows": totals["source_rows"],
            "mapped_rows": totals["mapped_rows"],
            "mapped_fraction": totals["mapped_rows"] / totals["source_rows"],
            "invalid_rows": totals["invalid_rows"],
            "invalid_fraction_of_raw": totals["invalid_rows"] / totals["source_rows"],
            "valid_rows": totals["valid_rows"],
            "valid_fraction_of_raw": totals["valid_rows"] / totals["source_rows"],
            "balanced_rows": 3365,
            "balanced_per_class": 673,
            "source_file_count": 8,
            "files_covering_all_five_main_classes": 0,
            "processed_split_exact_overlap": {"train_validation": 0, "train_test": 0, "validation_test": 0},
        },
        "feature_quality": {
            "feature_count": quality["feature_count"],
            "constant_feature_count": quality["constant_feature_count"],
            "near_zero_variance_count": quality["near_zero_variance_count"],
            "high_correlation_pair_count": quality["high_correlation_pair_count"],
            "note": "These are audit findings; the locked protocol is not silently changed.",
        },
        "nsl_kdd": {"split_protocol": "official KDDTrain+/KDDTest+", "minority_classes": ["R2L", "U2R"], "evidence_level": "single official split"},
        "unsw_nb15": {
            "split_protocol": "official training/testing CSVs",
            "cross_split_common_hash_keys": unsw_overlap["cross_split_common_hash_keys"],
            "matched_test_rows": unsw_overlap["cross_split_matched_test_rows"],
            "test_matched_row_fraction": unsw_overlap["test_matched_row_fraction"],
            "caveat": "Official split is retained, but overlap is reported as a dataset limitation and sensitivity analysis.",
        },
    }
    (OUT / "data_evidence_summary.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")

    report = [
        "# Data evidence pack (v1)",
        "",
        "本数据包只汇总和审计现有数据，不修改任何训练样本、标签或模型结果。所有比例均由机器可读表格计算。",
        "",
        "## CIC-IDS2017",
        "",
        f"原始记录 {totals['source_rows']:,} 条；标签映射后 {totals['mapped_rows']:,} 条（{totals['mapped_rows']/totals['source_rows']:.2%}）；有效数值记录 {totals['valid_rows']:,} 条（{totals['valid_rows']/totals['source_rows']:.2%}）。无效记录 {totals['invalid_rows']:,} 条，当前审计中均为无穷值行；另有 {totals['excluded_label_rows']:,} 条因标签不纳入主五分类任务。",
        "全局冲突审计、类别上限和五类等量抽样后，最终平衡研究子集为3,365条，每类673条。该子集用于受控比较，不代表原始全量分布。",
        "8个原始文件均缺少至少一个主类别，因此文件级结果只能作为覆盖和分布偏移审计。处理后train/validation/test的精确特征向量重叠均为0。",
        "",
        "## NSL-KDD and UNSW-NB15",
        "",
        "NSL-KDD保留KDDTrain+/KDDTest+官方文件边界，R2L和U2R是少数类，报告类别级支持数。",
        f"UNSW-NB15官方训练/测试文件之间存在{unsw_overlap['cross_split_common_hash_keys']:,}个共同规范化特征键，覆盖测试侧{unsw_overlap['cross_split_matched_test_rows']:,}条记录（{unsw_overlap['test_matched_row_fraction']:.2%}）。官方协议结果与去除匹配记录的敏感性结果必须分开解释。",
        "",
        "## Interpretation rules",
        "",
        "1. 任何Accuracy、Macro-F1或Balanced Accuracy都必须同时注明数据集、标签体系、样本构造和划分协议。",
        "2. 3,365条CIC样本只能称为balanced research subset，不能称为full CIC-IDS2017 performance。",
        "3. 文件覆盖不足时不得把留一文件结果写成完整五分类时间外泛化。",
        "4. 外部数据集结果是独立基准，不与CIC五分类指标直接横向排名。",
    ]
    (OUT / "data_evidence_report_v1.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"DATA_EVIDENCE_PACK_WRITTEN={OUT}")


if __name__ == "__main__":
    main()
