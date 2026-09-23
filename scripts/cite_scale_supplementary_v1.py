"""Cite the three newest supplementary items from the body text.

The JISA front-matter check only verified S01-S26, so S27 (the 7.8x scale run),
S28 (N-BaIoT) and S29 (the full corpus) were listed in the supplementary table
but never referenced from the results, leaving a reader with no pointer to
them.  The checker is now range-aware; this adds the missing citations.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

EN_OLD = ("negative - once the corpus is left completely unbalanced, which is the regime in which "
          "the mechanism would actually be deployed.")
EN_NEW = (EN_OLD + " Per-seed paired statistics, per-class reports and the scale summaries for all "
          "three runs are provided in Supplementary S27-S29.")

ZH_OLD = "只有把语料完全放开、进入真实部署会遇到的强不平衡状态时才变得可测——而且是负的。"
ZH_NEW = ZH_OLD + "三次运行的逐种子配对统计、类别级报告与规模汇总见补充材料 S27–S29。"


def main() -> int:
    en = BASE / "English_SCI_Manuscript_v4.md"
    text = en.read_text(encoding="utf-8")
    if "Supplementary S27-S29" in text:
        print("  English: S27-S29 already cited")
    elif EN_OLD in text:
        en.write_text(text.replace(EN_OLD, EN_NEW, 1), encoding="utf-8")
        print("  English: S27-S29 citation added")
    else:
        raise SystemExit("English anchor missing")

    zh = BASE / "中文SCI论文_v4_重构版.md"
    text = zh.read_text(encoding="utf-8")
    if "补充材料 S27–S29" in text:
        print("  Chinese: S27-S29 already cited")
    elif ZH_OLD in text:
        zh.write_text(text.replace(ZH_OLD, ZH_NEW, 1), encoding="utf-8")
        print("  Chinese: S27-S29 citation added")
    else:
        raise SystemExit("Chinese anchor missing")

    print("SCALE_SUPPLEMENTARY_CITED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
