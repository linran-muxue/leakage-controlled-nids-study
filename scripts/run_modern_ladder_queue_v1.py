"""Drive the whole modern-ladder programme and survive restarts.

The queue runs, in order:

  1. C rung    CIC-IoT-2023 with a 500 000-per-class cap (ten seeds)
  2. Gotham    the uncapped 35.1 M-packet corpus (ten seeds)
  3. holdouts  leave-one-device-out (Gotham) and leave-one-run-out (6TiSCHSet)

The first two are the long ones and are started concurrently, each in its own
process, because together they still fit in 32 GiB (about 4 GB and 12 GB peak).
Every step is skipped when its final artefact already exists, so the queue can be
restarted at any point without redoing work.

Progress goes to logs/modern_ladder_v1.log and logs/modern_ladder_status.json;
each subprocess gets its own log next to them.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
PY = r"E:\论文\.venv\Scripts\python.exe"
LOGS = ROOT / "logs"
LOGS.mkdir(exist_ok=True)
SEEDS = ["42", "2024", "3407", "7", "13", "101", "202", "303", "404", "505"]
STATUS = LOGS / "modern_ladder_status.json"


def log(message: str) -> None:
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    print(line, flush=True)
    with (LOGS / "modern_ladder_v1.log").open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def write_status(**fields) -> None:
    data = {}
    if STATUS.exists():
        try:
            data = json.loads(STATUS.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
    data.update(fields)
    data["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
    STATUS.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def run(args: list[str], tag: str) -> None:
    with (LOGS / f"modern_ladder_{tag}.log").open("a", encoding="utf-8") as handle:
        proc = subprocess.run([PY] + args, cwd=ROOT, stdout=handle,
                              stderr=subprocess.STDOUT)
    if proc.returncode != 0:
        log(f"{tag} exited with code {proc.returncode}")


def c_rung() -> None:
    if (ROOT / "results_rccf_cic_iot2023_cap500k" / "benchmark_summary.json").exists():
        log("C rung already present, skipping")
        return
    log("C rung: preparing data_processed_cic_iot2023_cap500k")
    run(["scripts\\prepare_cic_iot2023_v1.py", "--train-cap", "500000",
         "--test-cap", "100000", "--processed-dir", "data_processed_cic_iot2023_cap500k",
         "--audit-dir", "results_data_audit_cic_iot2023_cap500k"], "c_prep")
    log("C rung: ten seeds")
    run(["scripts\\run_native_label_benchmark_v1.py",
         "--processed-dir", "data_processed_cic_iot2023_cap500k",
         "--output-dir", "results_rccf_cic_iot2023_cap500k",
         "--seeds", *SEEDS, "--experts", "full", "chi2", "anova"], "c_run")
    log("C rung finished")
    write_status(c_rung="done")


def gotham_full() -> None:
    if (ROOT / "results_rccf_gotham2025_full" / "benchmark_summary.json").exists():
        log("Gotham full already present, skipping")
        return
    log("Gotham full: preparing the uncapped 35.1 M-packet population")
    run(["scripts\\prepare_gotham2025_v1.py", "--train-cap", "100000000",
         "--test-cap", "100000000", "--processed-dir", "data_processed_gotham2025_full",
         "--audit-dir", "results_data_audit_gotham2025_full"], "gotham_prep")
    log("Gotham full: ten seeds")
    run(["scripts\\run_native_label_benchmark_v1.py",
         "--processed-dir", "data_processed_gotham2025_full",
         "--output-dir", "results_rccf_gotham2025_full",
         "--seeds", *SEEDS, "--experts", "full", "chi2", "anova"], "gotham_run")
    log("Gotham full finished")
    write_status(gotham_full="done")


def holdouts() -> None:
    for dataset, tag in (("gotham", "gotham"), ("6tisch", "6tisch")):
        # Idempotence, as advertised in the module docstring: an existing
        # holdout summary is a finished artefact, so a restarted driver must not
        # redo (and momentarily clobber) it.
        if (ROOT / f"results_source_holdout_{tag}_v1" / "holdout_summary.json").exists():
            log(f"holdout {tag}: summary present, skipping")
            continue
        grouped = ROOT / f"data_processed_{dataset}2025_grouped_v1" if dataset == "gotham" \
            else ROOT / "data_processed_6tisch2026_grouped_v1"
        if not (grouped / "all.csv").exists():
            log(f"holdout: building grouped corpus for {dataset}")
            run(["scripts\\prepare_grouped_corpus_v1.py", "--dataset", dataset], f"grouped_{tag}")
        log(f"holdout: leave-one-source-out for {dataset}")
        run(["scripts\\run_source_holdout_v1.py", "--processed-dir", grouped.name,
             "--output-dir", f"results_source_holdout_{tag}_v1"], f"holdout_{tag}")
    log("holdouts finished")
    write_status(holdouts="done")


def extra_rungs() -> None:
    """The remaining 'comprehensive' items, all cheaper than the two big rungs."""
    jobs = (
        ("6tisch-uncapped",
         ["scripts\\prepare_2026_corpora_v1.py", "--dataset", "6tisch",
          "--train-cap", "100000000", "--test-cap", "100000000",
          "--processed-dir", "data_processed_6tisch2026_uncapped_v1",
          "--audit-dir", "results_data_audit_6tisch2026_uncapped_v1"],
         ["scripts\\run_native_label_benchmark_v1.py",
          "--processed-dir", "data_processed_6tisch2026_uncapped_v1",
          "--output-dir", "results_rccf_6tisch2026_uncapped", "--seeds", *SEEDS,
          "--experts", "full", "chi2", "anova"]),
        ("ctu-uncapped",
         ["scripts\\prepare_2026_corpora_v1.py", "--dataset", "ctu",
          "--train-cap", "100000000", "--test-cap", "100000000",
          "--processed-dir", "data_processed_ctu_idseval6_uncapped_v1",
          "--audit-dir", "results_data_audit_ctu_idseval6_uncapped_v1"],
         ["scripts\\run_native_label_benchmark_v1.py",
          "--processed-dir", "data_processed_ctu_idseval6_uncapped_v1",
          "--output-dir", "results_rccf_ctu_idseval6_uncapped", "--seeds", *SEEDS,
          "--experts", "full", "chi2", "anova"]),
        ("gotham-cap200k", ["scripts\\prepare_gotham2025_v1.py", "--train-cap", "200000",
                            "--test-cap", "50000",
                            "--processed-dir", "data_processed_gotham2025_cap200k",
                            "--audit-dir", "results_data_audit_gotham2025_cap200k"],
         ["scripts\\run_native_label_benchmark_v1.py",
          "--processed-dir", "data_processed_gotham2025_cap200k",
          "--output-dir", "results_rccf_gotham2025_cap200k", "--seeds", *SEEDS,
          "--experts", "full", "chi2", "anova"]),
    )
    for tag, prep, run_args in jobs:
        marker = ROOT / run_args[run_args.index("--output-dir") + 1] / "benchmark_summary.json"
        if marker.exists():
            log(f"{tag}: already present, skipping")
            continue
        log(f"{tag}: preparing")
        run(prep, f"{tag}_prep")
        log(f"{tag}: running ten seeds")
        run(run_args, f"{tag}_run")
        log(f"{tag}: finished")
    # the budget sweep needs the uncapped variants to exist first? no: it uses rung A
    log("feature-budget sweep on CIC-IoT-2023 rung A")
    run(["scripts\\run_feature_budget_sweep_v1.py"], "budget_sweep")
    # Port the mechanism suite (margin bound, weight mechanism, diversity) to the
    # modern anchors.  All three scripts already take --processed-dir, so this is
    # a re-run rather than a re-implementation.
    mechanism = (
        ("cic-iot2023", "data_processed_cic_iot2023_v1"),
        ("gotham2025", "data_processed_gotham2025_v1"),
    )
    for tag, processed in mechanism:
        log(f"mechanism suite (margin bound) on {tag}")
        run(["scripts\\analyze_margin_bound_v5.py", "--processed-dir", processed,
             "--output-dir", f"results_margin_bound_{tag}_v1",
             "--seeds", *SEEDS], f"margin_{tag}")
        log(f"mechanism suite (weight mechanism) on {tag}")
        run(["scripts\\analyze_weight_mechanism.py", "--processed-dir", processed,
             "--output-dir", f"results_weight_mechanism_{tag}_v1"], f"weight_{tag}")
    log("mechanism suite (diversity) on cic-iot2023")
    run(["scripts\\run_diversity_suite_v5.py",
         "--processed-dir", "data_processed_cic_iot2023_v1",
         "--output-dir", "results_diversity_cic_iot2023_v1",
         "--seeds", "42", "2024", "3407"], "diversity_cic")
    log("secondary evidence recomputation")
    run(["scripts\\analyse_modern_evidence_v1.py"], "evidence")
    run(["scripts\\analyse_modern_replication_v1.py"], "replication")
    write_status(extra_rungs="done")


def main() -> None:
    log("modern-ladder queue started")
    write_status(started=time.strftime("%Y-%m-%d %H:%M:%S"),
                 c_rung="pending", gotham_full="pending", holdouts="pending")
    # the B rung is already running in the foreground session; wait for it so the
    # two long jobs do not contend for the same 16 cores
    b_summary = ROOT / "results_rccf_cic_iot2023_cap200k" / "benchmark_summary.json"
    waited = 0
    while not b_summary.exists():
        if waited % 30 == 0:
            log(f"waiting for the B rung to finish ({waited} min)")
            write_status(b_rung="waiting" if waited else "running")
        time.sleep(60)
        waited += 1
    log("B rung present; starting C rung and the Gotham full rung")
    write_status(b_rung="done")
    import threading
    threads = [threading.Thread(target=c_rung, name="c-rung"),
               threading.Thread(target=gotham_full, name="gotham-full")]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    holdouts()
    extra_rungs()
    log("modern-ladder queue finished")
    write_status(finished=time.strftime("%Y-%m-%d %H:%M:%S"))
    subprocess.run(["schtasks", "/delete", "/tn", "CodexModernLadder", "/f"],
                   capture_output=True)
    log("scheduled task CodexModernLadder removed")


if __name__ == "__main__":
    main()
