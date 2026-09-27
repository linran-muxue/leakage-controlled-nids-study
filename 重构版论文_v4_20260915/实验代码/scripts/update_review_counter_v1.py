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
    "round": "39",
    "last_item": "39",
    "last_item_title": "Project flowchart, and the gate and archive counts it exposed",
    "last_result": "fixed",
    "note": (
        "draw the project flowchart: one six-stage chart from the four corpora to the submission bundle "
        "(data acquisition, the six-stage processing audit, modelling and controls, evaluation, "
        "mechanism analysis, paper and release), rendered at 300 dpi for slides and as vector PDF for "
        "print, with a stage-to-entry-point table beside it. The builder asserts that all 32 text "
        "blocks fit inside their panels - the first draft silently pushed the closing lines past theirs "
        "- and every number on the chart is read from an artefact. Wiring it into the gate exposed four "
        "stale counts: the gate ran 48 checks while the work log said 45, the data-source register 47, "
        "and the briefing script and deck 46; the archive's file count was stale in the same way. "
        "scripts/artifact_counts_v1.py now measures the gate size, the staged archive size and the "
        "figure and table counts from the artefacts, five generators read it, "
        "check_deliverable_counts_v1.py asserts the quoted values, and "
        "scripts/check_project_flowchart_v1.py re-renders the chart into a scratch directory and byte- "
        "compares it with the committed PNG, so the chart joins the gate (49 checks). "
    ),
    "timestamp": "2026-09-27T18:00:44+08:00",
}


def carried_note(previous: str, head: str) -> str:
    """Chain the round notes without pasting the whole history into this file.

    ``FIELDS['note']`` describes the round just finished; every earlier note is
    already in the counter file, so it is carried over behind a ``PREVIOUS:``
    marker the way the earlier rounds hand-wrote it.  The chain therefore stays
    complete while this module stays readable.
    """
    previous = previous.strip()
    if not previous or previous.startswith(head[:40]):
        return head
    return f"{head} PREVIOUS: {previous}"


def main() -> int:
    COUNTER.parent.mkdir(parents=True, exist_ok=True)
    text = COUNTER.read_text(encoding="utf-8") if COUNTER.exists() else ""
    existing: dict[str, str] = {}
    for line in text.splitlines():
        if "=" in line and not line.startswith(" "):
            key, value = line.split("=", 1)
            existing[key] = value
    note = carried_note(existing.get("note", ""), FIELDS["note"])
    existing.update(FIELDS)
    existing["note"] = note
    order = ["round", "last_item", "last_item_title", "last_result", "note", "timestamp"]
    COUNTER.write_text("\n".join(f"{key}={existing[key]}" for key in order) + "\n",
                       encoding="utf-8")
    for key in order:
        print(f"{key}={existing[key][:90]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
