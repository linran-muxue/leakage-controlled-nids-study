"""Refresh the reference-verification note after the DOI record was rebuilt.

The note in both manuscripts still dated the verification to 2026-09-16, when
the record still described a 45-entry list, and the English one was missing the
space after "left pending.". The rebuilt record verifies every DOI against
Crossref or DataCite, so the note now says so.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

EN_OLD = ("Note: all DOIs were verified against Crossref on 2026-09-16. Venues that do not assign "
          "Crossref DOIs (PMLR, NeurIPS, JMLR, USENIX) are marked as such rather than left pending."
          "The individual checks are recorded in Supplementary S24.")
EN_NEW = ("Note: all DOIs were verified against Crossref or DataCite on 2026-09-23. Venues that do "
          "not assign Crossref DOIs (PMLR, NeurIPS, JMLR, USENIX) are marked as such rather than "
          "left pending. The individual checks are recorded in Supplementary S24.")

ZH_OLD = ("说明：全部 DOI 已于 2026-09-16 通过 Crossref 核验。对不分配 Crossref DOI 的出版方"
          "（PMLR、NeurIPS、JMLR、USENIX），标注为无 DOI，而不再留待核验。逐条核验记录见补充材料 S24。")
ZH_NEW = ("说明：全部 DOI 已于 2026-09-23 通过 Crossref 或 DataCite 核验。对不分配 Crossref DOI 的出版方"
          "（PMLR、NeurIPS、JMLR、USENIX），标注为无 DOI，而不再留待核验。逐条核验记录见补充材料 S24。")


def fix(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise SystemExit(f"anchor not found exactly once in {path.name}: {text.count(old)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"updated {path.name}")


def main() -> None:
    fix(BASE / "English_SCI_Manuscript_v4.md", EN_OLD, EN_NEW)
    fix(BASE / "中文SCI论文_v4_重构版.md", ZH_OLD, ZH_NEW)
    print("REFERENCE_NOTE_FIXED")


if __name__ == "__main__":
    main()
