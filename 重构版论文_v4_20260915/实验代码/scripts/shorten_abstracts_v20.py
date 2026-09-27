"""Bring the abstracts inside the JISA limit of 250 English words.
The submitted abstract was 422 words, which the journal's Guide for Authors
rules out. Both languages are rewritten together so that the two manuscripts
keep an identical set of numeric claims and the cross-language check still
passes.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN_ABSTRACT = (
    "Reported performance differences between intrusion-detection models are highly sensitive to "
    "duplicate flows, conflicting labels, feature leakage and class priors. We test a widely "
    "adopted but rarely validated assumption: that fusing random-forest experts with "
    "sample-specific reliability weights (RCCF) beats equal voting. Under one "
    "leakage-controlled protocol we build a 53,237-flow natural-prior population and a 3,365-flow "
    "balanced control from CIC-IDS2017, add NSL-KDD and UNSW-NB15 as independent "
    "benchmarks, and compare four feature views over ten seeds. On the natural-prior protocol the "
    "two models differ by -0.00046 Macro-F1, with five seeds up and five down; the seed-level 90% "
    "interval [-0.00112, +0.00021] and the test-row paired bootstrap interval [-0.00425, +0.00338] "
    "both lie inside equivalence margins of 0.005 and 0.01. The four experts disagree on no test "
    "row and the learned weights have a normalised entropy of 0.99998, while class prior and "
    "deduplication order move Macro-F1 by +0.072 and up to +0.0060. Three identifiability "
    "conditions are derived; one becomes a row-wise bound: 99.91% of the 23,958 test rows are "
    "provably invariant, with a median decision margin 3,469 to 5,038 times that bound. All 108 "
    "gate configurations yield six distinct validation scores, excluding insufficient tuning; the "
    "gain is governed by expert diversity (slope 0.0646, r = 0.749). The mechanism is 4.1 "
    "times larger and 4.6 times slower per row than one forest, with no cost-sensitive advantage "
    "from 1:1 to 100:1. We contribute a reusable leakage-controlled protocol, an identifiability "
    "boundary and a quantitative map separating protocol effects from aggregation-rule "
    "differences; the evidence supports neither superiority nor production readiness."
)
ZH_ABSTRACT = (
    "公开入侵检测数据集上报告的模型性能差异，对重复样本、标签冲突、特征选择泄漏与类别先验高度敏感。"
    "本文检验一个被广泛采用却缺少受控验证的假设：按样本估计的可靠性权重对多个随机森林专家做条件加权"
    "融合（RCCF），能否稳定优于等权投票。在统一的泄漏受控协议下，我们用 CIC-IDS2017 构造 53 237 条"
    "自然先验总体与 3 365 条平衡控制总体，并以 NSL-KDD 与 UNSW-NB15 作为独立原生标签基准，在十个种子"
    "上比较四种特征视图。自然先验协议上，二者 Macro-F1 平均差为 −0.00046，逐种子方向五正五负；"
    "种子级 90% 区间 [−0.00112, +0.00021] 与测试行级配对 Bootstrap 区间 [−0.00425, +0.00338] "
    "均落在 0.005 与 0.01 的等价边界内。四个专家在测试集上无任何预测分歧，权重归一化熵为 0.99998；"
    "类别先验与去重顺序分别带来 +0.072 与至多 +0.0060 的变化。我们给出三个可辨识性条件，并把其中"
    "之一化为可逐行计算的判据：23 958 条测试样本中 99.91% 可证明不受权重影响，决策边距中位数为扰动"
    "上界的 3469 至 5038 倍。108 种门控配置只产生 6 个不同的验证集取值，排除了调参不足；增益受"
    "专家多样性支配（斜率 0.0646，r = 0.749）。该机制体积是单个"
    "等权森林的 4.1 倍、单行慢 4.6 倍，在 1:1 至 100:1 的代价比下没有代价敏感优势。本文的贡献在于"
    "一套可复用的泄漏受控协议、一组可辨识性边界，以及一张把协议效应与聚合规则差异分开量化的地图；"
    "证据不支持算法优越性或生产可用性的主张。"
)
def replace_abstract(text: str, heading: str, new_body: str) -> str:
    start = text.index(heading) + len(heading)
    rest = text[start:]
    end = rest.index("\n## ")
    old = rest[:end]
    return text[:start] + "\n\n" + new_body + "\n" + rest[end:]
def main() -> None:
    en_path = BASE / "English_SCI_Manuscript_v4.md"
    zh_path = BASE / "中文SCI论文_v4_重构版.md"
    en = replace_abstract(en_path.read_text(encoding="utf-8"), "## Abstract", EN_ABSTRACT)
    zh = replace_abstract(zh_path.read_text(encoding="utf-8"), "## 摘要", ZH_ABSTRACT)
    en_path.write_text(en, encoding="utf-8")
    zh_path.write_text(zh, encoding="utf-8")
    print(f"EN abstract words: {len(EN_ABSTRACT.split())}")
    print(f"ZH abstract chars: {len(re.sub(r'[[:space:]]', '', ZH_ABSTRACT))}")
if __name__ == "__main__":
    main()
