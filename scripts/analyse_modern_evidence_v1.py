"""Secondary evidence for every modern corpus, recomputed from released predictions.

The paper's secondary metrics (calibration, per-class behaviour, how often the
gate could change a label) were measured on CIC-IDS2017.  Every extension corpus
released its per-row predictions with the fused probabilities, so the same
quantities can be recomputed for each of them: expected calibration error,
per-class precision/recall/F1, macro one-vs-rest AUROC, and the number of labels
the gate moves relative to the same-members equal fusion.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results_modern_evidence_v1"
SEEDS = (42, 2024, 3407, 7, 13, 101, 202, 303, 404, 505)
CORPORA = (
    ("results_rccf_litnet2020_v1", "LITNET-2020", 2020),
    ("results_rccf_iot23_v1", "IoT-23", 2020),
    ("results_rccf_rt_iot2022_v1", "RT-IoT2022", 2022),
    ("results_rccf_aci_iot2023_v1", "ACI-IoT-2023", 2023),
    ("results_rccf_cic_iot2023_v1", "CIC-IoT-2023", 2023),
    ("results_rccf_uavids2025_v1", "UAVIDS-2025", 2025),
    ("results_rccf_genis2025_v1", "GeNIS", 2025),
    ("results_rccf_ids2025_v1", "IDS2025", 2025),
    ("results_rccf_gotham2025_v1", "Gotham-2025", 2025),
    ("results_rccf_gotham2025_v1_k8", "Gotham-2025 (k=8)", 2025),
    ("results_rccf_ctu_idseval6_v1", "CTU-IDSEVAL-6", 2026),
    ("results_rccf_6tisch2026_v1", "6TiSCHSet-2026", 2026),
    ("results_rccf_rtn2026_v1", "RTN-traffic-2026", 2026),
    ("results_rccf_cic_ids2018_v1", "CIC-IDS2018", 2018),
)


def ece(probabilities: np.ndarray, correct: np.ndarray, bins: int = 15) -> float:
    edges = np.linspace(0.0, 1.0, bins + 1)
    confidence = probabilities.max(axis=1)
    total = 0.0
    for low, high in zip(edges[:-1], edges[1:]):
        mask = (confidence > low) & (confidence <= high)
        if not mask.any():
            continue
        total += mask.mean() * abs(correct[mask].mean() - confidence[mask].mean())
    return float(total)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    rows = []
    for folder, label, year in CORPORA:
        directory = ROOT / folder
        if not (directory / "predictions_rccf_seed42.csv").exists():
            continue
        ece_gate, ece_equal, auc, moved, agreement = [], [], [], [], []
        precision = recall = f1 = None
        for seed in SEEDS:
            gate_path = directory / f"predictions_rccf_seed{seed}.csv"
            equal_path = directory / f"predictions_equal_fusion_seed{seed}.csv"
            if not (gate_path.exists() and equal_path.exists()):
                continue
            gate = pd.read_csv(gate_path)
            equal = pd.read_csv(equal_path)
            prob_columns = [c for c in gate.columns if c.startswith("prob_")]
            if not prob_columns:
                continue
            probabilities = gate[prob_columns].to_numpy(dtype=float)
            truth = gate["true_label"].astype(str).to_numpy()
            prediction = gate["predicted_label"].astype(str).to_numpy()
            classes = np.array([c[len("prob_"):] for c in prob_columns])
            correct = prediction == truth
            ece_gate.append(ece(probabilities, correct))
            equal_prob = equal[[c for c in equal.columns if c.startswith("prob_")]].to_numpy(float)
            equal_pred = equal["predicted_label"].astype(str).to_numpy()
            ece_equal.append(ece(equal_prob, equal_pred == truth))
            moved.append(int((prediction != equal_pred).sum()))
            agreement.append(float((prediction == equal_pred).mean()))
            if len(classes) > 2:
                try:
                    index_of = {name: i for i, name in enumerate(classes)}
                    truth_index = np.array([index_of.get(t, -1) for t in truth])
                    valid = truth_index >= 0
                    if valid.sum() < len(classes):
                        raise ValueError("too few rows carry a known class")
                    auc.append(float(roc_auc_score(
                        np.eye(len(classes))[truth_index[valid]],
                        probabilities[valid], average="macro", multi_class="ovr")))
                except ValueError:
                    pass
            if precision is None:
                precision, recall, f1, _ = precision_recall_fscore_support(
                    truth, prediction, labels=classes, average=None, zero_division=0)
        if not ece_gate:
            continue
        rows.append({
            "corpus": label, "published": year, "seeds": len(ece_gate),
            "ece_gate": float(np.mean(ece_gate)), "ece_equal": float(np.mean(ece_equal)),
            "macro_auroc_ovr": float(np.mean(auc)) if auc else None,
            "labels_moved_mean": float(np.mean(moved)),
            "labels_moved_max": int(np.max(moved)),
            "prediction_agreement": float(np.mean(agreement)),
            "classes": int(len(f1)) if f1 is not None else None,
            "weakest_class_f1": float(np.min(f1)) if f1 is not None else None,
        })
        print(f"{label:<20} seeds={len(ece_gate):>2} ECE {np.mean(ece_gate):.5f} vs "
              f"{np.mean(ece_equal):.5f} | moved {np.mean(moved):.1f} | "
              f"agreement {np.mean(agreement):.6f}", flush=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(OUT / "per_corpus_evidence.csv", index=False, encoding="utf-8-sig")
    summary = {
        "corpora": len(rows),
        "max_labels_moved_mean": float(frame["labels_moved_mean"].max()),
        "min_prediction_agreement": float(frame["prediction_agreement"].min()),
        "max_ece_gate": float(frame["ece_gate"].max()),
        "min_ece_gate": float(frame["ece_gate"].min()),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2),
                                      encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("MODERN_EVIDENCE_DONE")


if __name__ == "__main__":
    main()
