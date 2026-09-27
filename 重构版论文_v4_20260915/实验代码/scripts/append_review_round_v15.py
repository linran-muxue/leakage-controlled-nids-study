"""Record the fifteenth round: prose polish and verification against Word.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "遗漏问题审查报告.md"
SC = ROOT / "重构版论文_v4_20260915" / "论文自查表.md"
ADDITION = """

---

## U. 第十五轮审查（2026-09-18）：精修，以及第一次真正"看"交付文件

前十四轮检查的都是**源文件**（Markdown）。这一轮换了两件事：一是句级精修，二是**把 Word 文件真正渲染出来看**——本机装有 Word 16.0，可通过 COM 导出 PDF，于是"交付物长什么样"第一次成为可核验的对象。

### 一、Word 渲染暴露的真实缺陷（此前十四轮全部漏检）

导出 PDF 后逐行读取渲染结果，发现**编号列表跨全文连续计数**：

| 列表 | 应当 | 实际渲染 |
|---|---|---|
| §1.4 四项贡献 | 1–4 | 1–4 ✓ |
| §4.2 协议五项 | 1–5 | **5–9** ✗ |
| 算法 1 六步 | 1–6 | 1–6 ✓（在代码块内） |
| §4.5 对照五项 | 1–5 | **10–14** ✗ |
| §6.2 四种解释 | 1–4 | 15–18 ✗ |
| §6.4 八条建议 | 1–8 | 19–26 ✗ |

原因是所有列表段落共用 `List Number` 样式，Word 以样式级计数器累计。已在生成器中为**每个列表分配独立 numId 并加 `startOverride`**（只换 numId 不够：Word 按抽象编号定义计数，必须显式要求从 1 重开）。重渲染确认六段列表现已全部从 1 开始。

这条缺陷的性质值得记下：**它对所有只读 Markdown/XML 的检查都是不可见的**——文件里没有任何"错误文本"，错的是 Word 的呈现逻辑。十四轮没人看到，是因为十四轮都没打开过文件。

新增 `scripts/check_docx_numbering_v40.py` 并接入闸门：逐份 docx 检查每个编号段落是否有 numId、不同列表是否共用 numId、每个 numId 是否带 startOverride。闸门现含 **20 类检查**。

### 二、句级精修

| 位置 | 修改 |
|---|---|
| §5.2 表 5 评注 | 删除与紧随其后的「Third」条目重复的「相对全特征森林」一段，标题由"三行值得说明"改为"表 5 中有两行值得说明" |
| §6.5 局限性 | 「既不等于全语料，也不代表真实网络先验」与 §3.2 边界声明**逐字重复**，改写为"因此二者是审计流程的产物，而不是运行网络的样本" |
| §6.2 划分噪声 | 与 §5.4 近乎重复的表述（相似度 0.71）改写为「十次重复划分会让 Macro-F1 波动约 0.011，超过…；只有模型族差距…更大」 |
| 全文 | 删除 3 处 "Note that"、1 处 "very"、1 处「值得注意的是」等填充式引导；§5.3 measurement 1 的"移动幅度极小"改为"只移动了一点" |

另用相似度扫描（`scripts/find_near_duplicates_v37.py`，内容词 Jaccard ≥ 0.5）复核：余下 3 对高相似句分别是**摘要—结论**与**结果—讨论**的正常呼应，不是冗余。

### 三、渲染层面的其它确认

英文稿 30 页 / 12 236 词；中文稿 29 页。图片全部嵌入、表格未跨页断裂、行间公式以等宽数学字体显示（仍为 LaTeX 源码文本，转原生公式列入 F9）。文档启用了**连续行号**（便于审稿引用），如需关闭可在生成器中一行改掉。
"""
def main() -> None:
    text = MD.read_text(encoding="utf-8")
    if "## U. 第十五轮审查" not in text:
        MD.write_text(text.rstrip() + ADDITION, encoding="utf-8")
        print("ROUND15_RECORDED")
    else:
        print("already recorded")
    sc = SC.read_text(encoding="utf-8")
    old = "| F9 | 图形摘要与投稿信 | 与现主线一致 | **部分通过** |"
    line = next((l for l in sc.splitlines() if l.startswith("| F9 |")), "")
    if line and "check_docx_numbering_v40" not in line:
        new_line = line.rstrip(" |").rstrip() + \
            "；编号列表已改为每表独立计数（`scripts/check_docx_numbering_v40.py`，Word 渲染核验） |"
        sc = sc.replace(line, new_line, 1)
        SC.write_text(sc, encoding="utf-8")
        print("F9 evidence extended")
if __name__ == "__main__":
    main()
