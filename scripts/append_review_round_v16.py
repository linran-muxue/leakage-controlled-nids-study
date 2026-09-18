"""Record the sixteenth round: the document is now typeset, not just text.
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

## V. 第十六轮审查（2026-09-18）：把排版做掉——公式、表格、斜体

第十五轮第一次渲染 Word，本轮把渲染暴露的问题一并修完，并把"排版"从待办清单上划掉。

### 一、公式：LaTeX 源码 → Word 原生公式

此前 5 个行间公式在 Word 里是 `\\frac{\\exp[-r_e(x)]}{\\sum...}` 这样的**源码文本**（可编辑文本，符合"不使用公式图片"，但显然不是给编辑看的样子）。本轮用 Word COM 把每个公式按其 UnicodeMath 线性形式重建：

| 公式 | 结果 |
|---|---|
| (1) 权重与融合后验 | `exp[...]/∑_(j=1)^Q` 已建成真正的**分式与带上下限的求和** |
| (2) 边距上界 | `‖p_w−p̄‖₁ ≤ Σ… =: Δ(x)`，双竖线与下标正确 |
| (3) 熵亏缺恒等式 | `Q/(2 log Q)‖·‖₂²` 分式与范数正确 |
| (4) 一阶展开 | `Var(δ)/(2 log Q)` 分式正确 |
| (5) 归一化权重熵 | `−(1/log Q)Σ…log…` 正确 |

验证方式不是"看起来像"：脚本检查 docx 包内 `document.xml` 的 `<m:oMath>` 元素，**两份稿件各 5 个原生公式、0 处 LaTeX 残留**；再用 Word 渲染成 PDF、用 PyMuPDF 转成图片亲眼核对分式与编号位置。

过程中修掉两个自伤：① 用 `paragraph.Range` 写文本会把段落标记一起替换，导致公式与下一段合并（渲染图里出现 "Δ(x) (2)Let m(x)…"）；改为排除段落标记后，公式独占一行、编号在行末。② 中文稿还有 11 处**行内** LaTeX（`$\\bar p(x)=\\frac{1}{Q}…$`、`$C\\in\\{0.01,…\\}$` 等），英文稿用的是纯文本记法；已按同样口径改为 `p̄(x) = (1/Q) Σ_e p_e(y|x)` 这类写法，两稿均无 LaTeX 残留。

### 二、表格：去掉竖线

JISA 明确要求"避免竖线和底纹"。生成器原来用 `Table Grid`（全框线），现改为**三线表**：只有顶线、表头下线（`insideH`）与底线，左右与内部竖线显式设为 `none`。10 张表的 XML 已逐张核对。

### 三、斜体标记泄漏

渲染图里出现 `*Proof.*` 原样带星号——生成器只处理 `**粗体**`、`` `代码` `` 与 `$数学$`，**单星号斜体从未处理**。已补上，`*Proof.*`、`*families*` 这类标记现在真正以斜体呈现。

### 四、流水线顺序（重要）

公式转换是 docx 生成之后的**后处理**步骤：

```
build_restructured_manuscript_v4.py  →  convert_equations_word_v41.py  →  校验
```

重新生成 docx 会把公式还原成 LaTeX，因此闸门新增了检查（`check_docx_numbering_v40.py` 同时校验 `<m:oMath>` ≥ 5 且无 `\\frac` 残留）：忘记跑转换会被立即拦下。

### 五、F9 剩余项

公式已为原生公式、表格已为三线表、图形摘要 3300×2280 像素、页边距与单栏符合要求。**仍缺两件只能由作者完成的事**：套用投稿当天的 JISA 官方模板，以及填入作者与单位信息。
"""
def main() -> None:
    text = MD.read_text(encoding="utf-8")
    if "## V. 第十六轮审查" not in text:
        MD.write_text(text.rstrip() + ADDITION, encoding="utf-8")
        print("ROUND16_RECORDED")
    else:
        print("already recorded")
    sc = SC.read_text(encoding="utf-8")
    line = next((l for l in sc.splitlines() if l.startswith("| F9 |")), "")
    if line and "原生公式" not in line:
        new_line = line.rstrip(" |").rstrip() + \
            "；公式已转为 Word 原生公式（每稿 5 个 OMML，无 LaTeX 残留）、表格改为三线表（去竖线）、" \
            "斜体标记已正确渲染；**仅余套用官方模板与填写作者信息** |"
        sc = sc.replace(line, new_line, 1)
        SC.write_text(sc, encoding="utf-8")
        print("F9 evidence updated")
    else:
        print("F9 already updated or not found")
if __name__ == "__main__":
    main()
