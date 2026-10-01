"""Deployment-oriented metrics from the released per-row predictions.

Two prediction schemas are handled:
  * label + probability (``true_label``/``predicted_label``/``prob_*`` or
    ``y_true``/``y_pred``/``proba__*``) - gives AUROC, PR AUC, FPR at 95%/99%
    detection and the per-class one-vs-rest PR area;
  * label only (``y_true``/``y_pred``) - gives the operating-point confusion
    rates (false-positive rate on benign flows, attack recall and precision).

Everything is recomputed from published predictions, so no retraining is needed.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score, roc_curve

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
POSITIVE = "Normal"


def find_probability(frame: pd.DataFrame, label: str) -> np.ndarray | None:
    for pattern in (f"prob_{label}", f"proba__{label}", f"proba_{label}"):
        for column in frame.columns:
            if column.lower() == pattern.lower():
                return frame[column].to_numpy()
    return None


def seed_of(name: str) -> int | None:
    match = re.search(r"seed(\d+)\.csv$", name)
    return int(match.group(1)) if match else None


def model_of(name: str) -> str:
    rest = name[len("predictions_"):] if name.startswith("predictions_") else name
    rest = rest[:-4] if rest.endswith(".csv") else rest
    if "_seed" in rest:
        return rest.rsplit("_seed", 1)[0] or "rccf"
    return "rccf" if rest.startswith("seed") else (rest or "rccf")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dirs", nargs="+",
                    default=["results_full_corpus_v49", "results_scale_sensitivity_v46",
                             "results_seeds10_v5", "results_equal_fusion_control_v1",
                             "results_cic_natural_baselines_v3b/predictions"])
    ap.add_argument("--output-dir", default="results_deployment_metrics_v1")
    args = ap.parse_args()

    out = ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    class_rows: list[dict] = []
    for directory in args.dirs:
        folder = ROOT / directory
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob("predictions*.csv")):
            seed = seed_of(path.name)
            if seed is None:
                continue
            frame = pd.read_csv(path)
            if "true_label" in frame.columns:
                truth = frame["true_label"].astype(str)
                predicted = frame["predicted_label"].astype(str)
            elif "y_true" in frame.columns:
                truth = frame["y_true"].astype(str)
                predicted = frame["y_pred"].astype(str)
            else:
                continue
            model = model_of(path.name)
            attack_truth = (truth != POSITIVE).astype(int)
            attack_pred = (predicted != POSITIVE).astype(int)
            benign = attack_truth == 0
            entry = {
                "source": directory, "model": model, "seed": seed, "rows": int(len(frame)),
                "attack_support": int(attack_truth.sum()),
                "operating_fpr": float(attack_pred[benign].mean()) if benign.any() else np.nan,
                "operating_recall": (float((attack_pred & attack_truth).sum() /
                                           attack_truth.sum())
                                     if attack_truth.sum() else np.nan),
                "operating_precision": (float((attack_pred & attack_truth).sum() /
                                              attack_pred.sum())
                                        if attack_pred.sum() else np.nan),
            }
            normal_probability = find_probability(frame, POSITIVE)
            if normal_probability is not None and attack_truth.nunique() > 1:
                attack_probability = 1.0 - normal_probability
                fpr, tpr, _ = roc_curve(attack_truth, attack_probability)

                def fpr_at(target: float) -> float:
                    index = min(int(np.searchsorted(tpr, target)), len(fpr) - 1)
                    return float(fpr[index])

                entry.update({
                    "roc_auc": float(roc_auc_score(attack_truth, attack_probability)),
                    "pr_auc": float(average_precision_score(attack_truth, attack_probability)),
                    "fpr_at_95_tpr": fpr_at(0.95),
                    "fpr_at_99_tpr": fpr_at(0.99),
                    "tpr_at_1pct_fpr": float(tpr[min(int(np.searchsorted(fpr, 0.01)),
                                                    len(tpr) - 1)]),
                })
                for label in sorted(set(truth)):
                    binary = (truth == label).astype(int)
                    probability = find_probability(frame, label)
                    if probability is None or binary.nunique() < 2:
                        continue
                    class_rows.append({
                        "source": directory, "model": model, "seed": seed, "class": label,
                        "support": int(binary.sum()),
                        "pr_auc": float(average_precision_score(binary, probability)),
                    })
            rows.append(entry)
            print(f"{directory} {model} seed {seed}: "
                  f"operating FPR {entry['operating_fpr']:.5f}, "
                  f"AUROC {entry.get('roc_auc', float('nan')):.5f}", flush=True)

    metrics = pd.DataFrame(rows)
    metrics.to_csv(out / "deployment_metrics_by_seed.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(class_rows).to_csv(out / "per_class_pr_auc.csv", index=False,
                                    encoding="utf-8-sig")
    summary = {}
    for (source, model), group in metrics.groupby(["source", "model"]):
        summary[f"{source}|{model}"] = {
            "seeds": int(len(group)),
            "rows": int(group["rows"].iloc[0]),
            "operating_fpr": float(group["operating_fpr"].mean()),
            "operating_recall": float(group["operating_recall"].mean()),
            "operating_precision": float(group["operating_precision"].mean()),
        }
        for column in ("roc_auc", "pr_auc", "fpr_at_95_tpr", "fpr_at_99_tpr",
                       "tpr_at_1pct_fpr"):
            if column in group and group[column].notna().any():
                summary[f"{source}|{model}"][f"{column}_mean"] = \
                    float(group[column].mean())
    (out / "deployment_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in list(summary.items())[:6]},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
