"""Bring F9 in line with what is now done: only the template and author data remain."""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
SC = ROOT / "重构版论文_v4_20260915" / "论文自查表.md"
OLD = ("**尚余排版项**：① 套用 JISA 官方模板（单栏）；② 用 Word 公式编辑器的 LaTeX 模式把 5 个公式"
       "从 LaTeX 源码转为原生公式；③ 表格改为仅横线（本刊要求避免竖线）；④ 填入作者与单位信息；"
       "编号列表已改为每表独立计数（`scripts/check_docx_numbering_v40.py`，Word 渲染核验）")
NEW = ("已完成排版项：公式为 Word 原生公式（每稿 5 个 OMML，无 LaTeX 残留，`scripts/convert_equations_word_v41.py`）、"
       "表格改为三线表去竖线（10 张表逐张核对 XML）、斜体标记正确渲染、编号列表每表独立计数"
       "（`scripts/check_docx_numbering_v40.py`，Word 渲染核验）。**仅余两项需作者参与**："
       "① 套用投稿当天的 JISA 官方模板；② 填入作者、单位与通信信息")
def main() -> None:
    text = SC.read_text(encoding="utf-8")
    if OLD not in text:
        print("F9 anchor absent (already updated?)")
        return
    SC.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    print("F9 evidence updated to the current state")
if __name__ == "__main__":
    main()
