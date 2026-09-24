"""Refit the seed-42 equal-weight chi-square forest and see which release it matches.

``audit_selection_tiebreak_v1.py`` shows that RST Flag Count and ECE Flag Count
are element-wise identical on this corpus, so their chi-square scores tie
exactly at rank k = 60 and the two tie-breaks keep different features.  The two
runners also build the design matrix in different column orders
(``X[:, argsort(-score)]`` versus ``SelectKBest.transform``, which keeps the
original order).  Random forests subsample features by index, so both choices
change the fitted trees.

This script refits the four combinations and compares each one against the two
released prediction files, which is the only way to say what the releases
actually contain.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.metrics import f1_score
from sklearn.preprocessing import MinMaxScaler

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data_processed_cic_natural_v3b"
K, SEED = 60, 42


def main() -> int:
    frames = {s: pd.read_csv(DATA / f"{s}.csv", low_memory=False)
              for s in ("train", "test")}
    features = [c for c in frames["train"].columns if c != "target"]
    x_train_raw = frames["train"][features].apply(pd.to_numeric, errors="raise").to_numpy(float)
    x_test_raw = frames["test"][features].apply(pd.to_numeric, errors="raise").to_numpy(float)
    y_train = frames["train"]["target"].to_numpy()
    y_test = frames["test"]["target"].to_numpy()
    scaler = MinMaxScaler().fit(x_train_raw)
    x_train, x_test = scaler.transform(x_train_raw), scaler.transform(x_test_raw)

    scores, _ = chi2(x_train, y_train)
    scores = np.nan_to_num(scores, nan=0.0, posinf=0.0)
    order_score = np.argsort(-scores, kind="stable")
    set_three_seed = list(order_score[:K])
    mask = SelectKBest(chi2, k=K).fit(x_train, y_train).get_support()
    set_ten_seed = [i for i, keep in enumerate(mask) if keep]
    boundary_three = set(set_three_seed) - set(set_ten_seed)
    boundary_ten = set(set_ten_seed) - set(set_three_seed)
    print(f"three-seed selection keeps {[features[i] for i in sorted(boundary_three)]} "
          f"and drops {[features[i] for i in sorted(boundary_ten)]}")
    print(f"ten-seed   selection keeps {[features[i] for i in sorted(boundary_ten)]} "
          f"and drops {[features[i] for i in sorted(boundary_three)]}")
    ten_in_score_order = sorted(set_ten_seed, key=lambda i: (-scores[i], i))

    released = {
        "three_seed_run": ROOT / "results_cic_natural_baselines_v3b" / "predictions" /
                          "predictions_equal_rf_chi2_seed42.csv",
        "ten_seed_run": ROOT / "results_seeds10_v5" / "predictions" /
                        "predictions_equal_rf_chi2_seed42.csv",
    }
    stored = {}
    for name, path in released.items():
        frame = pd.read_csv(path)
        column = "y_pred" if "y_pred" in frame.columns else "predicted_label"
        stored[name] = frame[column].to_numpy()
        print(f"{name}: macro-F1 {f1_score(y_test, frame[column], average='macro', zero_division=0):.6f}")

    combinations = {
        "three-seed set, score order": (x_train[:, set_three_seed], x_test[:, set_three_seed]),
        "three-seed set, feature order": (x_train[:, sorted(set_three_seed)],
                                          x_test[:, sorted(set_three_seed)]),
        "ten-seed set, score order": (x_train[:, ten_in_score_order],
                                      x_test[:, ten_in_score_order]),
        "ten-seed set, feature order": (x_train[:, set_ten_seed], x_test[:, set_ten_seed]),
    }
    results = {}
    print()
    for label, (xa, xb) in combinations.items():
        model = RandomForestClassifier(n_estimators=100, min_samples_leaf=2,
                                       class_weight="balanced_subsample",
                                       random_state=SEED, n_jobs=-1)
        model.fit(xa, y_train)
        prediction = model.predict(xb)
        macro = f1_score(y_test, prediction, average="macro", zero_division=0)
        agreement = {name: int((prediction == values).sum()) for name, values in stored.items()}
        results[label] = {"macro_f1_seed42": float(macro),
                          "agreement_with": agreement}
        print(f"{label:34} macro-F1 {macro:.6f}   agreement "
              f"v3b {agreement['three_seed_run']}/7986  v5 {agreement['ten_seed_run']}/7986")

    out = ROOT / "results_review_v5" / "baseline_reproduction_v1.json"
    out.write_text(json.dumps({
        "protocol": "natural-prior population, seed 42, equal-weight chi-square forest",
        "note": ("the released three-seed and ten-seed baseline files use different "
                 "feature orderings and different tie-breaks for the chi-square tie at "
                 "rank 60, so they are two different forests under one name"),
        "combinations": results,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print()
    print(f"recorded in {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
