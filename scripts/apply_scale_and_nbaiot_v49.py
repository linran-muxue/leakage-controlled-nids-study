"""Write the scale-sensitivity and fourth-dataset results into both manuscripts.
Content added: the 413,209-flow CIC population (7.8x) with its ten-seed paired
analysis, the N-BaIoT IoT benchmark, updated coverage and limitation text, and
the two new supplementary items.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

SECTION_EN = """### 5.7 Scale and domain sensitivity

The primary population is a capped subset, so the equivalence reported above could in principle be an artefact of that cap. Two further runs address the question directly.

**A population 7.8 times larger.** Rebuilding the CIC-IDS2017 population with the identical audit but a 200,000-per-class cap yields 413,209 flows (train 289,246 / validation 61,982 / test 61,982). The minority classes cannot grow, so the enlarged population is more imbalanced than the primary one: Brute Force contributes 10,620 rows, Bot 1,948 and Web Attack 673. The headline pair was re-run over the full ten seeds. RCCF averages 0.856065 Macro-F1 against 0.857202 for the equal-weight chi-square forest, a mean paired difference of -0.001137 (SD 0.003156; seed-level 90% interval [-0.002966, +0.000692]). TOST is significant at both pre-specified margins (p = 0.0019 at 0.005, p = 4.8e-6 at 0.01), so the equivalence statement survives a 7.8-fold increase in population size; the point estimate now favours the control slightly rather than RCCF. The two arms disagree on 20-29 of the 61,982 test rows per seed (0.03%-0.05%), the same order as on the primary population. The context baselines behave as before: XGBoost reaches 0.827656 Macro-F1, extremely randomised trees 0.783747, an equal-weight full-feature forest 0.852953 and a depth-limited decision tree 0.809695.

**A fourth dataset from a different domain.** N-BaIoT records benign traffic and Mirai/Gafgyt botnet activity from nine consumer IoT devices with 115 flow-statistics features [17,18]. Deduplication removes 4,784,430 of 7,062,606 rows (67.8%), a higher duplicate share than any other dataset here, leaving a 180,000-flow three-class benchmark (60,000 per class; train 126,000 / validation 27,000 / test 27,000). Every model reaches at least 0.99983 Macro-F1: RCCF and the equal-weight chi-square forest are identical to machine precision (mean difference -3.7e-17, with 0-2 disagreements among 27,000 test rows). The benchmark is saturated for flow-feature classifiers, which is precisely the regime in which Condition 1 predicts that no weighting can act: it confirms the mechanism's inertness in a new domain without testing discrimination difficulty.

Together the two runs bound the result from both sides: the equivalence is not an artefact of the 53,237-flow cap, and it reproduces in a domain whose classes are trivially separable.

"""

SECTION_ZH = """### 5.7 规模与领域敏感性

主研究总体是带截断的子集，因此上文报告的等价性原则上可能是该截断造成的。以下两组实验直接回答这一质疑。

**总体扩大 7.8 倍。** 用完全相同的审计流程、仅把每类上限提高到 20 万条，重建 CIC-IDS2017 总体得到 413 209 条（训练 289 246 / 验证 61 982 / 测试 61 982）。少数类无法增长，因此扩大后的总体反而更不平衡：Brute Force 贡献 10 620 条、Bot 1 948 条、Web Attack 673 条。头条对照按完整的十个种子重跑：RCCF 平均 Macro-F1 为 0.856065，等权卡方森林为 0.857202，平均配对差 −0.001137（标准差 0.003156；种子级 90% 区间 [−0.002966, +0.000692]）。TOST 在两个预设边界上均显著（0.005 边界 p = 0.0019，0.01 边界 p = 4.8e-6），即等价性结论在总体扩大 7.8 倍后依然成立；此时点估计略微偏向等权森林而非 RCCF。两个分支每个种子在 61 982 条测试样本中仅有 20 至 29 条分歧（0.03%–0.05%），与主总体同量级。其余基线的表现与之前一致：XGBoost 为 0.827656、极端随机树为 0.783747、全特征等权森林为 0.852953、限深决策树为 0.809695。

**不同领域的第四个数据集。** N-BaIoT 记录了九种消费级物联网设备上的正常流量与 Mirai/Gafgyt 僵尸网络流量，含 115 维流统计特征 [17,18]。去重剔除了 7 062 606 行中的 4 784 430 行（67.8%），重复比例高于本研究的其他任何数据集，最终得到 18 万条、三分类的基准（每类 6 万；训练 126 000 / 验证 27 000 / 测试 27 000）。所有模型的 Macro-F1 都在 0.99983 以上：RCCF 与等权卡方森林在机器精度上完全一致（平均差 −3.7e-17，27 000 条测试样本中分歧 0 至 2 条）。该基准对流量特征分类器已经饱和，而这正是命题 1 预言"任何加权都无法起作用"的情形：它在新领域确认了机制的惰性，但并未检验判别难度。

