"""Verify that the committed figures are exactly what the builders produce.
Regenerates into place, compares bytes, and restores the originals if anything
differs, so the check never leaves the worktree modified.
"""
from __future__ import annotations
import hashlib
import subprocess
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
PY = sys.executable
BUILDERS = [
    ("scripts/build_figures_en_v5.py", BASE / "figures_en"),
    ("scripts/build_restructured_figures_v4.py", BASE / "figures"),
    ("scripts/build_graphical_abstract_v5.py", BASE),
]
def snapshot(folder: Path, pattern: str = "*.png") -> dict[str, bytes]:
    return {p.name: p.read_bytes() for p in sorted(folder.glob(pattern))}
def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:12]
def main() -> int:
    problems: list[str] = []
    for script, folder in BUILDERS:
        before = snapshot(folder)
        proc = subprocess.run([PY, script], capture_output=True, text=True, cwd=ROOT, timeout=900,
                              encoding="utf-8", errors="replace")
        after = snapshot(folder)
        restored = False
        for name, data in before.items():
            if name not in after or after[name] != data:
                (folder / name).write_bytes(data)
                restored = True
        changed = [n for n in before if n in after and after[n] != before[n]]
        missing = [n for n in before if n not in after]
        new = [n for n in after if n not in before]
        status = "identical" if not (changed or missing or new) else "DIFFERS"
        print(f"  {script}: {len(before)} figure(s) {status}"
              + (f" (changed {changed}, missing {missing}, new {new})" if status == "DIFFERS" else ""))
        if restored:
            print("     originals restored; worktree unchanged")
        if proc.returncode != 0:
            problems.append(f"{script} exited {proc.returncode}: {proc.stderr.strip()[:120]}")
        if changed or missing or new:
            problems.append(f"{script} output is not what is committed: {changed + missing + new}")
    print()
    if problems:
        for problem in problems:
            print(f"ISSUE {problem}")
        print("FIGURE_REPRODUCIBILITY_FAILED")
        return 1
    print("FIGURES_REPRODUCIBLE")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
