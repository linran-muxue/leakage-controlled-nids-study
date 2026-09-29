"""Bring the abstract back under the JISA limit after the same-members sentence.

Adding the equal-fusion control to the abstract pushed it to 271 words against
the journal's 250-word limit, which the format check and the readiness check both
reject.  The new sentence is shortened to its essential claim and four other
sentences are tightened, without removing any number the audits rely on (the
-0.000010 difference stays in Section 5.2 and in the conclusion, and the 79,860
comparisons stay in the abstract).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN = BASE / "English_SCI_Manuscript_v4.md"
ZH = BASE / "中文SCI论文_v4_重构版.md"

EN_EDITS: list[tuple[str, str]] = [
    (" Against equal voting over the identical four experts the gated fusion differs by -0.000010 "
     "and changes one label in 79,860 test predictions.",
     " Over the same four experts it changes one label in 79,860 predictions."),
    ("The four experts disagree on no test row, weight entropy is 0.99998, and class prior and "
     "deduplication order move Macro-F1 by +0.0725 and +0.0060.",
     "The experts never disagree; weight entropy is 0.99998; class prior and dedup order move "
     "Macro-F1 by +0.0725 and +0.0060."),
    ("the IoT corpus saturates for every model.", "the IoT corpus saturates."),
    ("The mechanism is 4.1 times larger and 4.6 times slower than one forest, without "
     "cost-sensitive advantage.",
     "The mechanism is 4.1 times larger and 4.6 times slower, without cost-sensitive advantage."),
    ("We contribute a reusable leakage-controlled protocol,",
     "We contribute a leakage-controlled protocol,"),
]

ZH_EDITS: list[tuple[str, str]] = [
    ("；对**完全相同的四个专家**做等权融合时，门控只改变 79 860 条测试预测中的 1 条，"
     "Macro-F1 差为 −0.000010。",
     "；对**同成员**等权融合时只改变 79 860 条预测中的 1 条。"),
    ("本文的贡献在于一套可复用的泄漏受控协议、一组可辨识性边界，",
     "本文贡献一套泄漏受控协议、一组可辨识性边界，"),
]


def apply(path: Path, edits: list[tuple[str, str]]) -> int:
    text = path.read_text(encoding="utf-8")
    applied = 0
    for anchor, replacement in edits:
        if anchor not in text:
            if replacement.strip()[-40:] in text:
                continue
            raise SystemExit(f"{path.name}: neither the old nor the new sentence is present: "
                             f"{anchor[:60]!r}")
        if replacement in text:
            continue
        if text.count(anchor) != 1:
            raise SystemExit(f"{path.name}: anchor appears {text.count(anchor)} times: "
                             f"{anchor[:60]!r}")
        text = text.replace(anchor, replacement, 1)
        applied += 1
    path.write_text(text, encoding="utf-8")
    return applied


def main() -> None:
    # repair: a re-run of the wording script had re-inserted the long sentence
    # beside the short one, so the duplicate is removed before the count check
    text_before = EN.read_text(encoding="utf-8")
    duplicate = (" Against equal voting over the identical four experts the gated fusion differs by "
                 "-0.000010 and changes one label in 79,860 test predictions.")
    if duplicate in text_before:
        EN.write_text(text_before.replace(duplicate, "", 1), encoding="utf-8")
        print("removed the duplicated abstract sentence")
    en_applied = apply(EN, EN_EDITS)
    zh_applied = apply(ZH, ZH_EDITS)
    text = EN.read_text(encoding="utf-8")
    abstract = text[text.index("## Abstract"):text.index("**Keywords:**")]
    words = len(abstract.split("## Abstract", 1)[1].split())
    print(f"English edits {en_applied}, Chinese edits {zh_applied}, abstract {words} words")
    if words > 250:
        raise SystemExit(f"abstract still over the limit: {words} words")
    if "79,860" not in abstract:
        raise SystemExit("the abstract lost the 79,860 comparison count")
    print("ABSTRACT_LENGTH_OK")


if __name__ == "__main__":
    main()
