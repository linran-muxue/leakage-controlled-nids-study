"""Re-sync the two audit documents with the artifacts they quote.

`论文自查表.md` and `遗漏问题审查报告.md` are shipped to the reviewer, and both
quote counts that are derived from other files:

* the number-traceability check now runs 69 assertions, but both documents still
  said 50;
* the DOI record was rebuilt (36 cited DOIs verified against Crossref or
  DataCite, 11 entries explicitly marked as having no DOI), while A3 still said
  "47 DOIs all verified via Crossref", which counts rows rather than DOIs.

Nothing here changes an experimental number; the counts are re-derived from the
artifacts and `check_selfcheck_claims_v1.py` keeps them tied together.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"


def counts() -> tuple[int, int, int, int]:
    import csv
    rows = list(csv.DictReader(
        open(ROOT / "results_review_v5" / "number_traceability.csv", encoding="utf-8-sig")))
    record = json.loads(
        (ROOT / "results_review_v5" / "doi_verification.json").read_text(encoding="utf-8"))
    verified = sum(1 for row in record if row["status"] == "ok")
    no_doi = sum(1 for row in record if row["status"] == "no-doi")
    return len(rows), len(record), verified, no_doi


def fix(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise SystemExit(f"anchor not found exactly once in {path.name}: {text.count(old)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"updated {path.name}")


def main() -> None:
    checks, refs, verified, no_doi = counts()
    selfcheck = BASE / "论文自查表.md"
    report = BASE / "遗漏问题审查报告.md"

    fix(selfcheck,
        f"`audit_number_traceability_v5.py`：50 项关键数字全部与源文件一致，零失配；",
        f"`audit_number_traceability_v5.py`：{checks} 项关键数字全部与源文件一致，零失配；")
    fix(selfcheck,
        "中英各 47/47 全覆盖，抽查 21 条零失配；**47 条 DOI 已全部通过 Crossref 核验**"
        "（含新增的 N-BaIoT 论文与数据集 DOI）（1 条补全、10 条确认为 "
        "PMLR/NeurIPS/JMLR/USENIX 无 DOI 并显式标注），待核验占位符清零",
        f"中英各 47/47 全覆盖，抽查 21 条零失配；{refs} 条条目中 **{verified} 条带 DOI 的条目"
        f"已全部通过 Crossref 或 DataCite 核验**（含新增的 N-BaIoT 论文与数据集 DOI，"
        f"数据集 DOI 走 DataCite），其余 {no_doi} 条经确认不分配 Crossref DOI 的出版方"
        "（PMLR/NeurIPS/JMLR/USENIX/JSTOR 等）已显式标注为无 DOI，待核验占位符清零")
    fix(selfcheck,
        "**自查日期**：2026-09-16",
        "**自查日期**：2026-09-16（此后各轮复审持续更新；最近一次更新 2026-09-24）")
    fix(report,
        "- `audit_number_traceability_v5.py`：**50 项关键数字全部与源文件一致，零失配。**",
        f"- `audit_number_traceability_v5.py`：**{checks} 项关键数字全部与源文件一致，零失配。**")

    print(f"counts used: traceability={checks}, references={refs}, "
          f"verified DOIs={verified}, entries without a DOI={no_doi}")
    print("SELFCHECK_COUNTS_FIXED")


if __name__ == "__main__":
    main()
