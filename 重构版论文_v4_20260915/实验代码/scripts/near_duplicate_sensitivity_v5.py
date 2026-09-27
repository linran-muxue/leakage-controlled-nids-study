"""Sensitivity check: recompute the primary metrics after removing test rows whose
rounded feature vector also appears in the training partition.

Uses the stored ten-seed predictions, so no model refitting is required.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data_processed_cic_natural_v3b"
RUN = ROOT / "results_seeds10_v5"
LABELS = ["Bot", "Brute Force", "DoS/DDoS", "Normal", "Web Attack"]
SEEDS = [42, 2024, 3407, 7, 13, 101, 202, 303, 404, 505]
DIGITS = 4


def load_features(path: Path) -> np.ndarray:
    frame = pd.read_csv(path, low_memory=False)
    return frame.drop(columns=["target"]).apply(pd.to_numeric).to_numpy()


def round_sig(x: np.ndarray, digits: int) -> np.ndarray:
    out = np.zeros_like(x)
    nz = x != 0
    mag = np.zeros_like(x)
    mag[nz] = np.floor(np.log10(np.abs(x[nz])))
    scale = np.power(10.0, mag - digits + 1)
    out[nz] = np.round(x[nz] / scale[nz]) * scale[nz]
    return out


def hashes(x: np.ndarray) -> np.ndarray:
    return np.array([hashlib.blake2b(r.tobytes(), digest_size=16).hexdigest()
                     for r in np.ascontiguousarray(x)])


def macro_f1(y, pred) -> float:
    return float(f1_score(y, pred, average="macro", labels=LABELS, zero_division=0))


def main() -> None:
    train_h = set(hashes(round_sig(load_features(PROC / "train.csv"), DIGITS)))
    test_h = hashes(round_sig(load_features(PROC / "test.csv"), DIGITS))
    overlap = np.array([h in train_h for h in test_h])

    rows = []
    for arm in ["rccf", "equal_rf_chi2", "extra_trees_chi2"]:
        full, filtered = [], []
        for seed in SEEDS:
            path = (RUN / f"predictions_seed{seed}.csv") if arm == "rccf" else \
                (RUN / "predictions" / f"predictions_{arm}_seed{seed}.csv")
            df = pd.read_csv(path)
            y = df["true_label" if "true_label" in df.columns else "y_true"].to_numpy()
            pred = df["predicted_label" if "predicted_label" in df.columns else "y_pred"].to_numpy()
            full.append(macro_f1(y, pred))
            filtered.append(macro_f1(y[~overlap], pred[~overlap]))
        rows.append({
            "model": arm,
            "test_rows": int(len(overlap)),
            "rows_removed": int(overlap.sum()),
            "removed_fraction": float(overlap.mean()),
            "macro_f1_full": float(np.mean(full)),
            "macro_f1_excluding_near_duplicates": float(np.mean(filtered)),
            "delta": float(np.mean(filtered) - np.mean(full)),
        })
    df = pd.DataFrame(rows)
    out = ROOT / "results_near_duplicate_v5"
    df.to_csv(out / "near_duplicate_sensitivity.csv", index=False, encoding="utf-8-sig")
    (out / "near_duplicate_sensitivity.json").write_text(json.dumps({
        "significant_digits": DIGITS,
        "test_rows_overlapping_training_at_this_resolution": int(overlap.sum()),
        "results": df.to_dict(orient="records"),
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(df.round(6).to_string(index=False))


if __name__ == "__main__":
    main()
