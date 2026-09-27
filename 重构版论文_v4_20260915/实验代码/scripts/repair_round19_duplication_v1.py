"""Remove the duplicated limitation bullet and split the conclusion addition.

``integrate_full_corpus_claims_v1.py`` was run twice; its idempotency test was
``new in text and old not in text``, which fails when the replacement text
contains the anchor (the Section 6.5 edit ends with the heading it replaces).
The limitation bullet was therefore inserted twice.  Separately, the sentence
added to the first conclusion repeated a numeric pair already present in the
same paragraph, which the sentence-duplication gate flags.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

EN = BASE / "English_SCI_Manuscript_v4.md"
ZH = BASE / "中文SCI论文_v4_重构版.md"

BULLET = ("**The equivalence depends on how the population is built.** It holds on the 53,237-flow "
          "natural-prior population and on the 7.8-fold larger one, but not on the fully uncapped "
          "2,429,503-flow corpus, where the same comparison becomes a small, consistent deficit. The "
          "statement that conditional weighting is indistinguishable from equal voting must therefore "
          "always be quoted together with the population it was measured on; it is not a scale-free "
          "property.")

CONC_OLD_EN = ("inference time. That equivalence is a property of the population, not of the "
               "mechanism: on the fully uncapped 2,429,503-flow corpus the difference turns into a "
               "consistent deficit of -0.005533 (all ten seeds, equivalent at 0.01 but not at 0.005) "
               "at a 175-fold training cost.")
CONC_NEW_EN = ("inference time.\n\n**A qualification on that equivalence.** It is a property of the "
               "population, not of the mechanism. On the fully uncapped 2,429,503-flow corpus the same "
               "comparison turns into a consistent deficit of -0.005533 across all ten seeds, at a "
               "175-fold training cost.")

CONC_OLD_ZH = ("训练代价 175 倍。")
CONC_NEW_ZH = ("\n\n**该等价性的限定条件。** 它取决于总体构造而非机制本身：训练代价 175 倍，"
               "十种子方向一致。")


def main() -> int:
    en = EN.read_text(encoding="utf-8")
    doubled = BULLET + "\n\n" + BULLET
    if doubled in en:
        en = en.replace(doubled, BULLET, 1)
        print("  English: duplicated limitation bullet removed")
    elif en.count(BULLET) == 1:
        print("  English: limitation bullet already single")
    else:
        raise SystemExit(f"unexpected bullet count: {en.count(BULLET)}")

    if CONC_OLD_EN in en:
        en = en.replace(CONC_OLD_EN, CONC_NEW_EN, 1)
        print("  English: conclusion addition moved to its own paragraph")
    elif CONC_NEW_EN in en:
        print("  English: conclusion addition already separated")
    else:
        raise SystemExit("English conclusion anchor missing")
    EN.write_text(en, encoding="utf-8")

    zh = ZH.read_text(encoding="utf-8")
    if CONC_NEW_ZH in zh:
        print("  Chinese: conclusion addition already separated")
    elif CONC_OLD_ZH in zh:
        zh = zh.replace(CONC_OLD_ZH, CONC_NEW_ZH, 1)
        print("  Chinese: conclusion addition moved to its own paragraph")
        ZH.write_text(zh, encoding="utf-8")
    else:
        raise SystemExit("Chinese conclusion anchor missing")

    print("ROUND19_DUPLICATION_REPAIRED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
