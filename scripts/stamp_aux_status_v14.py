"""Stamp the three internal planning documents with their current status.
研究缺口审计与优先级清单, P0_P1执行手册 and 论文结构诊断与重构方案 are dated
snapshots from 2026-09-15. Read on their own today they contradict the released
state: the audit still calls the missing equivalence test "当前稿子最大的逻辑
漏洞", and the manual still presents P0 as future work. Each one now carries the
same status block at the top, pointing to the authoritative files.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
MARKER = "> **状态说明"
STAMP = """> **状态说明（2026-09-17 更新）**
>
> 本文档是 **2026-09-15 的审计快照**，保留当时的判断、命令与优先级，便于追溯"为什么要做这些事"。
> 截至当前版本，快照中列出的 P0/P1 缺口与阶段 1–3 的任务已绝大部分完成（少数为作者信息与期刊模板这类外部输入）。
> 当前状态以下列文件为准，本文档不再单独代表最新进度：
>
> - `论文自查表.md`：66 项检查，62 项通过、4 项部分通过、0 项缺失；含每项的证据文件。
> - `遗漏问题审查报告.md`：第一至第十一轮的逐轮记录、发现的问题与处置方式。
> - `English_SCI_Manuscript_v4.md` / `中文SCI论文_v4_重构版.md`：正式稿件，v1.10.0。
>
> 建议阅读顺序：先看自查表结论 → 再看审查报告对应轮次 → 最后把本文档当作历史任务清单与命令参考。
"""
DOCS = ["研究缺口审计与优先级清单.md", "P0_P1执行手册.md", "论文结构诊断与重构方案.md"]
def main() -> None:
    for name in DOCS:
        path = BASE / name
        text = path.read_text(encoding="utf-8")
        if MARKER in text:
            print(f"{name}: already stamped")
            continue
        lines = text.splitlines()
        insert_at = 1 if lines and lines[0].startswith("#") else 0
        new = lines[:insert_at] + ["", STAMP.rstrip()] + lines[insert_at:]
        path.write_text("\n".join(new) + "\n", encoding="utf-8")
        print(f"{name}: stamped")
if __name__ == "__main__":
    main()
