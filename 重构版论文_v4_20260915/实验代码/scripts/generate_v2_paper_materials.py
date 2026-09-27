from pathlib import Path
import json
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data_processed_audit_v4"
TUNED = ROOT / "results_publication_final"
EXT = ROOT / "results_publication_final"
IMB = ROOT / "results_imbalanced_v3"
NSL = ROOT / "results_nsl_kdd_fair_v2"
ADDITIONAL = ROOT / "results_additional_evidence_v4"
COVERAGE = ROOT / "results_file_label_coverage_v4"
FEATURE_QUALITY = ROOT / "results_feature_quality_v4"
QUALITY = ROOT / "results_quality_upgrades"
REPEATED = ROOT / "results_repeated_splits_v3"
WEIGHT_MECHANISM = ROOT / "results_weight_mechanism_v3"
TUNING = ROOT / "results_tuning_v3"
OUT = ROOT / "results_paper_materials_v2"
TABLE = OUT / "tables"
FIG = OUT / "figures"

def save(df, name):
    df.to_csv(TABLE / name, index=False, encoding="utf-8-sig")

def save_main_summary(agg, metrics):
    """Write a compact, publication-readable main comparison table."""
    out = []
    feature_counts = {m: int(metrics.loc[metrics.model == m, "feature_count"].iloc[0])
                      for m in metrics.model.unique()}
    labels = {
        "decision_tree_chi2": "Decision tree + chi-square",
        "extra_trees_chi2": "ExtraTrees + chi-square",
        "random_forest_all": "Random forest (all features)",
        "random_forest_chi2": "Random forest + chi-square",
        "svm_all": "SVM (all features)",
        "weighted_rf_chi2": "Weighted random forest + chi-square",
    }
    for _, row in agg.iterrows():
        m = row["model"]
        out.append({
            "model": labels.get(m, m),
            "feature_count": feature_counts.get(m, ""),
            "accuracy_mean_std": f"{row['accuracy_mean']:.4f} ± {row['accuracy_std']:.4f}",
            "macro_f1_mean_std": f"{row['macro_f1_mean']:.4f} ± {row['macro_f1_std']:.4f}",
            "train_seconds_mean_std": f"{row['train_seconds_mean']:.4f} ± {row['train_seconds_std']:.4f}",
            "predict_seconds_mean_std": f"{row['predict_seconds_mean']:.4f} ± {row['predict_seconds_std']:.4f}",
        })
    save(pd.DataFrame(out), "table_v2_model_comparison.csv")

def save_feature_probability_summary(add_summary):
    labels = {"all": "All features", "chi2": "Chi-square", "mutual_info": "Mutual information", "anova": "ANOVA"}
    out = []
    for _, row in add_summary.iterrows():
        m = row["method"]
        out.append({
            "method": labels.get(m, m),
            "macro_f1_mean_std": f"{row['macro_f1_mean']:.4f} ± {row['macro_f1_std']:.4f}",
            "log_loss_mean_std": f"{row['log_loss_mean']:.4f} ± {row['log_loss_std']:.4f}",
            "macro_brier_mean_std": f"{row['brier_macro_mean']:.4f} ± {row['brier_macro_std']:.4f}",
            "ece_mean_std": f"{row['ece_mean']:.4f} ± {row['ece_std']:.4f}",
            "mce_mean_std": f"{row['mce_mean']:.4f} ± {row['mce_std']:.4f}",
            "train_seconds_mean_std": f"{row['train_seconds_mean']:.4f} ± {row['train_seconds_std']:.4f}",
            "predict_seconds_mean_std": f"{row['predict_seconds_mean']:.4f} ± {row['predict_seconds_std']:.4f}",
        })
    save(pd.DataFrame(out), "table_v4_feature_selection_probability_metrics.csv")

