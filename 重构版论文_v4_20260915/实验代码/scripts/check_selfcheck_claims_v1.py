"""Tie the counts quoted in the audit documents to the artifacts.

The self-check table and the gap report are shipped to the reviewer and both
quote numbers that other files produce: how many assertions the number
traceability check runs, and how many reference DOIs were verified.  Both had
drifted (50 assertions quoted against 69 actually run; "47 DOIs verified"
quoted against a record of 36 DOIs plus 11 entries with no DOI), and nothing
noticed because the existing verifier only counted the S-items.

This check re-derives every one of those figures and fails if a document drifts
again.  It complements verify_selfcheck_counts_v7.py, which keeps the
pass/partial/missing totals honest.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
SELFCHECK = BASE / "论文自查表.md"
REPORT = BASE / "遗漏问题审查报告.md"
TRACE = ROOT / "results_review_v5" / "number_traceability.csv"
DOI = ROOT / "results_review_v5" / "doi_verification.json"

problems: list[str] = []


def main() -> int:
    rows = list(csv.DictReader(TRACE.open(encoding="utf-8-sig")))
    record = json.loads(DOI.read_text(encoding="utf-8"))
    checks = len(rows)
    refs = len(record)
    verified = sum(1 for row in record if row["status"] == "ok")
    no_doi = sum(1 for row in record if row["status"] == "no-doi")
    if verified + no_doi != refs:
        problems.append(f"the DOI record has unclassified rows: {refs} != {verified} + {no_doi}")

    selfcheck = SELFCHECK.read_text(encoding="utf-8")
    report = REPORT.read_text(encoding="utf-8")

    quoted = re.findall(r"：(\d+) 项关键数字全部与源文件一致", selfcheck + report)
    if sorted(set(quoted)) != sorted({str(checks)}):
        problems.append(f"documents quote {sorted(set(quoted))} traceability assertions, "
                        f"the artifact has {checks}")
    if "47 条 DOI" in selfcheck:
        problems.append("the self-check table still counts rows instead of DOIs")
    for needle in (f"{verified} 条带 DOI 的条目已全部通过 Crossref 或 DataCite 核验",
                   f"其余 {no_doi} 条经确认不分配 Crossref DOI 的出版方",
                   f"{refs} 条条目中"):
        if needle not in selfcheck:
            problems.append(f"the self-check table no longer states {needle!r}")

    for name in ("English_SCI_Manuscript_v4.md", "中文SCI论文_v4_重构版.md"):
        text = (BASE / name).read_text(encoding="utf-8")
        if "DataCite" not in text:
            problems.append(f"{name} no longer names DataCite in the reference note")

    print(f"traceability assertions {checks} | reference entries {refs} "
          f"| verified DOIs {verified} | entries without a DOI {no_doi}")
    if problems:
        for problem in problems:
            print(f"ISSUE {problem}")
        print("SELFCHECK_CLAIMS_FAILED")
        return 1
    print("SELFCHECK_CLAIMS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
