"""Report the Holm-adjusted sign-flip values and align the methods claim."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
holm = pd.read_csv(ROOT / "results_seeds10_v5" / "signflip_holm.csv").set_index("comparison")


def fix(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"anchor missing: {label}")
    return text.replace(old, new, 1)


def main() -> None:
    en_path = BASE / "English_SCI_Manuscript_v4.md"
    t = en_path.read_text(encoding="utf-8")
    t = fix(t,
            "(iv) Holm correction for multiple comparisons [37];",
            "(iv) Holm correction across the family of three comparisons against RCCF [37], reported as adjusted "
            "sign-flip p-values in Table 5;", "en-methods")
    t = fix(t,
            "| Comparison | Mean difference | SD | Seed-level 95% interval | Seed-level 90% interval | TOST at 0.005 | TOST at 0.01 | Minimum detectable effect (80% power) | Cohen's d_z | Seeds favouring RCCF / baseline |",
            "| Comparison | Mean difference | SD | Seed-level 95% interval | Seed-level 90% interval | TOST at 0.005 | TOST at 0.01 | Minimum detectable effect (80% power) | Cohen's d_z | Holm-adjusted sign-flip p | Seeds favouring RCCF / baseline |",
            "en-table-head")
    t = fix(t,
            "| RCCF - equal RF (chi-square) | -0.000456 | 0.001152 | [-0.001280, +0.000368] | [-0.001124, +0.000212] | equivalent | equivalent | 0.001146 | -0.40 | 5 / 5 |",
            "| RCCF - equal RF (chi-square) | -0.000456 | 0.001152 | [-0.001280, +0.000368] | [-0.001124, +0.000212] | equivalent | equivalent | 0.001146 | -0.40 | 0.244 | 5 / 5 |",
            "en-row1")
    t = fix(t,
            "| RCCF - equal RF (all features) | +0.001613 | 0.001376 | [+0.000628, +0.002597] | [+0.000815, +0.002410] | equivalent | equivalent | 0.001369 | +1.17 | 9 / 1 |",
            "| RCCF - equal RF (all features) | +0.001613 | 0.001376 | [+0.000628, +0.002597] | [+0.000815, +0.002410] | equivalent | equivalent | 0.001369 | +1.17 | **0.020** | 9 / 1 |",
            "en-row2")
    t = fix(t,
            "| RCCF - ExtraTrees (chi-square) | +0.031788 | 0.001616 | [+0.030632, +0.032944] | [+0.030851, +0.032724] | not equivalent | not equivalent | 0.001607 | +19.68 | 10 / 0 |",
            "| RCCF - ExtraTrees (chi-square) | +0.031788 | 0.001616 | [+0.030632, +0.032944] | [+0.030851, +0.032724] | not equivalent | not equivalent | 0.001607 | +19.68 | **0.006** | 10 / 0 |",
            "en-row3")
    en_path.write_text(t, encoding="utf-8")

    zh_path = BASE / "中文SCI论文_v4_重构版.md"
    z = zh_path.read_text(encoding="utf-8")
    z = fix(z, "（iv）Holm 校正，用于多重比较 [37]；",
            "（iv）Holm 校正，用于对 RCCF 的三项对照这一比较族 [37]，结果以校正后的符号翻转 p 值列于表 5；", "zh-methods")
    z = fix(z,
            "| 对照 | 平均差 | 标准差 | 种子级 95% 区间 | 种子级 90% 区间 | SESOI = 0.005 | SESOI = 0.01 | 最小可检出效应（80% 功效） | Cohen's d_z | 支持 RCCF／基线的种子数 |",
            "| 对照 | 平均差 | 标准差 | 种子级 95% 区间 | 种子级 90% 区间 | SESOI = 0.005 | SESOI = 0.01 | 最小可检出效应（80% 功效） | Cohen's d_z | Holm 校正后符号翻转 p | 支持 RCCF／基线的种子数 |",
            "zh-table-head")
    z = fix(z,
            "| RCCF − 等权 χ² 森林 | −0.000456 | 0.001152 | [−0.001280, +0.000368] | [−0.001124, +0.000212] | 等价 | 等价 | 0.001146 | −0.40 | 5 / 5 |",
            "| RCCF − 等权 χ² 森林 | −0.000456 | 0.001152 | [−0.001280, +0.000368] | [−0.001124, +0.000212] | 等价 | 等价 | 0.001146 | −0.40 | 0.244 | 5 / 5 |",
            "zh-row1")
    z = fix(z,
            "| RCCF − 全特征等权森林 | +0.001613 | 0.001376 | [+0.000628, +0.002597] | [+0.000815, +0.002410] | 等价 | 等价 | 0.001369 | +1.17 | 9 / 1 |",
            "| RCCF − 全特征等权森林 | +0.001613 | 0.001376 | [+0.000628, +0.002597] | [+0.000815, +0.002410] | 等价 | 等价 | 0.001369 | +1.17 | **0.020** | 9 / 1 |",
            "zh-row2")
    z = fix(z,
            "| RCCF − 极端随机树（χ²） | +0.031788 | 0.001616 | [+0.030632, +0.032944] | [+0.030851, +0.032724] | 不等价 | 不等价 | 0.001607 | +19.68 | 10 / 0 |",
            "| RCCF − 极端随机树（χ²） | +0.031788 | 0.001616 | [+0.030632, +0.032944] | [+0.030851, +0.032724] | 不等价 | 不等价 | 0.001607 | +19.68 | **0.006** | 10 / 0 |",
            "zh-row3")
    zh_path.write_text(z, encoding="utf-8")
    print("HOLM_APPLIED")


if __name__ == "__main__":
    main()
