"""Report the extended robustness results (label noise, missing features, drift)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

EN_ADD = (
    "\n\n**Extended robustness.** Three further failure modes were probed. Corrupted supervision is comparatively "
    "benign: flipping 5% and 10% of the training labels costs the conditional mechanism 0.6% and 1.3% relative "
    "Macro-F1, and the equal-weight forest 0.8% in both cases. Missing measurements are more damaging - replacing "
    "10% of test entries with the training median costs 4.3% and 4.0% respectively - and calibration drift is the "
    "most damaging of the three: adding 1% of the training range to 20% of the feature columns costs 17.2% and "
    "18.8%. Ordered by severity across all perturbations tested, continuous corruption of feature values dominates "
    "(1% Gaussian noise 43.3%, calibration drift 17-19%, 10% missing values 4%), whereas corrupted supervision is "
    "an order of magnitude less harmful (0.6-1.3%). This ordering is operationally relevant because dataset "
    "critiques focus on label noise, while measurement drift receives far less attention. These three conditions "
    "were evaluated on a single seed and are reported as an exploratory diagnostic."
)

ZH_ADD = (
    "\n\n**扩展鲁棒性。** 我们另外考察了三类失效模式。监督信号被污染相对无害：把训练标签随机翻转 5% 与 10%，"
    "条件加权机制的 Macro-F1 相对下降仅 0.6% 与 1.3%，等权森林均为 0.8%。缺失测量更具破坏性——把 10% 的测试"
    "特征值替换为训练集中位数，两者分别下降 4.3% 与 4.0%；而标定漂移在三者中最严重：给 20% 的特征列加上"
    "训练值域的 1%，两者分别下降 17.2% 与 18.8%。按全部扰动的严重程度排序，**特征值本身的连续污染占主导**"
    "（1% 高斯噪声 43.3%、标定漂移 17–19%、10% 缺失值 4%），而监督被污染的危害小一个数量级（0.6–1.3%）。"
    "这一排序具有实践意义：数据集批评多聚焦于标签噪声，而对测量漂移关注不足。这三类条件在单个种子上评测，"
    "作为探索性诊断报告。"
)


def main() -> None:
    en_path = BASE / "English_SCI_Manuscript_v4.md"
    en = en_path.read_text(encoding="utf-8")
    anchor = "**Resource footprint.**"
    if "Extended robustness.**" not in en:
        en = en.replace(anchor, EN_ADD.strip() + "\n\n" + anchor, 1)
        en_path.write_text(en, encoding="utf-8")
    zh_path = BASE / "中文SCI论文_v4_重构版.md"
    zh = zh_path.read_text(encoding="utf-8")
    zanchor = "**资源占用。**"
    if "扩展鲁棒性。**" not in zh:
        zh = zh.replace(zanchor, ZH_ADD.strip() + "\n\n" + zanchor, 1)
        zh_path.write_text(zh, encoding="utf-8")
    print("ROBUSTNESS_TEXT_APPLIED")


if __name__ == "__main__":
    main()
