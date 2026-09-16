"""Add the dataset-coverage argument and strengthen the contribution positioning."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"


def fix(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"anchor missing: {label}")
    return text.replace(old, new, 1)


EN_COVERAGE = (
    "The three datasets are deliberately complementary rather than interchangeable. They span three capture eras "
    "(a 1998 line of descent for NSL-KDD, a 2015 synthetic testbed for UNSW-NB15 and a 2017 enterprise-like "
    "testbed for CIC-IDS2017), three feature extractors (a 41-feature connection record set, a 49-feature "
    "Argus/Bro-derived set and a 78-feature CICFlowMeter set), and three label spaces (5, 10 and 5 retained "
    "classes). Their known defects also differ: NSL-KDD carries the redundancy of its KDD lineage, UNSW-NB15 "
    "contains largely synthetically generated attacks and cross-split feature overlap, and CIC-IDS2017 contains "
    "duplicate flows, cross-label conflicts and constant columns. A fourth dataset would add most value if it "
    "covered an environment none of the three represents - an IoT or operational-technology deployment, a "
    "different capture vantage point, or a temporally separated capture from the same testbed. The coverage "
    "matrix is reported in the supplementary material.\n\n"
)

EN_POSITION = (
    "\n\nThe contribution is deliberately not incremental. Adding another classifier to an existing benchmark "
    "would answer no open question, because the literature already contains many such comparisons and they "
    "disagree. What the field lacks is a way to decide whether a reported difference is attributable to the "
    "method or to the protocol. This paper supplies that decision procedure in three parts: an auditable "
    "protocol that fixes the information boundary, a set of identifiability conditions that predict when an "
    "aggregation mechanism cannot act at all, and a measured magnitude for each source of variation so that a "
    "reader can see which choices actually move the number. The result is falsifiable - Condition 1 predicts "
    "zero gain for the expert sets used here, and the reverse experiment confirms that prediction - and it is "
    "usable by other authors regardless of which classifier they prefer.\n"
)

ZH_COVERAGE = (
    "三个数据集是刻意互补而非可互相替代的：它们跨越三个采集时期（NSL-KDD 承自 1998 年的数据脉络、"
    "UNSW-NB15 为 2015 年合成测试床、CIC-IDS2017 为 2017 年类企业测试床）、三种特征提取方式"
    "（41 维连接记录、49 维 Argus/Bro 派生特征、78 维 CICFlowMeter 特征）与三套标签体系"
    "（5 类、10 类与 5 类保留标签）。三者的已知缺陷也各不相同：NSL-KDD 带有 KDD 谱系的冗余，"
    "UNSW-NB15 的攻击多为人工合成且存在跨划分特征重叠，CIC-IDS2017 则存在重复流、跨标签冲突与恒定列。"
    "如果要引入第四个数据集，其最大价值在于覆盖三者都未代表的场景——物联网或工业控制环境、"
    "不同的采集观测点，或同一测试床上时间分离的采集。覆盖矩阵见补充材料。\n\n"
)

ZH_POSITION = (
    "\n\n本文的贡献刻意不是增量式的。在既有基准上再增加一个分类器不会回答任何开放问题——"
    "文献中此类比较已经很多，而且彼此矛盾。这个领域真正缺少的是判断「一个被报告的差异究竟来自方法还是来自协议」"
    "的手段。本文从三部分给出这一判断程序：一套固定信息边界的可审计协议；一组预测「聚合机制何时根本无法起作用」"
    "的可辨识性条件；以及为每一类变异来源测出的量级，使读者能看出究竟哪些选择在真正改变数字。"
    "该结论是可证伪的——条件 1 预测本文所用专家集合的增益为零，而反向实验证实了这一预测——"
    "并且无论其他作者偏好哪种分类器，都可直接使用。\n"
)


def main() -> None:
    en_path = BASE / "English_SCI_Manuscript_v4.md"
    en = en_path.read_text(encoding="utf-8")
    anchor = ("The three datasets use incompatible label spaces. Their scores are therefore never pooled, averaged "
              "or interpreted as evidence of transfer.")
    en = fix(en, anchor, EN_COVERAGE + anchor, "en-coverage")
    en = fix(en,
             "We explicitly do **not** claim that RCCF is a better classifier,",
             EN_POSITION.strip() + "\n\nWe explicitly do **not** claim that RCCF is a better classifier,",
             "en-position")
    en_path.write_text(en, encoding="utf-8")

    zh_path = BASE / "中文SCI论文_v4_重构版.md"
    zh = zh_path.read_text(encoding="utf-8")
    zanchor = "三者使用不同的标签体系，其分数因此**不得合并、不得平均、不得解释为迁移成功**。"
    zh = fix(zh, zanchor, ZH_COVERAGE + zanchor, "zh-coverage")
    zh = fix(zh, "我们明确不主张：本文不主张 RCCF 是更优的分类器",
             ZH_POSITION.strip() + "\n\n我们明确不主张：本文不主张 RCCF 是更优的分类器", "zh-position")
    zh_path.write_text(zh, encoding="utf-8")
    print("COVERAGE_AND_POSITIONING_APPLIED")


if __name__ == "__main__":
    main()
