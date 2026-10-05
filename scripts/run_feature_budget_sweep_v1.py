"""Sweep the feature budget on a modern corpus.

The paper's feature-budget sweep is on CIC-IDS2017: the gate starts to matter
once the views differ, which needs k to fall below the number of available
columns.  Gotham-2025 showed the same boundary at k = 8 of 16.  This script
repeats the sweep on CIC-IoT-2023 (39 columns) so the boundary has a second,
much larger corpus behind it.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
PY = r"E:\论文\.venv\Scripts\python.exe"
SEEDS = ["42", "2024", "3407", "7", "13", "101", "202", "303", "404", "505"]
BUDGETS = (8, 16, 32, 60)


def main() -> None:
    for k in BUDGETS:
        out = ROOT / f"results_rccf_cic_iot2023_k{k}"
        if (out / "benchmark_summary.json").exists():
            print(f"k={k}: already present", flush=True)
            continue
        print(f"k={k}: running ten seeds", flush=True)
        subprocess.run([PY, "scripts\\run_native_label_benchmark_v1.py",
                        "--processed-dir", "data_processed_cic_iot2023_v1",
                        "--output-dir", out.name, "--seeds", *SEEDS,
                        "--experts", "full", "chi2", "anova",
                        "--feature-k", str(k)], cwd=ROOT)
        summary = json.loads((out / "benchmark_summary.json").read_text(encoding="utf-8"))
        print(f"k={k}: RCCF {summary['rccf_mean_macro_f1']:.6f} "
              f"equal {summary['equal_fusion_mean_macro_f1']:.6f} "
              f"diff {summary['same_members_difference']:+.6f}", flush=True)
    print("FEATURE_BUDGET_SWEEP_DONE")


if __name__ == "__main__":
    main()
