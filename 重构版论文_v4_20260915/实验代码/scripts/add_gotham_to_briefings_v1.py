"""Bring the briefing material in line with Gotham-2025 and its positive result.

Two things change for a supervisor audience: the corpora count is fourteen (the
``_k8`` directory is a second feature budget on the same corpus, not a new one),
and the paper now has a case where the gate genuinely wins.  Both are added to
the intro, the talk script and the slide deck; the question count is updated.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
INTRO = ROOT / "scripts" / "build_paper_intro_v1.py"
TALK = ROOT / "scripts" / "build_talk_script_v1.py"
DECK = ROOT / "scripts" / "build_talk_deck_v1.py"
BUNDLE = ROOT / "scripts" / "package_submission_bundle_v18.py"


def patch(path: Path, pairs: list[tuple[str, str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new, note in pairs:
        if new in text and old not in text:
            print(f"{path.name}: already applied ({note})")
            continue
        if text.count(old) != 1:
            raise SystemExit(f"{path.name}: anchor {note!r} appears {text.count(old)} times")
        text = text.replace(old, new, 1)
        print(f"{path.name}: {note}")
    path.write_text(text, encoding="utf-8")


def main() -> None:
    # the _k8 run is a second budget on Gotham, not a fifteenth corpus
    for path in (INTRO, TALK, DECK):
        text = path.read_text(encoding="utf-8")
        old_helper = 'ROOT.glob("results_rccf_*_v1")'
        old_inline = 'ROOT.glob("results_rccf_*_v1")'
        if old_helper not in text and old_inline not in text:
            print(f"{path.name}: corpus pattern already guarded")
            continue
        new_pattern = ('[path for path in ROOT.glob("results_rccf_*_v1")\n'
                       '                       if not path.name.endswith("_k8")]')
        if path is DECK:
            text = text.replace(
                'corpora = 4 + len([path for path in ROOT.glob("results_rccf_*_v1")\n'
                '                       if (path / "benchmark_summary.json").exists()])',
                'corpora = 4 + len([path for path in ROOT.glob("results_rccf_*_v1")\n'
                '                       if not path.name.endswith("_k8")\n'
                '                       and (path / "benchmark_summary.json").exists()])', 1)
        else:
            text = text.replace(
                '    extension = [path for path in ROOT.glob("results_rccf_*_v1")\n'
                '                 if (path / "benchmark_summary.json").exists()]',
                '    extension = [path for path in ROOT.glob("results_rccf_*_v1")\n'
                '                 if not path.name.endswith("_k8")\n'
                '                 and (path / "benchmark_summary.json").exists()]', 1)
        # the 2025 summary line gains Gotham
        text = text.replace(
            '                          ("results_rccf_ids2025_v1", "IDS2025")):',
            '                          ("results_rccf_ids2025_v1", "IDS2025"),\n'
            '                          ("results_rccf_gotham2025_v1", "Gotham-2025")):', 1)
        path.write_text(text, encoding="utf-8")
        print(f"{path.name}: corpus count guarded, Gotham added to the 2025 line")

    patch(INTRO, [
        ('f"2020 年及以后、三份发布于 2025 年；2025 年语料上门控与同成员等权融合的"\n'
         '                 f"差值仍在 0.000004-0.000020 量级：{y2025_line}。")',
         'f"2020 年及以后、四份发布于 2025 年；2025 年语料上门控与同成员等权融合的"\n'
         '                 f"差值仍在 0.000004-0.000020 量级：{y2025_line}。"\n'
         '                 f"Gotham-2025 另给出全文唯一一个门控为正的案例：视图重合时差值恰为 0.000000，"\n'
         '                 f"把 16 列拆成 8 列让视图分化后增益 +0.0063（十个种子方向一致）。")',
         "recency paragraph gains Gotham"),
    ])

    patch(TALK, [
        ('         f"评测的 {corpora} 个语料里八个发布于 2020 年及以后，其中三份发布于 2025 年："\n'
         '         f"{y2025_line}；"\n'
         '         "全部语料都按同一套水库去重、同一组十个种子、同一组确定性视图评测，"\n'
         '         "结论不随语料年代改变。"),',
         '         f"评测的 {corpora} 个语料里八个发布于 2020 年及以后，其中四份发布于 2025 年："\n'
         '         f"{y2025_line}；"\n'
         '         "全部语料都按同一套水库去重、同一组十个种子、同一组确定性视图评测，"\n'
         '         "结论不随语料年代改变。"),\n'
         '        ("门控到底有没有用？",\n'
         '         "有用，但有条件——而且条件是可检验的。2025 年的 Gotham-2025 语料上，"\n'
         '         "16 列特征用满（60 维预算会选中全部列）时三个视图完全重合，差值恰为 0.000000；"\n'
         '         "把预算压到 16 选 8、让卡方与方差分析真正分歧后，门控以 +0.0063 超过同成员等权"\n'
         '         "融合，十个种子方向一致。这正是命题 1 预测的边界：成员可互换时门控必然无效，"\n'
         '         "成员可区分时它才可能有用。全文其余语料都在前一种情形里。"),',
         "gate-value question"),
        ('    lines.append("## 七、老师最可能追问的 23 个问题")',
         '    lines.append("## 七、老师最可能追问的 24 个问题")', "heading count"),
        ('    lines.append("前八问每次汇报都会出现；后面十五问按老师追问的方向取用"\n'
         '                 "（设计 4、统计 4、数据 4、流程与边界 3）。")',
         '    lines.append("前八问每次汇报都会出现；后面十六问按老师追问的方向取用"\n'
         '                 "（设计 4、统计 4、数据 4、机制 1、流程与边界 3）。")',
         "question breakdown"),
    ])

    patch(DECK, [
        ('            f"· 三个外部语料用各自原生标签，不重采样、不跨语料迁移，因此只能作为"\n'
         '            f"「结论方向不随语料改变」的旁证，不能当作迁移实验；\\n"\n'
         '            f"· 语料年代：{corpora} 个语料里八个发布于 2020 年及以后，其中三份发布于 2025 年，"\n'
         '            f"差值与上表同量级（见《向老师汇报要点》Q5）。",',
         '            f"· 三个外部语料用各自原生标签，不重采样、不跨语料迁移，因此只能作为"\n'
         '            f"「结论方向不随语料改变」的旁证，不能当作迁移实验；\\n"\n'
         '            f"· 语料年代：{corpora} 个语料里八个发布于 2020 年及以后，其中四份发布于 2025 年，"\n'
         '            f"差值与上表同量级（见《向老师汇报要点》Q5）；\\n"\n'
         '            f"· 门控并非永远无效：2025 年 Gotham-2025 语料上视图重合时差值恰为 0.000000，"\n'
         '            f"把 16 列压到 8 列、视图分化后增益 +0.0063（十个种子方向一致）。",',
         "deck robustness slide"),
    ])
    patch(BUNDLE, [("23 问预判问答", "24 问预判问答", "bundle README count")])
    print("GOTHAM_BRIEFINGS_ADDED")


if __name__ == "__main__":
    main()
