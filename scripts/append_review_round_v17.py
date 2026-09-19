"""Record the seventeenth round: figures verified at the image level."""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "遗漏问题审查报告.md"
SC = ROOT / "重构版论文_v4_20260915" / "论文自查表.md"
ADDITION = """

---

## W. 第十七轮审查（2026-09-19）：图里的数字

图是唯一一处"文本检查完全看不见"的内容：一个过期数字画进 PNG 之后，前面十六轮的脚本都读不到它。本轮专门补上这一层。

### 一、图注数值与正文对照

图的构建脚本把标注写在字符串字面量里，因此可以解析出来与稿件比对。`scripts/check_figure_annotations_v44.py` 用 AST 提取三个绘图脚本（英文图、中文图、图形摘要）的全部字符串字面量，抽出其中的小数与千分位整数，与对应稿件比对。

结果：**三份脚本中所有数据性数值都能在对应稿件中找到**。唯一被报出的"找不到"是 `pad=0.012`、`rounding_size=0.02`、`#444444` 这类样式参数与颜色值，已加入排除规则。该检查已接入闸门。

### 二、插图是否真的由当前代码生成

图脚本里读的是哪一份结果文件同样重要。逐条核查后，所有输入路径都来自规范化目录（`results_rccf_evidence_v3b`、`results_data_audit_cic_natural_v3b`、`results_cic_*_baselines_v3b`、`results_weight_mechanism_v3`、`results_protocol_sensitivity_v4`、`results_diversity_v5`、`results_margin_bound_v5` 等），**没有一处读 `superseded/`**。

随后做了一次更强的验证：把三份脚本全部重跑一遍，与仓库中已提交的 PNG **逐字节比对**——22 张图（英文 11 + 中文 11）与图形摘要全部完全一致，说明提交的插图确实是当前代码的输出。为让这项检查可长期使用，`scripts/check_figure_reproducibility_v45.py` 会在比对后把原始字节写回，保证检查过程不修改工作区。**该检查也已接入闸门，闸门现含 22 类检查。**

（这一轮最初是因为发现图脚本的修改时间晚于 PNG 的生成时间才起疑的。重跑之后确认是版本库检出造成的假象，而非内容过期——但"看起来可疑"和"验证过一致"是两回事，所以补了上面这道检查。）

### 三、渲染稿里的图表

两份 docx 各含 **10 张表、11 张内嵌图片**，无 `[缺图]` 标记，无 TODO/占位符（除作者信息）。图与表在 Word 中均未出现跨页断裂或空白图位。
"""
def main() -> None:
    text = MD.read_text(encoding="utf-8")
    if "## W. 第十七轮审查" not in text:
        MD.write_text(text.rstrip() + ADDITION, encoding="utf-8")
        print("ROUND17_RECORDED")
    else:
        print("already recorded")
    sc = SC.read_text(encoding="utf-8")
    line = next((l for l in sc.splitlines() if l.startswith("| E3 |")), "")
    if line and "check_figure_annotations_v44" not in line:
        new_line = line.rstrip(" |").rstrip() + \
            "；`check_figure_annotations_v44.py` 校验图注数值与正文一致，" \
            "`check_figure_reproducibility_v45.py` 逐字节确认插图可由当前代码复现 |"
        sc = sc.replace(line, new_line, 1)
        SC.write_text(sc, encoding="utf-8")
        print("E3 evidence extended")
    else:
        print("E3 already updated or not found")
if __name__ == "__main__":
    main()
