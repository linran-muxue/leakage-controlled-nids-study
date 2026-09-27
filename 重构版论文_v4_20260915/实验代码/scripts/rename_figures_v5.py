"""Align figure filenames with figure numbers across both languages and the generators."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

MAPPING = {
    "fig11_margin_bound": "fig6_margin_bound",
    "fig10_diversity_dose_response": "fig7_diversity_dose_response",
    "fig6_protocol_sensitivity": "fig8_protocol_sensitivity",
    "fig7_external_class_f1": "fig9_external_class_f1",
    "fig8_calibration_robustness": "fig10_calibration_robustness",
    "fig9_latency": "fig11_latency",
}

SCRIPTS = ["scripts/build_restructured_figures_v4.py", "scripts/build_v5_figures.py",
           "scripts/build_figures_en_v5.py"]
MANUSCRIPTS = ["重构版论文_v4_20260915/中文SCI论文_v4_重构版.md",
               "重构版论文_v4_20260915/English_SCI_Manuscript_v4.md"]


def rename_files(folder: Path) -> int:
    moved = 0
    for old, new in MAPPING.items():
        src = folder / f"{old}.png"
        if not src.exists():
            continue
        tmp = folder / f"__tmp_{new}.png"
        src.rename(tmp)
        tmp.rename(folder / f"{new}.png")
        moved += 1
    return moved


def rewrite(path: Path, applied: int) -> int:
    text = path.read_text(encoding="utf-8")
    for old, new in MAPPING.items():
        if old in text:
            text = text.replace(old, new)
            applied += 1
    path.write_text(text, encoding="utf-8")
    return applied


def main() -> None:
    for folder in ("figures", "figures_en"):
        n = rename_files(BASE / folder)
        print(f"renamed in {folder}: {n}")
    for rel in SCRIPTS + MANUSCRIPTS:
        path = ROOT / rel
        if path.exists():
            count = rewrite(path, 0)
            print(f"updated references in {rel}: {count}")


if __name__ == "__main__":
    main()
