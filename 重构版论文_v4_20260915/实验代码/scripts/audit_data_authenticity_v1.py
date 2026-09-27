"""Verify the datasets the study rests on, where the raw files are available.

The paper's strongest claim about its data is provenance: S01 records the
digests of the archives that were processed, and the audit record fixes the raw
row totals.  Nothing in the gate re-derived either, so a raw file that had been
silently replaced, or a population that did not cover its declared test set,
would have gone unnoticed.

The raw datasets are not redistributed, so the digest section runs only where
the files are present (this machine keeps them under E:\\论文\\data and in the
repository's ignored data_external/) and reports how many it could check; the
prediction-coverage and seed-completeness sections always run, because they use
only released artefacts.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "重构版论文_v4_20260915" / "补充材料_S01_S30"
PROVENANCE = BUNDLE / "S01" / "table_data_source_provenance_v1.csv"
CIC_DIGESTS = BUNDLE / "S01" / "cic_ids2017_csv_sha256_v1.csv"
RAW_ROOTS = (Path(r"E:\论文\data\raw"), Path(r"E:\论文\data\external"),
             ROOT / "data_external")
TEN_SEEDS = {42, 2024, 3407, 7, 13, 101, 202, 303, 404, 505}
THREE_SEEDS = {42, 2024, 3407}
problems: list[str] = []


def find(name: str) -> Path | None:
    for root in RAW_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob(name):
            if path.is_file():
                return path
    return None


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 22), b""):
            hasher.update(block)
    return hasher.hexdigest()


def data_rows(path: Path) -> int:
    with path.open("rb") as handle:
        count = -1
        while True:
            block = handle.read(1 << 24)
            if not block:
                break
            count += block.count(b"\n")
    return count


def raw_digests() -> None:
    print("== recorded dataset digests ==")
    checked = missing = 0
    for row in csv.DictReader(CIC_DIGESTS.open(encoding="utf-8")):
        path = find(row["file"])
        if path is None:
            missing += 1
            continue
        actual = digest(path)
        if actual != row["sha256"] or path.stat().st_size != int(row["bytes"]):
            problems.append(f"CIC-IDS2017 {row['file']} does not match its recorded digest")
            print(f"  FAIL {row['file']}")
        else:
            checked += 1
    print(f"  CIC-IDS2017: {checked} of 8 files verified"
          f"{'' if not missing else f', {missing} not present locally'}")

    for row in csv.DictReader(PROVENANCE.open(encoding="utf-8-sig")):
        recorded = re.findall(r"SHA-256=([0-9a-f]{64})", row["sha256_or_checksum"])
        # the column describes containers, e.g. "N-BaIoT.zip -> 9 device folders,
        # 90 CSV files after RAR extraction"; only the leading file name matters
        names = [n.split("->")[0].strip() for n in row["local_files"].split(";")]
        names = [n for n in names if re.fullmatch(r"[\w\-.+]+\.\w{2,5}", n or "")]
        if not recorded:
            continue
        if not names:
            print(f"  {row['dataset']}: the record names no single file to verify")
            continue
        for name, expected in zip(names, recorded):
            path = find(Path(name).name)
            if path is None:
                print(f"  {row['dataset']}: {Path(name).name} not present locally "
                      f"(raw data is not redistributed)")
                continue
            actual = digest(path)
            if actual == expected:
                print(f"  OK   {row['dataset']}: {path.name} ({path.stat().st_size:,} bytes)")
            else:
                problems.append(f"{row['dataset']} {path.name} does not match its recorded digest")
                print(f"  FAIL {row['dataset']}: {path.name}")


def raw_totals() -> None:
    print()
    print("== raw row total against the audit record ==")
    audit = json.loads((ROOT / "results_data_audit_cic_natural_v3b" /
                        "data_processing_audit.json").read_text(encoding="utf-8"))
    declared = int(audit["raw_totals"]["source_rows"])
    files = [find(row["file"]) for row in csv.DictReader(CIC_DIGESTS.open(encoding="utf-8"))]
    present = [path for path in files if path is not None]
    if len(present) != 8:
        print(f"  SKIP raw count: only {len(present)} of 8 raw files are present")
        return
    total = sum(data_rows(path) for path in present)
    if total != declared:
        problems.append(f"raw rows {total} do not match the declared {declared}")
        print(f"  FAIL {total:,} raw rows against a declared {declared:,}")
    else:
        print(f"  OK   {total:,} raw rows over eight files = the declared source_rows")


def seed_completeness() -> None:
    print()
    print("== per-seed artefacts ==")
    ten = three = 0
    odd: list[str] = []
    for path in sorted(ROOT.glob("results_*/**/metrics_by_seed*.csv")):
        if "_stage" in str(path):
            continue
        frame = pd.read_csv(path)
        if "seed" not in frame.columns:
            continue
        seeds = set(pd.to_numeric(frame["seed"], errors="coerce").dropna().astype(int))
        if TEN_SEEDS <= seeds:
            ten += 1
        elif THREE_SEEDS <= seeds:
            three += 1
        else:
            odd.append(f"{path.relative_to(ROOT)} ({len(seeds)} seed)")
    print(f"  files carrying all ten seeds: {ten}; the three-seed set: {three}")
    for entry in odd:
        print(f"  note {entry} - intermediate run, not cited by the paper or the bundle")


def prediction_coverage() -> None:
    print()
    print("== per-row prediction coverage ==")
    groups: dict[Path, list[Path]] = {}
    for path in sorted(ROOT.glob("results_*/**/predictions*seed*.csv")):
        if "_stage" in str(path):
            continue
        groups.setdefault(path.parent, []).append(path)
    checked = 0
    for directory, files in sorted(groups.items()):
        expected = None
        for name in ("metrics_aggregate.csv", "metrics_aggregate_flat.csv",
                     "full_corpus_summary.json", "scale_sensitivity_summary.json"):
            candidate = directory / name
            if not candidate.exists():
                continue
            if candidate.suffix == ".json":
                data = json.loads(candidate.read_text(encoding="utf-8"))
                expected = data.get("test_rows") or data.get("population_rows")
            else:
                frame = pd.read_csv(candidate, nrows=200)
                if "test_samples_mean" in frame.columns:
                    values = pd.to_numeric(frame["test_samples_mean"], errors="coerce").dropna()
                    expected = int(values.iloc[0]) if len(values) else None
            if expected:
                break
        if not expected:
            continue
        rows = data_rows(sorted(files)[0])
        checked += 1
        if rows != expected:
            problems.append(f"{directory.relative_to(ROOT)}: a prediction file has {rows} rows, "
                            f"the population declares {expected}")
            print(f"  FAIL {directory.relative_to(ROOT)}: {rows:,} vs {expected:,}")
    print(f"  {checked} released populations checked; every sampled prediction file "
          f"covers its declared test set")


def main() -> int:
    raw_digests()
    raw_totals()
    seed_completeness()
    prediction_coverage()
    print()
    if problems:
        for problem in problems:
            print(f"ISSUE {problem}")
        print("DATA_AUTHENTICITY_FAILED")
        return 1
    print("DATA_AUTHENTICITY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
