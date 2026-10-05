"""Relaunch only the Gotham full-corpus benchmark (never the preparation).

The generic queue skips a step only when its summary exists, so calling its
``gotham_full`` after an interruption would redo the 40-minute preparation.
This launcher runs the ten seeds directly, with absolute paths, so it can be
registered as a scheduled task whose working directory is not the repository.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
PY = r"E:\论文\.venv\Scripts\python.exe"
SEEDS = ["42", "2024", "3407", "7", "13", "101", "202", "303", "404", "505"]

if __name__ == "__main__":
    summary = ROOT / "results_rccf_gotham2025_full" / "benchmark_summary.json"
    if summary.exists():
        print("Gotham full already complete; nothing to do")
        raise SystemExit(0)
    # Guard against duplicate writers: this launcher is scheduled to re-run every
    # 15 minutes so that a killed run is restarted automatically, but it must do
    # nothing while a run is already in flight (the launcher's own command line
    # contains "launch_gotham_full_run", not "gotham2025_full", so it never
    # matches itself).
    probe = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "(Get-CimInstance Win32_Process -Filter \"Name like '%python%'\" | "
         "Where-Object { $_.CommandLine -match 'data_processed_gotham2025_full' } | "
         "Measure-Object).Count"], capture_output=True, text=True)
    try:
        if int(probe.stdout.strip() or 0) > 0:
            print("a Gotham full run is already in progress; exiting")
            raise SystemExit(0)
    except ValueError:
        pass
    log = ROOT / "logs" / "modern_ladder_gotham_run.log"
    log.parent.mkdir(exist_ok=True)
    with log.open("a", encoding="utf-8") as handle:
        handle.write("\n=== relaunch (resume mode) ===\n")
        subprocess.run([PY, "-u", str(ROOT / "scripts" / "run_native_label_benchmark_v1.py"),
                        "--processed-dir", "data_processed_gotham2025_full",
                        "--output-dir", "results_rccf_gotham2025_full",
                        "--seeds", *SEEDS, "--experts", "full", "chi2", "anova",
                        "--resume"], cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT)
