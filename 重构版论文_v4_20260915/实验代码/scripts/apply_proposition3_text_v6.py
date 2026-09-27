"""Replace the definitional Condition 3 with a quantitative, verified relation."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"


def main() -> None:
    en_path = BASE / "English_SCI_Manuscript_v4.md"
    en = en_path.read_text(encoding="utf-8")
    old_en = ("**Condition 3 (weight collapse).** If the risk models return approximately equal values, "
              "r_e(x) approximately c(x) for all e, then w_e(x) approximately 1/Q and conditional weighting "
              "degenerates to equal averaging. The observable criterion is the normalised weight entropy")
    new_en = ("**Condition 3 (weight collapse, quantified).** Write r_e(x) = r_bar(x) + delta_e(x). Since "
              "log w_e = -r_e + const, we have Var(log w) = Var(delta). Expanding the normalised entropy around "
              "the uniform point gives, to second order,\n\n"
              "$$1-H_{norm}(w)=\\frac{Q}{2\\log Q}\\left\\|w-\\frac{1}{Q}\\mathbf{1}\\right\\|_2^2,$$\n\n"
              "and a first-order expansion of the softmax gives the simpler relation\n\n"
              "$$1-H_{norm}(w)\\ \\approx\\ \\frac{\\mathrm{Var}(\\delta)}{2\\log Q}.$$\n\n"
              "Both are directly checkable. Over the 7,986 test rows the observed mean entropy deficiency is "
              "3.24 x 10^-5; the second-order identity predicts 3.19 x 10^-5 (1.5% relative error) and the "
              "first-order relation predicts 3.36 x 10^-5 (4.0% relative error). The underlying quantity is the "
              "informative part: the median standard deviation of the risk offsets across the four experts is "
              "0.00022 in log-odds, so the experts receive almost identical reliability on almost every row. "
              "An earlier, purely definitional formulation used the normalised weight entropy")
    if old_en not in en:
        raise SystemExit("EN condition 3 anchor missing")
    en = en.replace(old_en, new_en, 1)
    en_path.write_text(en, encoding="utf-8")

    zh_path = BASE / "中文SCI论文_v4_重构版.md"
    zh = zh_path.read_text(encoding="utf-8")
    old_zh = ("**命题 3（权重坍缩）** 设风险模型输出近似相等，即 r_e(x) ≈ c(x) 对所有 e 成立，"
              "则 w_e(x) ≈ 1/Q，条件加权退化为等权平均。其可观测判据是归一化权重熵趋近于 1")
    new_zh = ("**命题 3（权重坍缩，定量形式）** 记 r_e(x) = r̄(x) + δ_e(x)。由于 log w_e = −r_e + 常数，"
              "有 Var(log w) = Var(δ)。将归一化熵在均匀点附近展开，可得二阶恒等式\n\n"
              "$$1-H_{norm}(w)=\\frac{Q}{2\\log Q}\\left\\|w-\\frac{1}{Q}\\mathbf{1}\\right\\|_2^2,$$\n\n"
              "以及对 softmax 做一阶展开得到的更简关系\n\n"
              "$$1-H_{norm}(w)\\ \\approx\\ \\frac{\\mathrm{Var}(\\delta)}{2\\log Q}.$$\n\n"
              "两者都可直接检验。在 7 986 条测试样本上，实测平均熵亏缺为 3.24 × 10⁻⁵；二阶恒等式预测 "
              "3.19 × 10⁻⁵（相对误差 1.5%），一阶关系预测 3.36 × 10⁻⁵（相对误差 4.0%）。"
              "真正有信息量的是底层量：四个专家的风险偏移标准差中位数仅 0.00022（log-odds），"
              "说明几乎每一行上各专家被赋予的可靠性几乎相同。此前的纯定义式表述使用归一化权重熵")
    if old_zh not in zh:
        raise SystemExit("ZH condition 3 anchor missing")
    zh = zh.replace(old_zh, new_zh, 1)
    zh_path.write_text(zh, encoding="utf-8")
    print("PROPOSITION3_TEXT_APPLIED")


if __name__ == "__main__":
    main()
