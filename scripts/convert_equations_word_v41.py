"""Convert the five display equations into native Word equations (OMML).
The DOCX is built from Markdown, so the equations arrive as LaTeX source text.
JISA asks for editable formulas, and Word can build a real equation from
UnicodeMath linear input. This post-processing step runs after the DOCX build
and before any render check.

Usage:  python scripts/convert_equations_word_v41.py [--target path.docx]
        Without --target it converts both manuscripts in place.
"""
from __future__ import annotations
import argparse
import shutil
import sys
from pathlib import Path
import zipfile
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

# (marker that identifies the paragraph, UnicodeMath to build, equation number)
EQUATIONS = [
    ("frac{\\exp[-r_e(x)]}", "w_e (x)=exp[-r_e (x)]/∑_(j=1)^Q exp[-r_j (x)] , "
                             "p(y|x)=∑_(e=1)^Q w_e (x) p_e (y|x)", "1"),
    ("left\\|p_w", "‖p_w-p̅‖_1 ≤∑_(e=1)^Q |w_e-1/Q|=:Δ(x)", "2"),
    ("1-H_{norm}(w)=\\frac{Q}", "1-H_norm (w)=Q/(2 log Q) ‖w-1/Q 1‖_2^2", "3"),
    ("Var}(\\delta)}{2\\log Q}", "1-H_norm (w)≈Var(δ)/(2 log Q)", "4"),
    ("H_{norm}(x)=-\\frac{1}", "H_norm (x)=-1/(log Q) ∑_(e=1)^Q w_e (x) log w_e (x)", "5"),
]


def maths_in(path: Path) -> int:
    """Count native equations by looking for m:oMath in document.xml."""
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("word/document.xml").decode("utf-8", "replace")
    return xml.count("<m:oMath>")


def convert(path: Path) -> int:
    import win32com.client as win32
    word = win32.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    document = word.Documents.Open(str(path.resolve()))
    replaced = 0
    try:
        for marker, linear, number in EQUATIONS:
            for paragraph in document.Paragraphs:
                text = paragraph.Range.Text or ""
                if marker in text:
                    # a Paragraph range ends with the paragraph mark; writing to
                    # it would merge this paragraph with the next one
                    rng = document.Range(paragraph.Range.Start, paragraph.Range.End - 1)
                    rng.Text = f"{linear}  ({number})"
                    math_range = document.Range(rng.Start, rng.Start + len(linear))
                    document.OMaths.Add(math_range)
                    document.OMaths(document.OMaths.Count).BuildUp()
                    paragraph.Alignment = 1  # centre
                    replaced += 1
                    break
        document.Save()
    finally:
        document.Close(False)
        word.Quit()
    return replaced


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default=None)
    args = parser.parse_args()
    targets = ([Path(args.target)] if args.target
               else [BASE / "English_SCI_Manuscript_v4.docx",
                     BASE / "中文SCI论文_v4_重构版.docx"])
    for path in targets:
        backup = path.with_suffix(".latex.docx")
        before = maths_in(path)
        if before >= len(EQUATIONS):
            print(f"{path.name}: already converted ({before} native equations)")
            continue
        shutil.copy2(path, backup)
        replaced = convert(path)
        after = maths_in(path)
        print(f"{path.name}: paragraphs converted={replaced} | native equations {before} -> {after}")
        if after <= before:
            shutil.copy2(backup, path)
            print(f"   reverted: no native equation was produced")
        if backup.exists():
            backup.unlink()


if __name__ == "__main__":
    main()
