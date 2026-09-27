from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "results_data_processing_audit_v2"
OUT = ROOT / "results_paper_materials_v3" / "tables"

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    audit = json.loads((AUDIT / "data_processing_audit.json").read_text(encoding="utf-8"))
    files = []
    for row in audit["raw_files"]:
        files.append({"file": row["file"], "source_rows": row["source_rows"], "mapped_rows": row["mapped_rows"], "excluded_label_rows": row["excluded_label_rows"], "invalid_rows": row["invalid_rows"], "valid_rows": row["valid_rows"], "raw_md5": row["file_hash"]["md5"], "raw_sha256": row["file_hash"]["sha256"]})
    pd.DataFrame(files).to_csv(OUT / "table_v6_raw_file_processing_audit.csv", index=False, encoding="utf-8-sig")
    totals = audit["raw_totals"]
    pd.DataFrame([{"stage": "raw source", "rows": totals["source_rows"]}, {"stage": "label mapped", "rows": totals["mapped_rows"]}, {"stage": "invalid removed", "rows": totals["invalid_rows"]}, {"stage": "valid numeric", "rows": totals["valid_rows"]}, {"stage": "unique before conflict", "rows": 2429924}, {"stage": "unique after conflict", "rows": 2429791}, {"stage": "capped before balance", "rows": 53237}, {"stage": "balanced research subset", "rows": 3365}]).to_csv(OUT / "table_v6_processing_stage_counts.csv", index=False, encoding="utf-8-sig")
    q = audit["processed"]["train_feature_quality"]
    pd.DataFrame([{ "metric": "feature count", "value": audit["processed"]["splits"]["train"]["feature_count"]}, {"metric": "constant feature count", "value": len(q["constant_features"])}, {"metric": "near-zero variance feature count", "value": len(q["near_zero_variance_features"])}, {"metric": "missing cells", "value": q["missing_cells"]}, {"metric": "infinite cells", "value": q["infinite_cells"]}, {"metric": "train-validation exact overlap", "value": audit["processed"]["cross_split_exact_feature_overlap"]["train_validation"]}, {"metric": "train-test exact overlap", "value": audit["processed"]["cross_split_exact_feature_overlap"]["train_test"]}, {"metric": "validation-test exact overlap", "value": audit["processed"]["cross_split_exact_feature_overlap"]["validation_test"]}]).to_csv(OUT / "table_v6_feature_quality_and_leakage_checks.csv", index=False, encoding="utf-8-sig")
    external = ROOT / "results_file_external_generalization_v1" / "file_external_results.csv"
    if external.exists():
        pd.read_csv(external).to_csv(OUT / "table_v6_file_external_generalization.csv", index=False, encoding="utf-8-sig")
    unsw_cross = ROOT / "results_unsw_nb15_cross_split_sensitivity_v2" / "metrics_aggregate.csv"
    unsw_raw = ROOT / "results_unsw_nb15_cross_split_sensitivity_v2" / "metrics.csv"
    if unsw_cross.exists() and unsw_raw.exists():
        agg = pd.read_csv(unsw_cross, header=[0, 1], index_col=0)
        raw = pd.read_csv(unsw_raw)
        rows = []
        for protocol in ("official_split", "remove_test_overlap", "remove_both_overlap"):
            sample = raw[raw["protocol"] == protocol].iloc[0]
            row = {
                "protocol": protocol,
                "removed_train_rows": int(sample["removed_train_rows"]),
                "removed_test_rows": int(sample["removed_test_rows"]),
                "test_rows": int(sample["test_rows"]),
            }
            for metric in ("accuracy", "balanced_accuracy", "macro_f1", "log_loss", "brier_macro", "ece"):
                row[f"{metric}_mean_std"] = f"{agg.loc[protocol, (metric, 'mean')]:.4f} ± {agg.loc[protocol, (metric, 'std')]:.4f}"
            rows.append(row)
        pd.DataFrame(rows).to_csv(OUT / "table_v6_unsw_cross_split_sensitivity.csv", index=False, encoding="utf-8-sig")
    print(f"WROTE={OUT}")

if __name__ == "__main__": main()
