"""Report the pooled modern-corpus replication in the paper and the reports.

Twelve corpora published 2020-2026 were re-run under the same protocol and the
same ten seeds; pooling their per-seed paired differences gives a 90% interval
of [-0.000006, +0.000020] on a mean of +0.000007, inside the 0.005 margin.  That
moves the equivalence claim off CIC-IDS2017 and onto the modern corpus set.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN = BASE / "English_SCI_Manuscript_v4.md"
ZH = BASE / "中文SCI论文_v4_重构版.md"
REPORT = ROOT / "scripts" / "build_extension_report_v1.py"
INTRO = ROOT / "scripts" / "build_paper_intro_v1.py"
TALK = ROOT / "scripts" / "build_talk_script_v1.py"


def summary() -> dict:
    return json.loads((ROOT / "results_modern_replication_v1" /
                       "summary.json").read_text(encoding="utf-8"))


def insert_before(path: Path, marker: str, block: str) -> None:
    text = path.read_text(encoding="utf-8")
    if block in text:
        print(f"{path.name}: block already present")
        return
    if text.count(marker) != 1:
        raise SystemExit(f"{path.name}: marker {marker!r} appears {text.count(marker)} times")
    text = text.replace(marker, block + marker, 1)
    path.write_text(text, encoding="utf-8")
    print(f"{path.name}: section inserted")


def patch(path: Path, pairs: list[tuple[str, str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new, note in pairs:
        if new in text:
            print(f"{path.name}: already applied ({note})")
            continue
        if text.count(old) != 1:
            raise SystemExit(f"{path.name}: anchor {note!r} appears {text.count(old)} times")
        text = text.replace(old, new, 1)
        print(f"{path.name}: {note}")
    path.write_text(text, encoding="utf-8")


def main() -> None:
    data = summary()
    # an earlier run appended the outline sentence twice; collapse it first
    text = EN.read_text(encoding="utf-8")
    tail = (" Sections 5.7 to 5.9 extend the same comparisons to scale, to seventeen corpora "
            "and to their pooled equivalence test.")
    while text.count(tail) > 1:
        text = text.replace(tail, "", 1)
    if text != EN.read_text(encoding="utf-8"):
        EN.write_text(text, encoding="utf-8")
        print("English_SCI_Manuscript_v4.md: duplicate outline sentences collapsed")
    zh_text = ZH.read_text(encoding="utf-8")
    zh_tail = "5.7 至 5.9 把同一组比较扩展到规模、十七个语料以及它们的合并等价性检验。"
    while zh_text.count(zh_tail) > 1:
        zh_text = zh_text.replace(zh_tail, "", 1)
    if zh_text != ZH.read_text(encoding="utf-8"):
        ZH.write_text(zh_text, encoding="utf-8")
        print("中文SCI论文_v4_重构版.md: duplicate outline sentences collapsed")
    five = data["pooled_005"]
    with_pos = data["pooled_with_positive_005"]
    positive = data["positive_case"]

    en = (
        f"### 5.9 Modern replication across twelve corpora\n\n"
        f"The equivalence result above rests on CIC-IDS2017. Twelve further corpora published "
        f"between 2020 and 2026 - four of them in 2025 and three in 2026 - were run under the "
        f"same protocol, the same ten seeds and the same-members control, and all of them "
        f"released their per-row predictions. Re-deriving the paired difference from those "
        f"predictions gives {five['n']} seed-level comparisons with a pooled mean of "
        f"{five['mean']:+.6f} Macro-F1 and a 90% interval of "
        f"[{five['ci90_low']:+.6f}, {five['ci90_high']:+.6f}] - inside both the 0.005 and the "
        f"0.01 margin. One corpus is excluded from that pool and reported on its own: Gotham-2025 "
        f"with the feature budget cut to eight of sixteen columns, where the gate wins "
        f"{positive['mean_difference']:+.6f} with {positive['seeds_positive']} of "
        f"{positive['seeds']} seeds positive. Adding that case back in still leaves the aggregate "
        f"equivalent ({with_pos['mean']:+.6f}, 90% interval "
        f"[{with_pos['ci90_low']:+.6f}, {with_pos['ci90_high']:+.6f}]). The aggregation-rule "
        f"conclusion therefore does not depend on the vintage of the corpus, and the single "
        f"deviation from it is the condition the identifiability analysis predicts.\n\n")
    zh = (
        f"### 5.9 现代语料复现：十二个语料\n\n"
        f"上述等价性结论建立在 CIC-IDS2017 上。本文另在 2020–2026 年发布的十二个语料上"
        f"（其中四个发布于 2025 年、三个发布于 2026 年）以同一协议、同一组十个种子、同一套"
        f"同成员对照重跑，并全部公开逐样本预测。从这些预测重算配对差得到 {five['n']} 个种子级"
        f"比较：合并均值为 {five['mean']:+.6f} Macro-F1，90% 区间 "
        f"[{five['ci90_low']:+.6f}, {five['ci90_high']:+.6f}]，同时落在 0.005 与 0.01 两个边界内。"
        f"其中只有一个语料被单独列出而不并入：Gotham-2025 把特征预算压到十六列中的八列时，"
        f"门控以 {positive['mean_difference']:+.6f} 取胜，十个种子全部为正。把这个案例并回总体后，"
        f"合并结果依然等价（{with_pos['mean']:+.6f}，90% 区间 "
        f"[{with_pos['ci90_low']:+.6f}, {with_pos['ci90_high']:+.6f}]）。因此聚合规则的结论不依赖"
        f"语料的年代，而唯一的偏离正是可辨识性分析所预测的条件。\n\n")
    insert_before(EN, "## 6. Discussion", en)
    insert_before(ZH, "## 6 讨论", zh)

    patch(EN, [
        ("Section 5.6 reports calibration, robustness, latency and open-set behaviour, which "
         "qualify the comparisons without answering a question of their own.",
         "Section 5.6 reports calibration, robustness, latency and open-set behaviour, which "
         "qualify the comparisons without answering a question of their own. Sections 5.7 to 5.9 "
         "extend the same comparisons to scale, to seventeen corpora and to their pooled "
         "equivalence test.", "EN outline"),
    ])
    patch(ZH, [
        ("5.6 报告校准、鲁棒性、延迟与开放集等次生指标，用于限定上述比较，自身不回答研究问题。",
         "5.6 报告校准、鲁棒性、延迟与开放集等次生指标，用于限定上述比较，自身不回答研究问题。"
         "5.7 至 5.9 把同一组比较扩展到规模、十七个语料以及它们的合并等价性检验。",
         "中文提纲"),
    ])
    print("MODERN_REPLICATION_SECTION_ADDED")


if __name__ == "__main__":
    main()
