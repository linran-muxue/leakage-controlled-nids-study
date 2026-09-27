"""Recompute the per-class metrics and confusion matrices from the predictions.

``audit_released_evidence_v1.py`` recomputes accuracy and Macro-F1 from the
released per-row predictions, but the class-level tables and the normalised
confusion matrices were only ever compared with themselves - and the manuscript
quotes several of their cells directly (NSL-KDD's R2L and U2R behaviour,
UNSW-NB15's Analysis, Backdoor, DoS, Generic and Normal F1).  This audit closes
that layer: it recomputes every per-class precision, recall and F1 from the
predictions, compares them with the stored reports and matrices, and checks the
values the manuscript prints against the recomputed ones.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN = (BASE / "English_SCI_Manuscript_v4.md").read_text(encoding="utf-8")
METRIC_TOL = 1e-6
MATRIX_TOL = 5e-4
problems: list[str] = []
checked = 0

# label, predictions, stored report, stored matrix, seeds
RUNS = (
    ("CIC natural RCCF", "results_rccf_cic_natural_v3b/predictions_seed%s.csv",
     "results_rccf_cic_natural_v3b/classification_report_seed%s.csv",
     "results_rccf_cic_natural_v3b/confusion_matrix_normalized_seed%s.csv", (42, 2024, 3407)),
    ("CIC natural equal RF (chi-square)",
     "results_cic_natural_baselines_v3b/predictions/predictions_equal_rf_chi2_seed%s.csv",
     "results_cic_natural_baselines_v3b/classification_report_equal_rf_chi2_seed%s.csv",
     "results_cic_natural_baselines_v3b/confusion_matrix_normalized_equal_rf_chi2_seed%s.csv",
     (42, 2024, 3407)),
    ("NSL-KDD", "results_rccf_nsl_v2_final/predictions_seed%s.csv",
     "results_rccf_nsl_v2_final/classification_report_seed%s.csv",
     "results_rccf_nsl_v2_final/confusion_matrix_normalized_seed%s.csv", (42, 2024, 3407)),
    ("UNSW-NB15", "results_rccf_unsw_v2_final/predictions_seed%s.csv",
     "results_rccf_unsw_v2_final/classification_report_seed%s.csv",
     # the UNSW run stores per-class reports for two of its three seeds and no
     # normalised matrix; the paper's UNSW class-level claims are seed 42
     "results_rccf_unsw_v2_final/confusion_matrix_normalized_seed%s.csv", (42, 2024)),
)


def truth_columns(frame: pd.DataFrame) -> tuple[str, str]:
    for truth, prediction in (("true_label", "predicted_label"), ("y_true", "y_pred")):
        if truth in frame.columns and prediction in frame.columns:
            return truth, prediction
    raise SystemExit(f"unknown prediction columns: {list(frame.columns)[:6]}")


def main() -> int:
    global checked
    computed: dict[tuple[str, int], dict] = {}
    for label, prediction_pattern, report_pattern, matrix_pattern, seeds in RUNS:
        for seed in seeds:
            frame = pd.read_csv(ROOT / (prediction_pattern % seed))
            truth, predicted = truth_columns(frame)
            report = classification_report(frame[truth], frame[predicted],
                                           output_dict=True, zero_division=0)
            computed[(label, seed)] = report
            stored = pd.read_csv(ROOT / (report_pattern % seed))
            stored = stored.set_index(stored.columns[0])
            mismatches = []
            for class_label, values in report.items():
                if class_label in ("accuracy", "macro avg", "weighted avg"):
                    continue
                if class_label not in stored.index:
                    mismatches.append(f"{class_label} missing")
                    continue
                for metric in ("precision", "recall", "f1-score"):
                    checked += 1
                    if abs(float(stored.loc[class_label, metric]) - values[metric]) > METRIC_TOL:
                        mismatches.append(f"{class_label}.{metric}")
            matrix_path = ROOT / (matrix_pattern % seed)
            if matrix_path.exists():
                labels = sorted(set(frame[truth]) | set(frame[predicted]))
                recomputed = confusion_matrix(frame[truth], frame[predicted],
                                              labels=labels, normalize="true")
                matrix = pd.read_csv(matrix_path, index_col=0)
                checked += recomputed.size
                worst = float(np.abs(np.asarray(matrix, dtype=float) - recomputed).max())
                if worst > MATRIX_TOL:
                    mismatches.append(f"confusion matrix (max diff {worst:.2e})")
            status = "OK  " if not mismatches else "FAIL"
            print(f"  {status} {label} seed {seed}: {len(report) - 3} classes"
                  f"{'' if not mismatches else '  ' + ', '.join(mismatches[:4])}")
            if mismatches:
                problems.append(f"{label} seed {seed}: {mismatches[:4]}")

    print()
    print("== values the manuscript prints ==")
    claims = (
        ("NSL-KDD", 42, ("R2L", "recall"), r"R2L recall is ([\d.]+)"),
        ("NSL-KDD", 42, ("R2L", "f1-score"), r"R2L recall is [\d.]+ with an F1 of ([\d.]+)"),
        ("NSL-KDD", 42, ("U2R", "recall"), r"U2R recall is ([\d.]+)"),
        ("NSL-KDD", 42, ("U2R", "f1-score"), r"U2R recall is [\d.]+ with an F1 of ([\d.]+);"),
        ("UNSW-NB15", 42, ("Analysis", "f1-score"), r"Analysis has an F1 of ([\d.]+)"),
        ("UNSW-NB15", 42, ("Backdoor", "f1-score"), r"Backdoor ([\d.]+) and DoS"),
        ("UNSW-NB15", 42, ("DoS", "f1-score"), r"Backdoor [\d.]+ and DoS ([\d.]+)"),
        ("UNSW-NB15", 42, ("Generic", "f1-score"), r"Generic reaches ([\d.]+)"),
        ("UNSW-NB15", 42, ("Normal", "f1-score"), r"Normal ([\d.]+)\. Aggregate accuracy"),
    )
    for label, seed, (class_label, metric), pattern in claims:
        match = re.search(pattern, EN)
        if not match:
            problems.append(f"the manuscript no longer states the {label} {class_label} claim")
            print(f"  FAIL {label} {class_label}: claim not found")
            continue
        printed = match.group(1)
        value = computed[(label, seed)][class_label][metric]
        digits = len(printed.split(".")[1])
        rendered = f"{round(value, digits):.{digits}f}"
        if rendered == printed:
            print(f"  OK   {label} {class_label} {metric} = {printed}")
        else:
            problems.append(f"{label} {class_label} {metric}: printed {printed}, "
                            f"recomputed {rendered}")
            print(f"  FAIL {label} {class_label} {metric}: printed {printed}, recomputed {rendered}")

    print()
    print(f"per-class values verified: {checked}")
    if problems:
        for problem in problems:
            print(f"ISSUE {problem}")
        print("PER_CLASS_FAILED")
        return 1
    print("PER_CLASS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
