"""Turn Condition 3 from a definition into a quantitative, verified relation.

Theory. Let w_e = exp(-r_e) / sum_j exp(-r_j) and write r_e = r_bar + delta_e, so that
log w_e = -delta_e + const and Var(log w) = Var(delta). Expanding the entropy around the
uniform point w = 1/Q gives, to second order,

    1 - H_norm(w) = (Q / (2 log Q)) * ||w - 1/Q||_2^2 ,

and a first-order expansion of the softmax gives

    1 - H_norm(w) ~ Var(delta) / (2 log Q) .

The script fits the mechanism, recovers the expert weights on the test partition, and
compares the observed entropy deficiency with the predicted value.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.rccf_forest import RCCFForest  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]


def load(path: Path):
    frame = pd.read_csv(path, low_memory=False)
    return frame.drop(columns=["target"]).apply(pd.to_numeric).to_numpy(), frame["target"].to_numpy()


def main() -> None:
    proc = ROOT / "data_processed_cic_natural_v3b"
    Xtr, ytr = load(proc / "train.csv")
    Xva, yva = load(proc / "validation.csv")
    Xte, _ = load(proc / "test.csv")

    model = RCCFForest(n_estimators=100, feature_k=60, cv=5, random_state=42, n_jobs=-1)
    model.fit(Xtr, ytr, Xva, yva)
    model._raw_predict_proba(Xte)          # populates expert_weights_
    w = model.expert_weights_
    q = w.shape[1]

    log_w = np.log(np.clip(w, 1e-300, 1.0))
    var_delta = log_w.var(axis=1)                       # Var(log w) = Var(delta)
    entropy = -(w * log_w).sum(axis=1) / np.log(q)
    observed = 1.0 - entropy
    predicted = var_delta / (2 * np.log(q))
    l2 = ((w - 1.0 / q) ** 2).sum(axis=1)
    second_order = (q / (2 * np.log(q))) * l2

    out = ROOT / "results_margin_bound_v5"
    rows = {
        "n_test_rows": int(len(w)),
        "n_experts": int(q),
        "mean_entropy_deficiency_observed": float(observed.mean()),
        "mean_entropy_deficiency_predicted_from_var_delta": float(predicted.mean()),
        "mean_second_order_identity_value": float(second_order.mean()),
        "mean_var_log_weight": float(var_delta.mean()),
        "sd_risk_offset": float(np.sqrt(var_delta.mean())),
        "median_sd_risk_offset": float(np.median(np.sqrt(var_delta))),
        "max_sd_risk_offset": float(np.sqrt(var_delta).max()),
        "relative_error_of_first_order_prediction":
            float(abs(predicted.mean() - observed.mean()) / max(observed.mean(), 1e-12)),
        "relative_error_of_second_order_identity":
            float(abs(second_order.mean() - observed.mean()) / max(observed.mean(), 1e-12)),
    }
    per_row = pd.DataFrame({
        "row_id": np.arange(len(w)),
        "entropy": entropy,
        "entropy_deficiency_observed": observed,
        "entropy_deficiency_predicted": predicted,
        "sd_risk_offset": np.sqrt(var_delta),
    })
    per_row.to_csv(out / "proposition3_quantification.csv", index=False, encoding="utf-8-sig")
    (out / "proposition3_quantification.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    for k, v in rows.items():
        print(f"  {k:<52} {v}")


if __name__ == "__main__":
    main()
