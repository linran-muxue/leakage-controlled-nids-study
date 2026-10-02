"""Pool the modern corpora into one equivalence test.

The headline equivalence result was measured on CIC-IDS2017 (2017).  Twelve
extension corpora published between 2020 and 2026 were run under the same
protocol, the same ten seeds and the same same-members control, and every one of
them released its per-row predictions.  This script re-derives the per-seed
paired difference (gate minus same-members equal fusion) from those predictions,
then applies the paper's TOST logic to the pooled per-seed differences.

The Gotham reduced-budget run (k = 8 of 16) is the one corpus where the gate
genuinely wins, so it is reported separately rather than averaged into the
equivalence claim; both pooled variants are emitted so the exclusion is visible.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import f1_score

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results_modern_replication_v1"
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
    ("results_rccf_ctu_idseval6_v1", "CTU-IDSEVAL-6", 2026),
    ("results_rccf_6tisch2026_v1", "6TiSCHSet-2026", 2026),
    ("results_rccf_rtn2026_v1", "RTN-traffic-2026", 2026),
)
POSITIVE = ("results_rccf_gotham2025_v1_k8", "Gotham-2025 (8/16 features)", 2025)


def paired_differences(folder: str) -> tuple[list[float], float, float]:
    directory = ROOT / folder
    differences = []
    for seed in SEEDS:
        left = directory / f"predictions_rccf_seed{seed}.csv"
        right = directory / f"predictions_equal_fusion_seed{seed}.csv"
        if not (left.exists() and right.exists()):
            continue
        gate = pd.read_csv(left)
        control = pd.read_csv(right)
        truth = gate["true_label"].to_numpy()
        differences.append(
            f1_score(truth, gate["predicted_label"], average="macro", zero_division=0)
            - f1_score(truth, control["predicted_label"], average="macro", zero_division=0))
    summary = json.loads((directory / "benchmark_summary.json").read_text(encoding="utf-8"))
    return differences, float(summary["rccf_mean_macro_f1"]), float(summary["test_rows"])


def tost(values: list[float], margin: float) -> dict:
    data = np.asarray(values, dtype=float)
    n = len(data)
    mean = float(data.mean())
    sem = float(data.std(ddof=1) / np.sqrt(n))
    tcrit = float(stats.t.ppf(0.95, n - 1))
    low, high = mean - tcrit * sem, mean + tcrit * sem
    return {"n": n, "mean": mean, "ci90_low": low, "ci90_high": high,
            "equivalent": bool(low > -margin and high < margin)}


def main() -> None:
    OUT.mkdir(exist_ok=True)
    rows = []
    pooled: list[float] = []
    for folder, label, year in CORPORA:
        differences, macro_f1, test_rows = paired_differences(folder)
        pooled.extend(differences)
        rows.append({"corpus": label, "published": year, "seeds": len(differences),
                     "test_rows": test_rows, "rccf_macro_f1": macro_f1,
                     "mean_difference": float(np.mean(differences)),
                     "min_difference": float(np.min(differences)),
                     "max_difference": float(np.max(differences)),
                     "seeds_positive": int(np.sum(np.asarray(differences) > 0)),
                     "role": "equivalence pool"})
    positives, positive_f1, positive_rows = paired_differences(POSITIVE[0])
    rows.append({"corpus": POSITIVE[1], "published": POSITIVE[2], "seeds": len(positives),
                 "test_rows": positive_rows, "rccf_macro_f1": positive_f1,
                 "mean_difference": float(np.mean(positives)),
                 "min_difference": float(np.min(positives)),
                 "max_difference": float(np.max(positives)),
                 "seeds_positive": int(np.sum(np.asarray(positives) > 0)),
                 "role": "reported separately (gate wins)"})
    frame = pd.DataFrame(rows)
    frame.to_csv(OUT / "per_corpus_differences.csv", index=False, encoding="utf-8-sig")
    summary = {
        "corpora_in_pool": len(CORPORA),
        "corpora_reported_separately": 1,
        "seeds_per_corpus": len(SEEDS),
        "pooled_005": tost(pooled, 0.005),
        "pooled_010": tost(pooled, 0.01),
        "pooled_with_positive_005": tost(pooled + positives, 0.005),
        "positive_case": {"corpus": POSITIVE[1], "mean_difference": float(np.mean(positives)),
                          "seeds_positive": int(np.sum(np.asarray(positives) > 0)),
                          "seeds": len(positives)},
        "publication_years": sorted(year for _, _, year in CORPORA),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2),
                                      encoding="utf-8")
    for line in frame.itertuples():
        print(f"{line.corpus:<22} {line.published}  seeds={line.seeds}  "
              f"diff={line.mean_difference:+.6f}  "
              f"[{line.min_difference:+.6f}, {line.max_difference:+.6f}]  "
              f"positive {line.seeds_positive}/{line.seeds}")
    print()
    for key in ("pooled_005", "pooled_010"):
        block = summary[key]
        print(f"{key}: n={block['n']} mean={block['mean']:+.6f} "
              f"90% CI [{block['ci90_low']:+.6f}, {block['ci90_high']:+.6f}] "
              f"equivalent={block['equivalent']}")
    block = summary["pooled_with_positive_005"]
    print(f"including the Gotham positive case: mean={block['mean']:+.6f} "
          f"90% CI [{block['ci90_low']:+.6f}, {block['ci90_high']:+.6f}] "
          f"equivalent={block['equivalent']}")
    print("MODERN_REPLICATION_DONE")


if __name__ == "__main__":
    main()
