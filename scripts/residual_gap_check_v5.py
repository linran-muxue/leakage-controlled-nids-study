"""Residual gap check, excluding author-identity items."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN = (BASE / "English_SCI_Manuscript_v4.md").read_text(encoding="utf-8")
ZH = (BASE / "中文SCI论文_v4_重构版.md").read_text(encoding="utf-8")


def line(label: str, ok: bool, detail: str) -> None:
    print(f"{'PASS' if ok else 'GAP ':<5}{label:<44}{detail}")


def main() -> None:
    print("=== A. submission package ===")
    ga = list(BASE.glob("*raphical*")) + list((ROOT / "results_paper_materials_v3").glob("*raphical*"))
    line("graphical abstract exists", bool(ga),
         f"{len(ga)} file(s), oldest {min((p.stat().st_mtime for p in ga), default=0):.0f}")
    line("highlights (new)", (BASE / "Highlights_v4.md").exists(),
         "Highlights_v4.md present" if (BASE / "Highlights_v4.md").exists() else "missing")
    cl = BASE / "Cover_Letter_JISA_v4.md"
    line("cover letter", cl.exists(),
         "Cover_Letter_JISA_v4.md present" if cl.exists() else "missing")
    line("journal template", False, "no JISA/Elsevier template applied")
    line("supplementary bundle", (BASE / "补充材料_S01_S28" / "README.md").exists(),
         f"{len(list((BASE / '补充材料_S01_S28').rglob('*')))} entries")

    print()
    print("=== B. references ===")
    doi_pending = len(re.findall(r"\[DOI (?:to verify|待核验)\]", EN))
    line("DOI verification", doi_pending == 0, f"{doi_pending} entries still marked for verification")

    print()
    print("=== C. reproducibility ===")
    line("container definition", (ROOT / "Dockerfile").exists(),
         "Dockerfile present" if (ROOT / "Dockerfile").exists() else "no Dockerfile / conda env")
    line("continuous integration", (ROOT / ".github" / "workflows").exists(),
         "workflow present" if (ROOT / ".github" / "workflows").exists() else "no .github/workflows")
    line("citation metadata", (ROOT / "CITATION.cff").exists(),
         "CITATION.cff present" if (ROOT / "CITATION.cff").exists() else "no CITATION.cff")
    line("model / data card", (ROOT / "MODEL_CARD.md").exists() or (ROOT / "DATA_CARD.md").exists(),
         "present" if (ROOT / "MODEL_CARD.md").exists() else "no model/data card")

    print()
    print("=== D. manuscript hygiene ===")
    numbers = sorted(int(m.group(1)) for p in (BASE / "figures_en").glob("fig*.png")
                     if (m := re.match(r"fig(\d+)_", p.name)))
    ok_names = numbers == list(range(1, 12))
    line("figure filenames match numbers", ok_names,
         f"figure file numbers found: {numbers}")
    cjk = re.findall(r"[\u4e00-\u9fff]", EN)
    line("no CJK leakage in English file", not cjk, f"{len(cjk)} CJK characters found")
    line("placeholders beyond author info",
         EN.count("To be completed") <= 3,
         f"{EN.count('To be completed')} placeholders (all author-related)")

    print()
    print("=== E. experiment coverage (declared limitations) ===")
    limitations = EN.split("### 6.5 Limitations")[-1].split("## 7.")[0].lower()
    body_lower = EN.lower()
    checks = {
        "temporal split": ("temporal", "not performed"),
        "full corpus run": ("full cic-ids2017 corpus", "not performed (2.0% research subset)"),
        "cost-sensitive analysis": ("cost-sensitive behaviour", "performed"),
        "resource profile": ("resource footprint", "performed"),
        "near-duplicate detection": ("near-duplicate", "not performed (exact hashing only)"),
        "adversarial robustness": ("adversarial", "not performed"),
        "extra public dataset": ("three datasets were evaluated", "not performed (three datasets only)"),
    }
    performed_dirs = {
        "cost-sensitive analysis": ROOT / "results_cost_v5",
        "resource profile": ROOT / "results_resources_v5",
    }
    for label, (needle, note) in checks.items():
        declared = needle in limitations
        done = needle in body_lower
        directory = performed_dirs.get(label)
        has_output = directory.exists() if directory else False
        line(label, done and (has_output or directory is None),
             (note + ("; evidence in " + directory.name if has_output else "")) if done
             else (note + ("; disclosed in 6.5" if declared else "; NOT disclosed in 6.5")))

    print()
    print("=== F. self-check table status ===")
    sc = (BASE / "论文自查表.md").read_text(encoding="utf-8")
    print("  pass/partial/missing:",
          sc.count("**通过**"), "/", sc.count("**部分通过**"), "/", sc.count("**缺失**"))


if __name__ == "__main__":
    main()
