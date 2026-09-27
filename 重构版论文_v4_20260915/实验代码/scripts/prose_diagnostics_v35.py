"""Flag prose that needs polishing, in priority order.
Reports only, so the edits stay deliberate: over-long sentences, filler
constructions, vague sentence openers, stacked hedges, passive padding and
repeated sentence starts inside one paragraph.
"""
from __future__ import annotations
import re
import sys
from collections import Counter
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
FILLER = [
    (r"\bin order to\b", "to"),
    (r"\bdue to the fact that\b", "because"),
    (r"\bit (?:should|must) be noted that\b", "(delete)"),
    (r"\bit is worth noting that\b", "(delete)"),
    (r"\ba (?:large |small )?number of\b", "many / few"),
    (r"\bprior to\b", "before"),
    (r"\bsubsequent to\b", "after"),
    (r"\bin the event that\b", "if"),
    (r"\bfor the purpose of\b", "to"),
    (r"\bat this point in time\b", "now"),
    (r"\bhas the ability to\b", "can"),
    (r"\bwith respect to\b", "for / on"),
    (r"\bin terms of\b", "(consider recasting)"),
    (r"\bas a matter of fact\b", "(delete)"),
    (r"\bvery\b|\bquite\b|\brather\b|\bsomewhat\b|\bfairly\b", "(weak intensifier)"),
    (r"\bmore or less\b", "(vague)"),
    (r"\bmay possibly\b|\bcould potentially\b|\bmight possibly\b", "(stacked hedge)"),
]
def sentences(paragraph: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(\[])", paragraph)
    return [p.strip() for p in parts if p.strip()]
def main() -> int:
    total_flags = 0
    for name in ("English_SCI_Manuscript_v4.md", "中文SCI论文_v4_重构版.md"):
        text = (BASE / name).read_text("utf-8")
        body = text.split("## References")[0].split("## 参考文献")[0]
        print(f"===== {name}")
        if not name.startswith("English"):
            print("  (prose heuristics below are tuned for the English text; the Chinese text is")
            print("   checked for the same sentences through the mirrored edits)")
        paragraphs = [(i, p) for i, p in enumerate(body.split("\n\n"), 1) if p.strip()
                      and not p.lstrip().startswith(("|", "#", "!", "$$", "-", "*", "`"))]
        print("  -- longest sentences")
        ranked = []
        for index, paragraph in paragraphs:
            for sentence in sentences(paragraph):
                words = len(re.findall(r"[A-Za-z][A-Za-z'-]*", sentence))
                if words >= 40:
                    ranked.append((words, sentence))
        for words, sentence in sorted(ranked, reverse=True)[:8]:
            print(f"     {words}w: {sentence[:150]}")
        total_flags += len(ranked)
        print("  -- filler and hedges")
        hits = []
        for pattern, advice in FILLER:
            for match in re.finditer(pattern, body, flags=re.I):
                hits.append(f"'{match.group(0)}' -> {advice}")
        counts = Counter(hits)
        for item, count in counts.most_common(10):
            print(f"     x{count} {item}")
        print("  -- sentence openers that need an explicit referent")
        openers = Counter()
        for index, paragraph in paragraphs:
            for sentence in sentences(paragraph):
                match = re.match(r"(This|These|It|They|There)\b", sentence)
                if match:
                    openers[match.group(1)] += 1
        print(f"     {dict(openers)}")
        print("  -- passive padding (was/were ... by)")
        hits = re.findall(r"\b(?:was|were)\s+\w+ed\s+by\b", body)
        print(f"     {len(hits)}")
        print("  -- repeated sentence starts within a paragraph")
        repeats = 0
        for index, paragraph in paragraphs:
            starts = [re.match(r"(\w+)", s).group(1).lower() for s in sentences(paragraph)
                      if re.match(r"(\w+)", s)]
            if len(starts) >= 3 and len(set(starts)) <= len(starts) - 2:
                repeats += 1
                print(f"     paragraph {index}: starts {starts[:6]}")
        total_flags += repeats
    print()
    print(f"PROSE_FLAGS={total_flags}")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
