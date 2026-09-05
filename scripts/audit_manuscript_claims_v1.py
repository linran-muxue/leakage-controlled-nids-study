"""Static audit for stale numbers, unsupported table references and claim scope."""
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "results_paper_materials_v3" / "full_paper_body_v6_data_processing.md"


def main() -> None:
    text = MANUSCRIPT.read_text(encoding="utf-8")
    errors: list[str] = []
    if "表A36" in text or "表A43" in text:
        errors.append("stale table reference A36/A43")
    if "95.97%" in text or "96.05%" in text:
        errors.append("stale performance number")
    headings = re.findall(r"^### (\d+\.\d+) ", text, flags=re.M)
    if len(headings) != len(set(headings)):
        errors.append("duplicate subsection heading")
    if "CIC-IDS2017全量性能" in text and "不能外推" not in text:
        errors.append("CIC full-data extrapolation warning missing")
    if "完全独立外部验证" in text and "不能称" not in text:
        errors.append("UNSW independence limitation missing")
    refs = [int(x) for x in re.findall(r"^\[(\d+)\]", text, flags=re.M)]
    if refs and refs != list(range(1, max(refs) + 1)):
        errors.append("reference numbering gap")
    if errors:
        raise SystemExit("MANUSCRIPT_AUDIT_FAIL: " + "; ".join(errors))
    print(f"MANUSCRIPT_AUDIT_OK headings={len(headings)} references={len(refs)}")


if __name__ == "__main__":
    main()
