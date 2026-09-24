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
    "round": "17",
    "last_item": "17",
    "last_item_title": "Section 7 of the English manuscript stated one claim twice",
    "last_result": "fixed",
    "note": ("restarted the rotation at item 1 (cross-document numbers) and went after the region "
             "no assertion covered: Sections 6 and 7. The conclusion of the English manuscript "
             "carried the same claim twice inside one paragraph - the uncapped-corpus deficit of "
             "-0.005533 and its 175-fold training cost, first as a result and again after a "
             "rewrite that kept 47 characters verbatim (54 including the opening claim). "
             "check_duplicate_sentences_v27.py compares sentences exactly, so it could not see "
             "it, and self-check E11 claimed that no paragraph repeats a set of decimals while "
             "this one repeated -0.005533 three times. scripts/fix_conclusion_duplication_v1.py "
             "asserts the deficit, the ten seeds, both TOST verdicts and the 175.09x slowdown "
             "against results_full_corpus_v49/full_corpus_summary.json, folds the TOST verdict "
             "into the surviving sentence so nothing is lost, and drops the duplicate; the "
             "Chinese conclusion already stated it once. The new gate check "
             "scripts/check_repeated_claims_v1.py flags any two sentences of one paragraph that "
             "share a run of 40 characters - the accident shared 54 and 47, the longest "
             "legitimate pair in either body shares 35 (a repeated model name) and the Section "
             "5.2 contrast shares 22 - with three unit tests pinning both sides of the "
             "threshold. Gate 38 checks green; docx, manifest, bundle and desktop rebuilt. Note "
             "for the next round: Sections 6 and 7 still carry ~35 decimals with no assertion "
             "(the coverage audit now points at them), and the open-set metrics still have no "
             "supplementary item."),
    "timestamp": "2026-09-25T03:45:00+08:00",
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
