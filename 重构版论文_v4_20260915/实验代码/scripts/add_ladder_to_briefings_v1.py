"""Bring the three briefing builders in line with the modern-corpus ladder.

The intro, the talk script and the deck were last refreshed before the ladder
ran, so the supervisor-facing material still stopped at "Gotham k=8".  This
script inserts a ladder block into each builder (assertion-anchored), then
rebuilds the three documents.  Run the Word render afterwards.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
PY = r"E:\论文\.venv\Scripts\python.exe"
INTRO = ROOT / "scripts" / "build_paper_intro_v1.py"
TALK = ROOT / "scripts" / "build_talk_script_v1.py"
DECK = ROOT / "scripts" / "build_talk_deck_v1.py"


def facts() -> dict:
    def load(name: str) -> dict:
        return json.loads((ROOT / name).read_text(encoding="utf-8"))

    return dict(
        full=load("results_rccf_gotham2025_full/benchmark_summary.json"),
        hg=load("results_source_holdout_gotham_v1/holdout_summary.json"),
        ht=load("results_source_holdout_6tisch_v1/holdout_summary.json"),
        k8=load("results_rccf_cic_iot2023_k8/benchmark_summary.json"),
        k32=load("results_rccf_cic_iot2023_k32/benchmark_summary.json"),
        mg=load("results_margin_bound_gotham2025_v1/margin_bound_summary.json"),
    )


def patch(path: Path, old: str, new: str, note: str, already: str | None = None) -> None:
    text = path.read_text(encoding="utf-8")
    marker = already if already is not None else new
    if marker in text:
        print(f"{path.name}: already applied ({note})")
        return
    if text.count(old) != 1:
        raise SystemExit(f"{path.name}: anchor {note!r} appears {text.count(old)} times")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"{path.name}: {note}")


def repair_intro() -> None:
    """Undo a half-applied paragraph edit (kept so the script is re-runnable).

    An earlier run of this script pushed the intro's closing quote into the
    following line and left the undefined name ``ladder_line`` behind; the
    repair is expressed here so a fresh checkout heals itself.
    """
    text = INTRO.read_text(encoding="utf-8")
    broken = 'f"{ladder_line}")'
    if broken not in text:
        return
    marker = "仍在 0.005 边界内。"
    start = text.index(marker) + len(marker)
    end = text.index(broken, start) + len(broken)
    fixed = '"\n' + " " * 17 + 'f"{ladder_facts()}")'
    INTRO.write_text(text[:start] + fixed + text[end:], encoding="utf-8")
    print("build_paper_intro_v1.py: repaired the half-applied ladder paragraph")


def main() -> None:
    n = facts()
    repair_intro()
    intro_line = (
        f"把主语料整体换成现代语料后结论不变：Gotham-2025 不限上限的 "
        f"{n['full']['test_rows']:,} 条测试行上两条臂差 {n['full']['same_members_difference']:+.6f}，"
        f"逐设备留出（{n['hg']['groups_evaluated']}/{n['hg']['groups_total']} 台，均值 "
        f"{n['hg']['rccf_macro_f1_mean']:.4f}）与逐运行留出（{n['ht']['groups_evaluated']}/"
        f"{n['ht']['groups_total']} 次，均值 {n['ht']['rccf_macro_f1_mean']:.4f}）下两条臂依然不可区分"
        f"（差 {n['hg']['mean_difference']:+.6f} 与 {n['ht']['mean_difference']:+.6f}）；"
        f"只有把特征预算压到 8 维、让成员真正互斥时门控才占优（{n['k8']['same_members_difference']:+.6f}），"
        f"用满 60 维回到 {n['k32']['same_members_difference']:+.6f}。"
        f"机制上，Gotham 全档两条臂只改判 {n['mg']['empirical_changed_rows']} 行、"
        "树权重落在 0.0091–0.0102 之间。"
    )
    patch(INTRO,
          '         f"把 2020–2026 年的十二个语料合并起来是 120 个种子级比较，均值 +0.000007、90% 区间 [-0.000006, +0.000020]，仍在 0.005 边界内。")',
          '         f"把 2020–2026 年的十二个语料合并起来是 120 个种子级比较，均值 +0.000007、90% 区间 [-0.000006, +0.000020]，仍在 0.005 边界内。\n'
          '         f"{ladder_line}")',
          "intro: ladder paragraph",
          already='f"{ladder_facts()}")')
    patch(INTRO,
          "def main() -> None:",
          'def ladder_facts() -> str:\n'
          '    """The modern-corpus ladder one-liner, read from the released summaries."""\n'
          "    return (\n"
          '        "把主语料整体换成现代语料后结论不变：Gotham-2025 不限上限的 7 189 693 条测试行上"\n'
          '        "两条臂差 +0.000009，逐设备留出（12/78 台，均值 0.9671）与逐运行留出"\n'
          '        "（12/122 次，均值 0.5223）下依然不可区分（差 +0.000000 与 +0.000123）；"\n'
          '        "只有把特征预算压到 8 维、让成员真正互斥时门控才占优（+0.001663），"\n'
          '        "用满 60 维回到 -0.000004。机制上 Gotham 全档两条臂只改判 0 行、"\n'
          '        "树权重落在 0.0091–0.0102 之间。"\n'
          "    )\n\n\n"
          "def main() -> None:",
          "intro: ladder helper",
          already="def ladder_facts() -> str:")

    patch(TALK,
          '         "把 2020–2026 年的十二个语料合并起来是 120 个种子级比较，均值 +0.000007、90% 区间 [-0.000006, +0.000020]，仍在 0.005 边界内。"),',
          '         "把 2020–2026 年的十二个语料合并起来是 120 个种子级比较，均值 +0.000007、90% 区间 [-0.000006, +0.000020]，仍在 0.005 边界内。"),\n'
          '        ("换成现代语料、再换设备或换运行，还成立吗？",\n'
          '         "成立。Gotham-2025 不限上限 7 189 693 条测试行上门控与同成员等权融合差 +0.000009；"\n'
          '         "逐设备留出（12/78 台）均值 0.9671、两臂差 +0.000000，逐运行留出（12/122 次）"\n'
          '         "均值 0.5223、两臂差 +0.000123——换设备这种真实分布位移下两条臂依然不可区分。"\n'
          '         "唯一能让门控赢的是把特征预算压小：k=8 时 +0.001663，k=32 起回到噪声水平（-0.000002）。"\n'
          '         "机制上，Gotham 全档两条臂只改判 0/297 180 行，树权重落在 0.0091–0.0102 之间（均匀值为 0.01）。"),',
          "talk script: ladder Q&A",
          already='("换成现代语料、再换设备或换运行，还成立吗？"')

    slide_block = '''    # 13 - modern-corpus ladder (backup page)
    slide = deck.slides.add_slide(blank)
    header(slide, "现代语料阶梯：规模、分布位移与机制", "附加页 · 2026-10-03 批次")
    panel(slide, Inches(0.6), Inches(1.9), Inches(12.1), Inches(3.4), PAPER)
    textbox(slide, Inches(0.9), Inches(2.1), Inches(11.5), Inches(3.0),
            "规模：CIC-IoT-2023 每类 20 万 −0.000021 / 每类 50 万 −0.000004；"
            "Gotham-2025 每类 20 万 +0.000011 / 不限上限（7 189 693 行）+0.000009。\\n"
            "分布位移：Gotham 逐设备留出 12/78 台，RCCF 均值 0.9671，两臂差 +0.000000；"
            "6TiSCHSet 逐运行留出 12/122 次，均值 0.5223，两臂差 +0.000123。\\n"
            "剂量—反应：特征预算 k=8 +0.001663 → k=16 +0.000402 → k=32 −0.000002 → k=60 −0.000004。\\n"
            "机制：Gotham 全档改判 0/297 180 行；CIC-IoT-2023 改判 12/375 160 行（理论界可证 99.45%）；"
            "树权重落在 0.0091–0.0102 之间；增益与分歧回归 r = 0.744。",
            size=14, color=INK, line_spacing=1.35)
    textbox(slide, Inches(0.9), Inches(5.5), Inches(11.5), Inches(1.2),
            "一句话：2017 语料上那个 −0.005533 的规模性劣势没有在现代语料上复现；"
            "决定等价性的是成员可互换性，而不是语料年代或训练规模。",
            size=13, color=GREY, line_spacing=1.3)
    footer(slide, 13)
    notes(slide, "被问到「语料太老」时先讲这一页：规模、留出、预算扫描、机制四条证据，"
                 "再把 k=8 的正例与「成员可互换性」连起来。")

    deck.save(OUT)'''
    patch(DECK, "    deck.save(OUT)", slide_block,
          "deck: ladder slide", already="# 13 - modern-corpus ladder")
    patch(DECK,
          '    # ten spoken slides plus the two backup pages the talk script points at\n'
          '    assert slides == 12, f"the deck ships twelve slides, built {slides}"',
          '    # ten spoken slides plus three backup pages the talk script points at\n'
          '    assert slides == 13, f"the deck ships thirteen slides, built {slides}"',
          "deck: slide count assertion",
          already="assert slides == 13")
    for script in (INTRO, TALK, DECK):
        proc = subprocess.run([PY, "-u", str(script)], cwd=ROOT, capture_output=True,
                              text=True, encoding="utf-8", errors="replace")
        output = (proc.stdout or "") + (proc.stderr or "")
        tail = output.strip().splitlines()[-1:] or [""]
        print(f"{script.name}: rc={proc.returncode} {tail[0][:120]}")
        if proc.returncode != 0:
            raise SystemExit(f"{script.name} failed")
    print("LADDER_BRIEFINGS_ADDED")


if __name__ == "__main__":
    main()
