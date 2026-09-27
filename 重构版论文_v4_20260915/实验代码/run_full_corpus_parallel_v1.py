"""Drive the full-corpus RCCF batch with parallel workers and auto-resume.

One seed needs roughly nine CPU-hours, but a single worker only averages about
three of the sixteen logical cores (the OOF loop, the MinMaxScaler and the four
logistic risk models are single-threaded).  Two workers therefore nearly double
the throughput without exhausting the 32 GB of RAM or the core count.

The supervisor is idempotent and resumable: it recomputes the missing seeds on
every pass, splits them across workers, and relaunches any worker that exits
with work left.  A heartbeat file lets the watchdog tell a healthy supervisor
from a dead one.
"""

from __future__ import annotations

import argparse
import ctypes
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
PROCESSED = ROOT / "data_processed_cic_natural_v4_full"
OUTPUT = ROOT / "results_rccf_cic_natural_v4_full"
LOGS = ROOT / "logs"
SEEDS = [42, 2024, 3407, 7, 13, 101, 202, 303, 404, 505]
ERROR_ALREADY_EXISTS = 183
LOG_FILE = LOGS / "supervisor_stdout.log"


class _Tee:
    """Mirror stdout into a log file.

    The scheduled task starts python directly (Task Scheduler handles the
    Unicode paths natively, unlike wscript with an ANSI .vbs), so there is no
    shell redirection to capture the output; the supervisor writes its own log.
    """

    def __init__(self, *streams) -> None:
        self.streams = streams

    def write(self, data: str) -> None:
        for stream in self.streams:
            try:
                stream.write(data)
                stream.flush()
            except Exception:
                pass

    def flush(self) -> None:
        for stream in self.streams:
            try:
                stream.flush()
            except Exception:
                pass


def start_logging() -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    handle = LOG_FILE.open("a", encoding="utf-8")
    sys.stdout = _Tee(sys.__stdout__, handle)
    sys.stderr = _Tee(sys.__stderr__, handle)


def claim_single_instance() -> bool:
    """Return False when another supervisor already holds the named mutex.

    The supervisor is also started by a repeating scheduled task, so two
    instances could otherwise launch duplicate workers for the same seeds.
    """
    kernel32 = ctypes.windll.kernel32
    kernel32.CreateMutexW.restype = ctypes.c_void_p
    kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_wchar_p]
    handle = kernel32.CreateMutexW(None, False, "Global\\CodexRCCFSupervisor")
    if not handle:
        return True
    return kernel32.GetLastError() != ERROR_ALREADY_EXISTS


def completed(seed: int) -> bool:
    return (OUTPUT / f"predictions_seed{seed}.csv").exists()


def remaining() -> list[int]:
    return [seed for seed in SEEDS if not completed(seed)]


KEEP_AWAKE_HEARTBEAT = LOGS / "keep_awake_v3_heartbeat.txt"


def ensure_keep_awake() -> None:
    """Start the anti-standby helper when its heartbeat has gone stale.

    Doing this here (rather than in the launcher script) means the repeating
    scheduled task cannot pile up duplicate helpers: each supervisor tick sees
    whether the helper is alive before starting another one.
    """
    if KEEP_AWAKE_HEARTBEAT.exists():
        stamp = KEEP_AWAKE_HEARTBEAT.read_text(encoding="utf-8").strip().splitlines()[-1]
        try:
            age = (datetime.now() - datetime.fromisoformat(stamp)).total_seconds()
        except ValueError:
            age = 1e9
        if age < 120:
            return
    print(f"[{datetime.now():%H:%M:%S}] keep-awake heartbeat stale; starting helper",
          flush=True)
    flags = 0
    if hasattr(subprocess, "DETACHED_PROCESS"):
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    subprocess.Popen(
        [PY, "scripts/keep_awake_v1.py", "--hours", "336", "--interval", "20",
         "--heartbeat", str(KEEP_AWAKE_HEARTBEAT), "--jiggle-after", "120"],
        cwd=ROOT, creationflags=flags,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def launch(chunk: list[int], index: int) -> subprocess.Popen:
    LOGS.mkdir(parents=True, exist_ok=True)
    log_path = LOGS / f"full_corpus_rccf_w{index}.log"
    handle = log_path.open("w", encoding="utf-8")
    command = [PY, "-u", "scripts/run_rccf_cic_v1.py",
               "--processed-dir", str(PROCESSED),
               "--output-dir", str(OUTPUT),
               "--seeds", *[str(s) for s in chunk],
               "--n-estimators", "100", "--cv", "5"]
    print(f"[{datetime.now():%H:%M:%S}] worker {index}: seeds {chunk}", flush=True)
    return subprocess.Popen(command, cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--heartbeat", type=Path, default=LOGS / "supervisor_heartbeat.txt")
    args = parser.parse_args(argv)
    start_logging()
    if not claim_single_instance():
        print("another supervisor instance is already running; exiting", flush=True)
        return 0

    while True:
        todo = remaining()
        if not todo:
            print("ALL_SEEDS_COMPLETE", flush=True)
            return 0
        # Deal the missing seeds round-robin so both workers stay busy and the
        # last seed of one worker is not the last seed overall.
        chunks = [todo[i::args.workers] for i in range(args.workers)]
        slots = [i for i, chunk in enumerate(chunks) if chunk]
        procs = [launch(chunks[i], i) for i in slots]
        print(f"[{datetime.now():%H:%M:%S}] launched {len(procs)} worker(s) for {todo}",
              flush=True)
        while True:
            args.heartbeat.parent.mkdir(parents=True, exist_ok=True)
            args.heartbeat.write_text(datetime.now().isoformat(timespec="seconds") + "\n",
                                      encoding="utf-8")
            ensure_keep_awake()
            time.sleep(30)
            if all(p.poll() is not None for p in procs):
                break
            # A single worker can die (memory pressure, an unexpected error)
            # while the others keep running.  Relaunch that slot immediately
            # with whatever of its own seeds are still missing, rather than
            # waiting for the whole batch to drain.
            for position, proc in enumerate(procs):
                if proc.poll() is None:
                    continue
                slot = slots[position]
                left = [s for s in chunks[slot] if not completed(s)]
                if left:
                    print(f"[{datetime.now():%H:%M:%S}] worker {slot} exited "
                          f"(code {proc.returncode}); relaunching with {left}", flush=True)
                    chunks[slot] = left
                    procs[position] = launch(left, slot)
        codes = [p.returncode for p in procs]
        print(f"[{datetime.now():%H:%M:%S}] workers exited with {codes}; "
              f"still missing {remaining()}", flush=True)
        time.sleep(10)


if __name__ == "__main__":
    raise SystemExit(main())
