"""Mirror the release tree onto the desktop delivery folder, with assertions.

The manual ``robocopy`` that closed rounds 20a-20bi is easy to get subtly wrong
(it silently keeps a stale copy when only the size matches), so the delivery
step is scripted: the release tree is mirrored, the submission bundle is
refreshed, and a handful of key artefacts are compared by SHA-256 afterwards.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "重构版论文_v4_20260915"
TAG = "v1.11.0"
DESKTOP = Path(r"C:\Users\27677\Desktop") / f"论文_{TAG}_全语料版"
KEY_FILES = ["中文SCI论文_v4_重构版.md", "English_SCI_Manuscript_v4.md",
             "扩展实验报告.md", "数据与资料来源总表.md",
             "中文SCI论文_v4_重构版.docx", "English_SCI_Manuscript_v4.docx"]


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(block)
    return hasher.hexdigest()


def main() -> int:
    bundle = ROOT / "submission_package" / f"论文投稿包_{TAG}.zip"
    for path in (SRC, bundle):
        if not path.exists():
            raise SystemExit(f"missing release input: {path}")
    DESKTOP.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(["robocopy", str(SRC), str(DESKTOP), "/E", "/NFL", "/NDL",
                           "/NJH", "/NJS", "/R:1", "/W:1"], capture_output=True, text=True)
    # robocopy exits 0-7 on success (1 = files copied, 2 = extra files present)
    if proc.returncode > 7:
        raise SystemExit(f"robocopy failed with {proc.returncode}: {proc.stdout[-400:]}")
    target_zip = DESKTOP / bundle.name
    target_zip.write_bytes(bundle.read_bytes())
    checked = 0
    for name in KEY_FILES:
        source, target = SRC / name, DESKTOP / name
        if not target.exists():
            raise SystemExit(f"{name} did not reach the delivery folder")
        if digest(source) != digest(target):
            raise SystemExit(f"{name} differs between the release tree and the delivery folder")
        checked += 1
    if digest(bundle) != digest(target_zip):
        raise SystemExit("the submission bundle differs after copying")
    files = sum(1 for _ in DESKTOP.rglob("*") if _.is_file())
    size_mb = sum(p.stat().st_size for p in DESKTOP.rglob("*") if p.is_file()) / 1e6
    print(f"DESKTOP_SYNCED {DESKTOP} files={files} size_mb={size_mb:.1f} "
          f"verified={checked + 1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
