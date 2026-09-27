"""Check the numbers baked into the figures against the manuscripts.
Figure annotations are the one place a stale value is invisible to every
text-level check: the number lives inside a PNG. The builders keep those
numbers in string literals, so they can be extracted and compared.
"""
from __future__ import annotations
import ast
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
SCRIPTS = {
    "scripts/build_figures_en_v5.py": "English_SCI_Manuscript_v4.md",
    "scripts/build_restructured_figures_v4.py": "中文SCI论文_v4_重构版.md",
    "scripts/build_graphical_abstract_v5.py": "English_SCI_Manuscript_v4.md",
}
DECIMAL = re.compile(r"\d+\.\d{2,6}")
INTEGER = re.compile(r"\b\d{1,3}(?:[, ]\d{3})+\b|\b\d{4,7}\b")
# style parameters and colours are not data annotations
NOISE = re.compile(r"(pad=|rounding_size=|#[0-9a-fA-F]{6}|linewidth|alpha=|dpi=|figsize|"
                   r"fontsize|0x[0-9a-fA-F]+)")
def data_literals(literal: str) -> list[str]:
    kept = []
    for piece in literal.split("\n"):
        if NOISE.search(piece):
            continue
        kept.append(piece)
    return kept
def tokens(text: str) -> set[str]:
    return {t.replace(",", "").replace(" ", "") for t in DECIMAL.findall(text) + INTEGER.findall(text)}
def literals(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and any(c.isdigit() for c in node.value):
            found.append(node.value)
        elif isinstance(node, ast.JoinedStr):
            for part in node.values:
                if isinstance(part, ast.Constant) and isinstance(part.value, str) and any(c.isdigit() for c in part.value):
                    found.append(part.value)
    return found
def main() -> int:
    problems: list[str] = []
    for script, manuscript in SCRIPTS.items():
        path = ROOT / script
        if not path.exists():
            problems.append(f"{script} missing")
            continue
        known = tokens((BASE / manuscript).read_text(encoding="utf-8"))
        unknown: dict[str, str] = {}
        for literal in literals(path):
            for piece in data_literals(literal):
                for token in tokens(piece):
                    if token not in known:
                        unknown.setdefault(token, piece.replace("\n", " ")[:70])
        print(f"{script} -> {manuscript}: {len(unknown)} number(s) not present in the manuscript")
        for token, context in sorted(unknown.items()):
            print(f"    {token:<10} {context}")
        if unknown:
            problems.append(f"{script}: {sorted(unknown)}")
    print()
    if problems:
        for problem in problems:
            print(f"ISSUE {problem}")
        print("FIGURE_ANNOTATION_MISMATCH")
        return 1
    print("FIGURE_ANNOTATIONS_OK")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
