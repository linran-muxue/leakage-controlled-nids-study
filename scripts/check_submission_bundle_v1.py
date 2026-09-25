"""Verify the packaged submission against the repository it was built from.

The archive is what the editor receives, so three things must hold: its own
checksum list describes it truthfully, its structure matches what the README
inside promises, and every document inside is the released one rather than an
earlier revision.  The last is the failure mode that matters - a stale DOCX in
the archive would be invisible to every other check, because those all read the
working tree.

Rebuild with ``scripts/package_submission_bundle_v18.py`` when this reports a
mismatch.
"""
from __future__ import annotations

import hashlib
import re
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
BUNDLE = BASE / "补充材料_S01_S30"
TAG = "v1.11.0"
ARCHIVE = ROOT / "submission_package" / f"论文投稿包_{TAG}.zip"
EXPECTED_FOLDERS = ("01_正式稿件", "02_投稿文件", "03_图片", "04_补充材料",
                    "05_自查与审查", "06_研究与写作方案", "07_复现材料",
                    "08_主表", "09_投稿文本")
TRACKED = ("English_SCI_Manuscript_v4.docx", "English_SCI_Manuscript_v4.md",
           "中文SCI论文_v4_重构版.docx", "中文SCI论文_v4_重构版.md",
           "Highlights_v4.docx", "Cover_Letter_JISA_v4.docx",
           "Graphical_Abstract_v4.png", "Graphical_Abstract_v4.pdf",
           "论文自查表.docx", "遗漏问题审查报告.docx")
problems: list[str] = []


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    if not ARCHIVE.exists():
        print(f"ISSUE the archive is missing: {ARCHIVE.relative_to(ROOT)}")
        print("SUBMISSION_BUNDLE_FAILED")
        return 1
    with zipfile.ZipFile(ARCHIVE) as archive:
        names = archive.namelist()
        root = names[0].split("/")[0]
        contents = {name[len(root) + 1:]: name for name in names if "/" in name}
        data = {key: archive.read(value) for key, value in contents.items()}

    print(f"archive: {len(names)} entries, {ARCHIVE.stat().st_size / 1e6:.2f} MB")
    folders = {key.split("/")[0] for key in contents if "/" in key}
    for folder in EXPECTED_FOLDERS:
        if folder in folders:
            print(f"  OK   {folder}")
        else:
            problems.append(f"{folder} is missing from the archive")
            print(f"  ISSUE {folder} is missing")

    checksums = data.get("checksums.sha256", b"").decode("utf-8").splitlines()
    listed = 0
    for line in checksums:
        if not line.strip():
            continue
        expected, _, path = line.partition("  ")
        path = path[len(root) + 1:] if path.startswith(root + "/") else path
        listed += 1
        actual = data.get(path)
        if actual is None:
            problems.append(f"checksums.sha256 lists {path}, which is not in the archive")
        elif digest(actual) != expected:
            problems.append(f"{path} does not match its recorded checksum")
    print(f"  checksum list covers {listed} file(s); "
          f"{len(problems)} problem(s) so far")

    # the released documents must be the working tree's, byte for byte
    stale = 0
    for name in TRACKED:
        target = BASE / name
        packaged = next((key for key in data if key.endswith("/" + name)), None)
        if packaged is None:
            problems.append(f"{name} is not packaged")
            continue
        if digest(data[packaged]) != hashlib.sha256(target.read_bytes()).hexdigest():
            stale += 1
            problems.append(f"{name} in the archive differs from the released file "
                            f"(rebuild the archive)")
    print(f"  released documents in the archive: {len(TRACKED) - stale} of {len(TRACKED)} current")

    packaged_supp = {key.split("/", 1)[1] for key in data if key.startswith("04_补充材料/")}
    canonical = {str(path.relative_to(BUNDLE)).replace("\\", "/")
                 for path in BUNDLE.rglob("*") if path.is_file()}
    if packaged_supp != canonical:
        problems.append(f"the supplementary copy differs from the canonical bundle: "
                        f"only packaged {sorted(packaged_supp - canonical)[:3]}, "
                        f"missing {sorted(canonical - packaged_supp)[:3]}")
        print("  ISSUE supplementary copy differs from the canonical bundle")
    else:
        print(f"  supplementary copy matches all {len(canonical)} canonical files")

    readme = data.get("00_说明.md", b"").decode("utf-8")
    figures = len([key for key in data if key.startswith("03_图片/英文版/")])
    declared = re.search(r"正文插图（英文版与中文版，各 (\d+) 张）", readme)
    if not declared or int(declared.group(1)) != figures:
        problems.append(f"the README claims {declared.group(1) if declared else '?'} figures "
                        f"per language, the archive holds {figures}")
    tables = len([key for key in data if key.startswith("08_主表/") and key.endswith(".csv")])
    if tables != 9:
        problems.append(f"the archive holds {tables} exported tables, expected 9")
    print(f"  figures per language {figures}; exported tables {tables}")

    print()
    if problems:
        for problem in problems:
            print(f"ISSUE {problem}")
        print("SUBMISSION_BUNDLE_FAILED")
        return 1
    print("SUBMISSION_BUNDLE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
