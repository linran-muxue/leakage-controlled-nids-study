"""Align the abstract protocol sentence with the ten-seed main experiment."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"


def replace(path: Path, pairs: list[tuple[str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if old not in text:
            raise SystemExit(f"anchor missing in {path.name}: {old[:40]}")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    print(f"FIXED={path.name}")


def main() -> None:
    replace(BASE / "English_SCI_Manuscript_v4.md", [
        ("over three fixed seeds.", "over ten seeds, with a three-seed balanced control."),
    ])
    replace(BASE / "中文SCI论文_v4_重构版.md", [
        ("在三组固定随机种子上比较", "在十个种子上比较（平衡控制为三个种子）"),
    ])


if __name__ == "__main__":
    main()
