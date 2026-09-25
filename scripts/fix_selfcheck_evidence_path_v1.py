"""Point self-check row C1 at the gate configuration that actually ships.

Row C1 ("method reproducibility: pseudocode and parameters") listed
``final_config.json`` as its evidence.  No such file exists in the repository:
two retired runners used to write it, and the configuration that ships today is
``results_gate_tuning_v5/selected_gate_config.json``, registered as
supplementary item S16 alongside the 108-configuration search that produced it.

The row is corrected to cite the artefact that exists, and
``scripts/check_cited_paths_v1.py`` now fails the gate whenever a current-state
deliverable cites a path that is not on disk.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
TABLE = BASE / "论文自查表.md"
OLD = ("| C1 | 方法可复现描述 | 有伪代码与参数 | **通过** | 算法 1 伪代码、§4.5 对照与消融设计、"
       "`final_config.json` |")
NEW = ("| C1 | 方法可复现描述 | 有伪代码与参数 | **通过** | 算法 1 伪代码、§4.5 对照与消融设计、"
       "`results_gate_tuning_v5/selected_gate_config.json`（补充材料 S16） |")


def main() -> None:
    config = ROOT / "results_gate_tuning_v5" / "selected_gate_config.json"
    if not config.exists():
        raise SystemExit(f"the replacement artefact is missing: {config}")
    print(f"source: {config.relative_to(ROOT)} exists "
          f"({config.stat().st_size} bytes); final_config.json does not exist anywhere")

    text = TABLE.read_text(encoding="utf-8")
    if OLD in text:
        if text.count(OLD) != 1:
            raise SystemExit("row C1 anchor is not unique")
        TABLE.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
        print("updated 论文自查表.md")
    elif NEW in text:
        print("论文自查表.md: already fixed")
    else:
        raise SystemExit("row C1 could not be located")

    check = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_cited_paths_v1.py")],
                           cwd=ROOT, capture_output=True, text=True, errors="replace")
    print(check.stdout.strip().splitlines()[-1])
    if check.returncode != 0:
        raise SystemExit("cited-path check still fails")
    print("SELFCHECK_EVIDENCE_PATH_FIXED")


if __name__ == "__main__":
    main()
