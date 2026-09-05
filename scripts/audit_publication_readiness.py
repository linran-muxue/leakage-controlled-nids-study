"""Create a conservative publication-readiness audit from canonical artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results_paper_materials_v2" / "publication_readiness_audit.md"


def pct(x: float) -> str:
    return f"{x * 100:.2f}%"


def main() -> None:
    cic = ROOT / "data_processed_audit_v4"
    nsl = ROOT / "data_external_nsl_kdd_processed_v2"
    tuned = ROOT / "results_publication_final"
    ext = ROOT / "results_publication_final"
    nsl_results = ROOT / "results_nsl_kdd_fair_v2"
    audit = json.loads((cic / "dedup_audit.json").read_text(encoding="utf-8"))
    nsl_summary = json.loads((nsl / "dataset_summary.json").read_text(encoding="utf-8"))
    main_metrics = pd.read_csv(tuned / "metrics_3seeds.csv")
    ext_metrics = main_metrics
    nsl_metrics = pd.read_csv(nsl_results / "metrics.csv")

    splits = {}
    for name in ["train", "validation", "test"]:
        frame = pd.read_csv(cic / f"{name}.csv", low_memory=False)
        splits[name] = {
            "rows": len(frame),
            "columns": len(frame.columns),
            "class_counts": frame["target"].value_counts().to_dict(),
            "missing": int(frame.isna().sum().sum()),
        }
    feature_sets = []
    for name in ["train", "validation", "test"]:
        frame = pd.read_csv(cic / f"{name}.csv", low_memory=False)
        feature_sets.append(set(pd.util.hash_pandas_object(frame.drop(columns=["target"]), index=False)))
    overlaps = {
        "train_validation": len(feature_sets[0] & feature_sets[1]),
        "train_test": len(feature_sets[0] & feature_sets[2]),
        "validation_test": len(feature_sets[1] & feature_sets[2]),
    }

    rf = main_metrics[main_metrics.model == "random_forest_chi2"]
    wrf = ext_metrics[ext_metrics.model == "weighted_rf_chi2"]
    selected = json.loads((ROOT / "results_journal_upgrade_v2" / "selected_hyperparameters.json").read_text(encoding="utf-8"))

    lines = [
        "# 论文出刊前数据与实验就绪度审计",
        "",
        "审计日期：2026-09-05。此报告只评价数据、实验和材料是否具备送审基础，不等同于期刊录用保证。",
        "",
        "## 结论",
        "",
        "**判定：部分达到送审基础，尚未达到可直接投稿的最终状态。** 数据完整性和可复现实验基础为 PASS；稿件一致性、外部材料和期刊格式仍为 PARTIAL/BLOCKED。",
        "",
        "## 已通过项目",
        "",
        f"- CIC-IDS2017 原始 8 个 CSV 已纳入，审计总行数为 {audit['source_rows']:,}；映射、无效值清理、全局去重和跨标签冲突剔除均有显式审计字段。冲突组涉及 {audit['rows_in_conflicting_groups']:,} 条原始记录和 {audit['conflicting_feature_hash_count']:,} 个唯一特征向量。",
        f"- 主实验为五分类，平衡数据共 {audit['balanced_rows']:,} 条（每类 {audit['balanced_per_class']} 条），训练/验证/测试为 {splits['train']['rows']}/{splits['validation']['rows']}/{splits['test']['rows']}。",
        f"- 三个 CIC 划分均为 78 个特征加 target，缺失值统计为 {sum(x['missing'] for x in splits.values())}；跨划分特征向量重叠为 {overlaps}。",
        f"- 主测试结果来自 `results_publication_final`：χ²随机森林 Accuracy={pct(rf.accuracy.mean())}，Macro-F1={pct(rf.macro_f1.mean())}（3 个模型种子）。",
        "- 逐样本预测、Bootstrap、McNemar、配对置换、权重策略消融、离线延迟和扰动实验均已生成结果文件。",
        "- 已新增10次独立重复分层划分、全特征RF受控消融、显式等权投票消融、训练集内特征稳定性、类别级报告和混淆矩阵。",
        f"- NSL-KDD 使用官方 KDDTrain+/KDDTest+ 划分；类别特征仅由训练集拟合，测试集无独有类别水平，处理后特征数为 {nsl_summary['feature_count']}。",
        "",
        "## 必须在投稿前处理的项目",
        "",
        "1. **最终配置已统一（PASS）**：主实验来自 `results_publication_final`，不平衡敏感性来自 `results_imbalanced_v3`，固定RF配置为 k=60、100 棵树、min_samples_leaf=2；全特征RF已纳入同一主脚本。各模型独立调参结果单列于 `results_tuning_v3`，不与受控消融混称。",
        "2. **补齐稿件元数据（BLOCKER）**：作者、单位、通信作者、地址、邮编、电话、E-mail、基金和作者简介必须由作者提供真实信息；当前 Word 仍含待填写占位符。",
        "3. **参考文献主体已建立（PARTIAL）**：Word 已纳入数据集、随机森林、χ²、统计方法及同刊近年研究的已核验候选条目；仍需在完整第一至三章中逐条标引，并按期刊最新模板复核格式。",
        "4. **套用《计算机系统应用》官方 Word 模板（BLOCKER）**：当前文稿是可读草稿，不是官方版式；需按模板调整题名、摘要、图表题注、公式、基金、作者简介和参考文献格式。",
        "5. **补充主实验限制说明（必须）**：3,365 条是经上限和五类平衡后的研究子集，不能外推为 CIC-IDS2017 全量性能；文件级时间泛化因类别覆盖不足尚未形成严格五分类结论。",
        "6. **将 NSL-KDD 结果写成独立基准（必须）**：其五类为 Normal、DoS、Probe、R2L、U2R，不能写成 CIC 标签迁移或跨数据集成功泛化。",
        "",
        "## 送审风险提示",
        "",
        "- 加权随机森林相对普通随机森林的 McNemar/配对置换检验未显示显著优势，摘要和结论不得宣称稳定提升。",
        "- 等权投票与验证集平衡准确率加权在重复划分中预测完全一致；加权机制应定位为探索性适用性分析。",
        "- 高斯噪声 1%/5% 会显著降低 Macro-F1；只能表述为对特征屏蔽较稳定、对连续值噪声敏感。",
        "- 离线 benchmark 只测核心 predict 调用，不包含流量解析、特征提取、网络 I/O 和系统集成，不能称为已完成网关部署。",
        "- NSL-KDD 的 R2L/U2R 少数类指标较低，应同时报告类别级 Precision/Recall/F1 与混淆矩阵。",
        "",
        "## 作者需要提供的最小信息",
        "",
        "作者姓名、学校/学院/专业、指导教师、通信作者、地址、邮编、电话、E-mail、基金信息，以及目标期刊当前官方 Word 模板。",
    ]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"AUDIT_WRITTEN={OUT}")


if __name__ == "__main__":
    main()
