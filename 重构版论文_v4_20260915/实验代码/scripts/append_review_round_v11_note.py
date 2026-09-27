"""Add the manifest finding to the eleventh review round."""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "遗漏问题审查报告.md"
ADDITION = """
### 同轮续查（第六处）：发布清单 MANIFEST.json

顺着"辅助文档是否与产物一致"这条线继续查，发布清单里也有两处同类问题：

| 位置 | 清单中的陈述 | 实际 | 性质 |
|---|---|---|---|
| `public_release_tag` | `v1.0.2` | 实际发布标签已到 `v1.10.0` | 字面量写死，八个版本未更新 |
| `canonical_manuscript` | `results_paper_materials_v3/english_sci_manuscript_final.docx` | 当前正稿为 `重构版论文_v4_20260915/English_SCI_Manuscript_v4.docx` | 指向已被取代的旧稿 |

处置：

1. `build_publication_manifest.py` 改为**从 git 标签推导** `public_release_tag`（失败时回退到稿件引用的标签），不再写死版本号；`canonical_manuscript` 改指 v4 正稿，并新增 `canonical_manuscript_zh`；同时把两份 v4 文档加入哈希清单。
2. 新增 `scripts/check_publication_manifest_v12.py`：校验清单标签 = 最新标签 = 稿件引用标签，校验 canonical 路径为正稿，并**逐条重算清单中全部 80 个 SHA-256**。任何一份产物被改动而清单未重建，都会在提交前失败。
3. 该检查并入验证闸门，闸门现含 **12 类检查**。
"""
def main() -> None:
    text = MD.read_text(encoding="utf-8")
    if "同轮续查（第六处）" in text:
        print("already recorded")
        return
    MD.write_text(text.rstrip() + ADDITION, encoding="utf-8")
    print("ROUND11_NOTE_RECORDED")
if __name__ == "__main__":
    main()
