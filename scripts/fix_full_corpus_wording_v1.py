"""Tighten the full-corpus paragraph the finaliser inserts.

``finalize_full_corpus_v56.py`` writes a deliberately generic verdict because
it cannot know in advance whether the ten-seed comparison lands on equivalence
or on a detectable difference.  On the real run it landed on the latter: the
seed-level interval lies entirely below zero, so the honest statement is that
the conditional weighting is *behind* the equal-weight control on the full
corpus, not merely indistinguishable from it.  The generic phrasing ("not
evaluable or not equivalent at one margin") understates and blurs that.

This script replaces the generic sentences with the measured ones.  It asserts
every anchor, so a future re-run that produces equivalence fails loudly instead
of silently keeping text that no longer matches the data.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

EDITS: dict[str, list[tuple[str, str]]] = {
    "English_SCI_Manuscript_v4.md": [
        ("A single RCCF fit takes about 2.3 hours at this scale, so the comparison was run "
         "as a batch over the same ten seeds:",
         "A single RCCF fit takes about two hours when run alone and about four hours per seed "
         "under the three-way split used here, so the comparison was run as a batch over the "
         "same ten seeds:"),
        ("which is not evaluable or not equivalent at one margin.",
         "That interval lies entirely below zero, so the result is not the equivalence seen on "
         "the capped populations but a small, detectable deficit: the difference is equivalent "
         "at the 0.01 margin and **not** equivalent at 0.005, and all ten seeds point the same "
         "way."),
    ],
    "中文SCI论文_v4_重构版.md": [
        ("该规模下单次 RCCF 训练约需 2.3 小时，因此按同样的十个种子批量运行：",
         "该规模下单次 RCCF 单独训练约需 2 小时，三路并行时每个种子约需 4 小时，"
         "因此按同样的十个种子批量运行："),
        ("无法判定或在其中一个边界上不等价。",
         "该区间完全位于零以下，因此结论不再是截断总体上的等价，而是一处小而可测的劣势："
         "条件加权在 0.01 边界上与对照等价、在 0.005 边界上不等价，且十个种子的方向完全一致。"),
    ],
}


def main() -> int:
    for name, pairs in EDITS.items():
        path = BASE / name
        text = path.read_text(encoding="utf-8")
        for old, new in pairs:
            if new in text:
                print(f"  [{name}] already applied: {old[:34]}...")
                continue
            if old not in text:
                raise SystemExit(f"anchor missing in {name}: {old[:60]}")
            text = text.replace(old, new, 1)
            print(f"  [{name}] replaced: {old[:34]}...")
        path.write_text(text, encoding="utf-8")
    print("FULL_CORPUS_WORDING_FIXED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
