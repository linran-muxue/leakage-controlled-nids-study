"""English language consistency audit for the manuscript."""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
EN = (ROOT / "重构版论文_v4_20260915" / "English_SCI_Manuscript_v4.md").read_text("utf-8")
body = EN.split("## References")[0]

BRITISH_AMERICAN = [
    ("normalis", "normaliz"), ("randomis", "randomiz"), ("behaviour", "behavior"),
    ("generalis", "generaliz"), ("optimis", "optimiz"), ("analys", "analyz"),
    ("modelling", "modeling"), ("labelled", "labeled"), ("centre", "center"),
]

print("=== spelling-variant consistency ===")
for brit, amer in BRITISH_AMERICAN:
    b = len(re.findall(brit, body, re.I))
    a = len(re.findall(amer, body, re.I))
    if b or a:
        flag = "MIXED" if b and a else "ok"
        print(f"  {brit:<14} {b:>4}   {amer:<14} {a:>4}   {flag}")

print()
print("=== terminology consistency ===")
tokens = ["chi-square", "chi2", "RCCF", "conditional gate", "equal-weight", "Mondrian",
          "Macro-F1", "held-out", "out-of-fold"]
for t in tokens:
    print(f"  {t:<18} {len(re.findall(re.escape(t), body)):>4}")

print()
print("=== filler phrases ===")
fillers = ["it is worth noting", "it should be noted", "in order to", "as a matter of fact",
           "it is important to note", "needless to say", "in this paper, we"]
for f in fillers:
    c = len(re.findall(re.escape(f), body, re.I))
    if c:
        print(f"  {f:<28} {c}")
print("  (none listed above means none found)")

print()
print("=== sentence length ===")
sents = [s.strip() for s in re.split(r"(?<=[.])\s+", re.sub(r"\s+", " ", body)) if len(s.split()) > 3]
lengths = [len(s.split()) for s in sents]
long_sents = [s for s in sents if len(s.split()) > 45]
print(f"  sentences: {len(sents)}, mean words: {sum(lengths)/len(lengths):.1f}, "
      f"max: {max(lengths)}, over 45 words: {len(long_sents)}")
for s in long_sents[:3]:
    print(f"    [{len(s.split())}w] {s[:110]}...")

print()
print("=== repeated sentence openings ===")
openings = Counter(" ".join(s.split()[:2]) for s in sents)
for opening, count in openings.most_common(6):
    if count > 3:
        print(f"  {opening!r}: {count}")
