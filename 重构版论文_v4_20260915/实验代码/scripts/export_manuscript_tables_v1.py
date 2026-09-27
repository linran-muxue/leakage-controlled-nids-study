"""Export the eight main tables as editable CSV files.

The manuscripts carry their tables as Markdown, which is fine for reading and
for the Word build but awkward to hand to a production editor, who usually
wants each table as a separate file.  This script parses the numbered table
captions out of the English manuscript and writes one CSV per table (the two
panels of Table 4 become table4a and table4b), plus an index that records each
caption and its panel marker.

The Chinese manuscript carries the same numbers - the cross-language check
enforces that - so a single export is enough.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
OUT = ROOT / "results_publication_final" / "main_tables"
EN = (BASE / "English_SCI_Manuscript_v4.md").read_text(encoding="utf-8")
CAPTION = re.compile(r"^\*\*Table (\d+)\.\s*(.+?)\*\*\s*$", re.M)
PANEL = re.compile(r"^\(([ab])\)\s*(.+)$")


STOPWORDS = {"the", "a", "an", "on", "of", "for", "and", "in", "to", "with"}


def slug(text: str) -> str:
    """A file-name slug that keeps the caption's meaning and drops filler.

    The caption is cut at its first colon (the part after it is a sentence, not
    a title) and leading/trailing stopwords are removed, so Table 7 becomes
    "cic_ids2017_scale_ladder" rather than the truncated "..._the".
    """
    head = text.split(":")[0]
    words = [w for w in re.sub(r"[^a-z0-9]+", " ", head.lower()).split() if w]
    while words and words[0] in STOPWORDS:
        words.pop(0)
    while words and words[-1] in STOPWORDS:
        words.pop()
    return "_".join(words[:6])


def parse_tables() -> list[tuple[str, str, str, list[list[str]]]]:
    """Every numbered table as (number, panel marker, caption, rows).

    Exposed so the packaged CSVs can be compared back to the manuscript they
    were exported from without a second parser.
    """
    lines = EN.splitlines()
    captions = [(index, match) for index, line in enumerate(lines)
                if (match := CAPTION.match(line))]
    if len(captions) != 8:
        raise SystemExit(f"expected eight numbered tables, found {len(captions)}")
    parsed_tables = []
    for position, (start, match) in enumerate(captions):
        number, caption = match.group(1), match.group(2).strip()
        stop = captions[position + 1][0] if position + 1 < len(captions) else len(lines)
        # a table ends at the first line that is neither a row, a panel marker
        # nor blank - otherwise the parser runs on into the next prose block and
        # then into the supplementary index at the end of the manuscript
        block = []
        for line in lines[start + 1:stop]:
            if line.startswith("|") or PANEL.match(line) or not line.strip() \
                    or line.strip().startswith("(a)") or line.strip().startswith("(b)"):
                block.append(line)
                continue
            if block and any(candidate.startswith("|") for candidate in block):
                break
            block.append(line)
        panels: list[tuple[str, list[str]]] = []
        current_marker, current = "", []
        for line in block:
            panel = PANEL.match(line)
            if panel:
                if current:
                    panels.append((current_marker, current))
                current_marker, current = panel.group(1), []
                continue
            if line.startswith("|"):
                current.append(line)
        if current:
            panels.append((current_marker, current))
        if not panels:
            raise SystemExit(f"table {number} has no rows")
        for marker, rows in panels:
            parsed = []
            for row in rows:
                cells = [c.strip().replace("**", "") for c in row.strip("|").split("|")]
                if set("".join(cells)) <= set("-: "):
                    continue
                parsed.append(cells)
            parsed_tables.append((number, marker, caption, parsed))
    return parsed_tables


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    index_rows = []
    for number, marker, caption, parsed in parse_tables():
            suffix = marker or ""
            name = f"table{number}{suffix}_{slug(caption)}.csv"
            with (OUT / name).open("w", encoding="utf-8-sig", newline="") as handle:
                csv.writer(handle).writerows(parsed)
            index_rows.append((number, marker, caption, name, len(parsed) - 1))
            print(f"  {name:<58}{len(parsed) - 1} data row(s)")

    readme = ["# 正文主表导出 / Main tables (exported from the English manuscript)", "",
              "| 表 | 面板 | 标题 | 文件 | 数据行 |", "|---|---|---|---|---:|"]
    for number, marker, caption, name, rows in index_rows:
        readme.append(f"| {number} | {marker or '-'} | {caption} | {name} | {rows} |")
    readme += ["",
               "每个单元格的字面值与正文一致；中文稿使用同一组数字，"
               "由 `scripts/cross_language_number_diff_v10.py` 与 "
               "`scripts/audit_main_tables_v1.py` 持续核验。"]
    (OUT / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")
    print(f"wrote {len(index_rows)} CSV file(s) and README.md to "
          f"{OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
