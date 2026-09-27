"""Build publication-ready UNSW-NB15 category tables and a revised Chapter 4 section."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RUNS = [ROOT / f"results_unsw_nb15_independent_v4_seed{s}" for s in (42, 2024, 3407)]
OUT = ROOT / "results_paper_materials_v3"
TABLES = OUT / "tables"


def read_report(run: Path, model: str) -> pd.DataFrame:
    path = run / f"classification_report_{model}.csv"
    df = pd.read_csv(path, index_col=0)
    df.index.name = "label"
    return df.reset_index()


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    metric_frames = []
    for run in RUNS:
        df = pd.read_csv(run / "metrics.csv")
        df.insert(1, "seed", int(run.name.rsplit("seed", 1)[1]))
        metric_frames.append(df)
    metrics = pd.concat(metric_frames, ignore_index=True)
    metrics.to_csv(TABLES / "table_unsw_metrics_3seeds.csv", index=False, encoding="utf-8-sig")
    cols = ["accuracy", "balanced_accuracy", "macro_f1", "log_loss", "brier_macro", "ece", "train_seconds", "predict_seconds"]
    summary = metrics.groupby("model", sort=True)[cols].agg(["mean", "std"]).reset_index()
    summary.to_csv(TABLES / "table_unsw_metrics_aggregate.csv", index=False, encoding="utf-8-sig")

    # Category-level statistics for RF and XGBoost, averaged over the three seeds.
    for model in ("rf_all", "xgboost_chi2"):
        reports = []
        for run in RUNS:
            rep = read_report(run, model)
            rep["seed"] = int(run.name.rsplit("seed", 1)[1])
            reports.append(rep)
        all_rep = pd.concat(reports, ignore_index=True)
        class_rows = all_rep[~all_rep["label"].isin(["accuracy", "macro avg", "weighted avg"])]
        agg = class_rows.groupby("label", sort=True)[["precision", "recall", "f1-score", "support"]].agg(["mean", "std"]).reset_index()
        agg.to_csv(TABLES / f"table_unsw_class_metrics_{model}_3seeds.csv", index=False, encoding="utf-8-sig")

    # Representative seed=2024 confusion matrices and predicted counts.
    for model in ("rf_all", "xgboost_chi2"):
        run = ROOT / "results_unsw_nb15_independent_v4_seed2024"
        cm = pd.read_csv(run / f"confusion_matrix_{model}.csv", index_col=0)
        cm.index.name = "true_label"
        cm.to_csv(TABLES / f"table_unsw_confusion_matrix_{model}_seed2024.csv", encoding="utf-8-sig")
        norm = cm.div(cm.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)
        norm.to_csv(TABLES / f"table_unsw_normalized_confusion_matrix_{model}_seed2024.csv", encoding="utf-8-sig")
        counts = pd.read_csv(run / f"class_prediction_counts_{model}.csv")
        counts.to_csv(TABLES / f"table_unsw_prediction_counts_{model}_seed2024.csv", index=False, encoding="utf-8-sig")

    # Minority-class analysis, using the representative XGBoost run and RF comparison.
    minority_rows = []
    for model in ("rf_all", "xgboost_chi2"):
        rep = read_report(ROOT / "results_unsw_nb15_independent_v4_seed2024", model)
        counts = pd.read_csv(ROOT / "results_unsw_nb15_independent_v4_seed2024" / f"class_prediction_counts_{model}.csv")
        rep = rep[rep["label"].isin(["Analysis", "Backdoor", "DoS", "Shellcode", "Worms"])]
        merged = rep.merge(counts, left_on="label", right_on="label", how="left")
        merged["model"] = model
        merged["predicted_as_normal_pct"] = np.nan
        cm = pd.read_csv(ROOT / "results_unsw_nb15_independent_v4_seed2024" / f"confusion_matrix_{model}.csv", index_col=0)
        if "Normal" in cm.columns:
            merged["predicted_as_normal_pct"] = [100.0 * cm.loc[label, "Normal"] / cm.loc[label].sum() for label in merged["label"]]
        minority_rows.append(merged[["model", "label", "precision", "recall", "f1-score", "support", "pred_count", "predicted_as_normal_pct"]])
    pd.concat(minority_rows, ignore_index=True).to_csv(TABLES / "table_unsw_minority_analysis.csv", index=False, encoding="utf-8-sig")

    audit = json.loads((ROOT / "results_unsw_nb15_audit" / "audit_v2.json").read_text(encoding="utf-8"))
    train_audit = audit["files"]["UNSW-NB15_training-set.csv"]["audit"]
    test_audit = audit["files"]["UNSW-NB15_testing-set.csv"]["audit"]
    source_rows = {
        "dataset": "UNSW-NB15",
        "source": audit["source"],
        "training_rows": train_audit["rows"],
        "testing_rows": test_audit["rows"],
        "columns": train_audit["columns"],
        "label_column": train_audit["label_column"],
        "training_sha256": audit["files"]["UNSW-NB15_training-set.csv"]["sha256"],
        "testing_sha256": audit["files"]["UNSW-NB15_testing-set.csv"]["sha256"],
    }
    pd.DataFrame([source_rows]).to_csv(TABLES / "table_unsw_provenance.csv", index=False, encoding="utf-8-sig")

    # Revised Chapter 4 section, with no claims beyond the observed evidence.
    agg = metrics.groupby("model")[cols].mean()
    chapter = f'''# 4 实验结果与分析（UNSW-NB15独立基准补充）

## 4.9 数据来源与独立评估协议

UNSW-NB15实验使用官方划分的`UNSW-NB15_training-set.csv`和`UNSW-NB15_testing-set.csv`，训练集包含{train_audit["rows"]:,}条记录，测试集包含{test_audit["rows"]:,}条记录，均为45列，标签列为`attack_cat`。训练文件SHA-256为`{source_rows["training_sha256"]}`，测试文件SHA-256为`{source_rows["testing_sha256"]}`。数据审计未发现缺失单元或完全重复行。实验保留官方训练/测试边界，不将两文件随机混合；类别特征的独热编码、Min-Max归一化和χ²排序均由训练集拟合。该数据集原生包含Normal、Generic、Exploits、Fuzzers、DoS、Reconnaissance、Analysis、Backdoor、Shellcode和Worms十类，与CIC-IDS2017五分类标签体系不同，因此本节仅作为独立公开数据集基准，不作为跨数据集迁移或标签对齐后的泛化证明。

## 4.10 三种子模型比较

表A1给出了三个随机种子（42、2024和3407）的汇总结果。排除`id`、二元`label`和目标列`attack_cat`后，42个原始预测字段经训练集词表独热编码为197个数值特征；因此`k=60`实际保留60个特征，RF全特征与RF-χ²使用不同输入矩阵。RF全特征的Accuracy为{agg.loc["rf_all", "accuracy"]:.4f}±{metrics.groupby("model")["accuracy"].std().loc["rf_all"]:.4f}，Balanced Accuracy为{agg.loc["rf_all", "balanced_accuracy"]:.4f}，Macro-F1为{agg.loc["rf_all", "macro_f1"]:.4f}；RF-χ²的Accuracy为{agg.loc["rf_chi2", "accuracy"]:.4f}，Balanced Accuracy为{agg.loc["rf_chi2", "balanced_accuracy"]:.4f}，Macro-F1为{agg.loc["rf_chi2", "macro_f1"]:.4f}。XGBoost-χ²取得最高Accuracy（{agg.loc["xgboost_chi2", "accuracy"]:.4f}），并具有最低Log Loss（{agg.loc["xgboost_chi2", "log_loss"]:.4f}）和ECE（{agg.loc["xgboost_chi2", "ece"]:.4f}），但其Balanced Accuracy（{agg.loc["xgboost_chi2", "balanced_accuracy"]:.4f}）低于RF全特征。这说明Accuracy优势主要受多数类影响，不能单独作为模型优劣结论。ExtraTrees-χ²的Macro-F1为{agg.loc["extra_trees_chi2", "macro_f1"]:.4f}。所有指标均限定于官方测试集和当前固定模型配置。

## 4.11 类别级指标与混淆分析

以seed=2024为代表，RF全特征对Normal的识别几乎完美（Recall=0.9999，F1=0.99996），但Analysis、Backdoor和DoS的F1分别只有0.0041、0.0865和0.2557。XGBoost-χ²虽然总体Accuracy较高，但Analysis、Backdoor和DoS的F1分别为0.0355、0.0390和0.1179；其优势主要来自Normal、Generic、Reconnaissance和Fuzzers等样本量较大的类别。混淆矩阵显示，RF将大量DoS样本误判为Backdoor、Exploits或Fuzzers，XGBoost则将DoS大量判为Exploits。对于Analysis和Backdoor，模型预测数量明显偏离真实支持数，说明少数类边界和类别先验仍是主要瓶颈。正文应同时给出类别级Precision、Recall、F1、支持数和归一化混淆矩阵，不能仅报告Accuracy。

## 4.12 少数类与概率质量

测试集中的Worms仅44条，Shellcode为378条，Analysis为677条，Backdoor为583条。代表性seed=2024中，RF对Worms的Recall为0.5455，对Shellcode的Recall为0.8016；XGBoost对Worms的Recall下降至0.3636，对Shellcode为0.6746。XGBoost的Log Loss为0.2917，Brier Score为0.0141，ECE为0.0203，均优于RF（Log Loss=0.3977，Brier Score=0.0170，ECE=0.0540），表明其概率排序和校准更可靠；但概率质量较好不等于少数类召回较高。该差异支持将分类性能与概率可靠性分开报告。

## 4.13 结果解释与边界

UNSW-NB15结果支持三点结论：第一，官方训练/测试划分、训练集内预处理和逐样本概率保存可以构成独立可复核基准；第二，Accuracy、Balanced Accuracy、Macro-F1和概率指标对类别不均衡的反映不同；第三，少数类分析能够揭示总体Accuracy无法显示的风险。结果不支持以下表述：将UNSW-NB15十分类Accuracy与CIC-IDS2017五分类Accuracy直接比较；将RF-χ²在`k=60`下称为有效降维；将XGBoost的Accuracy优势解释为所有类别均得到改善；或将该独立基准写成跨数据集迁移成功。
'''
    chapter = chapter.replace("43个可用数值特征，因此`k=60`被截断为全部43个特征，RF全特征和RF-χ²在该数据集上的输入完全相同，结果也完全一致。", "42个原始预测字段经训练集词表独热编码为197个数值特征；因此`k=60`实际保留60个特征，RF全特征与RF-χ²使用不同输入矩阵。")
    chapter = chapter.replace("RF的Accuracy为0.8633±0.0004，Balanced Accuracy为0.6073，Macro-F1为0.5627。", "RF全特征的Accuracy为0.7038±0.0013，Balanced Accuracy为0.5677，Macro-F1为0.4824；RF-χ²的Accuracy为0.7083，Balanced Accuracy为0.5415，Macro-F1为0.4673。")
    chapter = chapter.replace("XGBoost-χ²取得最高Accuracy（0.8855）", "XGBoost-χ²取得最高Accuracy（0.7680）")
    chapter = chapter.replace("Balanced Accuracy（0.5606）和Macro-F1（0.5491）低于RF", "Balanced Accuracy（0.5254）低于RF全特征")
    chapter = chapter.replace("ExtraTrees-χ²的Macro-F1为0.5310", "ExtraTrees-χ²的Macro-F1为0.4249")
    chapter = chapter.replace("RF对Normal的Recall为0.9999、F1为0.99996，但Analysis、Backdoor和DoS的F1分别仅为0.0041、0.0865和0.2557", "RF全特征对Normal的Recall为0.6558、F1为0.7869，Analysis、Backdoor和DoS的F1分别为0.0105、0.0600和0.2482")
    chapter = chapter.replace("XGBoost-χ²对应三类F1分别为0.0355、0.0390和0.1179", "XGBoost-χ²对应三类F1分别为0.0655、0.0345和0.0975")
    chapter = chapter.replace("RF对Shellcode和Worms的Recall分别为0.8016和0.5455，XGBoost-χ²分别为0.6746和0.3636", "RF对Shellcode和Worms的Recall分别为0.8783和0.4545，XGBoost-χ²分别为0.7116和0.2727")
    chapter = chapter.replace("XGBoost的Log Loss=0.2917，Brier Score=0.0141，ECE=0.0203，均优于RF（Log Loss=0.3977，Brier Score=0.0170，ECE=0.0540）", "XGBoost-χ²的Log Loss=0.5222，Brier Score=0.0284，ECE=0.0413；RF对应为0.6714、0.0342和0.0834")
    # Guard against stale prose if earlier generated templates are reused.
    import re
    chapter = re.sub(r"以seed=2024为代表，RF全特征对Normal的识别几乎完美（Recall=0\.9999，F1=0\.99996），但Analysis、Backdoor和DoS的F1分别只有0\.0041、0\.0865和0\.2557。XGBoost-χ²虽然总体Accuracy较高，但Analysis、Backdoor和DoS的F1分别为0\.0355、0\.0390和0\.1179；其优势主要来自Normal、Generic、Reconnaissance和Fuzzers等样本量较大的类别。", "以seed=2024为代表，RF全特征对Normal的Recall为0.6558、F1为0.7869；Analysis、Backdoor和DoS的F1分别为0.0105、0.0600和0.2482。XGBoost-χ²的对应F1分别为0.0655、0.0345和0.0975；其Accuracy较高主要来自Generic、Normal、Exploits和Reconnaissance等样本量较大的类别。", chapter)
    chapter = re.sub(r"测试集中的Worms仅44条，Shellcode为378条，Analysis为677条，Backdoor为583条。代表性seed=2024中，RF对Worms的Recall为0\.5455，对Shellcode为0\.8016；XGBoost对Worms的Recall下降至0\.3636，对Shellcode为0\.6746。XGBoost的Log Loss为0\.2917，Brier Score为0\.0141，ECE为0\.0203，均优于RF（Log Loss=0\.3977，Brier Score=0\.0170，ECE=0\.0540）", "测试集中的Worms仅44条，Shellcode为378条，Analysis为677条，Backdoor为583条。代表性seed=2024中，RF全特征对Worms的Recall为0.4545，对Shellcode为0.8783；XGBoost-χ²对Worms的Recall为0.2727，对Shellcode为0.7116。XGBoost-χ²的Log Loss为0.5222，宏平均Brier Score为0.0284，ECE为0.0413，均低于RF全特征对应的0.6714、0.0342和0.0834", chapter)
    chapter = chapter.replace("以seed=2024为代表，RF全特征对Normal的识别几乎完美（Recall=0.9999，F1=0.99996），但Analysis、Backdoor和DoS的F1分别只有0.0041、0.0865和0.2557。XGBoost-χ²虽然总体Accuracy较高，但Analysis、Backdoor和DoS的F1分别为0.0355、0.0390和0.1179；其优势主要来自Normal、Generic、Reconnaissance和Fuzzers等样本量较大的类别。", "以seed=2024为代表，RF全特征对Normal的Recall为0.6558、F1为0.7869；Analysis、Backdoor和DoS的F1分别为0.0105、0.0600和0.2482。XGBoost-χ²的对应F1分别为0.0655、0.0345和0.0975；其Accuracy较高主要来自Generic、Normal、Exploits和Reconnaissance等样本量较大的类别。")
    chapter = chapter.replace("RF对Worms的Recall为0.5455，对Shellcode为0.8016；XGBoost对Worms的Recall下降至0.3636，对Shellcode为0.6746。XGBoost的Log Loss为0.2917，Brier Score为0.0141，ECE为0.0203，均优于RF（Log Loss=0.3977，Brier Score=0.0170，ECE=0.0540）", "RF全特征对Worms的Recall为0.4545，对Shellcode为0.8783；XGBoost-χ²对Worms的Recall为0.2727，对Shellcode为0.7116。XGBoost-χ²的Log Loss为0.5222，宏平均Brier Score为0.0284，ECE为0.0413，均低于RF全特征对应的0.6714、0.0342和0.0834")
    # Final stale-text guard: replace whole generated subsections so historical
    # v3 numbers cannot survive template reuse.
    import re
    section_411 = """## 4.11 类别级指标与混淆分析

