"""Record the fourteenth round: the character- and word-level sweep."""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "遗漏问题审查报告.md"
SC = ROOT / "重构版论文_v4_20260915" / "论文自查表.md"
ADDITION = """

---

## T. 第十四轮审查（2026-09-18）：逐字检查

这一轮降到字符层：**不可见字符、全半角混用、重复词、括号与加粗标记配对、单位空格、连字符修饰语、标点宽度**。检查器 `scripts/proofread_char_level_v33.py` 会跳过代码块与行间公式，因为数学记号里本来就会出现散文规则会误报的序列。

### 发现并修好的一处概念性错误

中文稿把交叉拟合产生的 **out-of-fold 概率**写成「**袋外**概率」——5 处（§4.2 交叉拟合风险模型、§4.3 第一步与第二步、算法 1 第 2 步与第 3 步）。「袋外」（out-of-bag）在集成学习里指自助抽样的袋外样本，与 K 折交叉拟合的折外预测是两个不同的量。术语错误会直接影响方法可复现性——读者按"袋外"理解就会以为描述子来自随机森林的自助采样。已全部改为「折外」，而 §2.3 中真正指 out-of-bag 误差加权的那一处「袋外误差」保留不动。

### 其余字符层修正

| 位置 | 问题 | 处置 |
|---|---|---|
| 算法 1 第 2 步（中英各 1 处） | 四个视图写成 `{full, chi2, MI, ANOVA}`，而 §4.1 定义处写 `chi-square` / `χ²` | 统一为 `chi-square` / `χ²` |
| 中文 §5.3 测量五 | 集合内用半角逗号「全量, 仅熵, 仅边距」 | 改为中文顿号「全量、仅熵、仅边距」 |
| 中文 §4.3 命题 2/3 证明开头 | 「证明.」用半角句点 | 改为「证明。」 |

### 确认无问题的项（逐字扫描）

- **不可见字符**：两稿与前置材料均无零宽空格、BOM、不换行空格、制表符。
- **全角字母数字**：0 处。
- **中英混排空格**：CJK 与拉丁字母之间 0 处缺空格。
- **英文拼写体系**：`normalised/randomised/generalisation/behaviour/artefact` 全用英式；唯一的 `randomized` 与三处 `generalization` 都出现在**参考文献标题**里，须保留原拼写；四处 `data set` 同样只出现在标题中。
- **负号**：英文 27 处用 ASCII 连字符、中文 20 处用 U+2212，各自内部一致。
- **范围连接符**：中文对数值范围用短横线、对引用范围用连字符，规则自洽；英文正文与参考文献一律用连字符。**未做批量替换**——参考文献页范围里混着 DOI（如 `s10994-006-6226-1`），盲替换会破坏 DOI，风险远大于收益。这一条已写入 F9 排版清单。

### 新增防护

`scripts/proofread_char_level_v33.py` 已接入闸门（失败标记 `CHAR_LEVEL_FINDINGS`），闸门现含 **19 类检查**。自查表 E5「术语与缩写一致」的证据补入本轮修正与脚本。
"""
E5_OLD = "| E5 | 术语与缩写一致 | 首现展开、中英一致 | **通过** | RF/MLP/MI/ANOVA/Mondrian/AUROC/CV 首现已展开；"
def main() -> None:
    text = MD.read_text(encoding="utf-8")
    if "## T. 第十四轮审查" not in text:
        MD.write_text(text.rstrip() + ADDITION, encoding="utf-8")
        print("ROUND14_RECORDED")
    else:
        print("already recorded")
    sc = SC.read_text(encoding="utf-8")
    line = next((l for l in sc.splitlines() if l.startswith("| E5 |")), "")
    if line and "proofread_char_level_v33" not in line:
        new_line = line.rstrip(" |").rstrip() + "；`scripts/proofread_char_level_v33.py` 逐字检查两稿与前置材料" \
                   "（不可见字符、全半角、重复词、括号配对、单位空格、连字符修饰语），并修正中文「袋外/折外」概念错用 5 处 |"
        sc = sc.replace(line, new_line, 1)
        SC.write_text(sc, encoding="utf-8")
        print("E5 evidence extended")
    else:
        print("E5 already updated or not found")
if __name__ == "__main__":
    main()
