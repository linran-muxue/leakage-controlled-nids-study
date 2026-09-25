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
    "round": "25",
    "last_item": "25",
    "last_item_title": "Submission readiness: one author-input gap was undeclared",
    "last_result": "fixed",
    "note": ("submission-readiness pass. The JISA hard limits all hold - abstract 249 of 250 "
             "words, seven keywords, five Highlights with the longest at 84 characters, equations "
             "(1)-(5) in order, graphical abstract 3300x2280 - and the content side is complete "
             "(44 gate checks). The open items are the eight places that need author input, and "
             "one of them was not declared anywhere: CITATION.cff still carries 'name: Author to "
             "be completed', while the self-check table named only the manuscript CRediT "
             "placeholder (A5) and the cover-letter signature block (F9). Row A5 and the "
             "author-action list now name the CFF field too. The same pass found row E10 quoting "
             "the longest Highlight as 83 characters when it is 84 (inside the 85 limit either "
             "way). scripts/check_submission_readiness_v1.py joins the gate (44 checks): it "
             "re-derives the JISA limits from the format checker and requires every remaining "
             "placeholder to be named by a 部分通过 row, so an author input can never be silently "
             "missing from the inventory. "
             "PREVIOUS: authenticity and completeness pass over the data the study rests on; no defect was "
             "found, so the round produced a new guard instead. Recorded digests: the eight "
             "CIC-IDS2017 SHA-256 values in supplementary S01 all match the raw CSVs on disk, and "
             "their rows sum to 2,830,743, exactly the source_rows the audit record declares; "
             "NSL-KDD KDDTrain+/KDDTest+ match (19,109,424 and 3,441,513 bytes); UNSW-NB15 "
             "training/testing match (175,341 and 82,332 rows, the published split); and the "
             "N-BaIoT archive matches byte for byte (1,772,922,927 bytes) and extracts to the "
             "recorded nine device folders. Completeness: of 27 per-seed metric files, nine carry "
             "the full ten-seed set and seventeen the three-seed set, plus one single-seed file "
             "from an intermediate MLP run that neither the paper nor the bundle cites; and every "
             "released per-row prediction file covers its population's entire declared test set "
             "(16 populations sampled, zero mismatches). scripts/audit_data_authenticity_v1.py "
             "joins the gate (43 checks) and repeats all of it, skipping the digest section "
             "wherever a raw dataset is absent, since the archives are not redistributed. "
             "PREVIOUS: finer-grained pass over the paths the deliverables cite. Every backticked file "
             "name in the four current-state deliverables (self-check table, README, DATA_CARD, "
             "MODEL_CARD) was resolved against the repository: 44 cited paths, one of which does "
             "not exist - self-check row C1 offered 'final_config.json' as its evidence for "
             "method reproducibility, and no such file is present anywhere (two retired runners "
             "used to write it). The configuration that ships is "
             "results_gate_tuning_v5/selected_gate_config.json, registered as S16 with the "
             "108-configuration search that produced it, so C1 now cites that. "
             "scripts/check_cited_paths_v1.py joins the gate and requires every cited path to "
             "exist; the four dated snapshots (review report, gap audit, P0/P1 manual, structure "
             "plan) are excluded on purpose because they record what was planned on a particular "
             "date and name scripts later built under other names. The same sweep found that all "
             "three snapshots described the review report as covering '第一至第十一轮' while its "
             "own headings run to 第十九轮; the range is now recomputed from those headings by "
             "check_deliverable_counts_v1.py and rewritten to 第一至第十九轮. Gate 42 checks "
             "green; docx, manifest, bundle and desktop rebuilt. "
             "PREVIOUS: main-table pass. Tables 4, 5 and 7 carry the main result and were the last tables "
             "whose cells had never been re-derived, so scripts/audit_main_tables_v1.py now "
             "re-derives all 137 of them from the released runs: Table 4(a) from "
             "results_seeds10_v5 plus the MLP files, 4(b) from the balanced-control runs, Table "
             "5 from the power, effect-size and sign-flip files, and Table 7 from the scale "
             "ladder and the full-corpus summary. The first pass found the Train (s) column of "
             "Table 4(b) printing 0.451 / 0.299 / 0.494 for the three forest rows while "
             "results_cic_balanced_baselines_v3b gives 0.249586 / 0.235422 / 0.130834 for the "
             "same models over the same seeds. No artefact in the repository contains the "
             "printed values - not the per-seed file, not the aggregate, not an earlier balanced "
             "run - and they are not a constant multiple of the released times (1.8x, 1.3x, "
             "3.8x), so they are not a machine-speed difference. Every other cell of those rows "
             "reproduces the released run exactly, as do the conditional-mechanism row (9.130 s) "
             "and the XGBoost row (0.398 s). scripts/fix_table4_balanced_train_times_v1.py "
             "asserts the three source means, rewrites the cells to 0.250 / 0.235 / 0.131 in "
             "both manuscripts and then requires the audit to pass; the audit joins the gate "
             "(41 checks) and README's count is recomputed by the deliverable-counts guard. Also "
             "verified this round: every per-row prediction behind the released runs is tracked "
             "in the public repository (722 files, including the ten 50 MB full-corpus ones), so "
             "the availability statement holds. "
             "PREVIOUS: front-matter pass. The cover letter claimed 'A 118-test suite runs in continuous "
             "integration' while the suite collects 138. The front-matter check could not see it "
             "for two reasons, both now closed in check_aux_documents_v13.py: it compared the "
             "auxiliary documents against the whole manuscript, so reference page ranges "
             "(1189-1232, 1157-1182) vouched for any three-digit number; and its token patterns "
             "matched only decimals and integers of four digits or more, so suite sizes, "
             "search-grid sizes and table counts were never compared at all. The comparison now "
             "uses the body without the reference list and requires every three-digit integer to "
             "appear there - it flagged the 118 immediately - and the suite size is additionally "
             "recomputed from pytest collection by check_deliverable_counts_v1.py, which now "
             "covers the cover letter as well. Fixed by fix_deliverable_counts_v1.py to 138. The "
             "rest of the cover letter was verified against source this round and reproduces: "
             "N-BaIoT 180,000 flows (three 60,000-row classes in dataset_summary.csv), the "
             "53,237 of 2,668,729 physically valid records (data_processing_audit.json), the "
             "7.8x scale-up, the 4.1x model size and 4.6x throughput, the 175x training penalty, "
             "and both TOST verdicts. The old note about the earlier deliverable-count sweep is "
             "kept below. "
             "PREVIOUS: global sweep for statements the deliverables make about themselves. Nine had "
             "drifted, all invisible to the existing gate because nothing recomputed them: the "
             "self-check table still said 118 unit tests (138 collect), 12,761 English words and "
             "35,338 Chinese characters (14,563 and 39,816), 507 numeric tokens per manuscript "
             "(589), and 7 main tables (8 captions, Table 1-8); README announced a 34-check gate "
             "(39 before this round, 40 after it); and the three working documents that open "
             "with a snapshot of the current state - the gap audit, the P0/P1 manual and the "
             "structure plan - still quoted the pre-Round-18 totals of 66 checks with 62 passing "
             "instead of 69 with 65. The gap audit's S8 status line also still described the "
             "English manuscript as 10,800 words with 10 tables. "
             "scripts/check_deliverable_counts_v1.py recomputes all nine from the artefacts "
             "(pytest collection, the gate table, the manuscripts, the figures directory and the "
             "self-check status counts) and fails if a deliverable states a different number; "
             "scripts/fix_deliverable_counts_v1.py re-measures through that check, rewrites the "
             "declarations and then requires the check to pass. The guard joins the gate, which "
             "is why README now says 40 rather than 39. Gate 40 checks green; docx, manifest, "
             "bundle and desktop rebuilt."),
    "timestamp": "2026-09-25T05:10:00+08:00",
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
