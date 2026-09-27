"""Structural consistency audit of the bilingual v4/v5 manuscripts."""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
DOCS = {
    "zh": BASE / "中文SCI论文_v4_重构版.md",
    "en": BASE / "English_SCI_Manuscript_v4.md",
}


def report(name: str, path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    print(f"=== {name}: {path.name} ===")

    # Figure captions actually present, in order of appearance
    caps = [(i + 1, m.group(1)) for i, line in enumerate(lines)
            if (m := re.match(r"!\[(?:Figure|图)\s*(\d+)", line))]
    numbers = [int(n) for _, n in caps]
    print("figure captions:", numbers)
    print("figure order strictly increasing:", numbers == sorted(numbers))
    print("figure numbering complete 1..11:", sorted(numbers) == list(range(1, 12)))
    dup = [n for n, c in Counter(numbers).items() if c > 1]
    print("duplicate figure numbers:", dup or "none")

    # In-text references
    fig_refs = sorted({int(m) for m in re.findall(r"(?:Figure|图)\s*(\d+)", text)})
    print("figure numbers referenced anywhere:", fig_refs)
    missing_refs = [n for n in fig_refs if n not in numbers]
    print("referenced but not captioned:", missing_refs or "none")

    # Tables
    table_caps = re.findall(r"^\*\*(Table|表)\s*(\d+[a-z]?)", text, flags=re.M)
    print("table captions:", [t[0] + " " + t[1] for t in table_caps])
    table_refs = sorted({m for m in re.findall(r"(?:Table|表)\s*(\d+[a-z]?)", text)})
    print("table numbers referenced:", table_refs)

    # Placeholders and TODO markers
    placeholders = re.findall(r"(To be completed|待作者|TBD|TODO|XXX|PLACEHOLDER)", text, flags=re.I)
    print("placeholder markers:", Counter(placeholders) or "none")

    # Images referenced vs files present
    img_paths = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)
    absent = [p for p in img_paths if not (path.parent / p).exists()]
    print("referenced images missing on disk:", absent or "none")

    # Reference list size
    refs = re.findall(r"^\d+\.\s+[A-Z]", text, flags=re.M)
    print("numbered reference entries:", len(refs))
    print("references marked DOI to verify:", text.count("[DOI to verify]") + text.count("[DOI 待核验]"))
    print()


def main() -> None:
    for name, path in DOCS.items():
        report(name, path)

    zh = DOCS["zh"].read_text(encoding="utf-8")
    en = DOCS["en"].read_text(encoding="utf-8")
    print("=== cross-language phrase checks ===")
    for phrase in ["five independent measurements", "三组独立测量"]:
        print(f"  '{phrase}' occurrences: zh={zh.count(phrase)} en={en.count(phrase)}")
    for figure_word in ["Figure 10", "Figure 11", "图 10", "图 11"]:
        print(f"  '{figure_word}' occurrences: zh={zh.count(figure_word)} en={en.count(figure_word)}")


if __name__ == "__main__":
    main()
