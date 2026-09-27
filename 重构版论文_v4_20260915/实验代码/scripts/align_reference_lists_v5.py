"""Make the Chinese reference list identical to the English one so that the numeric
in-text citations resolve to the same works in both manuscripts."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN = BASE / "English_SCI_Manuscript_v4.md"
ZH = BASE / "中文SCI论文_v4_重构版.md"

NOTE = (
    "说明：以下条目与英文稿完全一致，以保证 `[n]` 编号在两版中指向同一文献。"
    "标注 [DOI 待核验] 的条目需在投稿前用 Crossref 或出版社页面逐条核对。"
)


def main() -> None:
    en = EN.read_text(encoding="utf-8")
    idx = en.index("## References")
    body = en[idx:]
    end = body.find("\n---\n")
    block = body[:end] if end > 0 else body
    entries = re.findall(r"^\d+\.\s+.*$", block, flags=re.M)
    if len(entries) != 45:
        raise SystemExit(f"expected 45 English references, found {len(entries)}")

    zh = ZH.read_text(encoding="utf-8")
    zidx = zh.index("## 参考文献")
    tail = zh[zidx:]
    tail_end = tail.find("\n---\n")
    replacement = "## 参考文献\n\n" + NOTE + "\n\n" + "\n\n".join(entries) + "\n"
    if tail_end > 0:
        zh_new = zh[:zidx] + replacement + tail[tail_end:]
    else:
        zh_new = zh[:zidx] + replacement
    ZH.write_text(zh_new, encoding="utf-8")
    print(f"ZH_REFERENCES_ALIGNED={len(entries)}")


if __name__ == "__main__":
    main()
