"""Hold a Windows execution-state request during long unattended runs.

The full-corpus RCCF experiment needs about two hours of wall time per seed.
On this laptop the idle standby timer is 180 s on battery, so an unattended run
is suspended every few minutes and the experiment never finishes.  Lowering the
timeout with ``powercfg`` needs administrator rights, but
``SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)`` does not: it
marks the calling thread as busy for as long as the thread is alive and
therefore suppresses the idle standby timer.

The display is deliberately left alone (``ES_DISPLAY_REQUIRED`` is not set) so
the screen still blanks normally; only system sleep is blocked.  The process
also appends a heartbeat timestamp so a stalled monitor is easy to spot.
"""

from __future__ import annotations

import argparse
import ctypes
import sys
import time
from datetime import datetime
from pathlib import Path

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002
MOUSEEVENTF_MOVE = 0x0001


class _LastInputInfo(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]


def _idle_seconds() -> float:
    """Seconds since the last real user input, or 0 when it cannot be read."""
    info = _LastInputInfo()
    info.cbSize = ctypes.sizeof(info)
    if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info)):
        return 0.0
    tick = int(ctypes.windll.kernel32.GetTickCount())
    return max(0.0, (tick - int(info.dwTime)) / 1000.0)


def _jiggle() -> None:
    """Nudge the pointer one pixel and back so the idle timer is reset.

    A zero-delta move is filtered out, so the pointer is displaced and
    immediately restored; the net movement is nil and the cursor does not
    visibly move.  Only used after the user has been idle, so an active drag or
    selection is never disturbed.
    """
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVE, 1, 0, 0, 0)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVE, -1, 0, 0, 0)


def _set_state(flags: int) -> int:
    kernel32 = ctypes.windll.kernel32
    kernel32.SetThreadExecutionState.restype = ctypes.c_ulong
    kernel32.SetThreadExecutionState.argtypes = [ctypes.c_ulong]
    return int(kernel32.SetThreadExecutionState(ctypes.c_ulong(flags)))


def hold(hours: float, interval: float, heartbeat: Path | None,
         keep_display: bool = True, jiggle_after: float = 120.0) -> int:
    deadline = None if hours <= 0 else time.monotonic() + hours * 3600.0
    # ES_SYSTEM_REQUIRED alone is not enough on Modern Standby laptops: the
    # display powering off is itself the trigger for the S0 low-power idle
    # transition, and the suspended process stops computing.  ES_DISPLAY_REQUIRED
    # keeps the panel on so that transition never starts.  Measured on this
    # machine: with only ES_SYSTEM_REQUIRED the system entered standby twice in
    # six minutes (15:16 and 15:22 on 2026-09-21).
    flags = ES_CONTINUOUS | ES_SYSTEM_REQUIRED | (ES_DISPLAY_REQUIRED if keep_display else 0)
    if _set_state(flags) == 0:
        print("WARN: SetThreadExecutionState rejected the initial request", flush=True)
    while deadline is None or time.monotonic() < deadline:
        time.sleep(interval)
        # Re-assert on every tick: some drivers clear the request, and re-issuing
        # it is harmless when the request is still held.
        _set_state(flags)
        if jiggle_after > 0 and _idle_seconds() >= jiggle_after:
            _jiggle()
        if heartbeat is not None:
            heartbeat.parent.mkdir(parents=True, exist_ok=True)
            with heartbeat.open("a", encoding="utf-8") as handle:
                handle.write(datetime.now().isoformat(timespec="seconds") + "\n")
    _set_state(ES_CONTINUOUS)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hours", type=float, default=0.0,
                        help="stop after this many hours; 0 means run until killed")
    parser.add_argument("--interval", type=float, default=30.0,
                        help="seconds between re-assertions")
    parser.add_argument("--heartbeat", type=Path, default=None,
                        help="optional file that receives one timestamp per tick")
    parser.add_argument("--allow-display-off", action="store_true",
                        help="do not hold the display on (may allow Modern Standby)")
    parser.add_argument("--jiggle-after", type=float, default=120.0,
                        help="simulate input once the user has been idle this many "
                             "seconds; 0 disables the jiggle")
    args = parser.parse_args(argv)
    if sys.platform != "win32":
        print("keep_awake_v1 is a Windows-only helper", file=sys.stderr)
        return 2
    return hold(args.hours, args.interval, args.heartbeat,
                keep_display=not args.allow_display_off,
                jiggle_after=args.jiggle_after)


if __name__ == "__main__":
    raise SystemExit(main())
