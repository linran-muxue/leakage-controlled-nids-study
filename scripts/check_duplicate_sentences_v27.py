"""Find sentences that survive twice in a manuscript.
A sentence-level duplicate is almost always an editing accident: a replacement
that left the old tail behind. One such pair survived eleven rounds (the
balanced-control training time in Section 5.2) because every earlier check
compared documents against each other rather than a document against itself.
"""
from __future__ import annotations
import re
import sys
from collections import defaultdict
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
SPLIT = re.compile(r"(?<=[.。！？!?])\s+")
NUMBER = re.compile(r"\d+(?:[.,]\d+)?")
def normalise(sentence: str) -> str:
    return re.sub(r"[\s，。；：、,.;:]+", "", sentence.strip().strip("*_ ")).lower()
PLACEHOLDERS = ("To be completed by the author", "待作者填写", "待填")
def collect(text: str) -> tuple[dict[str, list[int]], dict[str, str]]:
    seen: dict[str, list[int]] = defaultdict(list)
    samples: dict[str, str] = {}
    for number, line in enumerate(text.splitlines(), 1):
        if line.startswith(("|", "#", "!", "$$", "```")):
            continue
        for raw in SPLIT.split(line):
            sentence = raw.strip().strip("*_ ")
            if len(sentence) < 25:
                continue
            if any(marker in sentence for marker in PLACEHOLDERS):
                continue
            key = normalise(raw)
            seen[key].append(number)
            samples.setdefault(key, sentence)
    return seen, samples
def main() -> int:
    problems: list[str] = []
    for name in ("English_SCI_Manuscript_v4.md", "中文SCI论文_v4_重构版.md"):
        text = (BASE / name).read_text(encoding="utf-8")
        body = text.split("## References")[0].split("## 参考文献")[0]
        # the declarations block legitimately repeats "To be completed by the author"
        body = body.split("## Declarations")[0].split("## 声明")[0]
        seen, samples = collect(body)
        duplicates = {k: v for k, v in seen.items() if len(v) > 1}
        print(f"{name}: {len(seen)} distinct sentences, {len(duplicates)} repeated")
        for key, lines in list(duplicates.items())[:8]:
            print(f"    lines {lines}: {samples[key][:110]}")
        if duplicates:
            problems.append(f"{name}: {len(duplicates)} repeated sentence(s)")
        repeated_facts = []
        for number, line in enumerate(body.splitlines(), 1):
            if line.startswith(("|", "#", "!", "$$", "```")) or len(line) < 80:
                continue
            tokens = NUMBER.findall(line)
            # only data values repeat meaningfully; structural integers (section
            # numbers, fold counts, k values) legitimately do so
            tokens = [t for t in tokens if "." in t]
            pairs: dict[tuple[str, str], int] = {}
            for first, second in zip(tokens, tokens[1:]):
                pairs[(first, second)] = pairs.get((first, second), 0) + 1
            hits = [pair for pair, count in pairs.items() if count > 1]
            if hits:
                repeated_facts.append((number, hits, line))
        print(f"    paragraphs repeating a numeric pair: {len(repeated_facts)}")
        for number, hits, line in repeated_facts[:5]:
            print(f"      line {number}: {hits} | {line.strip()[:120]}")
        if repeated_facts:
            problems.append(f"{name}: {len(repeated_facts)} paragraph(s) repeat a numeric fact")
    print()
    if problems:
        for problem in problems:
            print(f"ISSUE {problem}")
        print("SENTENCE_DUPLICATION_FOUND")
        return 1
    print("NO_DUPLICATE_SENTENCES")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
