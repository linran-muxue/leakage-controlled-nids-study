"""Number the display equations and reference them from the text.
JISA asks for equations to be numbered in order of appearance; the manuscript
had five unnumbered display equations and no in-text references to them. The
numbers sit inside the $$ delimiters so the DOCX renderer still recognises the
block as a display equation.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
BLOCK = re.compile(r"^(\$\$.+?)\$\$(\s*)$")
EN_TEXT_EDITS = [
    ("**Step 3, conditional weights and calibration.** The fusion weights are",
     "**Step 3, conditional weights and calibration.** The fusion weights and the fused "
     "posterior are given by Eq. (1):"),
    ("Because every expert posterior lies on the simplex (||p_e||_1 = 1),",
     "Because every expert posterior lies on the simplex (||p_e||_1 = 1), the fused posterior "
     "moves by at most the bound of Eq. (2):"),
    ("Both are directly checkable.", "Equations (3) and (4) are both directly checkable."),
    ("The corresponding observable is the normalised weight entropy",
     "The corresponding observable is the normalised weight entropy, Eq. (5)"),
]
ZH_TEXT_EDITS = [
    ("**第三步，条件加权与校准。** 融合权重按下式给出：",
     "**第三步，条件加权与校准。** 融合权重与融合后验由式(1)给出："),
    ("由于每个专家的后验位于概率单纯形上（$\\|p_e\\|_1=1$），有",
     "由于每个专家的后验位于概率单纯形上（$\\|p_e\\|_1=1$），融合后验的位移不超过式(2)的上界："),
    ("两者都可直接检验。", "式(3)与式(4)都可直接检验。"),
    ("对应的可观测判据是归一化权重熵：", "对应的可观测判据是归一化权重熵（式(5)）："),
]
def number(text: str) -> tuple[str, int]:
    count = 0
    out = []
    for line in text.splitlines():
        match = BLOCK.match(line)
        if match:
            count += 1
            out.append(f"{match.group(1)}  ({count})$$")
        else:
            out.append(line)
    return "\n".join(out) + "\n", count
def apply_text(text: str, edits: list[tuple[str, str]], label: str) -> str:
    for old, new in edits:
        if old in text:
            text = text.replace(old, new, 1)
        else:
            print(f"  [{label}] anchor absent: {old[:56]}...")
    return text
def main() -> None:
    for name, edits, label in (("English_SCI_Manuscript_v4.md", EN_TEXT_EDITS, "EN"),
                               ("中文SCI论文_v4_重构版.md", ZH_TEXT_EDITS, "ZH")):
        path = BASE / name
        text = path.read_text(encoding="utf-8")
        if re.search(r"\$\$.+\(\d\)\$\$", text):
            print(f"{name}: already numbered")
            continue
        text = apply_text(text, edits, label)
        text, count = number(text)
        path.write_text(text, encoding="utf-8")
        print(f"{name}: {count} equation(s) numbered")
if __name__ == "__main__":
    main()
