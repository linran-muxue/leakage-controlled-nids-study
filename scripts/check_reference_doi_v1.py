"""Tie the shipped DOI verification record to the reference list.

Supplementary S24 shipped a record generated when the list had 45 entries: after
refs 17 and 18 were inserted, every later entry was numbered two too low and the
record carried six DOIs that appear nowhere in the manuscript. This check
re-derives the reference list from both manuscripts and fails whenever the
record drifts from it again.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from assemble_supplementary_v5 import ITEMS  # noqa: E402

BASE = ROOT / "重构版论文_v4_20260915"
problems: list[str] = []


def normalize(doi: str) -> str:
    return str(doi).strip().rstrip(".").lower()


def references(name: str, marker: str) -> dict[int, tuple[str, str]]:
    block = (BASE / name).read_text(encoding="utf-8").split(marker)[-1]
    found: dict[int, tuple[str, str]] = {}
    for number, entry in re.findall(r"^(\d+)\.\s+(.*)$", block, flags=re.M):
        match = re.search(r"DOI:\s*(10\.\S+?)\.?\s*$", entry.strip())
        found[int(number)] = (entry, normalize(match.group(1)) if match else "")
    return found


def main() -> int:
    record_path = ROOT / ITEMS["S24"][1][0]
    record = json.loads(record_path.read_text(encoding="utf-8"))
    rows = {int(row["ref"]): row for row in record}
    en = references("English_SCI_Manuscript_v4.md", "## References")
    zh = references("中文SCI论文_v4_重构版.md", "## 参考文献")

    if not en or not zh:
        problems.append(f"could not parse the reference lists (en={len(en)}, zh={len(zh)})")
    if sorted(rows) != sorted(en):
        problems.append(f"record covers refs {sorted(rows)}, the manuscript has {sorted(en)}")
    for number, (entry, doi) in en.items():
        row = rows.get(number)
        if row is None:
            continue
        if normalize(row.get("cited_doi", "")) != doi:
            problems.append(f"ref {number}: record DOI {row.get('cited_doi')!r} != manuscript {doi!r}")
        status = row.get("status")
        if status in ("ok", "check") and not doi:
            problems.append(f"ref {number}: status {status} although the entry cites no DOI")
        if status not in ("ok", "check", "unresolved", "no-doi"):
            problems.append(f"ref {number}: unknown status {status!r}")
        if status == "no-doi" and doi:
            problems.append(f"ref {number}: status {status} although the entry cites {doi}")
        if status == "ok" and float(row.get("title_overlap", 0.0)) < 0.6:
            problems.append(f"ref {number}: status ok with title_overlap {row.get('title_overlap')}")
        if not row.get("matched_by") and status != "no-doi" and status != "unresolved":
            problems.append(f"ref {number}: status {status} without a registry match")
        if row.get("matched_by") == "doi" and row.get("registry") not in ("crossref", "datacite"):
            problems.append(f"ref {number}: matched by DOI but registry is {row.get('registry')!r}")

    en_dois = {doi for _, doi in en.values() if doi}
    zh_dois = {doi for _, doi in zh.values() if doi}
    if en_dois != zh_dois:
        problems.append("the two manuscripts cite different DOI sets: "
                        f"en-only {sorted(en_dois - zh_dois)}, zh-only {sorted(zh_dois - en_dois)}")
    record_dois = {normalize(row.get("cited_doi", "")) for row in record if row.get("cited_doi")}
    if record_dois != en_dois:
        problems.append("the record and the manuscript disagree on which entries carry a DOI: "
                        f"record-only {sorted(record_dois - en_dois)}, "
                        f"manuscript-only {sorted(en_dois - record_dois)}")

    counts: dict[str, int] = {}
    for row in record:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    summary = ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))
    print(f"record: {len(record)} entries, {len(en_dois)} DOIs ({summary})")
    print("needs manual check:", [r["ref"] for r in record if r["status"] == "check"] or "none")
    print("unresolved:", [r["ref"] for r in record if r["status"] == "unresolved"] or "none")
    if problems:
        for problem in problems:
            print(f"ISSUE {problem}")
        print("REFERENCE_DOI_FAILED")
        return 1
    print("REFERENCE_DOI_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
