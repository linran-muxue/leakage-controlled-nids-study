"""Add class-level metrics and confusion matrices to the imbalanced study."""
from pathlib import Path
import argparse
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", type=Path, required=True)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    result_dir = args.results_dir
    outputs = []
    for pred_path in sorted(result_dir.glob(f"predictions_*_seed{args.seed}.csv")):
        name = pred_path.stem.replace(f"predictions_", "").replace(f"_seed{args.seed}", "")
        pred = pd.read_csv(pred_path)
        labels = sorted(set(pred["y_true"]) | set(pred["y_pred"]))
        pd.DataFrame(classification_report(pred.y_true, pred.y_pred, labels=labels, output_dict=True, zero_division=0)).T.to_csv(result_dir / f"classification_report_{name}_seed{args.seed}.csv", encoding="utf-8-sig")
        pd.DataFrame(confusion_matrix(pred.y_true, pred.y_pred, labels=labels), index=labels, columns=labels).to_csv(result_dir / f"confusion_matrix_{name}_seed{args.seed}.csv", encoding="utf-8-sig")
        outputs.append(name)
    print("CLASS_REPORTS_WRITTEN=" + ",".join(outputs))


if __name__ == "__main__":
    main()
