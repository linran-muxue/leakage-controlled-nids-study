"""Wait for the Gotham full run, then finish the rest of the batch.

The first queue process died after launching the two long rungs (its children
survived and kept computing).  Re-running the queue would start a *second*
Gotham job writing into the same directory, so this phase-2 driver waits for the
existing Gotham run to finish and then executes only what is still missing:
the source holdouts, the three extra rungs, the feature-budget sweep and the
evidence/replication recomputation.

It is idempotent and safe to restart at any time.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import run_modern_ladder_queue_v1 as queue  # noqa: E402

GOTHAM = ROOT / "results_rccf_gotham2025_full" / "benchmark_summary.json"


def gotham_alive() -> bool:
    """Two independent signals: a python process for the run, or the task itself.

    A single pattern match produced a false negative once (the run was alive but
    the process filter missed it), which would have started a second Gotham job
    writing the same directory.  Asking the scheduler as well removes that risk.
    """
    script = (
        "$p = (Get-CimInstance Win32_Process -Filter \"Name like '%python%'\" | "
        "Where-Object { $_.CommandLine -match 'gotham2025_full|launch_gotham_full_run' } | "
        "Measure-Object).Count; "
        "$t = (schtasks /query /tn CodexGothamFullRun /fo LIST 2>$null | "
        "Select-String -Pattern 'Status:\\s+Running' | Measure-Object).Count; "
        "if ($p -gt 0 -or $t -gt 0) { 'yes' } else { 'no' }")
    out = subprocess.run(["powershell", "-NoProfile", "-Command", script],
                         capture_output=True, text=True)
    return out.stdout.strip().lower().startswith("yes")


def main() -> None:
    # scheduled every 30 minutes; exit at once if another copy is already waiting
    probe = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "(Get-CimInstance Win32_Process -Filter \"Name like '%python%'\" | "
         "Where-Object { $_.CommandLine -match 'run_modern_ladder_phase2' } | "
         "Measure-Object).Count"], capture_output=True, text=True)
    try:
        # a venv python shows up twice (the launcher stub plus the base
        # interpreter it spawns), so one running copy counts as two processes
        if int(probe.stdout.strip() or 0) > 2:
            print("another phase-2 driver is already running; exiting")
            return
    except ValueError:
        pass
    queue.log("phase-2 driver started; waiting for the Gotham full run")
    while not GOTHAM.exists():
        if not gotham_alive():
            # Relaunch through the resume launcher: it skips seeds whose prediction
            # files already exist, whereas queue.gotham_full() would redo the
            # 40-minute preparation and retrain every seed from scratch.
            queue.log("phase-2: the Gotham process is gone and its summary is missing - "
                      "relaunching in resume mode")
            launcher = ROOT / "scripts" / "launch_gotham_full_run_v1.py"
            subprocess.run([r"E:\论文\.venv\Scripts\python.exe", "-u", str(launcher)],
                           cwd=ROOT)
            # The call above blocks until its own child exits.  When that child
            # died (it did, twice: an out-of-memory error inside the single-view
            # fit), falling through here started the source holdouts and the
            # extra rungs while the Gotham rung was still missing - which is what
            # happened on 2026-10-04 19:36.  Leave the remaining steps to a later
            # tick that sees a finished Gotham rung.
            queue.log("phase-2: relaunch returned; deferring the remaining steps "
                      "to the next tick")
            return
        time.sleep(120)
    if not GOTHAM.exists():  # defensive: never start the rest on an unfinished rung
        queue.log("phase-2: the Gotham full summary is still missing; exiting")
        return
    if GOTHAM.exists():
        summary = json.loads(GOTHAM.read_text(encoding="utf-8"))
        queue.log(f"phase-2: Gotham full present: RCCF {summary['rccf_mean_macro_f1']:.6f} "
                  f"equal {summary['equal_fusion_mean_macro_f1']:.6f} "
                  f"diff {summary['same_members_difference']:+.6f}")
        queue.write_status(gotham_full="done")
    queue.holdouts()
    queue.extra_rungs()
    queue.log("phase-2 driver finished")
    queue.write_status(phase2="done")
    subprocess.run(["schtasks", "/delete", "/tn", "CodexModernLadderPhase2", "/f"],
                   capture_output=True)
    queue.log("scheduled task CodexModernLadderPhase2 removed")


if __name__ == "__main__":
    main()
