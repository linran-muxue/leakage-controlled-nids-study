"""Paired row-level statistical audit for CFRG result artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, f1_score, log_loss

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.paired_tests import mcnemar_exact


def _prob(frame, classes):
    return frame[[f"proba__{c}" for c in classes]].to_numpy(float)


def _metrics(frame, classes, indices=None):
    if indices is None:
        indices = np.arange(len(frame))
    y = frame.iloc[indices]["y_true"].to_numpy()
    pred = frame.iloc[indices]["y_pred"].to_numpy()
    p = _prob(frame.iloc[indices], classes)
    return {
        "macro_f1": float(f1_score(y, pred, labels=classes, average="macro", zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "log_loss": float(log_loss(y, p, labels=list(classes))),
    }


def audit_pair(frame_a, frame_b, classes, n_bootstrap=2000, n_permutations=5000, seed=42):
    if len(frame_a) != len(frame_b) or not np.array_equal(frame_a["y_true"].to_numpy(), frame_b["y_true"].to_numpy()):
        raise ValueError("paired frames must contain identical row order and y_true")
    rng = np.random.default_rng(seed)
    base_a, base_b = _metrics(frame_a, classes), _metrics(frame_b, classes)
    deltas = {f"delta_{name}": base_b[name] - base_a[name] for name in base_a}
    boot = {key: [] for key in deltas}
    n = len(frame_a)
    for _ in range(int(n_bootstrap)):
        idx = rng.integers(0, n, size=n)
        ma, mb = _metrics(frame_a, classes, idx), _metrics(frame_b, classes, idx)
        for name in base_a:
            boot[f"delta_{name}"].append(mb[name] - ma[name])
    result = dict(deltas)
    for key, values in boot.items():
        result[f"{key}_ci_low"] = float(np.quantile(values, 0.025))
        result[f"{key}_ci_high"] = float(np.quantile(values, 0.975))
        result[f"{key}_bootstrap_positive"] = float(np.mean(np.asarray(values) > 0))
    mc = mcnemar_exact(frame_a["y_true"], frame_a["y_pred"], frame_b["y_pred"])
    result.update({"mcnemar_b01": mc["a_only_correct"], "mcnemar_b10": mc["b_only_correct"], "mcnemar_p": mc["p_value"]})
    observed = result["delta_macro_f1"]
    pred_a = frame_a["y_pred"].to_numpy(copy=True)
    pred_b = frame_b["y_pred"].to_numpy(copy=True)
    y_true = frame_a["y_true"].to_numpy(copy=True)
    perm = np.empty(int(n_permutations), dtype=float)
    for j in range(len(perm)):
        swap = rng.integers(0, 2, size=n).astype(bool)
        shuffled_a = np.where(swap, pred_b, pred_a)
        shuffled_b = np.where(swap, pred_a, pred_b)
        perm[j] = f1_score(y_true, shuffled_b, labels=classes, average="macro", zero_division=0) - f1_score(y_true, shuffled_a, labels=classes, average="macro", zero_division=0)
    result["macro_f1_signflip_p"] = float((np.count_nonzero(np.abs(perm) >= abs(observed)) + 1) / (len(perm) + 1))
    return result


def run(result_dir, output_dir, model_a="equal_rf_chi2", model_b="cfrg_forest_chi2", seeds=(42, 2024, 3407), n_bootstrap=2000, n_permutations=5000):
    result_dir, output_dir = Path(result_dir), Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for seed in seeds:
        a = pd.read_csv(result_dir / "predictions" / f"predictions_{model_a}_seed{seed}.csv")
        b = pd.read_csv(result_dir / "predictions" / f"predictions_{model_b}_seed{seed}.csv")
        classes = [c.split("proba__", 1)[1] for c in a.columns if c.startswith("proba__")]
        row = audit_pair(a, b, classes, n_bootstrap=n_bootstrap, n_permutations=n_permutations, seed=seed)
        row.update({"seed": int(seed), "model_a": model_a, "model_b": model_b, "test_samples": len(a)})
        rows.append(row)
    frame = pd.DataFrame(rows)
    frame.to_csv(output_dir / "paired_effects.csv", index=False, encoding="utf-8-sig")
    (output_dir / "protocol.json").write_text(json.dumps({"model_a": model_a, "model_b": model_b, "seeds": list(map(int, seeds)), "bootstrap": int(n_bootstrap), "permutations": int(n_permutations), "pairing": "identical_test_row_order"}, indent=2), encoding="utf-8")
    print(frame.to_string(index=False))
    return frame


def main():
    p = argparse.ArgumentParser(); p.add_argument("--result-dir", type=Path, required=True); p.add_argument("--output-dir", type=Path, required=True); p.add_argument("--model-a", default="equal_rf_chi2"); p.add_argument("--model-b", default="cfrg_forest_chi2"); p.add_argument("--seeds", type=int, nargs="+", default=[42, 2024, 3407]); p.add_argument("--bootstrap", type=int, default=2000); p.add_argument("--permutations", type=int, default=5000); args = p.parse_args(); run(args.result_dir, args.output_dir, args.model_a, args.model_b, args.seeds, args.bootstrap, args.permutations)


if __name__ == "__main__": main()
