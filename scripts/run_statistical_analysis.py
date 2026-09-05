from pathlib import Path
import sys
import json
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.statistical_analysis import bootstrap_metric_ci


ROOT = Path(__file__).resolve().parents[1]
FAIR = ROOT / "results_fair_final_checked"
OUT = ROOT / "results_paper_materials" / "tables"


def load_prediction(path):
    report = pd.read_csv(path, index_col=0)
    # Reports are metrics, not row-level predictions; use confusion matrices for paired accuracy.
    raise RuntimeError("row-level predictions are required for bootstrap; current CSVs contain aggregate reports only")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # Derive per-seed confusion-matrix bootstrap intervals by expanding cell counts.
    rows = []
    for model in ["random_forest_all", "random_forest_chi2", "weighted_rf_chi2"]:
        for seed in [42, 2024, 3407]:
            cm = pd.read_csv(FAIR / f"confusion_matrix_{model}_seed{seed}.csv", index_col=0)
            y_true, y_pred = [], []
            for true_label in cm.index:
                for pred_label in cm.columns:
                    count = int(cm.loc[true_label, pred_label])
                    y_true.extend([true_label] * count)
                    y_pred.extend([pred_label] * count)
            lo, point, hi = bootstrap_metric_ci(y_true, y_pred, metric="accuracy", n_bootstrap=3000, seed=seed)
            flo, fpoint, fhi = bootstrap_metric_ci(y_true, y_pred, metric="macro_f1", n_bootstrap=3000, seed=seed)
            rows.append({"model": model, "seed": seed, "accuracy": point, "accuracy_ci_low": lo, "accuracy_ci_high": hi, "macro_f1": fpoint, "macro_f1_ci_low": flo, "macro_f1_ci_high": fhi, "test_samples": len(y_true)})
    table = pd.DataFrame(rows)
    table.to_csv(OUT / "table_bootstrap_confidence_intervals.csv", index=False, encoding="utf-8-sig")

    (OUT / "statistical_limits.md").write_text(
        "现有结果文件不包含逐样本预测序列，因此未执行McNemar或配对置换检验；从混淆矩阵重建样本顺序不能形成真实配对。若需要配对显著性检验，必须重新运行实验并保存每个测试样本的真实标签和各模型预测标签。",
        encoding="utf-8",
    )
    print("STATISTICAL_MATERIALS_WRITTEN")


if __name__ == "__main__":
    main()
