"""Chinese-side F2 text update (run after the English update)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "中文SCI论文_v4_重构版.md"

OLD = "这排除了「被检验方法没有得到充分调参」这一替代解释。"
NEW = (
    "这排除了「被检验方法没有得到充分调参」这一替代解释。该检查的最强形式在测试集一侧：把验证集选出的配置"
    "（三折、C = 1.0、边距描述子）在锁定的测试分区上评估一次，三个种子得到的预测与默认配置**逐条完全相同**——"
    "23 958 行中改判 0 条，Macro-F1 精确到六位小数一致。此外，至少 11 个配置的验证均值在前十位小数上相同，"
    "说明最优点是并列而非唯一。"
)


def main() -> None:
    text = MD.read_text(encoding="utf-8")
    if "该检查的最强形式在测试集一侧" in text:
        print("already applied")
        return
    if OLD not in text:
        raise SystemExit("anchor missing")
    MD.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    print("ZH_F2_TEXT_APPLIED")


if __name__ == "__main__":
    main()
