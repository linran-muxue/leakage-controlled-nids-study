"""Restore the keyword line that the abstract rewrite removed.
shorten_abstracts_v20.py replaced everything between the abstract heading and
the next section, which also swallowed the **Keywords** line and the horizontal
rule. The compliance check caught it; this restores both lines.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
ENTRIES = {
    "English_SCI_Manuscript_v4.md": (
        "## Abstract",
        "\n\n**Keywords:** network intrusion detection; ensemble learning; conditional weighting; "
        "data leakage; identifiability; reproducibility; CIC-IDS2017\n\n---\n",
        r"\*\*Keywords:\*\*",
    ),
    "中文SCI论文_v4_重构版.md": (
        "## 摘要",
        "\n\n**关键词：** 网络入侵检测；集成学习；条件加权；数据泄漏；可辨识性；可复现性；CIC-IDS2017"
        "\n\n---\n",
        r"\*\*关键词：\*\*",
    ),
}
def main() -> None:
    for name, (heading, block, marker) in ENTRIES.items():
        path = BASE / name
        text = path.read_text(encoding="utf-8")
        if marker in text:
            print(f"{name}: keywords already present")
            continue
        start = text.index(heading) + len(heading)
        rest = text[start:]
        end = rest.index("\n## ")
        body = rest[:end].rstrip("\n- ")
        text = text[:start] + "\n\n" + body + block + rest[end:]
        path.write_text(text, encoding="utf-8")
        print(f"{name}: keywords restored")
if __name__ == "__main__":
    main()