def main():
    TABLE.mkdir(parents=True, exist_ok=True); FIG.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="paper")
    plt.rcParams["figure.dpi"] = 180
    plt.rcParams["savefig.bbox"] = "tight"

    audit = json.loads((AUDIT / "dedup_audit.json").read_text(encoding="utf-8"))
    audit_labels = {
        "source_rows":"原始记录数", "mapped_rows":"标签映射后记录数", "invalid_rows":"清理无效记录数",
        "valid_rows":"有效数值记录数", "duplicate_rows":"重复记录数", "same_label_duplicate_rows":"同标签重复记录数",
        "cross_label_mismatch_rows":"跨标签不一致记录数", "conflicting_feature_hash_count":"冲突特征向量数",
        "rows_in_conflicting_groups":"冲突组原始记录数", "unique_rows_removed_for_conflicts":"冲突向量剔除数",
        "unique_rows_before_conflict":"冲突处理前唯一向量数", "unique_rows_after_conflict":"冲突处理后唯一向量数",
        "capped_rows_before_balance":"类别上限后记录数", "retained_rows_before_balance":"平衡前保留记录数",
        "balanced_rows":"平衡研究样本数", "balanced_per_class":"每类平衡样本数", "dedup_fingerprint_bits":"去重指纹位数"
    }
    audit_rows = [{"audit_item": audit_labels[k], "value": audit[k]} for k in audit_labels if k in audit]
    save(pd.DataFrame(audit_rows), "table_data_audit.csv")
    split_rows=[]
    for split in ["train","validation","test"]:
        f=pd.read_csv(AUDIT/f"{split}.csv", usecols=["target"])
        c=f.target.value_counts().rename_axis("target").reset_index(name="count"); c.insert(0,"split",split); split_rows.append(c)
    save(pd.concat(split_rows, ignore_index=True), "table_split_class_counts.csv")
    nsl_hash_path = NSL / "raw_file_hashes_v4.json"
    nsl_hashes = json.loads(nsl_hash_path.read_text(encoding="utf-8")) if nsl_hash_path.exists() else {}
    nsl_files = nsl_hashes.get("files", {})
    nsl_checksum = "; ".join(
        f"{name}: MD5={info.get('md5','')}; SHA-256={info.get('sha256','')}"
        for name, info in sorted(nsl_files.items())
    ) or "项目保留官方划分；投稿前复核"
    provenance = pd.DataFrame([
        {"dataset":"CIC-IDS2017", "source":"用户下载并解压的 MachineLearningCSV", "local_path":"data/raw/MachineLearningCVE", "raw_file_count":8, "raw_rows":audit["source_rows"], "task_labels":"Normal; DoS/DDoS; Brute Force; Web Attack; Bot", "split_protocol":"dedup-balanced frame, stratified 70/15/15", "checksum_note":"MachineLearningCSV.zip MD5=4f83860afbf29cac8163854095bf6cf7; SHA-256=c3f26274b36c837ccf28ffd2dbf4582941c30b3ee70a635c6e5b2f87c4727928"},
        {"dataset":"NSL-KDD", "source":"defcom17/NSL_KDD 公共仓库 KDDTrain+、KDDTest+", "local_path":"data/external/NSL-KDD", "raw_file_count":2, "raw_rows":"official train/test split", "task_labels":"Normal; DoS; Probe; R2L; U2R", "split_protocol":"official KDDTrain+/KDDTest+", "checksum_note":nsl_checksum},
    ])
    save(provenance, "table_v4_data_provenance.csv")
    sidecar = ROOT / "results_data_provenance_v4"
    if (AUDIT / "train_source_provenance.csv").exists():
        prov = pd.concat([pd.read_csv(AUDIT / f"{s}_source_provenance.csv") for s in ["train","validation","test"]], ignore_index=True)
        source_col = "_source_file" if "_source_file" in prov.columns else "source_file"
        target_col = "target" if "target" in prov.columns else "mapped_target"
        save(prov.groupby([source_col, target_col], as_index=False).size().rename(columns={source_col:"source_file", target_col:"mapped_target", "size":"count"}), "table_v4_source_file_label_counts.csv")

    # The canonical main comparison is the leakage-safe, uniformly tuned
    # result set.  Extended experiments (weight ablation, significance,
    # deployment and robustness) remain sourced from EXT below.
    metrics=pd.read_csv(TUNED/"metrics_3seeds.csv")
    extended_metrics=metrics
    agg=pd.read_csv(TUNED/"metrics_aggregate.csv", header=[0,1])
    agg.columns=["model" if i==0 else f"{a}_{b}" for i,(a,b) in enumerate(agg.columns)]
    save_main_summary(agg, metrics)
    save(pd.read_csv(EXT/"bootstrap_confidence_intervals.csv"), "table_v2_bootstrap_ci.csv")
    save(pd.read_csv(EXT/"paired_significance_tests.csv"), "table_v2_paired_tests.csv")
    effects_path = ADDITIONAL / "statistical_effects_holm.csv"
    if effects_path.exists():
        save(pd.read_csv(effects_path), "table_v4_statistical_effects_holm.csv")
    save(pd.read_csv(EXT/"weight_ablation_summary.csv", header=[0,1]).rename(columns={"weight_metric":"weight_metric"}), "table_v2_weight_ablation.csv")
    save(pd.read_csv(EXT/"deployment"/"deployment_benchmark.csv"), "table_v2_deployment.csv")
    save(pd.read_csv(EXT/"deployment"/"robustness_metrics.csv"), "table_v2_robustness.csv")
    nsl=pd.read_csv(NSL/"metrics.csv")
    save(nsl, "table_nsl_kdd_results.csv")
    save(pd.read_csv(NSL/"classification_report_extra_trees_chi2.csv"), "table_nsl_kdd_class_metrics_extra_trees.csv")
    save(pd.read_csv(NSL/"confusion_matrix_extra_trees_chi2.csv"), "table_nsl_kdd_confusion_matrix_extra_trees.csv")
    save(pd.read_csv(QUALITY/"repeated_split_summary.csv", header=[0,1]), "table_v2_repeated_split_summary.csv")
    save(pd.read_csv(QUALITY/"equal_weight_ablation_summary.csv", header=[0,1]), "table_v2_equal_weight_ablation.csv")
    save(pd.read_csv(QUALITY/"feature_stability_summary.csv", header=[0,1]), "table_v2_feature_stability.csv")
    # Canonical publication-final class reports (after feature-order correction).
    save(pd.read_csv(TUNED/"classification_report_random_forest_chi2_seed42.csv"), "table_v2_class_metrics_rf_chi2.csv")
    save(pd.read_csv(TUNED/"classification_report_random_forest_all_seed42.csv"), "table_v2_class_metrics_rf_all.csv")
    save(pd.read_csv(TUNED/"classification_report_weighted_rf_chi2_seed42.csv"), "table_v2_class_metrics_weighted_rf.csv")
    save(pd.read_csv(TUNED/"confusion_matrix_random_forest_chi2_seed42.csv"), "table_v2_confusion_matrix_rf_chi2.csv")
    save(pd.read_csv(TUNED/"confusion_matrix_random_forest_all_seed42.csv"), "table_v2_confusion_matrix_rf_all.csv")
    save(pd.read_csv(TUNED/"confusion_matrix_weighted_rf_chi2_seed42.csv"), "table_v2_confusion_matrix_weighted_rf.csv")
    save(pd.read_csv(REPEATED/"summary.csv", header=[0,1]), "table_v3_repeated_10split_summary.csv")
    save(pd.read_csv(REPEATED/"paired_split_tests.csv"), "table_v3_repeated_10split_tests.csv")
    save(pd.read_csv(WEIGHT_MECHANISM/"weight_mechanism_summary.csv"), "table_v3_weight_mechanism.csv")
    save(pd.read_csv(IMB/"classification_report_random_forest_chi2_seed42.csv"), "table_v3_imbalanced_class_metrics_rf_chi2.csv")
    save(pd.read_csv(IMB/"confusion_matrix_random_forest_chi2_seed42.csv"), "table_v3_imbalanced_confusion_matrix_rf_chi2.csv")
    save(pd.read_csv(TUNING/"test_metrics.csv"), "table_v3_individually_tuned_baselines.csv")
    if ADDITIONAL.exists():
        add_summary_table = pd.read_csv(ADDITIONAL/"method_comparison_summary.csv", header=[0,1])
        add_summary_table.columns = ["method" if i == 0 else f"{a}_{b}" for i, (a, b) in enumerate(add_summary_table.columns)]
        save_feature_probability_summary(add_summary_table)
        lat = pd.read_csv(ADDITIONAL/"deployment_latency_percentiles.csv")
        lat["thread_mode"] = lat["n_jobs"].map({1:"单线程", -1:"多线程"}).fillna(lat["n_jobs"].astype(str))
        for old, new in [("p50", "p50_ms"), ("p95", "p95_ms"), ("p99", "p99_ms")]:
            if old in lat.columns and new not in lat.columns: lat[new] = lat[old]
        if "count" not in lat.columns: lat["count"] = 30
        save(lat[["method", "thread_mode", "batch_size", "count", "p50_ms", "p95_ms", "p99_ms", "mean_ms"]], "table_v4_deployment_latency_percentiles.csv")
        rob4 = pd.read_csv(ADDITIONAL/"robustness_shared_perturbations.csv")
        rob_summary = rob4.groupby(["method","condition"], dropna=False)[["accuracy","balanced_accuracy","macro_f1","relative_macro_f1_drop"]].agg(["mean","std"]).reset_index()
        save(rob_summary, "table_v4_shared_robustness_summary.csv")
        save(pd.read_csv(ADDITIONAL/"calibration_curve_points.csv"), "table_v4_calibration_curve_points.csv")
        for fn, out_name in [("probability_metric_bootstrap_ci.csv","table_v4_probability_metric_bootstrap_ci.csv"),("paired_macro_f1_bootstrap_ci.csv","table_v4_paired_macro_f1_bootstrap_ci.csv"),("feature_selection_frequency.csv","table_v4_feature_selection_frequency.csv"),("protocol_sensitivity_metrics.csv","table_v4_protocol_sensitivity.csv")]:
            p = (ADDITIONAL / fn) if fn != "protocol_sensitivity_metrics.csv" else (ROOT / "results_protocol_sensitivity_v4" / fn)
            if p.exists(): save(pd.read_csv(p), out_name)
        for fn, out_name in [("imbalanced_predicted_class_counts.csv", "table_v4_imbalanced_predicted_class_counts.csv")]:
            p = ADDITIONAL / fn
            if p.exists(): save(pd.read_csv(p), out_name)
    if COVERAGE.exists():
        save(pd.read_csv(COVERAGE/"file_label_counts.csv"), "table_v4_file_label_coverage.csv")
        save(pd.read_csv(COVERAGE/"file_label_matrix.csv"), "table_v4_file_label_matrix.csv")
    if (NSL/"class_counts.csv").exists():
        save(pd.read_csv(NSL/"class_counts.csv"), "table_v4_nsl_kdd_class_counts.csv")
        save(pd.read_csv(NSL/"minority_analysis_summary.csv"), "table_v4_nsl_kdd_minority_analysis.csv")
    cm_path = TUNED / "confusion_matrix_random_forest_chi2_seed42.csv"
    if cm_path.exists():
        cm = pd.read_csv(cm_path, index_col=0)
        norm = cm.div(cm.sum(axis=1).replace(0, 1), axis=0)
        norm.index.name = "true_label"
        save(norm.reset_index(), "table_v4_normalized_confusion_matrix_rf_chi2.csv")
    if FEATURE_QUALITY.exists():
        fq = pd.read_csv(FEATURE_QUALITY/"feature_quality_summary.csv")
        fq_summary = pd.DataFrame([
            {"audit_item":"特征总数", "value":len(fq)},
            {"audit_item":"常量特征数", "value":int(fq["is_constant"].sum())},
            {"audit_item":"近零方差特征数", "value":int(fq["is_near_zero_variance"].sum())},
            {"audit_item":"存在缺失值的特征数", "value":int((fq["missing_count"] > 0).sum())},
            {"audit_item":"最大缺失值数量", "value":int(fq["missing_count"].max())},
            {"audit_item":"唯一值比例最小值", "value":float(fq["unique_ratio"].min())},
            {"audit_item":"唯一值比例最大值", "value":float(fq["unique_ratio"].max())},
        ])
        save(fq_summary, "table_v4_feature_quality_summary.csv")
        save(pd.read_csv(FEATURE_QUALITY/"high_correlation_pairs.csv"), "table_v4_high_correlation_pairs.csv")

    # Performance figure.
    plot=metrics.groupby("model", as_index=False)[["accuracy","macro_f1"]].mean().melt("model", var_name="metric", value_name="score")
    plot["model"] = plot["model"].map({
        "decision_tree_chi2":"Decision tree + χ²", "extra_trees_chi2":"ExtraTrees + χ²",
        "random_forest_all":"RF (all)", "random_forest_chi2":"RF + χ²",
        "svm_all":"SVM", "weighted_rf_chi2":"Weighted RF + χ²"}).fillna(plot["model"])
    plot["metric"] = plot["metric"].map({"accuracy":"Accuracy", "macro_f1":"Macro-F1"})
    plot.score*=100
    plt.figure(figsize=(8.5,4.8)); sns.barplot(data=plot,x="model",y="score",hue="metric",palette=["#4472C4","#ED7D31"])
    plt.ylabel("Score (%)"); plt.xlabel("Model"); plt.ylim(88,98); plt.xticks(rotation=20,ha="right"); plt.title("Unified model comparison"); plt.tight_layout(); plt.savefig(FIG/"fig_v2_model_performance.png"); plt.close()

    # Deployment figure.
    dep=pd.read_csv(ADDITIONAL/"deployment_latency_percentiles.csv")
    d=dep[dep.batch_size.isin([1,32,128,512])].copy()
    for old, new in [("p50", "p50_ms"), ("p95", "p95_ms"), ("p99", "p99_ms")]:
        if old in d.columns and new not in d.columns:
            d[new] = d[old]
    d["threads"] = d["n_jobs"].map({1:"Single thread", -1:"Multi thread"})
    d["method"] = d["method"].map({"all":"All features", "chi2":"Chi-square"}).fillna(d["method"])
    plt.figure(figsize=(8.5,4.8)); sns.lineplot(data=d,x="batch_size",y="p50_ms",hue="threads",style="method",markers=True,dashes=False)
    plt.xscale("log",base=2); plt.ylabel("P50 latency per sample (ms)"); plt.xlabel("Batch size"); plt.title("Offline inference P50 latency"); plt.tight_layout(); plt.savefig(FIG/"fig_v2_latency.png"); plt.close()

    # Robustness figure.
    rob=pd.read_csv(ADDITIONAL/"robustness_shared_perturbations.csv")
    r=rob[rob.condition!="clean"].copy(); r["condition"]=r.condition.map({"gaussian_noise_1pct":"Gaussian noise (1%)", "gaussian_noise_5pct":"Gaussian noise (5%)", "feature_mask_1pct":"Feature masking (1%)", "feature_mask_5pct":"Feature masking (5%)"}).fillna(r.condition)
    r["method"] = r["method"].map({"all":"All features", "chi2":"Chi-square", "mutual_info":"Mutual information", "anova":"ANOVA"}).fillna(r["method"])
    plt.figure(figsize=(10,5)); sns.barplot(data=r,x="condition",y="macro_f1",hue="method",errorbar="sd"); plt.ylabel("Macro-F1"); plt.xlabel("Shared perturbation"); plt.ylim(0,1); plt.xticks(rotation=20,ha="right"); plt.title("Robustness under shared perturbations"); plt.tight_layout(); plt.savefig(FIG/"fig_v2_robustness.png"); plt.close()
    stab=pd.read_csv(QUALITY/"feature_stability.csv")
    plt.figure(figsize=(7.5,4.6)); sns.barplot(data=stab, x="k", y="jaccard_mean", errorbar="sd", color="#70AD47")
    plt.ylim(0,1); plt.ylabel("Pairwise Jaccard similarity"); plt.xlabel("Number of selected features"); plt.title("Training-only chi-square feature stability"); plt.tight_layout(); plt.savefig(FIG/"fig_v2_feature_stability.png"); plt.close()

    if ADDITIONAL.exists():
        cal = pd.read_csv(ADDITIONAL/"calibration_curve_points.csv")
        cal["method"] = cal["method"].map({"all":"All features", "chi2":"Chi-square", "mutual_info":"Mutual information", "anova":"ANOVA"}).fillna(cal["method"])
        fig, axes = plt.subplots(2, 2, figsize=(10, 8), sharex=True, sharey=True)
        for ax, method in zip(axes.ravel(), cal["method"].drop_duplicates()):
            sub = cal[cal["method"] == method]
            sns.lineplot(data=sub, x="prob_pred", y="prob_true", hue="class", marker="o", ax=ax, legend=False)
            ax.plot([0,1],[0,1],"k--",linewidth=1); ax.set_title(method); ax.set_xlim(0,1); ax.set_ylim(0,1)
            ax.set_xlabel("Predicted probability"); ax.set_ylabel("Observed frequency")
        fig.suptitle("Test-set probability calibration", y=1.01); fig.tight_layout(); fig.savefig(FIG/"fig_v4_calibration_curves.png"); plt.close(fig)
        lat=pd.read_csv(ADDITIONAL/"deployment_latency_percentiles.csv")
        for old, new in [("p50", "p50_ms"), ("p95", "p95_ms"), ("p99", "p99_ms")]:
            if old in lat.columns and new not in lat.columns:
                lat[new] = lat[old]
        lat1=lat[lat.batch_size==1].copy(); lat1["threads"]=lat1.n_jobs.map({1:"single-thread",-1:"multi-thread"})
        plt.figure(figsize=(7.5,4.6)); sns.barplot(data=lat1,x="method",y="p50_ms",hue="threads"); plt.ylabel("P50 latency (ms/sample)"); plt.xlabel("Feature method"); plt.title("Single- and multi-thread P50 latency (batch=1)"); plt.tight_layout(); plt.savefig(FIG/"fig_v4_latency_p50.png"); plt.close()
        freq = pd.read_csv(ADDITIONAL/"feature_selection_frequency.csv").head(20)
        plt.figure(figsize=(8.5,6)); sns.barplot(data=freq, y="feature", x="selection_count", color="#4472C4"); plt.xlabel("Selection count across 5 folds"); plt.ylabel("Feature"); plt.title("Top-20 χ² feature selection frequency"); plt.tight_layout(); plt.savefig(FIG/"fig_v4_feature_selection_frequency.png"); plt.close()

    rf=metrics[metrics.model=="random_forest_chi2"]; rf_all=metrics[metrics.model=="random_forest_all"]; dt=metrics[metrics.model=="decision_tree_chi2"]; svm=metrics[metrics.model=="svm_all"]; et=metrics[metrics.model=="extra_trees_chi2"]
    wrf=extended_metrics[extended_metrics.model=="weighted_rf_chi2"]
    def mean_std(x,col): return f"{x[col].mean()*100:.2f}%±{x[col].std(ddof=1)*100:.2f}%"
    rep = pd.read_csv(REPEATED/"summary.csv", header=[0,1]); rep.columns=["model" if i==0 else f"{a}_{b}" for i,(a,b) in enumerate(rep.columns)]
    rep_tests = pd.read_csv(REPEATED/"paired_split_tests.csv"); rep_test = rep_tests.loc[rep_tests.metric=="macro_f1"].iloc[0]
    def rep_fmt(model):
        row=rep.loc[rep.model==model].iloc[0]
        return f"{row['macro_f1_mean']*100:.2f}%±{row['macro_f1_std']*100:.2f}%"
    add_summary = pd.read_csv(ADDITIONAL/"method_comparison_summary.csv", header=[0,1])
    add_summary.columns=["method" if i==0 else f"{a}_{b}" for i,(a,b) in enumerate(add_summary.columns)]
    def add_fmt(method, metric):
        row=add_summary.loc[add_summary.method==method].iloc[0]
        return f"{row[f'{metric}_mean']:.4f}±{row[f'{metric}_std']:.4f}"
    latency = pd.read_csv(ADDITIONAL/"deployment_latency_percentiles.csv")
    for old, new in [("p50", "p50_ms"), ("p95", "p95_ms"), ("p99", "p99_ms")]:
        if old in latency.columns and new not in latency.columns:
            latency[new] = latency[old]
    def latency_fmt(method, jobs, batch, col):
        row = latency[(latency.method == method) & (latency.n_jobs == jobs) & (latency.batch_size == batch)].iloc[0]
        return f"{row[col]:.4f}"
    rob4 = pd.read_csv(ADDITIONAL/"robustness_shared_perturbations.csv")
    def robust_drop_fmt(method, condition):
        row = rob4[(rob4.method == method) & (rob4.condition == condition)]
        return f"{row.relative_macro_f1_drop.mean()*100:.2f}%"
    # Read the canonical final class report and bootstrap interval so the
    # chapter draft cannot drift from the tables and Word manuscript.
    rf_report = pd.read_csv(TUNED/"classification_report_random_forest_chi2_seed42.csv")
    rf_report = rf_report.rename(columns={rf_report.columns[0]: "class"})
    def rf_f1(name):
        return float(rf_report.loc[rf_report["class"] == name, "f1-score"].iloc[0])
    boot = pd.read_csv(TUNED/"bootstrap_confidence_intervals.csv")
    boot42 = boot[(boot.model == "random_forest_chi2") & (boot.seed == 42)].iloc[0]
    imb = pd.read_csv(IMB/"metrics_3seeds.csv")
    imb_rf = imb[imb.model == "random_forest_chi2"]
    nsl_note = "NSL-KDD 主比较仅纳入使用完整官方 KDDTrain+ 训练集的模型；加权随机森林因需要额外验证集，不纳入该主表。"
    effects = pd.read_csv(ADDITIONAL/"statistical_effects_holm.csv") if (ADDITIONAL/"statistical_effects_holm.csv").exists() else pd.DataFrame()
    weighted_effect = effects[effects.comparison.str.startswith("weighted_rf")].iloc[0] if not effects.empty else None
    draft=f"""# 第四章 实验结果与分析（v4统一口径）

## 4.1 数据处理与审计

CIC-IDS2017原始8个CSV共包含 {audit['source_rows']:,} 条记录。标签映射后保留 {audit['mapped_rows']:,} 条，其中 {audit['invalid_rows']:,} 条因缺失、无穷或非数值特征被清除，有效数值记录为 {audit['valid_rows']:,} 条。全局特征向量去重后得到 {audit['unique_rows_before_conflict']:,} 个唯一向量。跨标签冲突组共涉及 {audit['rows_in_conflicting_groups']:,} 条原始记录和 {audit['conflicting_feature_hash_count']:,} 个唯一特征向量，其中后续标签与首次标签不一致的记录为 {audit['cross_label_mismatch_rows']:,} 条。剔除冲突向量后剩余 {audit['unique_rows_after_conflict']:,} 条。应用每类最多20,000条上限后保留 {audit['capped_rows_before_balance']:,} 条，按五类最小规模平衡后得到 {audit['balanced_rows']:,} 条样本，每类 {audit['balanced_per_class']} 条。最终训练、验证和测试集分别为2,355、505和505条。

## 4.2 无泄漏参数选择

统一最终实验协议固定为：χ²保留60个特征，随机森林、加权随机森林与ExtraTrees均使用100棵树、min_samples_leaf=2；决策树使用χ²60、最大深度10；SVM使用全部78维、C=100。超参数选择仅在训练集内通过5折分层交叉验证完成，每个折单独拟合MinMaxScaler和χ²排序。三个随机种子固定同一训练/验证/测试划分，仅改变模型随机状态，因此均值±标准差主要反映模型随机性，不代表跨数据划分方差。

## 4.3 CIC-IDS2017主结果

在三个随机种子下，χ²随机森林的平均Accuracy为{mean_std(rf,'accuracy')}、Macro-F1为{mean_std(rf,'macro_f1')}；同配置78维全特征随机森林的平均Accuracy为{mean_std(rf_all,'accuracy')}、Macro-F1为{mean_std(rf_all,'macro_f1')}。两种输入方案的均值几乎相同，χ²筛选的主要效果是将输入维度由78维压缩为60维，而不是带来可据此宣称的精度跃升。决策树、ExtraTrees和SVM的平均Macro-F1分别为 {mean_std(dt,'macro_f1')}、{mean_std(et,'macro_f1')}和{mean_std(svm,'macro_f1')}。该结论限定于本研究构建的平衡五分类子集，不外推为CIC-IDS2017全量性能。

## 4.4 加权随机森林与统计检验

加权随机森林使用验证集上的单树平衡准确率计算权重。其平均Accuracy为 {mean_std(wrf,'accuracy')}，Macro-F1为 {mean_std(wrf,'macro_f1')}，与普通随机森林接近。逐样本McNemar检验和配对置换检验均未显示加权模型相对普通随机森林存在统计显著差异；Holm校正后加权比较的p值仍为1.000，净Accuracy效应为0，discordant pair为0。因此加权投票仅作为探索性机制报告，不能据此宣称Macro-F1差异也完成了显著性检验。

## 4.5 置信区间与类别级分析

逐样本预测用于计算测试集Bootstrap置信区间，采用百分位法、95%置信水平和3,000次重采样，并保存于相应结果表。以最终协议seed=42的χ²随机森林为例，Accuracy为{boot42['accuracy']:.3f}，95%区间为[{boot42['accuracy_ci_low']:.3f},{boot42['accuracy_ci_high']:.3f}]；Macro-F1为{boot42['macro_f1']:.3f}，95%区间为[{boot42['macro_f1_ci_low']:.3f},{boot42['macro_f1_ci_high']:.3f}]。对应类别F1为：Bot {rf_f1('Bot'):.3f}、DoS/DDoS {rf_f1('DoS/DDoS'):.3f}、Normal {rf_f1('Normal'):.3f}、Brute Force {rf_f1('Brute Force'):.3f}、Web Attack {rf_f1('Web Attack'):.3f}。正式正文不以单一Accuracy替代宏平均指标。

## 4.6 特征选择公平对照与概率质量

在相同Top-60预算下，互信息、ANOVA、χ²和全特征方法的平均Macro-F1分别为{add_fmt('mutual_info','macro_f1')}、{add_fmt('anova','macro_f1')}、{add_fmt('chi2','macro_f1')}和{add_fmt('all','macro_f1')}；对应Log Loss分别为{add_fmt('mutual_info','log_loss')}、{add_fmt('anova','log_loss')}、{add_fmt('chi2','log_loss')}和{add_fmt('all','log_loss')}，宏平均Brier Score分别为{add_fmt('mutual_info','brier_macro')}、{add_fmt('anova','brier_macro')}、{add_fmt('chi2','brier_macro')}和{add_fmt('all','brier_macro')}。四种方法的ECE分别为全特征{add_fmt('all','ece')}、χ²{add_fmt('chi2','ece')}、互信息{add_fmt('mutual_info','ece')}和ANOVA{add_fmt('anova','ece')}。逐样本概率和校准曲线均已保存。互信息在Macro-F1和Log Loss上略占优势，但差异较小，不能据此宣称χ²为全局最优。

## 4.7 离线推理性能

部署实验测量模型核心predict调用的离线延迟，不包含原始流量解析和特征提取。统一新增协议下，χ²随机森林batch=1单线程P50/P95/P99为{latency_fmt('chi2',1,1,'p50_ms')}/{latency_fmt('chi2',1,1,'p95_ms')}/{latency_fmt('chi2',1,1,'p99_ms')} ms/样本，多线程为{latency_fmt('chi2',-1,1,'p50_ms')}/{latency_fmt('chi2',-1,1,'p95_ms')}/{latency_fmt('chi2',-1,1,'p99_ms')} ms/样本；batch=512时单线程为{latency_fmt('chi2',1,512,'p50_ms')}/{latency_fmt('chi2',1,512,'p95_ms')}/{latency_fmt('chi2',1,512,'p99_ms')} ms/样本，多线程为{latency_fmt('chi2',-1,512,'p50_ms')}/{latency_fmt('chi2',-1,512,'p95_ms')}/{latency_fmt('chi2',-1,512,'p99_ms')} ms/样本。结果仅反映当前个人电脑上的核心predict调用，不能等同于校园网关部署。

## 4.8 扰动鲁棒性

所有方法复用同一组固定噪声矩阵和特征屏蔽掩码。以χ²方法为例，1%高斯噪声和5%特征屏蔽造成的Macro-F1相对下降分别为{robust_drop_fmt('chi2','gaussian_noise_1pct')}和{robust_drop_fmt('chi2','feature_mask_5pct')}。该实验是受控扰动分析，不等同于真实攻击流量鲁棒性。

## 4.9 不平衡敏感性

在不进行五类等量平衡、仅保留每类上限的数据上，统一配置χ²随机森林三种种子的Macro-F1分别为{', '.join(f'{v*100:.2f}%' for v in imb_rf['macro_f1'])}，均值为{imb_rf['macro_f1'].mean()*100:.2f}%±{imb_rf['macro_f1'].std(ddof=1)*100:.2f}%。该结果低于平衡子集结果，说明类别分布会显著影响评价结果。

## 4.10 外部公开数据集与限制

NSL-KDD采用官方KDDTrain+和KDDTest+划分，独立构建Normal、DoS、Probe、R2L和U2R五类任务。三列类别特征的独热编码仅在训练集拟合，并将测试集列对齐到训练集列空间；本次数据检查未发现测试集独有类别水平。{nsl_note}该任务的特征体系和标签定义与CIC-IDS2017不同，只能作为独立公开基准，不能解释为未经对齐的跨数据集迁移。U2R和R2L少数类识别困难，说明类别分布会显著影响Macro-F1。CIC-IDS2017按原始文件切分存在类别覆盖不足问题，当前仅作泛化风险审计，不报告不满足类别覆盖条件的伪五分类结果。

## 4.11 重复划分、等权消融与特征稳定性

为避免固定划分带来的偶然性，进一步将去重平衡样本按70%/15%/15%进行10次独立分层划分。RF全特征Macro-F1为{rep_fmt("rf_all")}，χ²60 RF为{rep_fmt("rf_chi2")}；平均差为{rep_test["mean_delta_chi2_minus_all"]*100:.3f}个百分点，符号置换检验p={rep_test["paired_sign_flip_p_value"]:.3f}，不支持稳定显著优势。

等权投票消融将普通RF概率平均作为基线，并与基于验证集平衡准确率的树权重进行逐样本比较。初步三次划分下两种策略的Accuracy、Macro-F1均完全相同；进一步权重机制分析也显示505个测试样本的最终预测分歧数为0，说明当前数据和参数下加权策略没有改变最终类别决策，应作为适用性和负结果证据报告。

对seed=42的100棵树进一步分析，单树验证平衡准确率均值为0.9059、标准差为0.0114，权重变异系数仅为1.26%，归一化权重熵为0.999983。加权与等权概率的平均L1差异为0.000299，505个测试样本的预测分歧数为0。这说明森林内单树性能较为集中，线性归一化后权重接近均匀，是加权策略未改变最终分类的直接原因。

特征稳定性在每次训练集内进行五折分层交叉验证，并计算各折Top-k集合的两两Jaccard相似度。Top-10、Top-20和Top-60的平均相似度分别为0.851、0.915和0.957；较大的k具有更高稳定性，但这不等价于每个特征都具有因果意义。

## 4.12 结论边界

本章结果支持：严格折内预处理、训练集特征选择、交叉验证选参和数据泄漏审计能够构成可复现实验流程；随机森林在当前平衡抽样任务上性能最高；加权投票未产生稳定显著收益。结果不支持97%准确率、真实网关部署或跨数据集泛化已被证明等表述。
"""
    (OUT/"chapter4_results_draft.md").write_text(draft, encoding="utf-8")
    save(pd.read_csv(IMB/"metrics_3seeds.csv"), "table_unified_imbalanced_sensitivity.csv")
    (OUT/"README.md").write_text("主结果来自 results_publication_final（统一配置 k=60、100棵树、min_samples_leaf=2，并包含全特征RF）；10次重复划分来自 results_repeated_splits_v3；不平衡敏感性来自 results_imbalanced_v3；加权机制分析来自 results_weight_mechanism_v3；NSL-KDD来自 results_nsl_kdd_fair_v2。旧版结果目录不得与本目录混用。", encoding="utf-8")
    print(f"V2_PAPER_MATERIALS_WRITTEN={OUT}")

if __name__ == "__main__": main()




