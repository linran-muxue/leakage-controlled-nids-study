"""Build the Chinese-named submission bundle from the released artifacts.
Everything inside the archive is copied from the canonical locations recorded
in the self-check table and the publication manifest, so the bundle cannot
disagree with the paper. The archive also carries its own checksum list.
"""
from __future__ import annotations
import hashlib
import shutil
import sys
import zipfile
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
BUILD = ROOT / "submission_package"
TAG = "v1.10.0"
NAME = f"论文投稿包_{TAG}"
# each entry is (folder inside the archive, root used to derive relative paths, files)
SUPPLEMENTARY = BASE / "补充材料_S01_S26"
LAYOUT: list[tuple[str, Path, list[Path]]] = [
    ("01_正式稿件", BASE, [BASE / "English_SCI_Manuscript_v4.docx",
                           BASE / "English_SCI_Manuscript_v4.md",
                           BASE / "中文SCI论文_v4_重构版.docx",
                           BASE / "中文SCI论文_v4_重构版.md"]),
    ("02_投稿文件", BASE, [BASE / "Highlights_v4.md",
                           BASE / "Cover_Letter_JISA_v4.md",
                           BASE / "Graphical_Abstract_v4.png",
                           BASE / "Graphical_Abstract_v4.pdf"]),
    ("03_图片/英文版", BASE / "figures_en", sorted((BASE / "figures_en").glob("*.png"))),
    ("03_图片/中文版", BASE / "figures", sorted((BASE / "figures").glob("*.png"))),
    ("04_补充材料", SUPPLEMENTARY, sorted(p for p in SUPPLEMENTARY.rglob("*") if p.is_file())),
    ("05_自查与审查", BASE, [BASE / "论文自查表.docx", BASE / "论文自查表.md",
                             BASE / "遗漏问题审查报告.docx", BASE / "遗漏问题审查报告.md"]),
    ("06_研究与写作方案", BASE, [BASE / "论文结构诊断与重构方案.docx", BASE / "论文结构诊断与重构方案.md",
                                 BASE / "研究缺口审计与优先级清单.docx", BASE / "研究缺口审计与优先级清单.md",
                                 BASE / "P0_P1执行手册.docx", BASE / "P0_P1执行手册.md"]),
    ("07_复现材料", ROOT, [ROOT / "results_publication_final" / "MANIFEST.json",
                           ROOT / "README.md", ROOT / "CITATION.cff",
                           ROOT / "requirements-lock.txt"]),
]
README = f"""# 论文投稿包 {TAG}

本包由 `scripts/package_submission_bundle_v18.py` 从仓库中的规范化位置直接复制生成，
内容与《论文自查表》（66 项：62 通过 / 4 部分通过 / 0 缺失）及 `MANIFEST.json` 一致。

## 目录

| 目录 | 内容 |
|---|---|
| 01_正式稿件 | 英文稿与中文稿（可编辑 Word + Markdown 源文件） |
| 02_投稿文件 | Highlights、投稿信（JISA）、图形摘要（PNG/PDF） |
| 03_图片 | 正文插图（英文版与中文版，各 11 张） |
| 04_补充材料 | S01–S26，含索引 README 与 SHA-256 校验清单 |
| 05_自查与审查 | 论文自查表、遗漏问题审查报告（第一至第十一轮） |
| 06_研究与写作方案 | 结构诊断、缺口审计、P0/P1 执行手册（均标注为历史快照） |
| 07_复现材料 | 发布清单、仓库说明、CITATION、依赖锁定文件 |

## 投稿前仍需作者完成的三件事

1. 按 JISA 官方模板排版（Guide for Authors 获取当天版本）。
2. 填写署名、单位、通信作者、ORCID、基金与利益冲突声明。
3. 送一次母语润色（E6）。

代码与逐样本预测公开于 https://github.com/linran-muxue/leakage-controlled-nids-study （标签 {TAG}）。
"""
def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()
def main() -> None:
    BUILD.mkdir(parents=True, exist_ok=True)
    archive = BUILD / f"{NAME}.zip"
    if archive.exists():
        archive.unlink()
    staged: list[tuple[str, Path]] = []
    for folder, root, files in LAYOUT:
        for path in files:
            if not path.exists():
                raise SystemExit(f"missing artifact: {path}")
            relative = path.relative_to(root)
            staged.append((f"{NAME}/{folder}/{relative.as_posix()}", path))
    checksums = []
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr(f"{NAME}/00_说明.md", README)
        for arcname, path in staged:
            bundle.write(path, arcname)
            checksums.append(f"{digest(path)}  {arcname}")
        bundle.writestr(f"{NAME}/checksums.sha256", "\n".join(checksums) + "\n")
    print(f"BUNDLE={archive}")
    print(f"BUNDLE_FILES={len(staged)}")
    print(f"BUNDLE_MB={archive.stat().st_size / 1024 / 1024:.2f}")
if __name__ == "__main__":
    main()
