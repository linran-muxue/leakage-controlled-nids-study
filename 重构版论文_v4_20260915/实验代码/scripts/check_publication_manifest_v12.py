"""Check that the publication manifest still describes the released artifacts.
The manifest is what an editor or reviewer downloads to verify the package, so
every field must match the files on disk: the release tag, the canonical
manuscript path and every recorded SHA-256. The tag stayed at v1.0.2 for eight
releases because nothing checked it.
"""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "results_publication_final" / "MANIFEST.json"
BASE = ROOT / "重构版论文_v4_20260915"
def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()
def main() -> int:
    problems: list[str] = []
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    tags = subprocess.run(["git", "tag"], capture_output=True, text=True,
                          cwd=ROOT).stdout.split()
    latest = sorted(tags, key=lambda t: [int(x) for x in re.findall(r"\d+", t)])[-1] if tags else ""
    en = (BASE / "English_SCI_Manuscript_v4.md").read_text("utf-8")
    zh = (BASE / "中文SCI论文_v4_重构版.md").read_text("utf-8")
    cited = set(re.findall(r"v1\.\d+\.\d+", en)) | set(re.findall(r"v1\.\d+\.\d+", zh))
    manifest_tag = payload.get("public_release_tag", "")
    print(f"manifest tag: {manifest_tag} | latest tag: {latest} | manuscript cites: {sorted(cited)}")
    if manifest_tag != latest:
        problems.append(f"manifest tag {manifest_tag} != latest tag {latest}")
    if cited != {latest}:
        problems.append(f"manuscripts cite {sorted(cited)}, latest tag is {latest}")
    canonical = payload.get("canonical_manuscript", "")
    print(f"canonical manuscript: {canonical}")
    if not (ROOT / canonical).exists():
        problems.append(f"canonical manuscript missing: {canonical}")
    if "重构版论文_v4_20260915" not in canonical:
        problems.append(f"canonical manuscript is not the current v4 document: {canonical}")
    artifacts = payload.get("artifacts", [])
    stale = []
    for entry in artifacts:
        path = ROOT / entry["path"]
        if not path.exists():
            stale.append(f"missing {entry['path']}")
        elif path.stat().st_size != entry["bytes"]:
            stale.append(f"size {entry['path']}")
        elif digest(path) != entry["sha256"]:
            stale.append(f"hash {entry['path']}")
    print(f"artifacts verified: {len(artifacts) - len(stale)}/{len(artifacts)}")
    if stale:
        problems.extend(stale[:10])
        if len(stale) > 10:
            problems.append(f"... and {len(stale) - 10} more")
    print()
    if problems:
        for problem in problems:
            print(f"ISSUE {problem}")
        print("MANIFEST_MISMATCH")
        return 1
    print("MANIFEST_OK")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
