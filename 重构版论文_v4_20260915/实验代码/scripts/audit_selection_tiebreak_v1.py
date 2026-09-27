"""Explain why the three-seed and ten-seed baseline runs disagree on one seed.

``results_cic_natural_baselines_v3b`` and ``results_seeds10_v5`` both report an
"equal RF (chi-square, k = 60)" baseline on the same split with the same seed,
yet seed 42 gives Macro-F1 0.890773 in the first and 0.891714 in the second, and
2558 of 7986 test rows carry different probabilities.  The RCCF arm matches
exactly between the two runs, so the difference is in the baseline only.

The two runners select the feature subset differently:

* ``run_cfrg_cic_v1.py`` (three-seed run) takes ``np.argsort(-scores)[:k]``;
* ``run_seeds10_v5.py`` (ten-seed run) takes ``SelectKBest(chi2, k)``.

Both rank by the same chi-square score, so they agree unless scores tie at the
k-th boundary - and then the two tie-breaks pick different features.  This
script recomputes the ranking from the processed training split, reports every
tie at the boundary, and prints the symmetric difference between the two
selections.  It writes a record next to the review evidence; it does not touch
any released result.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.preprocessing import MinMaxScaler

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data_processed_cic_natural_v3b"
K = 60


def load() -> tuple[np.ndarray, np.ndarray, list[str]]:
    frame = pd.read_csv(DATA / "train.csv", low_memory=False)
    features = [c for c in frame.columns if c != "target"]
    x = frame[features].apply(pd.to_numeric, errors="raise").to_numpy(float)
    return x, frame["target"].to_numpy(), features


def main() -> int:
    x_raw, y, features = load()
    x = MinMaxScaler().fit_transform(x_raw)
    scores, _ = chi2(x, y)
    scores = np.nan_to_num(scores, nan=0.0, posinf=0.0)

    # selection A: what run_cfrg_cic_v1.py does
    order_desc = np.argsort(-scores, kind="stable")
    selection_a = [features[i] for i in order_desc[:K]]
    # selection B: what run_seeds10_v5.py does
    selector = SelectKBest(chi2, k=K).fit(x, y)
    mask = selector.get_support()
    selection_b = [f for f, keep in zip(features, mask) if keep]

    recorded_path = ROOT / "results_cic_natural_baselines_v3b" / "selected_features.json"
    recorded = json.loads(recorded_path.read_text(encoding="utf-8"))

    boundary = scores[np.argsort(-scores, kind="stable")[K - 1]]
    ties = [f for f, s in zip(features, scores) if np.isclose(s, boundary, rtol=0, atol=1e-12)]
    near = sorted(((float(s), f) for f, s in zip(features, scores)), reverse=True)[K - 4:K + 3]

    only_a = sorted(set(selection_a) - set(selection_b))
    only_b = sorted(set(selection_b) - set(selection_a))

    print(f"features: {len(features)}   k: {K}")
    print(f"boundary score (rank {K}): {boundary:.12g}")
    print(f"features tied at the boundary: {len(ties)} -> {ties}")
    print("ranks around the boundary:")
    for rank, (score, name) in enumerate(near, start=K - 3):
        print(f"  {rank:>3}  {score:.12g}  {name}")
    print()
    # The recorded list is in feature order, the recomputed ones in score order,
    # so the comparison has to be set-based.
    same_a = set(selection_a) == set(recorded)
    same_b = set(selection_b) == set(recorded)
    print(f"run_cfrg_cic_v1 selection == recorded selected_features.json: {same_a}")
    print(f"SelectKBest selection           == recorded selected_features.json: {same_b}")

    # Both tied features are rare flag counters; check whether they are in fact
    # the same column on this corpus, which is what makes the scores identical.
    frame = pd.read_csv(DATA / "train.csv", low_memory=False)
    test = pd.read_csv(DATA / "test.csv", low_memory=False)
    tied = ties[:2]
    if len(tied) == 2:
        for split_name, part in (("train", frame), ("test", test)):
            equal = bool((part[tied[0]].to_numpy() == part[tied[1]].to_numpy()).all())
            print(f"{split_name}: {tied[0]!r} == {tied[1]!r} element-wise: {equal}"
                  f"  (unique values: {sorted(part[tied[0]].unique())[:5]} vs "
                  f"{sorted(part[tied[1]].unique())[:5]})")
    print(f"the two selections differ in {len(only_a) + len(only_b)} feature(s)")
    print(f"  only in run_cfrg_cic_v1: {only_a}")
    print(f"  only in run_seeds10_v5 : {only_b}")

    record = {
        "boundary_rank": K,
        "boundary_score": boundary,
        "features_tied_at_boundary": ties,
        "ranks_around_boundary": [{"rank": r, "score": float(s), "feature": f}
                                  for r, (s, f) in enumerate(near, start=K - 3)],
        "run_cfrg_cic_v1_selection_matches_record": bool(same_a),
        "selectkbest_selection_matches_record": bool(same_b),
        "tied_features_identical_on_train": bool(
            (frame[ties[0]].to_numpy() == frame[ties[1]].to_numpy()).all()) if len(ties) == 2 else None,
        "tied_features_identical_on_test": bool(
            (test[ties[0]].to_numpy() == test[ties[1]].to_numpy()).all()) if len(ties) == 2 else None,
        "only_in_three_seed_run": only_a,
        "only_in_ten_seed_run": only_b,
        "conclusion": ("the two released baseline runs differ because the chi-square "
                       "score ties at the k-th boundary and the two runners break the "
                       "tie differently"),
    }
    out = ROOT / "results_review_v5" / "selection_tiebreak_audit_v1.json"
    out.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print()
    print(f"recorded in {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
