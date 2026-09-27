"""Keep the two released baseline runs from being silently confused.

The three-seed release (``results_cic_natural_baselines_v3b``) and the ten-seed
release (``results_seeds10_v5``) both contain an "equal RF (chi-square, k = 60)"
arm, yet for seed 42 they give Macro-F1 0.890773 and 0.891714 and disagree on 11
of 7986 test rows.  ``scripts/audit_selection_tiebreak_v1.py`` and
``scripts/audit_baseline_reproduction_v1.py`` established why:

* the chi-square scores tie exactly at rank k = 60, because RST Flag Count and
  ECE Flag Count are element-wise identical on this corpus;
* more importantly the two runners build the design matrix in different column
  orders (descending score versus original feature order), and a random forest
  subsamples columns by index, so the two orders fit different trees.

Neither released directory is wrong and the manuscript quotes each one
consistently, but a reader comparing them deserves the explanation.  This check
recomputes the tie and the identical-column fact from the processed split,
verifies that the recorded selections match, and fails if the audit records or
the canonical selector go missing.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
from sklearn.preprocessing import MinMaxScaler

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.feature_selection import chi2_top_k  # noqa: E402

DATA = ROOT / "data_processed_cic_natural_v3b"
K = 60
TIE_AUDIT = ROOT / "results_review_v5" / "selection_tiebreak_audit_v1.json"
REPRO_AUDIT = ROOT / "results_review_v5" / "baseline_reproduction_v1.json"
RECORDED = ROOT / "results_cic_natural_baselines_v3b" / "selected_features.json"
problems: list[str] = []


def report() -> int:
    if problems:
        for problem in problems:
            print(f"ISSUE {problem}")
        print("SELECTION_REPRODUCIBILITY_FAILED")
        return 1
    print("SELECTION_REPRODUCIBILITY_OK")
    return 0


def main() -> int:
    for path in (TIE_AUDIT, REPRO_AUDIT, RECORDED):
        if not path.exists():
            problems.append(f"missing {path.relative_to(ROOT)}")
    if problems:
        return report()

    train = pd.read_csv(DATA / "train.csv", low_memory=False)
    test = pd.read_csv(DATA / "test.csv", low_memory=False)
    features = [c for c in train.columns if c != "target"]
    x = MinMaxScaler().fit_transform(
        train[features].apply(pd.to_numeric, errors="raise").to_numpy(float))
    selection = chi2_top_k(x, train["target"].to_numpy(), K, feature_names=features)

    if selection.tied_at_boundary != ["ECE Flag Count", "RST Flag Count"]:
        problems.append(f"boundary tie changed: {selection.tied_at_boundary}")
    for split_name, frame in (("train", train), ("test", test)):
        if not bool((frame["RST Flag Count"].to_numpy() == frame["ECE Flag Count"].to_numpy()).all()):
            problems.append(f"{split_name}: RST Flag Count and ECE Flag Count are no longer identical")

    recorded = json.loads(RECORDED.read_text(encoding="utf-8"))
    if set(recorded) != set(selection.names):
        problems.append("selected_features.json no longer matches the canonical selection")
    if len(recorded) != K or len(selection.names) != K:
        problems.append(f"selection size changed: recorded {len(recorded)}, canonical {len(selection.names)}")
    if list(selection.names) != sorted(selection.names, key=features.index):
        problems.append("canonical selection is no longer in ascending feature order")

    tie_audit = json.loads(TIE_AUDIT.read_text(encoding="utf-8"))
    repro = json.loads(REPRO_AUDIT.read_text(encoding="utf-8"))
    if tie_audit.get("features_tied_at_boundary") != ["RST Flag Count", "ECE Flag Count"]:
        problems.append("selection_tiebreak_audit_v1.json does not record the boundary tie")
    if not tie_audit.get("tied_features_identical_on_train"):
        problems.append("selection_tiebreak_audit_v1.json does not record the identical columns")

    combos = repro.get("combinations", {})
    expected = {"three-seed set, score order": "three_seed_run",
                "ten-seed set, feature order": "ten_seed_run"}
    for label, key in expected.items():
        agreement = combos.get(label, {}).get("agreement_with", {}).get(key)
        if agreement != 7986:
            problems.append(f"baseline_reproduction_v1.json: {label} no longer reproduces "
                            f"{key} exactly (agreement {agreement})")
    three = combos.get("three-seed set, score order", {}).get("macro_f1_seed42")
    ten = combos.get("ten-seed set, feature order", {}).get("macro_f1_seed42")
    if three is None or ten is None:
        problems.append("baseline_reproduction_v1.json is missing the refit macro-F1 values")
    else:
        print(f"canonical selection: {K} features, boundary tie {selection.tied_at_boundary}")
        print(f"recorded selections agree | score order reproduces {three} and "
              f"feature order reproduces {ten}")
    return report()


if __name__ == "__main__":
    raise SystemExit(main())
