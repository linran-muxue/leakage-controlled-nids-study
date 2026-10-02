"""Quote the Gotham packet count exactly, in both languages.

The English paragraph said "35.1 M packets" while the Chinese said "3 510 万";
the cross-language audit compares numeric tokens, so the two spellings were two
different numbers.  Both now state the scanned total, 35,134,281.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

EDITS = (
    (BASE / "English_SCI_Manuscript_v4.md",
     "its processed tables hold 35.1 M packets and 18 classes",
     "its processed tables hold 35,134,281 packets and 18 classes"),
    (BASE / "中文SCI论文_v4_重构版.md",
     "处理表含 3 510 万条数据包、18 个类别",
     "处理表含 35 134 281 条数据包、18 个类别"),
    (ROOT / "scripts" / "build_extension_report_v1.py",
     "f\"Gotham-2025（Zenodo 14502760，CC BY 4.0）在 78 台 IoT 设备上采集 3 510 万条\"",
     "f\"Gotham-2025（Zenodo 14502760，CC BY 4.0）在 78 台 IoT 设备上采集 35 134 281 条\""),
)


def main() -> None:
    for path, old, new in EDITS:
        text = path.read_text(encoding="utf-8")
        if new in text and old not in text:
            print(f"{path.name}: already applied")
            continue
        if text.count(old) != 1:
            raise SystemExit(f"{path.name}: anchor appears {text.count(old)} times")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        print(f"{path.name}: packet count")
    print("GOTHAM_PACKET_COUNT_FIXED")


if __name__ == "__main__":
    main()
