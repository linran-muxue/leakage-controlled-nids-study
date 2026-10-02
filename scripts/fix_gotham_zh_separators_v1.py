"""Chinese prose never uses comma thousands separators, and the data-products
inventory has to list the new processed population."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"


def replace(path: Path, old: str, new: str, note: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text and old not in text:
        print(f"{path.name}: already applied ({note})")
        return
    if text.count(old) != 1:
        raise SystemExit(f"{path.name}: anchor {note!r} appears {text.count(old)} times")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"{path.name}: {note}")


def main() -> None:
    replace(BASE / "中文SCI论文_v4_重构版.md", "全部 29,718 条测试行", "全部 29 718 条测试行",
            "test row separator")
    replace(BASE / "中文SCI论文_v4_重构版.md", "29,718 条标签中有 38–50 条被改判",
            "29 718 条标签中有 38–50 条被改判", "label separator")
    replace(ROOT / "scripts" / "add_gotham_to_paper_v1.py",
            'f"在本文协议下，剔除设备地址与时间戳后只剩十六个可用列（保留它们等于把攻击者身份交给分类器），"\n'
            '        f"因此 60 维预算会选中全部列、三个视图完全重合：门控与同成员融合在全部 {rows:,} 条测试行上完全"',
            'f"在本文协议下，剔除设备地址与时间戳后只剩十六个可用列（保留它们等于把攻击者身份交给分类器），"\n'
            '        f"因此 60 维预算会选中全部列、三个视图完全重合：门控与同成员融合在全部 {rows_zh} 条测试行上完全"',
            "generator test row separator")
    replace(ROOT / "scripts" / "add_gotham_to_paper_v1.py",
            'f"改判。成员可互换时门控无效、成员不可互换时门控有用，这正是可辨识性条件所预测的边界，"',
            'f"改判。成员可互换时门控无效、成员不可互换时门控有用，这正是可辨识性条件所预测的边界，"',
            "no-op guard")
    replace(ROOT / "scripts" / "add_gotham_to_paper_v1.py",
            'f"相同，十个种子无一例外。把同样的比较改到十六列中的八列——卡方与方差分析此时才真正不同——"\n'
            '        f"结论反转：门控增益 {gain:+.4f} Macro-F1，十个种子全部为正，{rows:,} 条标签中有 38–50 条被"',
            'f"相同，十个种子无一例外。把同样的比较改到十六列中的八列——卡方与方差分析此时才真正不同——"\n'
            '        f"结论反转：门控增益 {gain:+.4f} Macro-F1，十个种子全部为正，{rows_zh} 条标签中有 38–50 条被"',
            "generator label separator")
    replace(ROOT / "scripts" / "add_gotham_to_paper_v1.py",
            "    gain = k8[\"same_members_difference\"]",
            "    gain = k8[\"same_members_difference\"]\n"
            "    rows_zh = f\"{rows:,}\".replace(\",\", \" \")",
            "rows_zh helper")
    replace(ROOT / "scripts" / "build_data_products_doc_v1.py",
            '    "data_external_nsl_kdd_processed_v2": ("NSL-KDD 原生标签", "表 8、S28", 22_544),',
            '    "data_external_nsl_kdd_processed_v2": ("NSL-KDD 原生标签", "表 8、S28", 22_544),\n'
            '    "data_processed_gotham2025_v1": ("Gotham-2025 数据包级基准（2025）",\n'
            '                                      "扩展实验报告九、S31", 29_718),',
            "data products entry")
    print("GOTHAM_SEPARATORS_AND_INVENTORY_FIXED")


if __name__ == "__main__":
    main()
