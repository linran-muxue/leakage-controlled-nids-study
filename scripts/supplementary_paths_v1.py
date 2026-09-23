"""Locate the canonical supplementary bundle whatever its S-range name.

The bundle directory is renamed every time a supplementary item is added
(``补充材料_S01_S26`` -> ``S01_S28`` -> ``S01_S29``).  Five scripts used to
hard-code that name, so each addition required editing all of them.  They now
derive the name from the item ids registered in ``assemble_supplementary_v5.py``.
"""

from __future__ import annotations

import re
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ITEM = re.compile(r'^\s*"(S\d+)"\s*:', re.M)


def latest_bundle_name() -> str:
    """Return the bundle directory name implied by the registered item ids."""
    text = (_HERE / "assemble_supplementary_v5.py").read_text(encoding="utf-8")
    ids = _ITEM.findall(text)
    if not ids:
        raise FileNotFoundError("no supplementary ids found in assemble_supplementary_v5.py")
    return f"补充材料_S01_S{max(int(i[1:]) for i in ids):02d}"


def supplementary_bundle(base: Path) -> Path:
    """Resolve the bundle under ``base``, tolerating a not-yet-renamed folder."""
    expected = base / latest_bundle_name()
    if expected.exists():
        return expected
    candidates = sorted(base.glob("补充材料_S01_S*"))
    return candidates[-1] if candidates else expected
