"""Static audit for stale numbers, unsupported table references and claim scope."""
from __future__ import annotations

import re
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "results_paper_materials_v3" / "english_sci_manuscript_final.md"


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
    refs = re.findall(r"^\[(\d+)\]", text, flags=re.M)
    if refs:
        errors.append("unexpected numeric reference style in author-year manuscript")
    if "Table 1" not in text or "Figure 1" not in text:
        errors.append("canonical manuscript missing core table/figure citation")
    if "3,365" not in text or "balanced research subset" not in text:
        errors.append("CIC balanced-subset scope missing")
    for stale in ("0.14725", "0.01419", "0.02104", "10.48%", "74.7%", "corrected v4 protocol"):
        if stale in text:
            errors.append(f"stale CFRG result value: {stale}")
    for stale_path in ("results_cfrg_cic_v1", "results_cfrg_nsl_v1", "results_cfrg_open_set_v4", "results_cfrg_unsw_v1"):
        if stale_path in text:
            errors.append(f"stale canonical result path: {stale_path}")
    if "not as direct evidence of cross-dataset transfer" not in text:
        errors.append("external-benchmark boundary missing")
    if "No test-row argmax changed" in text:
        errors.append("stale gate diagnostic: verified predictions contain one changed argmax per locked seed")
    manifest = json.loads((ROOT / "results_publication_final" / "MANIFEST.json").read_text(encoding="utf-8"))
    release_tag = manifest.get("public_release_tag")
    if release_tag and f"release {release_tag}" not in text:
        errors.append(f"manuscript release tag does not match manifest: {release_tag}")
    supplement = ROOT / "results_publication_final" / "supplementary"
    missing_supplements = [index for index in range(1, 16) if not list(supplement.glob(f"S{index}_*.csv"))]
    if missing_supplements:
        errors.append(f"missing canonical supplementary files: {missing_supplements}")
    if errors:
        raise SystemExit("MANUSCRIPT_AUDIT_FAIL: " + "; ".join(errors))
    print(f"MANUSCRIPT_AUDIT_OK headings={len(headings)} references={len(refs)}")


if __name__ == "__main__":
    main()
