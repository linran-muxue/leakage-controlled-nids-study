"""Align the seed scope of the neural-baseline row, its paragraph and Figure 4.

The ten-seed upgrade rewrote Table 4(a) and the surrounding text, but three
places still mixed the three-seed run into a ten-seed frame:

* the panel (a) header claimed ten seeds for every row, including the MLP row,
  which is a mean over the three seeds common to both runs;
* the MLP paragraph quoted RCCF's three-seed values without saying so for the
  balanced-accuracy and Brier comparisons;
* Figure 4 was drawn from the three-seed run while its caption said ten seeds.

The figure builders are updated separately (scripts/build_figures_en_v5.py and
scripts/build_restructured_figures_v4.py); check_seed_scope_v5.py re-derives
every value from the source files and guards the wording.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN = BASE / "English_SCI_Manuscript_v4.md"
ZH = BASE / "中文SCI论文_v4_重构版.md"


def fix(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"anchor missing: {label}")
    if text.count(old) != 1:
        raise SystemExit(f"anchor not unique ({text.count(old)}x): {label}")
    return text.replace(old, new, 1)


def main() -> None:
    en = EN.read_text(encoding="utf-8")
    en = fix(
        en,
        "(a) Natural-prior population P_nat, 7,986 test rows, mean of ten seeds",
        "(a) Natural-prior population P_nat, 7,986 test rows, mean of ten seeds "
        "(MLP row: three seeds common to both runs)",
        "en table head",
    )
    en = fix(
        en,
        "reaches 0.97679 accuracy, essentially the same as RCCF's 0.97792 over the three seeds "
        "common to both runs, but only 0.797654 Macro-F1, 0.092 below RCCF. Its balanced accuracy "
        "is 0.79666 against 0.94920, and its Brier score is 0.036701 against 0.006312.",
        "reaches 0.97679 accuracy against RCCF's 0.97792, but only 0.797654 Macro-F1 against "
        "0.889955, i.e. 0.092 lower. Its balanced accuracy is 0.79666 against 0.94920 and its "
        "Brier score is 0.036701 against 0.006312. Every comparison in this paragraph is computed "
        "on the three seeds common to both runs (42, 2024, 3407), the seeds on which the neural "
        "baseline was trained; Table 4(a) gives the corresponding ten-seed RCCF values.",
        "en mlp paragraph",
    )
    en = fix(
        en,
        "![Figure 4. Main results on both populations (ten seeds for the natural-prior panel) "
        "and paired bootstrap intervals]",
        "![Figure 4. Main results on both populations (ten seeds for the natural-prior panel; "
        "the MLP bar uses the three seeds common to both runs) and paired bootstrap intervals]",
        "en figure 4 caption",
    )
    EN.write_text(en, encoding="utf-8")

    zh = ZH.read_text(encoding="utf-8")
    zh = fix(
        zh,
        "（a）自然先验总体 P_nat，测试集 7 986 条，十种子均值",
        "（a）自然先验总体 P_nat，测试集 7 986 条，十种子均值（MLP 行为两次运行共有的三个种子）",
        "zh table head",
    )
    zh = fix(
        zh,
        "其自然先验测试准确率为 0.97679，与 RCCF 在两者共有的三个种子上的 0.97792 几乎相同；"
        "但其 Macro-F1 仅为 0.797654，比 RCCF 低 0.092，平衡准确率为 0.79666 对 0.94920，"
        "Brier 分数为 0.036701 对 0.006312。",
        "其自然先验测试准确率为 0.97679，与 RCCF 的 0.97792 几乎相同；但其 Macro-F1 仅为 "
        "0.797654，对 RCCF 的 0.889955 低 0.092，平衡准确率为 0.79666 对 0.94920，Brier 分数为 "
        "0.036701 对 0.006312。本段所有对照均在两次运行共有的三个种子（42、2024、3407，即该神经"
        "基线训练所用的种子）上计算；表 4(a) 给出对应的十种子 RCCF 数值。",
        "zh mlp paragraph",
    )
    zh = fix(
        zh,
        "注：图 4(a) 纵轴从 0.75 起，目的是显示千分位量级的差异；图 4(b) 的配对区间表明这些差异在统计上不可区分。",
        "注：图 4(a) 纵轴从 0.75 起，目的是显示千分位量级的差异，自然先验面板为十种子均值"
        "（MLP 柱为两次运行共有的三个种子），平衡控制面板为三种子均值；图 4(b) 的配对区间表明"
        "这些差异在统计上不可区分。",
        "zh figure 4 note",
    )
    ZH.write_text(zh, encoding="utf-8")
    print("SEED_SCOPE_FIX_APPLIED")


if __name__ == "__main__":
    main()
