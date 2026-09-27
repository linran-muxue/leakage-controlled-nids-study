"""Reword the limitation so it stops repeating the Section 3.2 boundary line.
The two sentences were identical apart from one noun, which reads as padding in
a section a reviewer reads closely.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN_OLD = ("Neither equals the full CIC-IDS2017 corpus, and neither represents real network priors. "
          "Every number in this paper is conditioned on these two populations.")
EN_NEW = ("Both are therefore artefacts of the audit procedure rather than samples of an operational "
          "network, and every number in this paper is conditioned on them.")
ZH_OLD = "二者都不是 CIC-IDS2017 全语料，更不代表真实网络类别先验。本文所有数值都限定在这两个总体之上。"
ZH_NEW = "因此二者是审计流程的产物，而不是运行网络的样本；本文所有数值都限定在这两个总体之上。"
def main() -> None:
    for name, old, new in (("English_SCI_Manuscript_v4.md", EN_OLD, EN_NEW),
                           ("中文SCI论文_v4_重构版.md", ZH_OLD, ZH_NEW)):
        path = BASE / name
        text = path.read_text(encoding="utf-8")
        if old not in text:
            print(f"{name}: anchor absent")
            continue
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        print(f"{name}: limitation reworded")
if __name__ == "__main__":
    main()
