"""Record in the self-check table what the formatting pass still has to do.
The compliance sweep confirmed five presentation items that belong to the
journal-template step: the official template itself, Word-native equations,
tables without vertical rules, and author-supplied metadata.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
SC_PATH = ROOT / "重构版论文_v4_20260915" / "论文自查表.md"
OLD = "已按新主线重做 `Graphical_Abstract_v4.png/pdf`（四面板：协议、十种子等价、机制、协议效应）与 `Cover_Letter_JISA_v4.md`；**尚余按 JISA 官方模板排版**"
NEW = ("已按新主线重做 `Graphical_Abstract_v4.png/pdf`（四面板：协议、十种子等价、机制、协议效应，3300×2280 像素）"
       "与 `Cover_Letter_JISA_v4.md`；公式已按 (1)–(5) 编号。**尚余排版项**："
       "① 套用 JISA 官方模板（单栏）；② 用 Word 公式编辑器的 LaTeX 模式把 5 个公式从 LaTeX 源码转为原生公式；"
       "③ 表格改为仅横线（本刊要求避免竖线）；④ 填入作者与单位信息")
def main() -> None:
    text = SC_PATH.read_text(encoding="utf-8")
    if OLD not in text:
        print("F9 evidence anchor absent (already updated?)")
        return
    SC_PATH.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    print("F9 evidence extended with the formatting checklist")
if __name__ == "__main__":
    main()
