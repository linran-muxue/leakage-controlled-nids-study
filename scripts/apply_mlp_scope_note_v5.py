"""Clarify that the neural-baseline comparison uses the three seeds common to both runs."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"


def main() -> None:
    en_path = BASE / "English_SCI_Manuscript_v4.md"
    en = en_path.read_text(encoding="utf-8")
    old_en = "reaches 0.97679 accuracy, essentially the same as RCCF's 0.97792, but only 0.797654 Macro-F1"
    new_en = ("reaches 0.97679 accuracy, essentially the same as RCCF's 0.97792 over the three seeds common to both "
              "runs, but only 0.797654 Macro-F1")
    if old_en not in en:
        raise SystemExit("English MLP anchor missing")
    en_path.write_text(en.replace(old_en, new_en, 1), encoding="utf-8")

    zh_path = BASE / "中文SCI论文_v4_重构版.md"
    zh = zh_path.read_text(encoding="utf-8")
    old_zh = "其自然先验测试准确率为 0.97679，与 RCCF 的 0.97792 几乎相同"
    new_zh = "其自然先验测试准确率为 0.97679，与 RCCF 在两者共有的三个种子上的 0.97792 几乎相同"
    if old_zh not in zh:
        raise SystemExit("Chinese MLP anchor missing")
    zh_path.write_text(zh.replace(old_zh, new_zh, 1), encoding="utf-8")
    print("MLP_SCOPE_NOTE_APPLIED")


if __name__ == "__main__":
    main()
