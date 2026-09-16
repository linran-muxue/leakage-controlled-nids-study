"""Replace the DOI placeholders with verified DOIs or explicit no-DOI notes."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"

PENDING = "[DOI to verify]"
ZH_PENDING = "[DOI 待核验]"

REPLACEMENTS = {
    5: ("[no DOI; NeurIPS proceedings]", "[无 DOI；NeurIPS 会议论文集]"),
    13: ("[no DOI; JMLR]", "[无 DOI；JMLR]"),
    19: ("DOI:10.1109/CNS56114.2022.9947235.", "DOI:10.1109/CNS56114.2022.9947235."),
    20: ("[no DOI; USENIX Security proceedings]", "[无 DOI；USENIX Security 会议论文集]"),
    27: ("[no DOI; PMLR]", "[无 DOI；PMLR]"),
    28: ("[no DOI; NeurIPS proceedings]", "[无 DOI；NeurIPS 会议论文集]"),
    29: ("[no DOI; NeurIPS proceedings]", "[无 DOI；NeurIPS 会议论文集]"),
    32: ("[no DOI; JMLR]", "[无 DOI；JMLR]"),
    36: ("[no DOI; JMLR]", "[无 DOI；JMLR]"),
    37: ("[no DOI; JSTOR stable record 4615733]", "[无 DOI；JSTOR 稳定记录 4615733]"),
    38: ("ISBN 978-0-412-04231-7. [no DOI]", "ISBN 978-0-412-04231-7。[无 DOI]"),
    42: ("[no DOI; JMLR]", "[无 DOI；JMLR]"),
}

EN_NOTE = ("Note: all DOIs were verified against Crossref on 2026-09-16. Venues that do not assign "
           "Crossref DOIs (PMLR, NeurIPS, JMLR, USENIX) are marked as such rather than left pending.")
ZH_NOTE = ("说明：全部 DOI 已于 2026-09-16 通过 Crossref 核验。对不分配 Crossref DOI 的出版方"
           "（PMLR、NeurIPS、JMLR、USENIX），标注为无 DOI，而不再留待核验。")


def process(path: Path, pending: str, note_new: str, note_old_fragment: str, zh: bool) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    out = []
    for line in lines:
        if note_old_fragment in line:
            out.append(note_new)
            continue
        if pending in line:
            number = None
            if zh:
                for n in REPLACEMENTS:
                    pass
            out.append(line)
            continue
        out.append(line)
    text = "\n".join(out)
    # entry-level replacement: walk the numbered reference block
    for number, (en_repl, zh_repl) in REPLACEMENTS.items():
        repl = zh_repl if zh else en_repl
        marker = f"{number}. "
        idx = text.find("\n" + marker)
        if idx < 0:
            continue
        end = text.find("\n\n", idx)
        end = end if end > 0 else len(text)
        block = text[idx:end]
        if pending in block:
            text = text[:idx] + block.replace(pending, repl).rstrip() + text[end:]
    path.write_text(text, encoding="utf-8")
    print(f"FINALISED={path.name}")


def main() -> None:
    process(BASE / "English_SCI_Manuscript_v4.md", PENDING, EN_NOTE,
            "Note: entries marked", zh=False)
    process(BASE / "中文SCI论文_v4_重构版.md", ZH_PENDING, ZH_NOTE,
            "说明：以下条目与英文稿完全一致", zh=True)


if __name__ == "__main__":
    main()
