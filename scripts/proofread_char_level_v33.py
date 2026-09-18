"""Character- and word-level proofreading scan for both manuscripts.
Everything here is the layer below the other checks: invisible characters,
mixed widths, stray punctuation, repeated words, unbalanced brackets and
inconsistent unit spacing. Lines inside fenced blocks and display equations are
skipped, because mathematical notation legitimately contains sequences the
prose rules would flag.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
FILES = ["English_SCI_Manuscript_v4.md", "中文SCI论文_v4_重构版.md",
         "Cover_Letter_JISA_v4.md", "Highlights_v4.md"]
INVISIBLE = {"\u200b": "zero-width space", "\u200c": "ZWNJ", "\u200d": "ZWJ",
             "\ufeff": "BOM", "\u00a0": "non-breaking space", "\u2028": "line separator",
             "\u2029": "paragraph separator", "\t": "tab"}
ABBREV = re.compile(r"(et al|e\.g|i\.e|etc|vs|cf|Fig|Eq|No)\.", re.I)
FAILURES: list[str] = []
def text_lines(text: str) -> list[tuple[int, str]]:
    out, fenced = [], False
    for number, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced or line.lstrip().startswith("$$"):
            continue
        out.append((number, line))
    return out
def report(label: str, hits: list[str], strict: bool = True, limit: int = 6) -> bool:
    if not hits:
        return False
    print(f"  [{label}] {len(hits)} hit(s)")
    for item in hits[:limit]:
        print(f"      {item}")
    if len(hits) > limit:
        print(f"      ... and {len(hits) - limit} more")
    if strict:
        FAILURES.append(f"{label} ({len(hits)})")
    return True
def scan(name: str) -> int:
    text = (BASE / name).read_text(encoding="utf-8")
    body = text.split("## References")[0].split("## 参考文献")[0]
    english = name.startswith("English")
    chinese = name.startswith("中文")
    lines = text_lines(body)
    found = 0
    print(f"=== {name} ===")
    hits = [f"line {i}: {INVISIBLE[ch]} x{line.count(ch)}"
            for i, line in enumerate(text.splitlines(), 1) for ch in set(line) & set(INVISIBLE)]
    found += report("invisible characters", hits)
    hits = [f"line {i}: trailing whitespace" for i, line in enumerate(text.splitlines(), 1)
            if line != line.rstrip()]
    found += report("trailing whitespace", hits)
    hits = [f"line {i}: {m.group(0)}" for i, line in lines
            for m in re.finditer(r"[\uff10-\uff19\uff21-\uff3a\uff41-\uff5a]+", line)]
    found += report("full-width alphanumerics", hits)
    hits = []
    for i, line in lines:
        for m in re.finditer(r"\b([A-Za-z]{2,})\s+\1\b", line, flags=re.I):
            hits.append(f"line {i}: '{m.group(0)}'")
    found += report("repeated words", hits)
    hits = []
    for i, line in lines:
        cleaned = ABBREV.sub(lambda m: m.group(0)[:-1], line)
        leftover = re.findall(r"[,.;:]{2,}", cleaned)
        if leftover and "..." not in leftover:
            hits.append(f"line {i}: doubled punctuation {leftover[:3]}")
        if re.search(r"[A-Za-z\u4e00-\u9fff]\s+[,.;:]", line):
            hits.append(f"line {i}: space before punctuation")
        if re.search(r"[a-z]\s{2,}[a-zA-Z]", line):
            hits.append(f"line {i}: double space inside a sentence")
    found += report("punctuation and spacing", hits)
    hits = []
    for i, line in lines:
        for opener, closer in (("(", ")"), ("[", "]"), ("（", "）"), ("【", "】")):
            if line.count(opener) != line.count(closer):
                hits.append(f"line {i}: {opener}{closer} {line.count(opener)}/{line.count(closer)}")
        if line.count("**") % 2:
            hits.append(f"line {i}: odd number of '**'")
    found += report("unbalanced brackets or markers", hits)
    hits = []
    for i, line in lines:
        for m in re.finditer(r"\d(?:s|ms|MB|GB|px)\b", line):
            hits.append(f"line {i}: missing space before unit '{m.group(0)}'")
        for m in re.finditer(r"\d\s+%", line):
            hits.append(f"line {i}: space before percent '{m.group(0)}'")
    found += report("unit spacing", hits)
    variants = {"chi-square": "chi square", "leakage-controlled": "leakage controlled",
                "equal-weight": "equal weight", "near-duplicate": "near duplicate",
                "cross-fitting": "cross fitting"}
    hits = []
    for canonical, variant in variants.items():
        pattern = rf"\b{re.escape(variant)}\b\s+(forest|test|study|experiment|setting|splits?|" \
                  rf"evaluation|models?|voting|comparison|figure|table)"
        for m in re.finditer(pattern, body, flags=re.I):
            hits.append(f"'{m.group(0)}' should be '{canonical}'")
    found += report("hyphenation as a modifier", hits)
    if chinese:
        hits = [f"line {i}: {m.group(0)}" for i, line in lines
                for m in re.finditer(r"\d{1,3},\d{3}", line)]
        found += report("comma thousands separators in Chinese", hits)
        hits = []
        for i, line in lines:
            for m in re.finditer(r"[\u4e00-\u9fff]\s*[,;:?!]\s*[\u4e00-\u9fff]|[\u4e00-\u9fff][,;:?!]", line):
                if "$" in line[max(0, m.start() - 12):m.end() + 12]:
                    continue
                hits.append(f"line {i}: '{m.group(0)}'")
        found += report("ASCII punctuation against CJK", hits)
    print(f"  -> {found} categor(ies) with findings")
    return found
def main() -> int:
    total = sum(scan(name) for name in FILES)
    print()
    print(f"TOTAL_CATEGORIES_WITH_FINDINGS={total}")
    if FAILURES:
        for failure in FAILURES:
            print(f"ISSUE {failure}")
        print("CHAR_LEVEL_FINDINGS")
        return 1
    print("CHAR_LEVEL_OK")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
