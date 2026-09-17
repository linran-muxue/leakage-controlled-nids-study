"""Check the submission front matter against the manuscript it describes.
Highlights and the cover letter are read by the editor before the manuscript is
opened. If they quote a number the manuscript no longer contains - or a release
tag that has moved on - the first impression is of a stale submission.
"""
from __future__ import annotations
import re
import subprocess
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN = (BASE / "English_SCI_Manuscript_v4.md").read_text("utf-8")
ZH = (BASE / "中文SCI论文_v4_重构版.md").read_text("utf-8")
AUX = ["Highlights_v4.md", "Cover_Letter_JISA_v4.md"]
DECIMAL = re.compile(r"\d+\.\d{2,6}")
INTEGER = re.compile(r"\b\d{1,3}(?:[, ]\d{3})+\b|\b\d{4,7}\b")
def tokens(text: str) -> set[str]:
    return {f.replace(" ", "").replace(",", "") for f in DECIMAL.findall(text) + INTEGER.findall(text)}
def main() -> int:
    problems: list[str] = []
    tags = subprocess.run(["git", "tag"], capture_output=True, text=True, cwd=ROOT).stdout.split()
    latest = sorted(tags, key=lambda t: [int(x) for x in re.findall(r"\d+", t)])[-1] if tags else ""
    known = tokens(EN) | tokens(ZH)
    body = EN.split("## References")[0]
    for name in AUX:
        text = (BASE / name).read_text("utf-8")
        extra = sorted(tokens(text) - known)
        print(f"=== {name} ===")
        print(f"  numeric tokens not present in either manuscript: {extra if extra else 'none'}")
        if extra:
            problems.append(f"{name} quotes numbers the manuscripts do not contain: {extra}")
        versions = sorted(set(re.findall(r"v1\.\d+\.\d+", text)))
        print(f"  release tags cited: {versions if versions else 'none'}")
        if versions and versions != [latest]:
            problems.append(f"{name} cites {versions}, latest tag is {latest}")
        for phrase in ["Protocol Sensitivity Dominates", "JISA", "Journal of Information Security and Applications"]:
            if name.startswith("Cover") and phrase not in text:
                problems.append(f"{name} is missing '{phrase}'")
    print("=== internal planning documents ===")
    for name in ["研究缺口审计与优先级清单.md", "P0_P1执行手册.md", "论文结构诊断与重构方案.md"]:
        text = (BASE / name).read_text("utf-8")
        stamped = "> **状态说明" in text and "论文自查表.md" in text
        print(f"  {name}: {'stamped' if stamped else 'NO STATUS STAMP'}")
        if not stamped:
            problems.append(f"{name} has no status stamp pointing at the current state")
    print("=== graphical abstract source ===")
    ga = (ROOT / "scripts" / "build_graphical_abstract_v5.py").read_text("utf-8")
    for bad in ["dominates model choice", "3,500"]:
        if bad in ga:
            problems.append(f"graphical abstract still carries '{bad}'")
            print(f"  stale text: {bad}")
    for good in ["aggregation-rule differences", "3,469-5,038"]:
        if good not in ga:
            problems.append(f"graphical abstract is missing '{good}'")
            print(f"  missing text: {good}")
    print(f"  title/ratio: {'ok' if not any(b in ga for b in ['dominates model choice', '3,500']) else 'stale'}")
    print("=== public repository metadata ===")
    readme = (ROOT / "README.md").read_text("utf-8")
    cff = (ROOT / "CITATION.cff").read_text("utf-8")
    for name, text in (("README.md", readme), ("CITATION.cff", cff)):
        found_tags = sorted(set(re.findall(r"v1\.\d+\.\d+", text)))
        stale_tags = [t for t in found_tags if t != latest]
        print(f"  {name}: release tags {found_tags or 'none'}")
        if stale_tags:
            problems.append(f"{name} still cites {stale_tags}")
    if "Provenance-Aware" in readme:
        problems.append("README.md still names a superseded manuscript title")
    number = latest.lstrip("v")
    if f'version: "{number}"' not in cff:
        problems.append(f"CITATION.cff version does not match {latest}")
    if "Aggregation-Rule Differences" not in readme:
        problems.append("README.md does not name the current manuscript title")
    print()
    if problems:
        for problem in problems:
            print(f"ISSUE {problem}")
        print("AUX_MISMATCH")
        return 1
    print("AUX_OK")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
