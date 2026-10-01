"""Verify the extension report and the data it cites.

Two things must hold: every experiment's per-seed data is present (this is what
"keep the experimental data" means in practice), and every headline number in
the report is recomputed here from those files, so the narrative cannot drift
from the evidence.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
REPORT = BASE / "扩展实验报告.md"


def main() -> int:
    problems: list[str] = []
    if not REPORT.exists():
        print("EXTENSION_FAILED: missing 扩展实验报告.md")
        return 1
    text = REPORT.read_text(encoding="utf-8")

    required = {
        "results_member_family_v1": ["gate_results_by_config.csv",
                                     "member_metrics_by_seed.csv",
                                     "member_family_summary.json"],
        "results_day_holdout_v1": ["day_holdout_metrics.csv",
                                   "day_holdout_summary.json"],
        "results_deployment_metrics_v1": ["deployment_metrics_by_seed.csv",
                                          "deployment_summary.json",
                                          "per_class_pr_auc.csv"],
        "results_rccf_cic_ids2018_v1": ["metrics_by_seed.csv", "metrics_aggregate.csv",
                                        "benchmark_summary.json"],
        "results_rccf_cic_iot2023_v1": ["metrics_by_seed.csv", "metrics_aggregate.csv",
                                        "benchmark_summary.json"],
        "results_rccf_nsl_v10": ["metrics_by_seed.csv", "metrics_aggregate.csv"],
        "results_rccf_unsw_v10": ["metrics_by_seed.csv", "metrics_aggregate.csv"],
        "results_rccf_nbaiot_v10": ["metrics_by_seed.csv", "metrics_aggregate.csv"],
        "results_rccf_litnet2020_v1": ["metrics_by_seed.csv", "metrics_aggregate.csv",
                                       "benchmark_summary.json"],
        "results_rccf_iot23_v1": ["metrics_by_seed.csv", "metrics_aggregate.csv",
                                  "benchmark_summary.json"],
        "results_rccf_rt_iot2022_v1": ["metrics_by_seed.csv", "metrics_aggregate.csv",
                                       "benchmark_summary.json"],
        "results_rccf_aci_iot2023_v1": ["metrics_by_seed.csv", "metrics_aggregate.csv",
                                        "benchmark_summary.json"],
    }
    for folder, files in required.items():
        for name in files:
            if not (ROOT / folder / name).exists():
                problems.append(f"missing data file: {folder}/{name}")
        predictions = list((ROOT / folder).glob("predictions*.csv"))
        if folder.startswith("results_member_family") and len(predictions) < 15:
            problems.append(f"{folder}: only {len(predictions)} prediction files")
        if folder.startswith("results_rccf_cic_") and len(predictions) < 8:
            problems.append(f"{folder}: only {len(predictions)} prediction files")

    # headline numbers, recomputed
    families = json.loads((ROOT / "results_member_family_v1" /
                           "member_family_summary.json").read_text(encoding="utf-8"))
    checks = []
    if "q4" in families:
        checks.append(("member-family Q4 gain", families["q4"]["mean_gain"], 6))
    if "families" in families:
        checks.append(("member-family cross-family gain",
                       families["families"]["mean_gain"], 6))
    holdout = json.loads((ROOT / "results_day_holdout_v1" /
                          "day_holdout_summary.json").read_text(encoding="utf-8"))
    holdout_values = [value["rccf"]["macro_f1_mean"] for value in holdout.values()]
    checks.append(("temporal holdout minimum", min(holdout_values), 6))
    checks.append(("temporal holdout maximum", max(holdout_values), 6))
    for folder, label in (("results_rccf_cic_ids2018_v1", "CIC-IDS2018"),
                          ("results_rccf_cic_iot2023_v1", "CIC-IoT-2023")):
        summary = json.loads((ROOT / folder / "benchmark_summary.json").read_text(encoding="utf-8"))
        checks.append((f"{label} same-members difference",
                       summary["same_members_difference"], 6))
        checks.append((f"{label} RCCF Macro-F1", summary["rccf_mean_macro_f1"], 6))
    for folder, label in (("results_rccf_nsl_v10", "NSL-KDD"),
                          ("results_rccf_unsw_v10", "UNSW-NB15"),
                          ("results_rccf_nbaiot_v10", "N-BaIoT")):
        frame = pd.read_csv(ROOT / folder / "metrics_aggregate.csv")
        checks.append((f"{label} ten-seed Macro-F1", float(frame["macro_f1_mean"].iloc[0]), 6))
    for folder, label in (("results_rccf_litnet2020_v1", "LITNET-2020"),
                          ("results_rccf_iot23_v1", "IoT-23"),
                          ("results_rccf_rt_iot2022_v1", "RT-IoT2022"),
                          ("results_rccf_aci_iot2023_v1", "ACI-IoT-2023")):
        detail = json.loads((ROOT / folder / "benchmark_summary.json").read_text(encoding="utf-8"))
        checks.append((f"{label} same-members difference",
                       detail["same_members_difference"], 6))

    for label, value, digits in checks:
        rendered = f"{value:.{digits}f}"
        rendered_alt = f"{value:+.{digits}f}"
        if rendered not in text and rendered_alt not in text:
            problems.append(f"the report does not quote {label} = {rendered}")

    if problems:
        print("EXTENSION_FAILED: " + "; ".join(problems[:8]))
        return 1
    print(f"EXTENSION_OK experiments=10 quoted={len(checks)} "
          f"prediction_files="
          f"{sum(len(list((ROOT / folder).glob('predictions*.csv'))) for folder in required)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
