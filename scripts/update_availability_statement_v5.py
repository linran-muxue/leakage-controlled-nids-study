"""Point the availability statements at the release that contains the v5 evidence."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"


def main() -> None:
    en_path = BASE / "English_SCI_Manuscript_v4.md"
    en = en_path.read_text(encoding="utf-8")
    if "(release v1.2.0, tag v1.2.0)" in en:
        en = en.replace("(release v1.2.0, tag v1.2.0)", "(release v1.3.0, tag v1.3.0)", 1)
        en_path.write_text(en, encoding="utf-8")
    zh_path = BASE / "中文SCI论文_v4_重构版.md"
    zh = zh_path.read_text(encoding="utf-8")
    if "（发布版本 v1.2.0，标签 v1.2.0）" in zh:
        zh = zh.replace("（发布版本 v1.2.0，标签 v1.2.0）", "（发布版本 v1.3.0，标签 v1.3.0）", 1)
        zh_path.write_text(zh, encoding="utf-8")
    print("AVAILABILITY_UPDATED")


if __name__ == "__main__":
    main()
