from pathlib import Path
import json
import shutil

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[1]
FAIR = ROOT / "results_fair_final_checked"
SAFE = ROOT / "results_leakage_safe_checked3"
PROCESSED = Path(r"E:\论文\data\processed_dedup")
OUT = ROOT / "results_paper_materials"
FIG = OUT / "figures"
TABLE = OUT / "tables"


def save_table(df, name):
    df.to_csv(TABLE / name, index=False, encoding="utf-8-sig")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    TABLE.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="paper")
    plt.rcParams["figure.dpi"] = 160
    plt.rcParams["savefig.bbox"] = "tight"

    metrics = pd.read_csv(FAIR / "metrics_summary.csv")
    agg = pd.read_csv(FAIR / "metrics_aggregate_flat.csv")
    k = pd.read_csv(SAFE / "k_selection_validation_summary.csv")
    scores = pd.read_csv(FAIR / "feature_scores_training_only.csv")

    # Core tables
    model_order = [
        "decision_tree_all", "decision_tree_chi2", "svm_all", "svm_chi2",
        "random_forest_all", "random_forest_chi2", "weighted_rf_chi2"
    ]
    agg["model"] = pd.Categorical(agg["model"], model_order, ordered=True)
    agg = agg.sort_values("model")
    save_table(agg, "table_model_comparison.csv")
    ablation = agg[agg["model"].isin(["random_forest_all", "random_forest_chi2", "weighted_rf_chi2"])].copy()
    save_table(ablation, "table_ablation.csv")

    reports = []
    for path in FAIR.glob("classification_report_*.csv"):
        name = path.stem.replace("classification_report_", "")
        report = pd.read_csv(path, index_col=0)
        for label in ["Bot", "Brute Force", "DoS/DDoS", "Normal", "Web Attack"]:
            if label in report.index:
                row = report.loc[label, ["precision", "recall", "f1-score", "support"]].to_dict()
                row.update({"model": name, "label": label, "source": path.name})
                reports.append(row)
    class_df = pd.DataFrame(reports)
    class_avg = class_df.groupby(["model", "label"], as_index=False)[["precision", "recall", "f1-score", "support"]].mean()
    save_table(class_avg, "table_class_metrics_by_model.csv")
    key_class = class_avg[class_avg["model"].isin(["random_forest_all_seed42", "random_forest_chi2_seed42", "weighted_rf_chi2_seed42"])]
    save_table(key_class, "table_class_metrics_key_models.csv")

    with open(SAFE / "selected_k.json", encoding="utf-8") as f:
        selected_k = json.load(f)
    with open(PROCESSED / "dedup_audit.json", encoding="utf-8") as f:
        audit = json.load(f)
    summary = pd.read_csv(PROCESSED / "dataset_summary.csv")
    split_rows = []
    for split in ["train", "validation", "test"]:
        frame = pd.read_csv(PROCESSED / f"{split}.csv", usecols=["target"])
        counts = frame["target"].value_counts().rename_axis("target").reset_index(name="count")
        counts.insert(0, "split", split)
        split_rows.append(counts)
    split_table = pd.concat(split_rows, ignore_index=True)
    save_table(split_table, "table_split_class_counts.csv")
    data_audit = pd.DataFrame([{
        "source_rows": audit["source_rows"], "mapped_rows": audit["mapped_rows"],
        "invalid_rows": audit["invalid_rows"], "duplicate_rows": audit["duplicate_rows"],
        "cross_label_conflicts": audit["cross_label_conflicts"],
        "valid_rows": audit.get("valid_rows"),
        "unique_rows_before_conflict": audit.get("unique_rows_before_conflict"),
        "cross_label_conflict_hashes": audit.get("cross_label_conflict_hashes"),
        "cross_label_conflict_rows": audit.get("cross_label_conflict_rows"),
        "unique_rows_after_conflict": audit.get("unique_rows_after_conflict"),
        "capped_rows_before_balance": audit.get("capped_rows_before_balance", audit.get("retained_rows_before_balance")),
        "balanced_rows": audit["balanced_rows"], "balanced_per_class": audit["balanced_per_class"],
        "selected_k": selected_k["best_k"], "feature_count_original": 78,
        "feature_count_selected": 60,
    }])
    save_table(data_audit, "table_data_audit.csv")

    # Figure 1: chi-square ranking
    top = scores.head(20).sort_values("chi2")
    plt.figure(figsize=(7.2, 6.0))
    plt.barh(top["feature"], top["chi2"], color="#4472C4")
    plt.xlabel("Chi-square score")
    plt.ylabel("Feature")
    plt.title("Top 20 features ranked by chi-square score")
    plt.tight_layout()
    plt.savefig(FIG / "fig_chi2_top20.png")
    plt.close()

    # Figure 2: k selection
    plt.figure(figsize=(6.4, 4.2))
    plt.plot(k["k"], k["validation_macro_f1"] * 100, marker="o", label="Validation Macro-F1")
    best = int(selected_k["best_k"])
    best_row = k.loc[k["k"] == best].iloc[0]
    plt.scatter([best], [best_row["validation_macro_f1"] * 100], color="#C00000", zorder=3)
    plt.annotate(f"selected k={best}", (best, best_row["validation_macro_f1"] * 100), xytext=(-35, 12), textcoords="offset points")
    plt.xlabel("Number of selected features (k)")
    plt.ylabel("Validation Macro-F1 (%)")
    plt.title("Chi-square feature-count selection")
    plt.ylim(85, 96)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG / "fig_k_selection.png")
    plt.close()

    # Figure 3: performance comparison
    plot_df = agg.copy()
    plot_df["label"] = plot_df["model"].astype(str).str.replace("_", " ")
    long = plot_df.melt(id_vars=["label"], value_vars=["accuracy_mean", "macro_f1_mean"], var_name="metric", value_name="value")
    long["value"] *= 100
    long["metric"] = long["metric"].map({"accuracy_mean": "Accuracy", "macro_f1_mean": "Macro-F1"})
    plt.figure(figsize=(9.2, 4.8))
    sns.barplot(data=long, x="label", y="value", hue="metric", palette=["#4472C4", "#ED7D31"])
    plt.ylabel("Score (%)")
    plt.xlabel("Model")
    plt.title("Model performance comparison")
    plt.xticks(rotation=30, ha="right")
    plt.ylim(88, 98)
    plt.legend(title="Metric")
    plt.tight_layout()
    plt.savefig(FIG / "fig_model_performance.png")
    plt.close()

    # Figure 4: time comparison
    time_long = plot_df.melt(id_vars=["label"], value_vars=["train_seconds_mean", "predict_seconds_mean"], var_name="metric", value_name="seconds")
    time_long["metric"] = time_long["metric"].map({"train_seconds_mean": "Training", "predict_seconds_mean": "Inference"})
    plt.figure(figsize=(9.2, 4.8))
    sns.barplot(data=time_long, x="label", y="seconds", hue="metric", palette=["#70AD47", "#A5A5A5"])
    plt.ylabel("Time (seconds)")
    plt.xlabel("Model")
    plt.title("Training and inference time")
    plt.xticks(rotation=30, ha="right")
    plt.legend(title="Phase")
    plt.tight_layout()
    plt.savefig(FIG / "fig_time_comparison.png")
    plt.close()

    # Figure 5: confusion matrix for representative seed
    cm_path = FAIR / "confusion_matrix_random_forest_chi2_seed42.csv"
    cm = pd.read_csv(cm_path, index_col=0)
    plt.figure(figsize=(5.5, 4.6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False)
    plt.xlabel("Predicted label")
    plt.ylabel("True label")
    plt.title("Confusion matrix: random forest + chi-square (seed 42)")
    plt.tight_layout()
    plt.savefig(FIG / "fig_confusion_matrix_rf_chi2_seed42.png")
    plt.close()

    # Draft text for Chapter 4
    rf = agg.loc[agg["model"] == "random_forest_chi2"].iloc[0]
    rf_all = agg.loc[agg["model"] == "random_forest_all"].iloc[0]
    wrf = agg.loc[agg["model"] == "weighted_rf_chi2"].iloc[0]
    draft = f"""# 第四章实验结果材料（数据驱动初稿）

## 4.1 数据处理结果

CIC-IDS2017原始数据共包含 {audit['source_rows']:,} 条记录。经过标签映射后保留 {audit['mapped_rows']:,} 条记录，其中有效数值记录为 {audit.get('valid_rows', audit['mapped_rows'] - audit['invalid_rows']):,} 条；清除无效值 {audit['invalid_rows']:,} 条。全局去重后得到 {audit.get('unique_rows_before_conflict', 0):,} 个唯一特征向量，删除跨标签冲突向量 {audit.get('cross_label_conflict_hashes', audit['cross_label_conflicts']):,} 个，冲突剔除后剩余 {audit.get('unique_rows_after_conflict', audit.get('retained_rows_before_balance', 0)):,} 条。应用每类上限后保留 {audit.get('capped_rows_before_balance', audit.get('retained_rows_before_balance', 0)):,} 条，再按最小类别规模平衡得到 {audit['balanced_rows']:,} 条样本，每类 {audit['balanced_per_class']} 条。

训练集、验证集和测试集分别为 2355、505 和 505 条，三份数据内部重复数和跨集合特征交集均为0。

## 4.2 特征选择结果

原始输入包含78个数值特征。卡方检验仅在训练集上计算，候选特征数为10、20、30、40和60。根据三个随机种子验证结果的平均Macro-F1，最终选择 k={selected_k['best_k']}，验证集Macro-F1为 {best_row['validation_macro_f1']*100:.2f}%。

## 4.3 模型对比结果

随机森林使用全部78维特征时Accuracy为 {rf_all['accuracy_mean']*100:.2f}%±{rf_all['accuracy_std']*100:.2f}%，Macro-F1为 {rf_all['macro_f1_mean']*100:.2f}%±{rf_all['macro_f1_std']*100:.2f}%。使用χ²筛选后的60维特征时Accuracy为 {rf['accuracy_mean']*100:.2f}%±{rf['accuracy_std']*100:.2f}%，Macro-F1为 {rf['macro_f1_mean']*100:.2f}%±{rf['macro_f1_std']*100:.2f}%。两者性能接近，说明降维没有造成明显性能损失。

加权随机森林的Accuracy为 {wrf['accuracy_mean']*100:.2f}%±{wrf['accuracy_std']*100:.2f}%，Macro-F1为 {wrf['macro_f1_mean']*100:.2f}%±{wrf['macro_f1_std']*100:.2f}%，与普通χ²随机森林结果一致。因此，本文不将加权投票描述为已被实验证明的性能提升，而将其作为一种可复现的探索性融合机制进行讨论。

## 4.4 类别级分析

从混淆矩阵和分类报告看，DoS/DDoS、Normal和Bot的识别相对稳定；Brute Force与Web Attack之间存在一定混淆，是当前五分类任务中的主要困难类别。该现象说明宏平均指标之外，还应报告类别级Precision、Recall和F1。

## 4.5 结果边界

本文实验结果支持“χ²特征选择能够在减少18个特征的同时基本保持随机森林性能”，但不支持“加权随机森林显著优于普通随机森林”或“准确率达到97%”等表述。训练和推理时间仅作为本机环境下的相对参考，不外推为固定倍数。
"""
    (OUT / "chapter4_results_draft.md").write_text(draft, encoding="utf-8")
    print(f"MATERIALS_WRITTEN={OUT}")


if __name__ == "__main__":
    main()
