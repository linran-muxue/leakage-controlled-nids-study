"""Download the newest openly licensed intrusion-detection corpora (2026).

Three deposits, all CC BY 4.0 and all published within the last four months:

  6TiSCHSet-2026   Zenodo 22113022  888 MB   6TiSCH telemetry, leakage-aware benchmark
  CTU-IDSEVAL-6    Zenodo 21027042   46 MB   Zeek flows with benign/malicious labels
  RTN traffic      Zenodo 18910837   38 MB   packet-level CSV for IDS evaluation

Each file is verified against the MD5 Zenodo publishes, and the result is
recorded in a manifest next to the files.
"""
from __future__ import annotations

import hashlib
import json
import ssl
import sys
import time
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(r"E:\论文\data\external\y2026")
API = "https://zenodo.org/api/records"
TARGETS = (
    ("6TiSCHSet-2026", "22113022", "61baydin/6tisch-attack-dataset-v1.0.0.zip",
     "9d2bd5d9009df18ccf9940c83cd291ba"),
    ("CTU-IDSEVAL-6", "21027042", "zeek.zip", "33b57c813053eed12ec3738b65f27ef0"),
    ("CTU-IDSEVAL-6", "21027042", "labels.zip", "a017b6f47fe0603595cec7d643f7e4a2"),
    ("CTU-IDSEVAL-6", "21027042", "CTU-IDSEVAL-6-summary.csv",
     "e408b8431e38428e8f9dfd0538986254"),
    ("RTN-traffic", "18910837", "RTN_traffic_dataset.csv",
     "81e307809d1d0ddeb31c934c689d5b19"),
)
CTX = ssl.create_default_context()


def digest(path: Path) -> str:
    hasher = hashlib.md5()
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
    for dataset, record, key, md5 in TARGETS:
        target = ROOT / dataset / Path(key).name
        url = f"{API}/{record}/files/{urllib.parse.quote(key, safe='')}/content"
        if target.exists() and digest(target) == md5:
            print(f"{dataset}/{target.name}: present, hash ok", flush=True)
        else:
            started = time.time()
            download(url + "?download=1", target)
            print(f"{dataset}/{target.name}: {target.stat().st_size / 1e6:.1f} MB in "
                  f"{time.time() - started:.0f}s", flush=True)
        actual = digest(target)
        if actual != md5:
            raise SystemExit(f"{target.name}: md5 mismatch {actual} != {md5}")
        manifest.append({"dataset": dataset, "record": record, "file": str(target),
                         "bytes": target.stat().st_size, "md5": actual,
                         "source": f"https://zenodo.org/records/{record}",
                         "license": "CC BY 4.0"})
    out = ROOT / "corpora_2026_manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"FETCH_2026_DONE files={len(manifest)} manifest={out}")


if __name__ == "__main__":
    import urllib.parse  # noqa: E402  (used in the loop above)
    main()
