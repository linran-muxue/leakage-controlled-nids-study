"""Fix the wording and punctuation defects found by the character-level sweep.
The substantive one is terminological: the Chinese manuscript called the
cross-fitted out-of-fold probabilities 袋外 (out-of-bag), which is a different
quantity in ensemble learning. The rest are width and symbol consistency.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
ZH = BASE / "中文SCI论文_v4_重构版.md"
EN = BASE / "English_SCI_Manuscript_v4.md"
ZH_EDITS = [
    # out-of-fold (cross-fitting) is 折外, not 袋外 (out-of-bag)
    ("袋外概率", "折外概率"),
    ("完整袋外表", "完整折外表"),
    # Chinese list should use the Chinese enumeration comma
    ("全量, 仅熵, 仅边距", "全量、仅熵、仅边距"),
    # a Chinese sentence ends with a full-width period
    ("*证明.*", "*证明。*"),
    # keep the four-view set identical to the one defined in Section 4.1
    ("q ∈ {full, chi2, MI, ANOVA}", "q ∈ {full, χ², MI, ANOVA}"),
]
EN_EDITS = [
    ("q in {full, chi2, MI, ANOVA}", "q in {full, chi-square, MI, ANOVA}"),
]
def apply(path: Path, edits: list[tuple[str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new in edits:
        count = text.count(old)
        if count:
            text = text.replace(old, new)
        print(f"  [{path.name}] '{old[:36]}' -> '{new[:36]}': {count} replacement(s)")
    path.write_text(text, encoding="utf-8")
def main() -> None:
    apply(ZH, ZH_EDITS)
    apply(EN, EN_EDITS)
if __name__ == "__main__":
    main()
