"""Rewrite logs/review_round_counter.txt from explicit fields.

The counter is local state (logs/ is gitignored) but it is the only record of
which rotation item each review round covered, so it has to stay readable and
correct.  Editing it through a script avoids the long single-line note drifting
out of sync with the header.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
COUNTER = ROOT / "logs" / "review_round_counter.txt"

FIELDS = {
    "round": "13",
    "last_item": "13",
    "last_item_title": "Verification gate on a fresh clone: document and handle its data prerequisites",
    "last_result": "fixed",
    "note": ("reviewed the archive as a reader would receive it. Three of the 34 gate checks "
             "(audit chain numbers, full-corpus data audit, selection reproducibility) recompute "
             "from the derived populations data_processed_cic_natural_v3b / "
             "data_processed_cic_balanced_v3b / data_processed_cic_natural_v4_full, which the "
             "archive deliberately does not redistribute (DATA_CARD says so). On a fresh clone "
             "they therefore died with FileNotFoundError tracebacks and a reader would conclude "
             "the package was broken. verify_all_v8.py now declares those inputs, prints SKIP with "
             "the missing folder and names the skipped checks in the summary instead of a "
             "traceback; locally all 34 still run (verified: nothing skipped). "
             "audit_released_evidence_v1.py now also prints which supplementary source folders "
             "were absent, so its 320-value coverage claim stays honest on a partial checkout. "
             "README documents the prerequisite (and check_release_hygiene_v1 fails if that "
             "documentation disappears). Also verified in this round: the CI workflow installs "
             "requirements-direct.txt and runs pytest + compileall, and no unit test reads the "
             "non-redistributed data, so CI is green on a fresh clone; requirements-direct.txt "
             "pins the eleven direct dependencies. Gate 34 checks green; bundle rebuilt and "
             "desktop synced."),
    "timestamp": "2026-09-25T00:30:00+08:00",
}


def main() -> int:
    COUNTER.parent.mkdir(parents=True, exist_ok=True)
    text = COUNTER.read_text(encoding="utf-8") if COUNTER.exists() else ""
    existing: dict[str, str] = {}
    for line in text.splitlines():
        if "=" in line and not line.startswith(" "):
            key, value = line.split("=", 1)
            existing[key] = value
    existing.update(FIELDS)
    order = ["round", "last_item", "last_item_title", "last_result", "note", "timestamp"]
    COUNTER.write_text("\n".join(f"{key}={existing[key]}" for key in order) + "\n",
                       encoding="utf-8")
    for key in order:
        print(f"{key}={existing[key][:90]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
