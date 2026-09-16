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
    ("reference annotations", ["scripts/check_noDOI_notes_v5.py"], ("CHECK",)),
    ("cross-document audit", ["scripts/fresh_audit_v7.py"], ("ISSUE",)),
    ("language consistency", ["scripts/language_audit_v6.py"], ("MIXED",)),
    ("body hygiene", ["scripts/body_hygiene_check_v9.py"], ("ISSUE", "BODY_HYGIENE_FAILED")),
    ("cross-language numbers", ["scripts/cross_language_number_diff_v10.py"], ("MISMATCH",)),
    ("self-check counts", ["scripts/verify_selfcheck_counts_v7.py"], ("SELFCHECK_MISMATCH",)),
    ("publication manifest", ["scripts/check_publication_manifest_v12.py"], ("MANIFEST_MISMATCH",)),
    ("submission front matter", ["scripts/check_aux_documents_v13.py"], ("AUX_MISMATCH",)),
]


def run(label: str, args: list[str]) -> tuple[str, str]:
    try:
        proc = subprocess.run([PY] + args, capture_output=True, text=True,
                              cwd=ROOT, timeout=900, errors="replace")
        return proc.stdout, proc.stderr
    except Exception as exc:  # pragma: no cover
        return "", f"{label} failed to run: {exc}"


def main() -> int:
    failures = []
    for label, args, markers in CHECKS:
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
    print("GATE_PASSED  all checks green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
