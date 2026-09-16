"""Record the eighth round: the verification gate."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "遗漏问题审查报告.md"

ADDITION = """

---

## N. 第八轮审查（2026-09-17）：验证闸门与自检

第七轮暴露出一个流程缺陷：版本升级脚本因缩进错误静默失败，但提交与打标签照常执行，导致稿件引用的版本与仓库标签不一致。这一轮针对**检查流程本身**做了修补。

### 新增：单一验证闸门 `scripts/verify_all_v8.py`

把此前分散的检查串成一道命令，任一项失败即以非零退出码报错：

| 检查项 | 覆盖内容 |
|---|---|
| unit tests | 118 项单元测试 |
| compile all sources | src / scripts / tests 全量编译 |
| manuscript structure | 图表编号连续性、图片文件存在性、DOI 占位符 |
| citation coverage | 45 条文献的文内覆盖率 |
| number traceability | 63 项关键数字与源文件比对 |
| reference annotations | 无 DOI 标注的出版方一致性 |
| cross-document audit | 新加内容、补充材料清单、Highlights、自查表内部一致性 |
| language consistency | 拼写体系混用检测 |
| release tag | **稿件引用的版本号与最新 git 标签是否一致（本轮新增）** |

### 闸门的故障注入自检

为避免"验证器本身不验证"，对闸门做了一次故障注入：把英文稿中的 `v1.7.0` 临时改为 `v1.4.0`，闸门立即报出两项失败（cross-document audit、release tag）并以退出码 1 结束；恢复后重新通过。**验证器已验证有效。**

### 本轮同时修正的两处闸门误报

- 结构检查的失败标记字符串过短，会匹配到通过输出，已改为精确匹配。
- 参考文献标注检查未接受 JSTOR 稳定标识作为 1979 年 Scandinavian Journal of Statistics 条目的正确句柄，已加入该例外。

### 本轮未发现新的论文内容问题

对全部枚举式表述做了分区计数核对：英文 §5.2 五项读数、§5.3 六组测量、§6.1 三个条件、§7 三条结论，以及四项贡献、八条报告建议、五组对照，**声明数量与实际条目全部一致**。中文稿使用"第一，**…**"格式（序数在加粗之外），属中英排版差异，非错误。
"""


def main() -> None:
    text = MD.read_text(encoding="utf-8")
    if "## N. 第八轮审查" in text:
        print("already recorded")
        return
    MD.write_text(text.rstrip() + ADDITION, encoding="utf-8")
    print("ROUND8_RECORDED")


if __name__ == "__main__":
    main()
