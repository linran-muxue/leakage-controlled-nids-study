"""One-shot status board for the full-corpus RCCF run.

Prints everything the watchdog needs in a single command: which seeds are done,
whether the supervisor and the keep-awake helper are alive, how much CPU the
workers are burning, whether the machine has been entering standby, and a rough
estimate of the remaining wall time.
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results_rccf_cic_natural_v4_full"
LOGS = ROOT / "logs"
SEEDS = [42, 2024, 3407, 7, 13, 101, 202, 303, 404, 505]


def heartbeat_age(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    stamp = path.read_text(encoding="utf-8").strip().splitlines()[-1]
    age = (datetime.now() - datetime.fromisoformat(stamp)).total_seconds()
    return f"{age:.0f}s ago ({stamp})"


def python_workers() -> list[str]:
    # Identify workers by accumulated CPU rather than memory: a worker drops
    # below 1 GB during its lighter phases (seen at 19:00 on 2026-09-22), which
    # made a memory threshold report "0 workers" while all three were healthy.
    script = (
        # Either test alone produces false negatives: a freshly launched worker
        # has not accumulated 300 s of CPU yet, and a worker in its light phase
        # can drop below 500 MB.  The union of the two tests never hides a live
        # worker, which is what made a memory-only threshold dangerous.
        "Get-Process | Where-Object { $_.ProcessName -match 'python' -and "
        "($_.CPU -gt 300 -or $_.WorkingSet64 -gt 500MB) } | ForEach-Object { "
        "'{0} {1:N0}MB {2:N2}h' -f $_.Id, ($_.WorkingSet64/1MB), ($_.CPU/3600) }"
    )
    result = subprocess.run(["powershell", "-NoProfile", "-Command", script],
                            capture_output=True, text=True, errors="replace")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def standby_count(minutes: int) -> int:
    # Built without a ``$start`` variable: the hash-literal form gets mangled
    # when the command is passed as a single -Command argument.
    since = (datetime.now() - timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%S")
    script = (
        "Get-WinEvent -LogName System -MaxEvents 500 -ErrorAction SilentlyContinue | "
        "Where-Object { $_.ProviderName -eq 'Microsoft-Windows-Kernel-Power' "
        f"-and $_.Id -eq 506 -and $_.TimeCreated -gt '{since}' }} | "
        "Measure-Object | Select-Object -ExpandProperty Count"
    )
    # Windows PowerShell 5.1 cannot load Microsoft.PowerShell.Diagnostics when
    # spawned inside the sandbox; pwsh 7 can.
    shells = [
        Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe",
        Path("powershell"),
    ]
    result = None
    for shell in shells:
        try:
            result = subprocess.run([str(shell), "-NoProfile", "-Command", script],
                                    capture_output=True, text=True, errors="replace")
            if result.returncode == 0:
                break
        except OSError:
            continue
    if result is None:
        return -1
    try:
        return int(result.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        print(f"  [standby probe rc={result.returncode} "
              f"stdout={result.stdout.strip()[:120]!r} stderr={result.stderr.strip()[:200]!r}]")
        return -1


def main() -> int:
    done = [s for s in SEEDS if (OUTPUT / f"predictions_seed{s}.csv").exists()]
    todo = [s for s in SEEDS if s not in done]
    print(f"time            : {datetime.now():%Y-%m-%d %H:%M:%S}")
    print(f"seeds done      : {len(done)}/10 {done}")
    print(f"seeds remaining : {todo}")
    print(f"supervisor      : {heartbeat_age(LOGS / 'supervisor_heartbeat.txt')}")
    print(f"keep-awake v3   : {heartbeat_age(LOGS / 'keep_awake_v3_heartbeat.txt')}")
    workers = python_workers()
    print(f"workers (>300s) : {len(workers)}")
    for line in workers:
        print(f"                  {line}")
    print(f"standby (506)   : {standby_count(40)} in the last 40 min")
    # The supervisor assigns one slot per remaining seed, up to the worker cap.
    expected = min(3, len(todo))
    if todo and len(workers) < expected:
        print(f"ACTION          : fewer than {expected} workers alive; restart the supervisor")
    if not todo:
        print("ACTION          : all seeds complete; run the finalisation pipeline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
