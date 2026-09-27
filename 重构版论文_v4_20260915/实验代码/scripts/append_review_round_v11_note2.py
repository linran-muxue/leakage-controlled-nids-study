"""Add the front-matter and planning-document findings to the eleventh round."""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "遗漏问题审查报告.md"
ADDITION = """
### 同轮续查（第七处）：投稿前置材料与内部规划文档

继续沿"辅助文档是否与稿件一致"往下查，投稿前置材料（编辑先读的部分）和内部规划文档也有问题：

| 文档 | 问题 | 处置 |
|---|---|---|
| `Highlights_v4.md` | 第 5 条写「协议差异 0.073」，稿件用的是 0.0725 | 改为 0.0725 |
| `Cover_Letter_JISA_v4.md` | 「decision margins roughly 3,500 times that bound」——与稿件中已修正的粗略比值同源 | 改为「median decision margin 3,469 to 5,038 times that bound」 |
| `Cover_Letter_JISA_v4.md` | 引用「release v1.2.0, tag v1.2.0」 | 改为 v1.10.0 |
| `Cover_Letter_JISA_v4.md` | 「protocol effects **exceed model effects** by an order of magnitude」——正是第九轮从正文中收窄掉的那句过度声称，投稿信里还留着 | 改为「protocol choices exceed **aggregation-rule** differences by an order of magnitude, while model-family differences remain larger still」 |
| 三份内部规划文档 | 仍以「当前稿子最大的逻辑漏洞」「P0 八项待办」的口吻书写，与已完成的事实冲突 | 统一在文首加「状态说明」，声明其为 2026-09-15 审计快照，当前状态以自查表与审查报告为准 |

投稿信是编辑读到的第一份文件，它保留被正文否定的结论，比正文写错更危险。

新增 `scripts/check_aux_documents_v13.py` 并接入闸门：把 Highlights 与投稿信的**全部数值 token** 与两份稿件比对（投稿信曾出现稿件中不存在的 3500），校验其中的发布标签，并检查三份规划文档是否带有状态说明。闸门现含 **13 类检查**。
"""
def main() -> None:
    text = MD.read_text(encoding="utf-8")
    if "同轮续查（第七处）" in text:
        print("already recorded")
        return
    MD.write_text(text.rstrip() + ADDITION, encoding="utf-8")
    print("ROUND11_NOTE2_RECORDED")
if __name__ == "__main__":
    main()
