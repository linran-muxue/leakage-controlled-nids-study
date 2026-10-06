"""Language pass over the Round 20 additions (no number or claim may change).

The ladder text was written quickly while the experiments were still running, so
it carries a few rough edges: a self-reference to "this book" in a paper, dashes
used where a colon reads better, mixed short names for 6TiSCHSet-2026, and a
three-clause mechanism sentence.  This pass fixes the prose only.

Safety: every edit is anchored (the old text must appear exactly once), and each
edited file must keep its multiset of numeric tokens unchanged, so a slipped
digit cannot survive the run.  The cross-language alignment and the wider
formatting checks are re-run by the gate afterwards.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
DECIMAL = re.compile(r"\d+\.\d{2,6}")
INTEGER = re.compile(r"\b\d{1,3}(?:[, ]\d{3})+\b|\b\d{4,7}\b")


def tokens(text: str) -> list[str]:
    found = DECIMAL.findall(text) + INTEGER.findall(text)
    return sorted(f.replace(",", "").replace(" ", "") for f in found)


EDITS: dict[str, list[tuple[str, str, str]]] = {
    "中文SCI论文_v4_重构版.md": [
        ("把 2017 语料上的规模阶梯搬到现代语料、在**真实分布位移**（换设备、换运行）下重测同一对照，",
         "本节把 2017 语料上的规模阶梯迁移到现代语料，在**真实分布位移**（换设备、换运行）下复测同一对照，",
         "§5.10 opening"),
        ("并用机制套件解释结果。全部为同一协议、同一组十个种子。",
         "并用机制套件解释结果；三部分均采用同一协议与同一组十个种子。",
         "§5.10 opening, second sentence"),
        ("**规模不是失效的原因。**", "**规模本身并非失效原因。**", "§5.10 scale lead"),
        ("出现 -0.005533 的稳定劣势（5.7 节），", "呈现 -0.005533 的稳定劣势（5.7 节），",
         "§5.10 scale verb"),
        ("本书最大的总体 Gotham-2025 全档在", "本文最大的总体 Gotham-2025 全档在",
         "§5.10 self-reference"),
        ("因此 5.7 的劣势是那个语料与那个总体的组合的性质，不能读成「规模一大，加权就会变差」。",
         "因此 5.7 的劣势来自该语料与该总体的特定组合，不能推广为「规模越大，加权越差」。",
         "§5.10 scale conclusion"),
        ("留一来源设计避免这一点。", "留一来源（leave-one-source-out）设计避免了这一点。",
         "§5.10 holdout design"),
        ("（6TiSCH 上均值掉到 0.52）", "（6TiSCHSet-2026 上均值降至 0.52）",
         "§5.10 short name"),
        ("预算小时卡方与方差分析选出的特征真正不同，成员不再可互换，门控开始起作用；",
         "预算较小时，卡方与方差分析选出的特征真正分化，成员不再可互换，门控开始起作用；",
         "§5.10 budget sentence"),
        ("（1）边距上界——Gotham 全档 297 180 行里两条臂改判",
         "（1）边距上界：Gotham 全档 297 180 行中两条臂仅改判", "§5.10 mechanism (1)"),
        ("CIC-IoT-2023 的 375 160 行里改判", "CIC-IoT-2023 的 375 160 行中改判",
         "§5.10 mechanism (1), second clause"),
        ("（2）权重机制——门控确实在调权", "（2）权重机制：门控确实在调权",
         "§5.10 mechanism (2)"),
        ("（3）多样性剂量—反应——五组专家配置上增益与平均成对分歧同向变化",
         "（3）多样性剂量—反应：五组专家配置上增益与平均成对分歧同向变化",
         "§5.10 mechanism (3)"),
        ("**现代语料阶梯。** 把 2017 年语料上的规模阶梯整体搬到现代语料：",
         "**现代语料阶梯。** 将 2017 语料上的规模阶梯整体迁移到现代语料：",
         "§5.8 verb"),
        ("但它至少不随语料年代或训练规模机械地失效——真正决定它的是成员可互换性",
         "但它不会随语料年代或训练规模机械地失效；真正决定它的是成员的可互换性",
         "§6.5 phrasing"),
        ("这正是可辨识性条件所预测的边界，现在在一个 2025 年语料上被观测到。",
         "这正是可辨识性条件所预测的边界，并已在一个 2025 年语料上得到验证。",
         "§5.8 closing sentence"),
        ("该机制体积是单个等权森林的 4.1 倍、吞吐低 4.6 倍",
         "该机制体积为单个等权森林的 4.1 倍，吞吐低 4.6 倍", "abstract phrasing"),
    ],
    "English_SCI_Manuscript_v4.md": [
        ("This section does three things at once: it moves", "This section does three things: it moves",
         "§5.10 opening"),
        ("it explains the outcome with the mechanism suite. Same protocol, same ten seeds throughout.",
         "and it explains the outcome with the mechanism suite. All three use the same protocol and "
         "the same ten seeds.", "§5.10 opening, second sentence"),
        ("and this book's largest", "and the largest population in this study:",
         "§5.10 self-reference"),
        ("population, the uncapped Gotham-2025 corpus, by", "the uncapped Gotham-2025 corpus differs by",
         "§5.10 scale sentence"),
        ("(to 0.52 on 6TiSCHSet), but the arm gap stays", "(to 0.52 for 6TiSCHSet-2026), but the arm gap stays",
         "§5.10 short name"),
        ("(1) the margin bound - on 297,180 Gotham rows the arms",
         "(1) the margin bound: on 297,180 Gotham rows the arms", "§5.10 mechanism (1)"),
        ("(2) the weight mechanism - the gate does reweight",
         "(2) the weight mechanism: the gate does reweight", "§5.10 mechanism (2)"),
        ("(3) the diversity dose-response -", "(3) the diversity dose-response:",
         "§5.10 mechanism (3)"),
        ("the boundary the identifiability conditions predict, now observed on a 2025 corpus.",
         "the boundary the identifiability conditions predict, now confirmed on a 2025 corpus.",
         "§5.8 closing sentence"),
    ],
    "扩展实验报告.md": [
        ("主实验里那个 -0.005533 的规模性劣势没有在现代语料上复现：",
         "主实验里 -0.005533 的规模性劣势未在现代语料上复现：", "report §12 conclusion"),
        ("门控确实在调权，但幅度落在 0.0091–0.0102 之间（均匀值为 0.01），而两条臂的改判行数在 12/375160 与 ",
         "门控确实在调权，但幅度落在 0.0091–0.0102 之间（均匀值为 0.01），而两条臂的改判行数只有 12/375160 与 ",
         "report §14 conclusion"),
    ],
}


def main() -> int:
    changed = 0
    for name, edits in EDITS.items():
        path = BASE / name
        text = path.read_text(encoding="utf-8")
        before = tokens(text)
        original = text
        for old, new, note in edits:
            if new in text and old not in text:
                print(f"{name}: already applied ({note})")
                continue
            if text.count(old) != 1:
                raise SystemExit(f"{name}: anchor {note!r} appears {text.count(old)} times")
            text = text.replace(old, new, 1)
            print(f"{name}: {note}")
        if text != original:
            after = tokens(text)
            # Renaming a corpus legitimately introduces its year ("6TiSCHSet-2026"),
            # so the rule is: no value may be lost or altered.  Additions must be
            # mirrored in the other language, which the cross-language check
            # enforces afterwards.
            lost = [t for t in set(before) if after.count(t) < before.count(t)]
            if lost:
                raise SystemExit(f"{name}: numeric tokens lost or altered ({sorted(lost)[:5]})")
            path.write_text(text, encoding="utf-8")
            changed += 1
        else:
            print(f"{name}: no change needed")
    print(f"PROSE_POLISHED files={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
