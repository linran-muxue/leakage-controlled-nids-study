"""Recompute the paper's McNemar result from the raw per-row predictions.

The only concrete McNemar numbers the manuscript quotes are the MLP-versus-RCCF
comparison: pooled p = 0.383 over 23,958 rows, per-seed 1.000 / 0.768 / 0.261.
Those values exist only in a summary file, so if the pairing were ever rebuilt
from different predictions nothing would notice.  This recomputes the 2x2
counts and the exact test from the two prediction files per seed.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from scipy.stats import binomtest

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
MLP = ROOT / "results_mlp_final_v5"
RCCF = ROOT / "results_rccf_cic_natural_v3b"
SEEDS = (42, 2024, 3407)
problems: list[str] = []


def exact_mcnemar(left_only: int, right_only: int) -> float:
    n = left_only + right_only
    if n == 0:
        return 1.0
    k = min(left_only, right_only)
    p = binomtest(k, n, 0.5, alternative="two-sided").pvalue
    return min(1.0, p)


stored = pd.read_csv(MLP / "mlp_vs_rccf_paired.csv").set_index("seed")
pooled = [0, 0]
print(f"{'seed':>6}{'mlp_right_rccf_wrong':>22}{'mlp_wrong_rccf_right':>22}{'p':>12}")
for seed in SEEDS:
    mlp = pd.read_csv(MLP / f"predictions_seed{seed}.csv")
    rccf = pd.read_csv(RCCF / f"predictions_seed{seed}.csv")
    if not (mlp["true_label"].to_numpy() == rccf["true_label"].to_numpy()).all():
        problems.append(f"seed {seed}: the two runs do not share the same test rows")
        continue
    truth = mlp["true_label"].to_numpy()
    a = ((mlp["predicted_label"].to_numpy() == truth)
         & (rccf["predicted_label"].to_numpy() != truth)).sum()
    b = ((mlp["predicted_label"].to_numpy() != truth)
         & (rccf["predicted_label"].to_numpy() == truth)).sum()
    a, b = int(a), int(b)
    pooled[0] += a
    pooled[1] += b
    p = exact_mcnemar(a, b)
    print(f"{seed:>6}{a:>22}{b:>22}{p:>12.4f}")
    for label, recomputed, recorded in (
        ("mlp_right_rccf_wrong", float(a), float(stored.loc[seed, "mlp_right_rccf_wrong"])),
        ("mlp_wrong_rccf_right", float(b), float(stored.loc[seed, "mlp_wrong_rccf_right"])),
        ("mcnemar p", p, float(stored.loc[seed, "mcnemar_p_vs_rccf"])),
    ):
        if abs(recomputed - recorded) > 1e-6:
            problems.append(f"seed {seed} {label}: recomputed {recomputed} vs recorded {recorded}")

summary = pd.read_json(MLP / "mlp_vs_rccf_summary.json", typ="series")
pooled_p = exact_mcnemar(pooled[0], pooled[1])
print(f"\npooled: {pooled[0]} vs {pooled[1]}, p = {pooled_p:.6f}")
for label, recomputed, recorded in (
    ("pooled_mlp_right_rccf_wrong", float(pooled[0]), float(summary["pooled_mlp_right_rccf_wrong"])),
    ("pooled_mlp_wrong_rccf_right", float(pooled[1]), float(summary["pooled_mlp_wrong_rccf_right"])),
    ("pooled p", pooled_p, float(summary["pooled_mcnemar_p"])),
):
    if abs(recomputed - recorded) > 1e-6:
        problems.append(f"{label}: recomputed {recomputed} vs recorded {recorded}")

english = (BASE / "English_SCI_Manuscript_v4.md").read_text(encoding="utf-8")
chinese = (BASE / "中文SCI论文_v4_重构版.md").read_text(encoding="utf-8")
for label, token in (("pooled p rounded", "0.383"), ("seed 42 p", "1.000"),
                     ("seed 2024 p", "0.768"), ("seed 3407 p", "0.261"),
                     ("pooled row count", "23,958")):
    if token not in english:
        problems.append(f"English manuscript does not state the {label} ({token})")
    if token.replace(",", " ") not in chinese and token.replace(",", "") not in chinese:
        problems.append(f"Chinese manuscript does not state the {label} ({token})")

print()
if problems:
    for problem in problems:
        print(f"ISSUE {problem}")
    print("MCNEMAR_RECOMPUTATION_FAILED")
    raise SystemExit(1)
print("MCNEMAR_RECOMPUTATION_OK")
