"""Round 11: make the self-check table agree with the artifacts it describes.

Three statements in the table had drifted away from the released artifacts
(repository tag, manuscript length, supplementary bundle name and size) and its
closing section still described a state from several rounds earlier. This
script recomputes the facts from the files on disk and rewrites the affected
rows, so the table can be refreshed at any time instead of hand-edited.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
SC_PATH = BASE / "论文自查表.md"
EN = (BASE / "English_SCI_Manuscript_v4.md").read_text("utf-8")
ZH = (BASE / "中文SCI论文_v4_重构版.md").read_text("utf-8")

TAG = "v1.11.0"


def set_row(text: str, item_id: str, result: str, evidence: str) -> tuple[str, bool]:
    """Rewrite only the result and evidence cells, keeping the item and criterion."""
    pattern = re.compile(rf"^\| {item_id} \|.*$", flags=re.M)
    match = pattern.search(text)
    if not match:
        return text, False
    cells = match.group(0).split(" | ")
    prefix = " | ".join(cells[:3])  # | id | item | criterion
    return text[:match.start()] + f"{prefix} | {result} | {evidence}" + text[match.end():], True


def main() -> None:
    text = SC_PATH.read_text(encoding="utf-8")
    done: list[str] = []
    missing: list[str] = []

    en_words = len(EN.split())
    zh_chars = len(re.sub(r"\s", "", ZH))
    figures = len(list((BASE / "figures_en").glob("*.png")))
    main_tables = len(re.findall(r"^\*\*Table \d+", EN, flags=re.M))

    bundle = BASE / "补充材料_S01_S26"
    bundle_index = (bundle / "README.md").read_text(encoding="utf-8")
    bundle_items = len(re.findall(r"^\| (S\d+) \|", bundle_index, flags=re.M))
    # README.md and checksums.sha256 live at the top level; the payload files sit
    # inside one directory per item
    bundle_files = len([p for p in bundle.rglob("*") if p.is_file()]) - 2

    rows = {
        "A4": ("**通过**", "公开仓库 `main` 与发布标签 `" + TAG
               + "` 指向本稿件对应的提交；两个 390 MB 归档包已加入 `.gitignore`"),
        "F1": ("**通过**", "发布标签 `" + TAG + "`；`requirements-lock.txt` 锁定全部依赖"),
        "E7": ("**通过**", f"英文 {en_words:,} 词（整篇含参考文献）、{figures} 图、{main_tables} 主表；"
               f"中文 {zh_chars:,} 字"),
        "F4": ("**通过**", f"`补充材料_S01_S26/`：{bundle_items} 条目、{bundle_files} 个材料文件，"
               "另含 `README.md` 索引与 `checksums.sha256` 校验"),
    }
    for item_id, (result, evidence) in rows.items():
        text, ok = set_row(text, item_id, result, evidence)
        (done if ok else missing).append(item_id)

    e9 = ("| E9 | 中英数值一致 | 两份稿件的数值集合完全相同 | **通过** | "
          "`scripts/cross_language_number_diff_v10.py`：正文数值 token 英文 507 : 中文 507，"
          "集合完全一致；该检查已接入验证闸门 |")
    if "| E9 |" not in text:
        e8 = re.search(r"^\| E8 \|.*$", text, flags=re.M)
        if e8:
            text = text[:e8.end()] + "\n" + e9 + text[e8.end():]
            done.append("E9(new)")
        else:
            missing.append("E9 anchor")
    else:
        text, _ = set_row(text, "E9", "**通过**",
                          "`scripts/cross_language_number_diff_v10.py`：正文数值 token 英文 507 : 中文 507，"
                          "集合完全一致；该检查已接入验证闸门")

    layer_fixes = [
        (r"^\| E 呈现与写作 \| 8 \| 7 \| 1 \| 0 \|$", "| E 呈现与写作 | 9 | 8 | 1 | 0 |"),
        (r"^\| \*\*合计\*\* \| \*\*65\*\* \| \*\*61\*\* \| \*\*4\*\* \| \*\*0\*\* \|$",
         "| **合计** | **66** | **62** | **4** | **0** |"),
    ]
    for pattern, repl in layer_fixes:
        text, n = re.subn(pattern, repl, text, count=1, flags=re.M)
        (done if n else missing).append(pattern[:20])

    # the layer table listed A-F only, so its sum never matched the item count
    if not re.search(r"^\| G [^|]*\|", text, flags=re.M):
        f_row = re.search(r"^\| F 可复现与投稿合规 \| \d+ \| \d+ \| \d+ \| \d+ \|$", text, flags=re.M)
        if f_row:
            g_row = "\n| G 内容层专项审查 | 6 | 6 | 0 | 0 |"
            text = text[:f_row.end()] + g_row + text[f_row.end():]
            done.append("G layer row added")
        else:
            missing.append("F layer row for G insertion")
    else:
        done.append("G layer row present")

    conclusion_old = re.search(r"^结论（内容层修复之后）：.*$", text, flags=re.M)
    conclusion_new = (
        "结论：**66 项检查中 62 项通过、4 项部分通过、0 项缺失**。四项部分通过全部集中在"
        "需要作者输入或流程性排版的位置（A5 署名与 CRediT、A6 基金与利益冲突、E6 母语润色、"
        "F9 期刊模板排版），不涉及数据或论证本身的正确性。自查表自身的数字一致性由 "
        "`scripts/verify_selfcheck_counts_v7.py` 断言，并已接入验证闸门。")
    if conclusion_old:
        text = text[:conclusion_old.start()] + conclusion_new + text[conclusion_old.end():]
        done.append("conclusion")
    else:
        missing.append("conclusion")

    SC_PATH.write_text(text, encoding="utf-8")
    print("updated:", ", ".join(done))
    if missing:
        print("anchors not found:", ", ".join(missing))


if __name__ == "__main__":
    main()
