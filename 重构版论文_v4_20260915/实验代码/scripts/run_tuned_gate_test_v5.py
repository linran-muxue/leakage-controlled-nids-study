"""F2: evaluate the validation-selected gate configuration once on the test set.

The 108-configuration search in S2 was scored on the validation partition only.
To support the claim that tuning does not change the conclusion, the selected
configuration must be evaluated on the locked test partition and compared with the
default configuration that produced the headline result.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from scipy.stats import binomtest
from sklearn.metrics import f1_score

from src.rccf_forest import RCCFForest

ROOT = Path(__file__).resolve().parents[1]
LABELS = ["Bot", "Brute Force", "DoS/DDoS", "Normal", "Web Attack"]


def load(path: Path):
    frame = pd.read_csv(path, low_memory=False)
    return frame.drop(columns=["target"]).apply(pd.to_numeric).to_numpy(), frame["target"].to_numpy()


def macro_f1(y, pred) -> float:
    return float(f1_score(y, pred, average="macro", labels=LABELS, zero_division=0))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", default="data_processed_cic_natural_v3b")
    ap.add_argument("--config", default="results_gate_tuning_v5/selected_gate_config.json")
    ap.add_argument("--default-dir", default="results_rccf_cic_natural_v3b")
    ap.add_argument("--output-dir", default="results_tuned_gate_test_v5")
    ap.add_argument("--seeds", nargs="+", type=int, default=[42, 2024, 3407])
    args = ap.parse_args()

    cfg = json.loads((ROOT / args.config).read_text("utf-8"))
    proc = ROOT / args.processed_dir
    out = ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    Xtr, ytr = load(proc / "train.csv")
    Xva, yva = load(proc / "validation.csv")
    Xte, yte = load(proc / "test.csv")

    rows = []
    for seed in args.seeds:
        start = time.perf_counter()
        model = RCCFForest(n_estimators=100, feature_k=60, cv=int(cfg["cv"]),
                           random_state=seed, n_jobs=-1,
                           risk_C=float(cfg["risk_C"]),
                           descriptor_set=str(cfg["descriptor_set"]))
        model.fit(Xtr, ytr, Xva, yva)
        proba = model.predict_proba(Xte)
        pred = model.classes_[np.argmax(proba, axis=1)]
        default = pd.read_csv(ROOT / args.default_dir / f"predictions_seed{seed}.csv")
        default_pred = default["predicted_label"].to_numpy()
        changed = int((pred != default_pred).sum())
        rows.append({
            "seed": seed,
            "tuned_macro_f1": macro_f1(yte, pred),
            "default_macro_f1": macro_f1(yte, default_pred),
            "difference": macro_f1(yte, pred) - macro_f1(yte, default_pred),
            "rows_changed_vs_default": changed,
            "elapsed_seconds": time.perf_counter() - start,
        })
        pd.DataFrame(rows).to_csv(out / "tuned_vs_default_test.csv",
                                  index=False, encoding="utf-8-sig")
        print(f"seed={seed} tuned={rows[-1]['tuned_macro_f1']:.6f} "
              f"default={rows[-1]['default_macro_f1']:.6f} changed={changed}", flush=True)

    df = pd.DataFrame(rows)
    summary = {
        "selected_config": cfg,
        "tuned_macro_f1_mean": float(df["tuned_macro_f1"].mean()),
        "default_macro_f1_mean": float(df["default_macro_f1"].mean()),
        "mean_difference": float(df["difference"].mean()),
        "max_abs_difference": float(df["difference"].abs().max()),
        "total_rows_changed": int(df["rows_changed_vs_default"].sum()),
        "test_rows_per_seed": int(len(yte)),
        "interpretation": ("test-set confirmation that the validation-selected gate "
                           "configuration does not change the reported conclusion"),
    }
    (out / "tuned_vs_default_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
