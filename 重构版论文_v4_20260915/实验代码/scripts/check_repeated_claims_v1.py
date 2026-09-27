"""Find a repeated claim that survived an edit in paraphrase.

``check_duplicate_sentences_v27.py`` compares sentences exactly, so it catches a
replacement that left the identical old sentence behind.  It cannot catch a
rewrite that keeps a long run of the original wording - and that is what the
conclusion of the English manuscript carried: the uncapped-corpus deficit and
its 175-fold training cost were stated twice in one paragraph, the second time
after a rewrite that preserved a 47-character run verbatim.

Similarity ratios do not separate the two cases: the duplicated pair scores
0.59 on ``difflib``, while the legitimate contrast in Section 5.2 ("natural
prior over ten seeds" against "balanced control over three seeds") scores 0.54
on sentences that only share formatting.  The longest common run does separate
them, because an accident preserves wording while a deliberate contrast
preserves structure.  Measured over both bodies:

    the accidental duplication        54 and 47 characters
    the longest legitimate pair       35 characters (a repeated model name)
    the Section 5.2 contrast          22 characters

The threshold is therefore 40 characters: below every observed accident and
above every legitimate repetition.  The check also reports, without failing,
paragraphs that use the same decimal twice, which is where an accidental
duplication usually shows up first.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z(\[])")
ZH_SPLIT = re.compile(r"(?<=[。！？])")
DECIMAL = re.compile(r"\d+\.\d{3,}")
MIN_SENTENCE = 25
MIN_RUN = 40


def longest_common_run(first: str, second: str) -> tuple[int, str]:
    """Length and text of the longest substring shared by two sentences."""
    best = 0
    sample = ""
    previous = [0] * (len(second) + 1)
    for i in range(1, len(first) + 1):
        current = [0] * (len(second) + 1)
        for j in range(1, len(second) + 1):
            if first[i - 1] == second[j - 1]:
                current[j] = previous[j - 1] + 1
                if current[j] > best:
                    best = current[j]
                    sample = first[i - best:i]
            else:
                current[j] = 0
        previous = current
    return best, sample


def paragraphs(name: str, splitter: re.Pattern) -> list[tuple[int, list[str]]]:
    text = (BASE / name).read_text(encoding="utf-8")
    body = text.split("## References")[0].split("## 参考文献")[0]
    out = []
    for number, line in enumerate(body.splitlines(), 1):
        if line.lstrip().startswith(("|", "#", "!", "$")) or len(line) < 120:
            continue
        sentences = [s.strip() for s in splitter.split(line) if len(s.strip()) >= MIN_SENTENCE]
        out.append((number, sentences))
    return out


def main() -> int:
    problems: list[str] = []
    worst = 0
    for name, splitter in (("English_SCI_Manuscript_v4.md", EN_SPLIT),
                           ("中文SCI论文_v4_重构版.md", ZH_SPLIT)):
        print(f"{name}")
        for number, sentences in paragraphs(name, splitter):
            for i in range(len(sentences)):
                for j in range(i + 1, len(sentences)):
                    size, sample = longest_common_run(sentences[i], sentences[j])
                    worst = max(worst, size)
                    if size >= MIN_RUN:
                        problems.append(f"{name} line {number}: {size}-character repeated run")
                        print(f"  ISSUE line {number}: shared run of {size} characters")
                        print(f"        {sample[:150]}")
            counts: dict[str, int] = {}
            line_text = " ".join(sentences)
            for token in DECIMAL.findall(line_text):
                counts[token] = counts.get(token, 0) + 1
            repeated = sorted(t for t, n in counts.items() if n > 1)
            if repeated:
                print(f"  note  line {number}: decimal used twice in one paragraph {repeated}")
        print()
    print(f"longest shared run anywhere in the two bodies: {worst} characters "
          f"(threshold {MIN_RUN})")
    if problems:
        for problem in problems:
            print(f"ISSUE {problem}")
        print("REPEATED_CLAIM_FOUND")
        return 1
    print("NO_REPEATED_CLAIM")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
