"""Add the graphical-abstract and public-metadata findings to round eleven."""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "遗漏问题审查报告.md"
ADDITION = """
### 同轮续查（第八处）：图形摘要与公开仓库元数据

第八项是本轮最不该出现的一处：**图形摘要的标题仍是已被本文数据证伪的旧标题**。

| 文档 | 问题 | 处置 |
|---|---|---|
| `Graphical_Abstract_v4.png/pdf` | 大标题「Protocol sensitivity dominates **model choice** in flow-based NIDS」——第九轮已把稿件标题收窄为 aggregation-rule differences，图形摘要未同步 | 重绘，标题改为「…dominates aggregation-rule differences…」 |
| `Graphical_Abstract_v4.png/pdf` | 面板 C 注记「margins exceed the perturbation bound by about **3,500x**」 | 改为「3,469-5,038x」 |
| `README.md` | 「Submission release: `v1.0.2`（tag present in the local checkout; verify the remote tag before submission）」 | 改为 `v1.10.0`，并写明已推送 |
| `README.md` | 首段引用的稿件标题是 *Provenance-Aware and Uncertainty-Aware Evaluation…*——一份**已不存在的旧稿** | 改为当前标题 |
| `CITATION.cff` | `version: "1.2.0"`、`date-released: 2026-09-16`，标题为泛化描述 | 版本改为 1.10.0、日期更新、标题指向当前稿件 |
| `docs/` 下 5 份「看起来仍有效」的历史文档 | `final_submission_gate_v2` 仍写「稿件当前引用 tag v1.0.2」「参考文献 24 条」「补充材料 S1–S15」 | 统一加历史记录状态说明 |

图形摘要会被编辑与审稿人**先于正文**看到，它宣示一个正文已经否定的结论，是这份材料里传播风险最高的一处不一致。

`build_graphical_abstract_v5.py` 原先只输出 PNG，PDF 属于游离产物，现已改为同时输出 PNG 与 PDF，二者同源。`check_aux_documents_v13.py` 相应增加了图形摘要源码与公开元数据的检查：源码不得出现旧标题或 3,500，README 不得出现旧标签与旧标题，CITATION.cff 版本必须等于最新标签。
"""
def main() -> None:
    text = MD.read_text(encoding="utf-8")
    if "同轮续查（第八处）" in text:
        print("already recorded")
        return
    MD.write_text(text.rstrip() + ADDITION, encoding="utf-8")
    print("ROUND11_NOTE3_RECORDED")
if __name__ == "__main__":
    main()
