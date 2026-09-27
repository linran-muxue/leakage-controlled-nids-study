"""Retire the first data-sources document now that the full register replaces it.

``数据来源总表`` covered only the evaluation datasets; ``数据与资料来源总表``
covers datasets, derived populations, software, literature, journal
requirements, archives and the material moved out of the release.  The old pair
is moved (not deleted) to ``.quarantine/superseded_docs/`` and dropped from the
index, so the substitution stays auditable.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
DEST = ROOT / ".quarantine" / "superseded_docs"


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    for name in ("数据来源总表.md", "数据来源总表.docx"):
        source = BASE / name
        if not source.exists():
            print(f"  {name}: already retired")
            continue
        target = DEST / name
        shutil.move(str(source), str(target))
        subprocess.run(["git", "rm", "--cached", "--quiet", f"重构版论文_v4_20260915/{name}"],
                       cwd=ROOT, check=False)
        print(f"  moved {name} -> {target.relative_to(ROOT)} ({target.stat().st_size:,} bytes)")
    replacement = BASE / "数据与资料来源总表.md"
    if not replacement.exists():
        raise SystemExit("the replacement document is missing")
    print(f"replacement in place: {replacement.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
