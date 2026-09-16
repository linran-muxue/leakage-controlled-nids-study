"""Keep the data- and code-availability statement in step with the released tag."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
TARGET = "v1.7.0"


def main() -> None:
    for name in ("English_SCI_Manuscript_v4.md", "中文SCI论文_v4_重构版.md"):
        path = BASE / name
        text = path.read_text(encoding="utf-8")
        updated, n = re.subn(r"v1\.\d+\.\d+", TARGET, text)
        if n == 0:
            raise SystemExit(f"no version string found in {name}")
        path.write_text(updated, encoding="utf-8")
        found = sorted(set(re.findall(r"v1\.\d+\.\d+", updated)))
        print(f"UPDATED={name} versions={found}")


if __name__ == "__main__":
    main()
