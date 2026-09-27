"""Remove the last 'protocol versus model effects' overclaims in both languages."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"


def main() -> None:
    en_path = BASE / "English_SCI_Manuscript_v4.md"
    en = en_path.read_text(encoding="utf-8")
    old = ("This is the largest single protocol effect observed in the study and an order of magnitude larger "
           "than any model-to-model difference (at most +0.0078).")
    new = ("This is the largest single protocol effect observed in the study. It exceeds every aggregation-rule "
           "and tuning-budget difference (at most +0.0078), though not the model-family gaps of 0.0318 and 0.0916.")
    if old in en:
        en = en.replace(old, new, 1)
        print("EN 5.4 overclaim corrected")
    en = en.replace("a quantitative map that separates protocol effects from model effects;",
                    "a quantitative map that separates protocol effects from aggregation-rule effects;", 1)
    en_path.write_text(en, encoding="utf-8")

    zh_path = BASE / "中文SCI论文_v4_重构版.md"
    zh = zh_path.read_text(encoding="utf-8")
    zh = zh.replace("把协议效应与模型效应分开量化的失效地图",
                    "把协议效应与聚合策略差异分开量化的失效地图", 1)
    zh_path.write_text(zh, encoding="utf-8")
    print("ZH abstract wording corrected")


if __name__ == "__main__":
    main()
