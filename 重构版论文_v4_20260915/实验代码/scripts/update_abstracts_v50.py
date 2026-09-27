"""Rewrite both abstracts around the scale check and the fourth dataset.
The English abstract sits at the JISA limit of 250 words, so the new evidence is
paid for by dropping the interval endpoints (they remain in Section 5.2) and
the tuning-margin aside. Both languages keep the same set of numeric claims.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN = (
    "Reported performance differences between intrusion-detection models are sensitive to duplicate "
    "flows, conflicting labels, feature leakage and class priors. We test a widely adopted but rarely "
    "validated assumption: that fusing random-forest experts with sample-specific reliability weights "
    "(RCCF) beats equal voting. Under one leakage-controlled protocol we build a 53,237-flow "
    "natural-prior population and a 3,365-flow balanced control from CIC-IDS2017, add NSL-KDD, "
    "UNSW-NB15 and an IoT corpus as independent benchmarks, and compare four feature views "
    "over ten seeds. The two models differ by -0.000456 Macro-F1 (five up, five down); the "
    "seed-level 90% and test-row paired bootstrap intervals both lie inside equivalence margins of "
    "0.005 and 0.01. The four experts disagree on no test row, the learned weights have a normalised "
    "entropy of 0.99998, and class prior and deduplication order move Macro-F1 by +0.0725 and "
    "+0.0060. Three identifiability conditions are derived, one becoming a row-wise bound: 99.91% of "
    "the 23,958 test rows are provably invariant, with a median decision margin 3,469 to 5,038 times "
    "that bound. All 108 gate configurations yield six distinct validation scores; the gain is "
    "governed by expert diversity (slope 0.0646, r = 0.749). The equivalence reproduces on a "
    "population 7.8 times larger and on the IoT corpus, where every model exceeds 0.9998 Macro-F1. "
    "The mechanism is 4.1 times larger and 4.6 times lower in throughput than one forest, with no "
    "cost-sensitive advantage. We contribute a reusable leakage-controlled protocol, an "
    "identifiability boundary and a quantitative map separating protocol effects from aggregation-rule "
    "differences; the evidence supports neither superiority nor production readiness."
)
ZH = (
    "公开入侵检测数据集上报告的模型性能差异，对重复样本、标签冲突、特征选择泄漏与类别先验高度敏感。"
    "本文检验一个被广泛采用却缺少受控验证的假设：按样本估计的可靠性权重对多个随机森林专家做条件加权"
    "融合（RCCF），能否稳定优于等权投票。在统一的泄漏受控协议下，我们用 CIC-IDS2017 构造 53 237 条"
    "自然先验总体与 3 365 条平衡控制总体，并以 NSL-KDD、UNSW-NB15 与一个物联网僵尸网络语料作为独立"
    "基准，在十个种子上比较四种特征视图。二者 Macro-F1 平均差为 −0.000456（五正五负），种子级 90% "
    "区间与测试行级配对 Bootstrap 区间均落在 0.005 与 0.01 的等价边界内。四个专家在测试集上无任何"
    "预测分歧，权重归一化熵为 0.99998；类别先验与去重顺序分别带来 +0.0725 与至多 +0.0060 的变化。"
    "我们给出三个可辨识性条件，并把其中之一化为可逐行计算的判据：23 958 条测试样本中 99.91% 可证明"
    "不受权重影响，决策边距中位数为扰动上界的 3469 至 5038 倍。108 种门控配置只产生 6 个不同的验证"
    "集取值，增益受专家多样性支配（斜率 0.0646，r = 0.749）。该等价性在总体扩大 7.8 倍与物联网语料上"
    "同样成立，后者所有模型的 Macro-F1 均超过 0.9998。该机制体积是单个等权森林的 4.1 倍、吞吐低 "
    "4.6 倍，没有代价敏感优势。本文的贡献在于一套可复用的泄漏受控协议、一组可辨识性边界，以及一张"
    "把协议效应与聚合规则差异分开量化的地图；证据不支持算法优越性或生产可用性的主张。"
)
def replace(path: Path, heading: str, keyword: str, text: str, label: str) -> None:
    content = path.read_text(encoding="utf-8")
    start = content.index(heading) + len(heading)
    rest = content[start:]
    end = rest.index("\n## ")
    block = rest[:end]
    tail = block[block.index(keyword):]
    path.write_text(content[:start] + "\n\n" + text + "\n\n" + tail.lstrip("\n") + rest[end:],
                    encoding="utf-8")
    print(f"{label}: abstract replaced ({len(text.split())} words)")
def main() -> None:
    if len(EN.split()) > 250:
        raise SystemExit(f"English abstract is {len(EN.split())} words, limit is 250")
    replace(BASE / "English_SCI_Manuscript_v4.md", "## Abstract", "**Keywords:**", EN, "EN")
    replace(BASE / "中文SCI论文_v4_重构版.md", "## 摘要", "**关键词：**", ZH, "ZH")
if __name__ == "__main__":
    main()
