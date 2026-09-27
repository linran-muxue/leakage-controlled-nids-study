"""Remove the duplicated full-feature entry in Section 5.2.
The commentary under Table 5 restated, in condensed form, what the Third
reading immediately below states in full (same statistic, same interval
argument, same feature-view comparison). Keeping both wastes a paragraph on a
reader who is already being told the same thing twice.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN_OLD = ("Three entries deserve comment. **Power.** With ten seeds and the observed standard deviation, "
          "the smallest difference detectable at 80% power is 0.00115 to 0.00161 Macro-F1; anything "
          "smaller would be missed, which is precisely why the equivalence margins are stated explicitly "
          "rather than inferred from a non-significant test. **Versus the full-feature forest.** The "
          "difference is positive and statistically detectable - the interval excludes zero and nine of "
          "ten seeds favour RCCF - yet its magnitude of 0.0016 lies inside the 0.005 equivalence margin: "
          "it is real but practically negligible, and Section 5.4 shows it is the same size as a "
          "feature-view choice. **Versus extremely randomised trees.**")
EN_NEW = ("Two entries in Table 5 deserve comment. **Power.** With ten seeds and the observed standard "
          "deviation, the smallest difference detectable at 80% power is 0.00115 to 0.00161 Macro-F1; "
          "anything smaller would be missed, which is precisely why the equivalence margins are stated "
          "explicitly rather than inferred from a non-significant test. **Versus extremely randomised "
          "trees.**")
ZH_OLD = ("有三行值得说明。**功效**：在十个种子与实测标准差下，80% 功效可检出的最小差异为 0.00115 至 0.00161 Macro-F1，"
          "更小的效应会被漏检——这正是必须显式声明等价边界、而不能用「检验不显著」代替等价结论的原因。**相对全特征森林**："
          "差异为正且可被统计检出（区间不含零，十个种子中九个支持 RCCF），但幅度 0.0016 仍落在 0.005 的等价边界内，"
          "属于「真实但工程上可忽略」；5.4 节进一步显示它与一次特征视图选择同量级。**相对极端随机树**：")
ZH_NEW = ("表 5 中有两行值得说明。**功效**：在十个种子与实测标准差下，80% 功效可检出的最小差异为 0.00115 至 0.00161 Macro-F1，"
          "更小的效应会被漏检——这正是必须显式声明等价边界、而不能用「检验不显著」代替等价结论的原因。**相对极端随机树**：")
def apply(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        print(f"{path.name}: anchor absent")
        return
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"{path.name}: duplicated entry removed")
def main() -> None:
    apply(BASE / "English_SCI_Manuscript_v4.md", EN_OLD, EN_NEW)
    apply(BASE / "中文SCI论文_v4_重构版.md", ZH_OLD, ZH_NEW)
if __name__ == "__main__":
    main()
