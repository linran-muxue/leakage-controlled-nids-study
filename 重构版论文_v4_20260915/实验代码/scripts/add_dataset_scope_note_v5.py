"""Disclose the three-dataset scope in the limitations section."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"


def main() -> None:
    en_path = BASE / "English_SCI_Manuscript_v4.md"
    en = en_path.read_text(encoding="utf-8")
    anchor = "**Adversarial robustness was not assessed.**"
    add = ("**Three datasets were evaluated; a fourth was not.** The conclusions are conditional on CIC-IDS2017, "
           "NSL-KDD and UNSW-NB15. A genuinely new dataset would test whether the reported protocol sensitivity "
           "and the inertness of conditional weighting extend beyond these three sources.\n\n")
    if "Three datasets were evaluated" not in en:
        en = en.replace(anchor, add + anchor, 1)
        en_path.write_text(en, encoding="utf-8")

    zh_path = BASE / "中文SCI论文_v4_重构版.md"
    zh = zh_path.read_text(encoding="utf-8")
    zanchor = "**未评估对抗鲁棒性。**"
    zadd = ("**只评测了三个数据集，未引入第四个。** 本文结论以 CIC-IDS2017、NSL-KDD 与 UNSW-NB15 为条件。"
            "若要检验所报告的协议敏感性与条件加权的失效是否越出这三个来源，需要引入一个真正独立的新数据集。\n\n")
    if "只评测了三个数据集" not in zh:
        zh = zh.replace(zanchor, zadd + zanchor, 1)
        zh_path.write_text(zh, encoding="utf-8")
    print("DATASET_SCOPE_NOTE_ADDED")


if __name__ == "__main__":
    main()
