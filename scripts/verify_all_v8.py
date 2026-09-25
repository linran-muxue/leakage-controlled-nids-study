"""Single pre-commit verification gate.

Every audit script is executed as a subprocess and its output scanned for failure
markers. The gate exits non-zero if any check fails, so that a script which fails
silently (as happened with an availability-statement update) cannot slip through.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

CHECKS: list[tuple[str, list[str], tuple[str, ...]]] = [
    ("unit tests", ["-m", "pytest", "-q"], (" failed", "error")),
    ("compile all sources", ["-m", "compileall", "-q", "src", "scripts", "tests"], ()),
    ("manuscript structure", ["scripts/audit_manuscripts_v5.py"],
     ("figure order strictly increasing: False", "referenced images missing on disk: [",
      "references marked DOI to verify: 1")),
    ("citation coverage", ["scripts/check_citation_coverage_v5.py"], ("uncited = [1", "uncited = [2")),
    ("number traceability", ["scripts/audit_number_traceability_v5.py"], ("mismatches: 1", "mismatches: 2")),
    # The coverage audit showed that only 54 of the 338 decimals in the body were
    # matched by a headline assertion; this closes the gap for the Section 5.5
    # external benchmarks and the Section 5.7 scale ladder (37 more values).
    ("external and scale numbers", ["scripts/audit_calibration_and_external_numbers_v1.py"],
     ("mismatches 1", "mismatches 2", "ISSUE ")),
    # Section 5.3 reports six mechanism measurements and Table 6; two correlation
    # cells and one entropy cell did not match the released diversity suite at the
    # printed precision, so the whole set is re-derived here (46 assertions).
    ("mechanism and Table 6 numbers", ["scripts/audit_mechanism_numbers_v1.py"],
     ("mismatches 1", "mismatches 2", "ISSUE ")),
    # Sections 5.4 and 5.6: the protocol-sensitivity comparisons, the secondary
    # metrics and the open-set ranges.  The open-set sentence quoted two of the
    # three released seeds (and, for the conditional arm, one of its two
    # probability exports), so both spreads were understated; the check reads
    # every printed endpoint back out of the manuscripts, Table 8 and the
    # self-check table and re-renders it from the released suite (99 assertions).
    ("protocol and secondary numbers", ["scripts/audit_protocol_and_secondary_numbers_v1.py"],
     ("mismatches 1", "mismatches 2", "ISSUE ")),
    # Verifies the processed files against the counts the manuscript quotes,
    # plus split integrity and ten-seed test-set identity. Added after an
    # off-by-one in the quoted train/validation sizes survived every other check.
    ("full-corpus data audit", ["scripts/audit_full_corpus_data_v1.py"], ("DATA_AUDIT_FAILED",)),
    # A resumed batch rewrites metrics_by_seed.csv with only its own seeds; this
    # catches an aggregate that describes fewer seeds than the run produced.
    ("metrics aggregation", ["scripts/check_metrics_aggregation_v1.py"],
     ("METRICS_AGGREGATION_FAILED",)),
    # Recomputes every released metric from the released per-row predictions,
    # over the directories the supplementary bundle ships.
    ("released evidence", ["scripts/audit_released_evidence_v1.py"],
     ("RELEASED_EVIDENCE_FAILED",)),
    ("reference annotations", ["scripts/check_noDOI_notes_v5.py"], ("CHECK",)),
    ("cross-document audit", ["scripts/fresh_audit_v7.py"], ("ISSUE",)),
    ("language consistency", ["scripts/language_audit_v6.py"], ("MIXED",)),
    ("body hygiene", ["scripts/body_hygiene_check_v9.py"], ("ISSUE", "BODY_HYGIENE_FAILED")),
    ("cross-language numbers", ["scripts/cross_language_number_diff_v10.py"], ("MISMATCH",)),
    # The abstract is the most-quoted part of the paper and was the one
    # front-matter document never checked for numbers it does not support.
    ("abstract numbers", ["scripts/check_abstract_numbers_v1.py"], ("ABSTRACT_NUMBERS_FAILED",)),
    # Table 3, Figure 2 and the graphical abstract all render the audit chain;
    # this ties every stage count to the audit records and the split files.
    ("audit chain numbers", ["scripts/check_audit_chain_numbers_v1.py"], ("AUDIT_CHAIN_FAILED",)),
    # Recomputes the paper's only concrete McNemar result from the raw
    # per-row predictions of both models.
    ("McNemar recomputation", ["scripts/check_mcnemar_recomputation_v1.py"],
     ("MCNEMAR_RECOMPUTATION_FAILED",)),
    # The ten-seed upgrade left the neural-baseline row, its paragraph and
    # Figure 4 on the three-seed run while the captions said ten seeds; this
    # re-derives both scopes from their source files and guards the wording.
    ("seed scope", ["scripts/check_seed_scope_v5.py"], ("SEED_SCOPE_FAILED",)),
    ("self-check counts", ["scripts/verify_selfcheck_counts_v7.py"], ("SELFCHECK_MISMATCH",)),
    # The self-check table and the gap report quote the number of traceability
    # assertions and of verified DOIs; both had drifted (50 vs 69 assertions,
    # "47 DOIs" against 36 DOIs plus 11 entries with no DOI). This re-derives
    # those figures from the artifacts.
    ("self-check claims", ["scripts/check_selfcheck_claims_v1.py"], ("SELFCHECK_CLAIMS_FAILED",)),
    ("publication manifest", ["scripts/check_publication_manifest_v12.py"], ("MANIFEST_MISMATCH",)),
    ("submission front matter", ["scripts/check_aux_documents_v13.py"], ("AUX_MISMATCH",)),
    ("supplementary mirror", ["scripts/sync_supplementary_mirror_v16.py", "--check"],
     ("SUPPLEMENTARY_MIRROR_MISMATCH",)),
    # S27/S28/S29 listed two same-named sources per section, so the second copy
    # overwrote the first and the bundle shipped fewer files than the index
    # promised; this ties the index, the bundle and checksums.sha256 together.
    ("supplementary index", ["scripts/check_supplementary_index_v1.py"],
     ("SUPPLEMENTARY_INDEX_FAILED",)),
    # Nine statements the deliverables make about themselves had drifted: the
    # self-check table still said 118 tests, 12,761 English words, 35,338
    # characters, 507 numeric tokens and 7 tables, README announced a 34-check
    # gate, and the three working documents that open with a state snapshot
    # quoted the pre-Round-18 totals.  All nine are recomputed here.
    ("deliverable counts", ["scripts/check_deliverable_counts_v1.py"],
     ("DELIVERABLE_COUNTS_FAILED", "ISSUE ")),
    # Tables 4, 5 and 7 carry the main result and were the last tables whose cells
    # were never re-derived.  The first pass found the Train (s) column of Table
    # 4(b) printing 0.451 / 0.299 / 0.494 where the released balanced run gives
    # 0.249586 / 0.235422 / 0.130834 for the same three models and seeds.
    ("main tables", ["scripts/audit_main_tables_v1.py"],
     ("mismatches 1", "mismatches 2", "ISSUE ")),
    # Self-check row C1 cited final_config.json, which exists nowhere in the
    # repository; the gate configuration that ships is S16's
    # results_gate_tuning_v5/selected_gate_config.json.  Every path a
    # current-state deliverable cites is now required to exist.  The four dated
    # snapshots are excluded on purpose: they name scripts that were later built
    # under other names.
    ("cited paths", ["scripts/check_cited_paths_v1.py"], ("CITED_PATHS_FAILED", "ISSUE ")),
    # Supplementary S24 shipped a DOI record generated for the previous 45-item
    # reference list (two-off numbering plus six DOIs of unrelated works); this
    # ties the record to the list parsed from both manuscripts.
    ("reference DOI record", ["scripts/check_reference_doi_v1.py"],
     ("REFERENCE_DOI_FAILED",)),
    # The public repository tracked 46 scratch/third-party files and its README,
    # MODEL_CARD and DATA_CARD still described three datasets and one
    # population; this ties the released metadata to the paper's actual scope.
    ("release hygiene", ["scripts/check_release_hygiene_v1.py"], ("RELEASE_HYGIENE_FAILED",)),
    # The three-seed and ten-seed releases both contain an "equal RF (chi-square)"
    # arm and disagree for the same seed, because one sorts the selected columns
    # by score and the other keeps the feature order; this keeps the explanation,
    # the canonical selector and both audit records honest.
    ("selection reproducibility", ["scripts/check_selection_reproducibility_v1.py"],
     ("SELECTION_REPRODUCIBILITY_FAILED",)),
    ("docx freshness", ["scripts/check_docx_freshness_v17.py"], ("DOCX_STALE",)),
    ("JISA format limits", ["scripts/check_jisa_format_v22.py"], ("JISA_FORMAT_MISMATCH",)),
    ("duplicate sentences", ["scripts/check_duplicate_sentences_v27.py"], ("SENTENCE_DUPLICATION_FOUND",)),
    # The exact-match duplicate check cannot see a rewrite that keeps a long run
    # of the original wording.  The conclusion of the English manuscript carried
    # the uncapped-corpus claim twice that way (47- and 54-character runs) while
    # self-check E11 claimed no paragraph repeats a set of decimals.
    ("repeated claims", ["scripts/check_repeated_claims_v1.py"], ("REPEATED_CLAIM_FOUND",)),
    # Sections 6 and 7 were the last region no audit covered, and they held two
    # defects: the decision matrix quoted a Log Loss pair from the three-seed runs
    # beside an ECE clause from the ten-seed run (the bundle warns those two sets
    # must not be mixed), and the limitations called 104 cross-split rows "104
    # test rows" (17 test rows is 0.21% of the test set).  The check re-derives
    # all 33 decimals these two sections print and fails if any of them is not
    # asserted, so the coverage gap cannot reopen.
    ("discussion and conclusion numbers", ["scripts/audit_discussion_numbers_v1.py"],
     ("mismatches 1", "mismatches 2", "ISSUE ")),
    ("section and equation refs", ["scripts/check_section_refs_v32.py"], ("SECTION_REF_MISMATCH",)),
    ("character-level proofing", ["scripts/proofread_char_level_v33.py"], ("CHAR_LEVEL_FINDINGS",)),
    ("docx list numbering", ["scripts/check_docx_numbering_v40.py"], ("DOCX_NUMBERING_BROKEN",)),
    ("figure annotations", ["scripts/check_figure_annotations_v44.py"], ("FIGURE_ANNOTATION_MISMATCH",)),
    ("figure reproducibility", ["scripts/check_figure_reproducibility_v45.py"], ("FIGURE_REPRODUCIBILITY_FAILED",)),
]

# Three checks recompute from the *derived* populations (the capping and
# de-duplication step).  The archive deliberately does not redistribute those
# files - DATA_CARD says so and ships the scripts that rebuild them - so on a
# fresh clone the checks cannot run.  Rather than printing three tracebacks,
# they are reported as skipped with the input that is missing, and the summary
# names them.  Locally, where the processed folders exist, nothing is skipped.
LOCAL_INPUTS: dict[str, tuple[str, ...]] = {
    "audit chain numbers": ("data_processed_cic_natural_v3b",
                            "data_processed_cic_balanced_v3b",
                            "data_processed_cic_natural_v4_full"),
    "full-corpus data audit": ("data_processed_cic_natural_v4_full",),
    "selection reproducibility": ("data_processed_cic_natural_v3b",),
}


def missing_inputs(label: str) -> list[str]:
    return [name for name in LOCAL_INPUTS.get(label, ()) if not (ROOT / name).is_dir()]


def run(label: str, args: list[str]) -> tuple[str, str]:
    try:
        proc = subprocess.run([PY] + args, capture_output=True, text=True,
                              cwd=ROOT, timeout=900, errors="replace")
        return proc.stdout, proc.stderr
    except Exception as exc:  # pragma: no cover
        return "", f"{label} failed to run: {exc}"


def main() -> int:
    failures = []
    skipped: list[tuple[str, list[str]]] = []
    for label, args, markers in CHECKS:
        absent = missing_inputs(label)
        if absent:
            skipped.append((label, absent))
            print(f"SKIP  {label:<26} needs {', '.join(absent)} (not redistributed)")
            continue
        out, err = run(label, args)
        combined = out + err
        problems = [m for m in markers if m in combined]
        if "Traceback" in combined or problems:
            failures.append((label, problems or ["exception"], combined))
            print(f"FAIL  {label:<26} {problems or 'exception'}")
        else:
            tail = [l for l in combined.strip().splitlines() if l.strip()][-1:] 
            print(f"PASS  {label:<26} {tail[0][:70] if tail else ''}")

    # release-tag consistency, checked directly rather than through a subprocess
    tags = subprocess.run(["git", "tag"], capture_output=True, text=True, cwd=ROOT).stdout.split()
    latest = sorted(tags, key=lambda t: [int(x) for x in re.findall(r"\d+", t)])[-1] if tags else ""
    en = (ROOT / "重构版论文_v4_20260915" / "English_SCI_Manuscript_v4.md").read_text("utf-8")
    zh = (ROOT / "重构版论文_v4_20260915" / "中文SCI论文_v4_重构版.md").read_text("utf-8")
    cited = set(re.findall(r"v1\.\d+\.\d+", en)) | set(re.findall(r"v1\.\d+\.\d+", zh))
    if cited != {latest}:
        failures.append(("release tag", [f"cited {sorted(cited)} vs latest {latest}"], ""))
        print(f"FAIL  {'release tag':<26} cited {sorted(cited)} vs latest {latest}")
    else:
        print(f"PASS  {'release tag':<26} {latest}")

    print()
    if failures:
        print(f"GATE_FAILED  {len(failures)} check(s)")
        for label, problems, output in failures:
            print(f"\n--- {label} ---")
            print(output.strip()[:1200])
        return 1
    if skipped:
        print(f"GATE_PASSED  all runnable checks green; {len(skipped)} skipped for missing "
              f"local input(s): {', '.join(label for label, _ in skipped)}")
        print("Rebuild them with the scripts in scripts/ (see DATA_CARD.md) to run the "
              "skipped checks.")
    else:
        print("GATE_PASSED  all checks green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
