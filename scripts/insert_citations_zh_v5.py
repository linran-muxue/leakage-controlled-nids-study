"""Insert numeric in-text citations into the Chinese manuscript (audit finding F1)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "中文SCI论文_v4_重构版.md"

INSERTS = [
    ("CIC-IDS2017、NSL-KDD 与 UNSW-NB15 是这一方向使用最广的三个公开数据集", " [14-16]", "intro-datasets"),
    ("围绕它们已经积累了数千篇论文", " [22,23]", "intro-surveys"),
    ("近年多个工作表明，泄漏与预处理顺序足以改变入侵检测研究中的结论方向。", " [18-20]", "intro-leakage"),
    ("CIC-IDS2017 由 Sharafaldin 等人在 2018 年发布", " [14]", "2.1-cic"),
    ("NSL-KDD 是 KDD CUP 99 的改进版本", " [15]", "2.1-nsl"),
    ("UNSW-NB15 由 Moustafa 与 Slay 在 2015 年发布", " [16]", "2.1-unsw"),
    ("围绕这些数据集，文献已经识别出多项结构性缺陷", " [17]", "2.1-defects"),
    ("Engelen 等人与 Liu 等人分别指出", " [18,19]", "2.1-order"),
    ("那么协议本身就必须成为被报告、被检验的对象。", " 这一立场属于对安全领域机器学习方法更广泛的方法学批评的一部分 [20,21,24]。", "2.1-critique"),
    ("卡方检验衡量特征与标签的统计相关性，互信息刻画非线性依赖，方差分析比较类间与类内方差之比。", " [12,13]", "2.2-filters"),
    ("这类泄漏在入侵检测文献中并不罕见", " [20]", "2.2-leakage"),
    ("以等权投票或概率平均聚合。", " [1,2,8,9]", "2.3-rf"),
    ("这一思路在文献中有多种实现形式：", " [8-11,29]", "2.3-implementations"),
    ("近期面向开放集的入侵检测工作进一步引入了极值理论、原型学习与自编码器重构误差来构造拒绝机制。", " [25,26,40,41]", "2.3-openset"),
    ("Log Loss、Brier 分数与期望校准误差（ECE）更重要。", " [27]", "2.4-metrics"),
    ("硬标签相同的两个模型可以有显著不同的校准表现", " [28,29]", "2.4-calibration"),
    ("本文使用三个公开数据集，全部通过官方或公开镜像获取", " [14-16]", "3.1-datasets"),
    ("并用蒙德里安保形预测给出可选的 `unknown` 输出（显著性水平 α = 0.1）。", " [30-33]", "3.4-conformal"),
    ("（i）精确 McNemar 检验，用于硬标签分歧", " [34]", "3.5-mcnemar"),
    ("（ii）种子级符号翻转检验，用于方向稳定性", " [35,36]", "3.5-signflip"),
    ("（iii）分层配对 Bootstrap，用于 Macro-F1 差的区间估计", " [38]", "3.5-bootstrap"),
    ("（iv）Holm 校正，用于多重比较", " [37]", "3.5-holm"),
    ("（v）等价性检验（TOST）", " [39]", "3.5-tost"),
    ("极端随机树、XGBoost 与多层感知机（MLP）。", " 集成与提升方法的相关文献见 [3-7]。", "4.1-learners"),
    ("融合概率随后在验证集上做温度缩放", " [27]", "4.2-temperature"),
    ("报告的时间为单机测量值，不构成跨平台可移植性主张。", " 软件栈见 [42-45]。", "4.4-software"),
    ("在不控制重复样本、变换泄漏、类别先验与调参预算的情况下", " [18-20]", "6.2-attribution"),
]


def main() -> None:
    text = MD.read_text(encoding="utf-8")
    applied, skipped = 0, []
    for anchor, insert, label in INSERTS:
        if anchor not in text:
            skipped.append(label)
            continue
        text = text.replace(anchor, anchor + insert, 1)
        applied += 1
    MD.write_text(text, encoding="utf-8")
    print(f"ZH_CITATIONS_APPLIED={applied}")
    if skipped:
        print("anchors not found:", skipped)


if __name__ == "__main__":
    main()
