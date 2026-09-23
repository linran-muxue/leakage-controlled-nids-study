"""Record the SHA-256 of every extracted CIC-IDS2017 CSV.

The provenance table records the checksum of the MachineLearningCSV archive,
but that archive is not retained locally, so nobody can verify that the eight
CSVs actually used are the ones it contained.  This writes a per-file checksum
table next to the provenance table and ships it in supplementary item S01, so
the files a reader can obtain are directly checkable.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
RAW = Path(r"E:\论文\data\raw\MachineLearningCVE")
OUT = ROOT / "results_paper_materials_v3" / "tables" / "cic_ids2017_csv_sha256_v1.csv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    files = sorted(RAW.glob("*.csv"))
    if len(files) != 8:
        raise SystemExit(f"expected 8 CIC-IDS2017 CSVs, found {len(files)}")
    rows = [{"file": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in files]
    frame = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUT, index=False, encoding="utf-8")
    print(f"wrote {len(rows)} checksums to {OUT.relative_to(ROOT)}")
    for row in rows:
        print(f"  {row['file']:<62}{row['sha256'][:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
