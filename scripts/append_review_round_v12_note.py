"""Add the supplementary-citation finding to the twelfth round."""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "遗漏问题审查报告.md"
ADDITION = """

### 同轮续查（第十处）：补充材料没有被正文引用

JISA 明确要求「补充材料：正文必须引用每个补充文件」。核查结果是：**正文里一次都没有出现补充材料编号**——S01–S26 只出现在文末的清单表里，图表与正文全都指向不到它们。审稿人若要核对某个数字的原始证据，只能自己在那张表里翻。

处置：按内容归属，在七个小节各补一句分组引用，并在参考文献的核验说明后补一句 S24 指引，26 个条目**全部被正文引用**且不重复引用：

| 位置 | 引用 |
|---|---|
| §4.1 特征视图与基学习器 | S01–S04（来源校验、逐文件计数、类别支持、特征得分） |
| §4.3 可辨识性 | S17、S25（逐行边距上界、命题 3 定量验证） |
| §5.2 主结果 | S05–S07、S20（逐种子指标、逐类别报告、混淆矩阵、等价性检验） |
| §5.3 机制诊断 | S08–S09、S16、S18（权重记录、门控搜索、多样性实验） |
| §5.4 协议敏感性 | S10–S11（协议对照、嵌套交叉验证） |
| §5.5 外部有效性 | S12–S14、S19（两个外部基准、文件级外推、神经基线） |
| §5.6 次生指标 | S15、S21–S23、S26（校准/鲁棒性/延迟、近重复、资源、代价敏感、扩展鲁棒性） |
| 参考文献说明 | S24（DOI 逐条核验记录） |

该覆盖已写入 `scripts/check_jisa_format_v22.py`：正文若漏引任一补充条目，闸门即报 `JISA_FORMAT_MISMATCH`。

同轮还核对了图表引用：11 张图与 7 个编号表在两种语言中**全部被正文引用**，无孤儿图表。
"""
def main() -> None:
    text = MD.read_text(encoding="utf-8")
    if "同轮续查（第十处）" in text:
        print("already recorded")
        return
    MD.write_text(text.rstrip() + ADDITION, encoding="utf-8")
    print("ROUND12_NOTE_RECORDED")
if __name__ == "__main__":
    main()
