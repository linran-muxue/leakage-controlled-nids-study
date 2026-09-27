"""Find sentence pairs that say nearly the same thing.
Two different wordings of one finding are harder to spot than an exact repeat
and just as costly to the reader. Content-word overlap above a threshold, with
numbers treated as content, surfaces them for review.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
STOP = set("""a an the of to and in is are was were that this these those for on by with as at it its
be been being we our their they them he she his her not no or but if then than so such can could may
might must should would will shall do does did done have has had which who whom whose when where why
how all any both each few more most other some only own same too very s t d ll m re ve y""".split())
NUMBER = re.compile(r"\d+(?:[.,]\d+)?")
def content(sentence: str) -> set[str]:
    words = re.findall(r"[A-Za-z][A-Za-z'-]+", sentence.lower())
    tokens = {w for w in words if w not in STOP and len(w) > 2}
    tokens |= set(NUMBER.findall(sentence))
    return tokens
def sentences(text: str) -> list[tuple[int, str]]:
    out = []
    for number, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith(("|", "#", "!", "$$", "```")) or not line.strip():
            continue
        for s in re.split(r"(?<=[.!?])\s+(?=[A-Z(\[])", line.strip()):
            if len(re.findall(r"[A-Za-z][A-Za-z'-]+", s)) >= 8:
                out.append((number, s))
    return out
def main() -> int:
    for name in ("English_SCI_Manuscript_v4.md", "中文SCI论文_v4_重构版.md"):
        text = (BASE / name).read_text(encoding="utf-8")
        body = text.split("## References")[0].split("## 参考文献")[0]
        items = sentences(body)
        sets = [(n, s, content(s)) for n, s in items]
        hits = []
        for i in range(len(sets)):
            for j in range(i + 1, len(sets)):
                a, b = sets[i][2], sets[j][2]
                if len(a) < 6 or len(b) < 6:
                    continue
                jaccard = len(a & b) / len(a | b)
                if jaccard >= 0.5:
                    hits.append((jaccard, sets[i], sets[j]))
        hits.sort(reverse=True, key=lambda h: h[0])
        print(f"===== {name}: {len(hits)} near-duplicate pair(s) at >= 0.50 overlap")
        for score, first, second in hits[:8]:
            print(f"  {score:.2f}  line {first[0]}: {first[1][:110]}")
            print(f"        line {second[0]}: {second[1][:110]}")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
