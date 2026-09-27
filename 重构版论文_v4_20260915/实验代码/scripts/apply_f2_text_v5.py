"""Record the test-side confirmation of the gate-tuning result in both manuscripts."""
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


def main() -> None:
    en_path = BASE / "English_SCI_Manuscript_v4.md"
    en = en_path.read_text(encoding="utf-8")
    en = fix(en,
             "This excludes the alternative explanation that the mechanism was under-tuned.",
             "This excludes the alternative explanation that the mechanism was under-tuned. "
             "The strongest form of this check is test-side: the configuration selected on validation "
             "(three folds, C = 1.0, margin descriptors) was then evaluated once on the locked test partition and produced "
             "**bit-identical predictions** to the default configuration on all three seeds - 0 of 23,958 rows changed and "
             "identical Macro-F1 to six decimal places. We also note that at least eleven configurations share the same "
             "validation mean to ten decimal places, so the optimum is a tie rather than a unique point.",
             "en-f2")
    en_path.write_text(en, encoding="utf-8")

    zh_path = BASE / "中文SCI论文_v4_重构版.md"
    zh = zh_path.read_text(encoding="utf-8")
    zh = fix(zh,
             "这排除了“被检验方法没有得到充分调参”这一替代解释。",
             "这排除了“被检验方法没有得到充分调参”这一替代解释。该检查的最强形式在测试集一侧：把验证集选出的配置"
             "（三折、C = 1.0、边距描述子）在锁定的测试分区上评估一次，三个种子得到的预测与默认配置**逐条完全相同**——"
             "23 958 行中改判 0 条，Macro-F1 精确到六位小数一致。此外，至少 11 个配置的验证均值在前十位小数上相同，"
             "说明最优点是并列而非唯一。",
             "zh-f2")
    zh_path.write_text(zh, encoding="utf-8")
    print("F2_TEXT_APPLIED")


if __name__ == "__main__":
    main()
