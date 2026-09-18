"""Replace the Chinese manuscript's inline LaTeX with plain-text notation.
The English manuscript writes inline mathematics as text, so the Chinese copy
was the only place leaving raw LaTeX in the Word file. The five display
equations are converted to native Word equations separately.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
ZH_PATH = ROOT / "重构版论文_v4_20260915" / "中文SCI论文_v4_重构版.md"
EDITS = [
    (r"$\bar p(x)=\frac{1}{Q}\sum_e p_e(y\mid x)$", "p̄(x) = (1/Q) Σ_e p_e(y|x)"),
    (r"$p_w(x)=\sum_e w_e(x)\,p_e(y\mid x)$", "p_w(x) = Σ_e w_e(x) p_e(y|x)"),
    (r"$\|p_e\|_1=1$", "‖p_e‖₁ = 1"),
    (r"$2\Delta(x)<m(x)$", "2Δ(x) < m(x)"),
    (r"$\Delta(x)$", "Δ(x)"),
    (r"$\bar p$", "p̄"),
    (r"$C\in\{0.01,0.1,1,10\}$", "C ∈ {0.01, 0.1, 1, 10}"),
    (r"$\in\{3,5,10\}$", "∈ {3, 5, 10}"),
    (r"$\in\{$", "∈ {"),
    (r"$\}$", "}"),
]
def main() -> None:
    text = ZH_PATH.read_text(encoding="utf-8")
    applied = 0
    for old, new in EDITS:
        if old in text:
            applied += text.count(old)
            text = text.replace(old, new)
        else:
            print(f"  anchor absent: {old[:48]}")
    ZH_PATH.write_text(text, encoding="utf-8")
    print(f"inline LaTeX spans replaced: {applied}")
if __name__ == "__main__":
    main()
