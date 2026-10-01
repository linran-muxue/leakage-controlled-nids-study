"""Download the 2025 intrusion-detection corpora that are openly available."""
from __future__ import annotations

import hashlib
import json
import ssl
import sys
import time
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(r"E:\论文\data\external\y2025")
ZEN = "https://zenodo.org/records"
MEN = "https://data.mendeley.com/public-files/datasets/pkskt3fv3v/files/f312df3b-ff0a-4fb1-b8ec-65af43f7eb8e/file_downloaded"
TARGETS = [
    {"dataset": "UAVIDS-2025", "url": ZEN + "/15336998/files/UAVIDS-2025.csv?download=1",
     "name": "UAVIDS-2025.csv", "sha256": None},
    {"dataset": "GeNIS", "url": ZEN + "/14919237/files/4-preprocessed.zip?download=1",
     "name": "4-preprocessed.zip", "sha256": None},
    {"dataset": "IDS2025", "url": MEN, "name": "IDS2025.xlsx",
     "sha256": "d9f1d15abb54c80ade4efd264edd3a65821b72ec9619f0a64c8ebb7587134544"},
]
CTX = ssl.create_default_context()


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 22), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def download(url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "rccf-repro/1.0"})
    with urllib.request.urlopen(request, timeout=900, context=CTX) as response, \
            target.open("wb") as handle:
        while chunk := response.read(1 << 22):
            handle.write(chunk)


def main() -> None:
    manifest = []
    for entry in TARGETS:
        target = ROOT / entry["dataset"] / entry["name"]
        if target.exists() and target.stat().st_size > 0:
            print(f"{entry['dataset']}: present, hashing", flush=True)
        else:
            started = time.time()
            download(entry["url"], target)
            print(f"{entry['dataset']}: {target.stat().st_size / 1e6:.1f} MB in "
                  f"{time.time() - started:.0f}s", flush=True)
        record = {"dataset": entry["dataset"], "file": str(target),
                  "bytes": target.stat().st_size, "sha256": digest(target)}
        if entry.get("sha256"):
            if record["sha256"] != entry["sha256"]:
                raise SystemExit(f"{entry['dataset']}: sha256 mismatch")
            record["sha256_verified"] = True
        manifest.append(record)
    out = ROOT / "corpora_2025_manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"FETCH_2025_DONE files={len(manifest)} manifest={out}")


if __name__ == "__main__":
    main()
