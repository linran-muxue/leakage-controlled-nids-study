"""Point the CIC-IDS2017 provenance row at the per-file checksum table.

The archive itself is not retained, so its checksum alone cannot be checked
against the files that were actually processed.  The row now records both: the
archive checksum as downloaded, and the per-file checksums of the extracted
CSVs that ship as a separate table in S01.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
PROVENANCE = ROOT / "results_paper_materials_v3" / "tables" / "table_data_source_provenance_v1.csv"
PER_FILE = "results_paper_materials_v3/tables/cic_ids2017_csv_sha256_v1.csv"

OLD_SUFFIX = "SHA-256=c3f26274b36c837ccf28ffd2dbf4582941c30b3ee70a635c6e5b2f87c4727928; MD5=4f83860afbf29cac8163854095bf6cf7"
NEW_SUFFIX = ("Archive SHA-256=c3f26274b36c837ccf28ffd2dbf4582941c30b3ee70a635c6e5b2f87c4727928; "
              "MD5=4f83860afbf29cac8163854095bf6cf7; archive not retained locally; per-file SHA-256 "
              f"of the eight extracted CSVs: {PER_FILE}")
OLD_NOTE = "Main task uses an audited five-class balanced research subset, not the full archive"
NEW_NOTE = (OLD_NOTE + "; the per-file checksums let a reader verify the copies actually processed "
            "without re-downloading the archive")


def main() -> int:
    frame = pd.read_csv(PROVENANCE)
    row = frame["dataset"] == "CIC-IDS2017"
    if not row.any():
        raise SystemExit("CIC-IDS2017 row not found")
    if PER_FILE in frame.loc[row, "sha256_or_checksum"].iloc[0]:
        print("provenance already references the per-file table")
        return 0
    frame.loc[row, "sha256_or_checksum"] = frame.loc[row, "sha256_or_checksum"].str.replace(
        OLD_SUFFIX, NEW_SUFFIX, regex=False)
    frame.loc[row, "notes"] = frame.loc[row, "notes"].str.replace(OLD_NOTE, NEW_NOTE, regex=False)
    frame.to_csv(PROVENANCE, index=False, encoding="utf-8")
    print("CIC-IDS2017 provenance row updated")
    print("  hash cell:", frame.loc[row, "sha256_or_checksum"].iloc[0][:120], "...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
