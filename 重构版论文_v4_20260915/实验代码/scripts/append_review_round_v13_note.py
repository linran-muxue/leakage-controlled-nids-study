"""Add the cross-reference and retired-artifact findings to round thirteen."""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "遗漏问题审查报告.md"
SC = ROOT / "重构版论文_v4_20260915" / "论文自查表.md"
ADDITION = """

### 同轮续查（第十一处）：交叉引用与已废弃证据的隔离

本轮另外查了两件此前从未查过的事：

**（一）章节与公式的交叉引用是否指向真实存在的目标。** 稿件正文里有 15 处（英文）/ 9 处（中文）「Section X.Y」式引用，以及 5 处公式引用。逐条比对后全部有效，无悬空引用。该检查写成 `scripts/check_section_refs_v32.py` 并入闸门——它拦的正是"改了小节编号却忘了改引用"这类事故。

**（二）审计脚本是否会扫到已废弃的证据。** `audit_selective_reporting_v5.py` 的用途是"扫描全部结果表，看有没有藏着对条件加权有利、但正文没报告的结果"。它以 `rglob("*.csv")` 扫描整个仓库，于是把 `superseded/` 里 5 张**旧鲁棒性协议**的表也扫了进去，在"条件机制的劣势"排行榜上把已废弃数字（−0.12 Macro-F1）排在最前面。

这不是稿件的问题，而是**审计工具本身会把退役证据当成现役证据**——比稿件写错更难发现，因为脚本跑起来很正常。处置：扫描跳过 `superseded/` 并在输出中说明跳过了几张表。修正后同一份扫描给出的最大劣势来自共享扰动协议下的 `robustness_shared.csv`（RCCF 0.692 对极端随机树 0.801），而这正是正文 §5.6 明确报告过的"极端随机树更鲁棒"。

### 自查表更新

E4「编号与交叉引用」的证据补入 `check_section_refs_v32.py`；闸门现含 **18 类检查**（另加发布标签一致性校验）。
"""
E4_OLD = "| E4 | 编号与交叉引用 | 连续、无悬空 | **通过** | 图 1–11、表 1–7 连续无缺无重；中英一致；引用的图片文件全部存在 |"
E4_NEW = ("| E4 | 编号与交叉引用 | 连续、无悬空 | **通过** | 图 1–11、表 1–7 连续无缺无重；中英一致；"
          "引用的图片文件全部存在；`scripts/check_section_refs_v32.py` 另校验 15 处（英文）/ 9 处（中文）"
          "章节引用与 (1)–(5) 公式引用均指向真实目标 |")
def main() -> None:
    text = MD.read_text(encoding="utf-8")
    if "同轮续查（第十一处）" not in text:
        MD.write_text(text.rstrip() + ADDITION, encoding="utf-8")
        print("ROUND13_NOTE_RECORDED")
    else:
        print("already recorded")
    sc = SC.read_text(encoding="utf-8")
    if E4_OLD in sc:
        SC.write_text(sc.replace(E4_OLD, E4_NEW, 1), encoding="utf-8")
        print("E4 evidence extended")
    else:
        print("E4 anchor absent (already updated?)")
if __name__ == "__main__":
    main()