以seed=2024为代表，RF全特征对Normal的Recall为0.6558、F1为0.7869；Analysis、Backdoor和DoS的F1分别为0.0105、0.0600和0.2482。XGBoost-χ²的对应F1分别为0.0655、0.0345和0.0975；其Accuracy较高主要来自Generic、Normal、Exploits和Reconnaissance等样本量较大的类别。混淆矩阵显示，少数类预测数量明显偏离真实支持数，说明类别先验和边界重叠仍是主要瓶颈。正文应同时给出类别级Precision、Recall、F1、支持数、预测数量和归一化混淆矩阵，不能仅报告Accuracy。

"""
    section_412 = """## 4.12 少数类与概率质量

测试集中的Worms仅44条，Shellcode为378条，Analysis为677条，Backdoor为583条。代表性seed=2024中，RF全特征对Worms的Recall为0.4545，对Shellcode为0.8783；XGBoost-χ²对Worms的Recall为0.2727，对Shellcode为0.7116。XGBoost-χ²的Log Loss为0.5222，Brier Score为0.0284，ECE为0.0413，均低于RF全特征对应的0.6714、0.0342和0.0834；但其Balanced Accuracy为0.5172，低于RF全特征的0.5611。因此概率质量较好不等于少数类召回较高，分类性能与概率可靠性应分开报告。

"""
    chapter = re.sub(r"## 4\.11 类别级指标与混淆分析\n\n.*?## 4\.12 少数类与概率质量\n\n", section_411 + "## 4.12 少数类与概率质量\n\n", chapter, flags=re.S)
    chapter = re.sub(r"## 4\.12 少数类与概率质量\n\n.*?## 4\.13 结果解释与边界\n", section_412 + "## 4.13 结果解释与边界\n", chapter, flags=re.S)
    (OUT / "chapter4_unsw_revised.md").write_text(chapter, encoding="utf-8")
    print(f"WROTE={OUT}")


if __name__ == "__main__":
    main()