两组实验从两侧界定了结论：等价性既不是 53 237 条截断造成的，也会在类别高度可分的领域重现。

"""

EN_EDITS = [
    ("Three public datasets are used, all obtained from official or public sources [14-16].",
     "Four public datasets are used, all obtained from official or public sources [14-18]."),
    ("| UNSW-NB15 | UNSW Canberra Cyber, official project page | Official training and testing CSV | 2026-09-04 | Page requires citation of the original paper; no SPDX identifier | SHA-256 recorded for both files |",
     "| UNSW-NB15 | UNSW Canberra Cyber, official project page | Official training and testing CSV | 2026-09-04 | Page requires citation of the original paper; no SPDX identifier | SHA-256 recorded for both files |\n"
     "| N-BaIoT | UCI Machine Learning Repository, dataset 442 | Mirai and Gafgyt captures from nine consumer IoT devices; 115 flow features | 2026-09-19 | CC BY 4.0, stated on the dataset page | SHA-256 of the 1.77 GB archive recorded (Table S1) |"),
    ("The three datasets are deliberately complementary rather than interchangeable. They span three capture eras (a 1998 line of descent for NSL-KDD, a 2015 synthetic testbed for UNSW-NB15 and a 2017 enterprise-like testbed for CIC-IDS2017), three feature extractors (a 41-feature connection record set, a 49-feature Argus/Bro-derived set and a 78-feature CICFlowMeter set), and three label spaces (5, 10 and 5 retained classes). Their known defects also differ: NSL-KDD carries the redundancy of its KDD lineage, UNSW-NB15 contains largely synthetically generated attacks and cross-split feature overlap, and CIC-IDS2017 contains duplicate flows, cross-label conflicts and constant columns. A fourth dataset would add most value if it covered an environment none of the three represents - an IoT or operational-technology deployment, a different capture vantage point, or a temporally separated capture from the same testbed. The coverage matrix is reported in the supplementary material.",
     "The four datasets are deliberately complementary rather than interchangeable. They span four capture settings (a 1998 line of descent for NSL-KDD, a 2015 synthetic testbed for UNSW-NB15, a 2017 enterprise-like testbed for CIC-IDS2017 and a 2018 consumer-IoT testbed for N-BaIoT), four feature extractors (41 connection-record features, 49 Argus/Bro-derived features, 78 CICFlowMeter features and 115 IoT flow features), and four label spaces (5, 10, 5 retained and 3 native classes). Their known defects also differ: NSL-KDD carries the redundancy of its KDD lineage, UNSW-NB15 contains largely synthetically generated attacks and cross-split feature overlap, CIC-IDS2017 contains duplicate flows, cross-label conflicts and constant columns, and N-BaIoT repeats 67.8% of its rows exactly. Together they cover the environment the earlier draft identified as missing, a consumer-IoT deployment, while none is a temporally separated capture from a common testbed. The coverage matrix is reported in the supplementary material."),
    ("Protocol effects are an order of magnitude larger than the aggregation effect the literature usually reports.",
     "Protocol effects are an order of magnitude larger than the aggregation effect the literature usually reports, and the equivalence is reproduced on a population 7.8 times larger and on a fourth, IoT-domain benchmark."),
    ("**Three datasets were evaluated; a fourth was not.** The conclusions are conditional on CIC-IDS2017, NSL-KDD and UNSW-NB15. A genuinely new dataset would test whether the reported protocol sensitivity and the inertness of conditional weighting extend beyond these three sources.",
     "**Four datasets were evaluated, and the largest population is still a subset.** The conclusions are conditional on CIC-IDS2017, NSL-KDD, UNSW-NB15 and N-BaIoT. The scale check of Section 5.7 trains on 413,209 of the 2,429,503 deduplicated CIC records (17%), so a full-corpus run remains untested, and N-BaIoT is saturated for flow-feature classifiers (every model at or above 0.9998 Macro-F1), so it probes the mechanics of the aggregation step rather than discrimination difficulty. None of the four datasets represents production traffic."),
    ("| S26 | Extended robustness: label noise, missing values and calibration drift |",
     "| S26 | Extended robustness: label noise, missing values and calibration drift |\n"
     "| S27 | Scale sensitivity: 413,209-flow population, ten-seed paired comparison |\n"
     "| S28 | N-BaIoT benchmark: audit, class support, per-seed metrics and paired comparison |"),
]

ZH_EDITS = [
    ("本文使用三个公开数据集，全部通过官方或公开镜像获取 [14-16]",
     "本文使用四个公开数据集，全部通过官方或公开镜像获取 [14-18]"),
    ("| UNSW-NB15 | 新南威尔士大学官方项目页 | 官方训练/测试 CSV | 2026-09-04 | 页面要求引用原始论文，未给出 SPDX 标识 | 两个文件的 SHA-256 均记录 |",
     "| UNSW-NB15 | 新南威尔士大学官方项目页 | 官方训练/测试 CSV | 2026-09-04 | 页面要求引用原始论文，未给出 SPDX 标识 | 两个文件的 SHA-256 均记录 |\n"
     "| N-BaIoT | UCI 机器学习库第 442 号数据集 | 九种消费级物联网设备的 Mirai/Gafgyt 攻击与正常流量，115 维流特征 | 2026-09-19 | 数据集页面明确标注 CC BY 4.0 | 1.77 GB 归档的 SHA-256 已记录（表 S1） |"),
    ("三个数据集是刻意互补而非可互相替代的：它们跨越三个采集时期（NSL-KDD 承自 1998 年的数据脉络、UNSW-NB15 为 2015 年合成测试床、CIC-IDS2017 为 2017 年类企业测试床）、三种特征提取方式（41 维连接记录、49 维 Argus/Bro 派生特征、78 维 CICFlowMeter 特征）与三套标签体系（5 类、10 类与 5 类保留标签）。三者的已知缺陷也各不相同：NSL-KDD 带有 KDD 谱系的冗余，UNSW-NB15 的攻击多为人工合成且存在跨划分特征重叠，CIC-IDS2017 则存在重复流、跨标签冲突与恒定列。如果要引入第四个数据集，其最大价值在于覆盖三者都未代表的场景——物联网或工业控制环境、不同的采集观测点，或同一测试床上时间分离的采集。覆盖矩阵见补充材料。",
     "四个数据集是刻意互补而非可互相替代的：它们覆盖四种采集场景（NSL-KDD 承自 1998 年的数据脉络、UNSW-NB15 为 2015 年合成测试床、CIC-IDS2017 为 2017 年类企业测试床、N-BaIoT 为 2018 年消费级物联网测试床）、四种特征提取方式（41 维连接记录、49 维 Argus/Bro 派生特征、78 维 CICFlowMeter 特征、115 维物联网流特征）与四套标签体系（5 类、10 类、5 类保留标签与 3 类原生标签）。它们的已知缺陷也各不相同：NSL-KDD 带有 KDD 谱系的冗余，UNSW-NB15 的攻击多为人工合成且存在跨划分特征重叠，CIC-IDS2017 存在重复流、跨标签冲突与恒定列，而 N-BaIoT 有 67.8% 的行是完全重复的。四者合起来覆盖了此前指出的缺失场景——消费级物联网部署；但没有一个是同一测试床上时间分离的采集。覆盖矩阵见补充材料。"),
    ("结论是协议效应比聚合规则差异高出一个数量级。",
     "结论是协议效应比聚合规则差异高出一个数量级，且该等价性在总体扩大 7.8 倍与第四个物联网领域数据集上都可复现。"),
    ("**只评测了三个数据集，未引入第四个。** 本文结论以 CIC-IDS2017、NSL-KDD 与 UNSW-NB15 为条件。若要检验所报告的协议敏感性与条件加权的失效是否越出这三个来源，需要引入一个真正独立的新数据集。",
     "**评测了四个数据集，但最大总体仍是语料子集。** 本文结论以 CIC-IDS2017、NSL-KDD、UNSW-NB15 与 N-BaIoT 为条件。5.7 节的规模实验在 2 429 503 条去重后的 CIC 记录中训练了 413 209 条（17%），因此全语料训练仍未验证；而 N-BaIoT 对流量特征分类器已经饱和（所有模型 Macro-F1 均在 0.9998 以上），它检验的是聚合环节的机制而非判别难度。四个数据集都不代表生产流量。"),
    ("| S26 | 扩展鲁棒性：标签噪声、缺失值与标定漂移 |",
     "| S26 | 扩展鲁棒性：标签噪声、缺失值与标定漂移 |\n"
     "| S27 | 规模敏感性：413 209 条总体与十种子配对比较 |\n"
     "| S28 | N-BaIoT 基准：审计、类别支持度、逐种子指标与配对比较 |"),
]


def apply(name: str, edits: list[tuple[str, str]]) -> None:
    path = BASE / name
    text = path.read_text(encoding="utf-8")
    applied = 0
    for old, new in edits:
        if old in text:
            text = text.replace(old, new, 1)
            applied += 1
        else:
            print(f"  [{name}] anchor absent: {old[:60]}...")
    if name.startswith("English"):
        text = text.replace("## 6 Discussion", SECTION_EN + "## 6 Discussion", 1)
    else:
        text = text.replace("## 6 讨论", SECTION_ZH + "## 6 讨论", 1)
    path.write_text(text, encoding="utf-8")
    print(f"{name}: {applied}/{len(edits)} text edits applied, section inserted")


def main() -> None:
    apply("English_SCI_Manuscript_v4.md", EN_EDITS)
    apply("中文SCI论文_v4_重构版.md", ZH_EDITS)


if __name__ == "__main__":
    main()
