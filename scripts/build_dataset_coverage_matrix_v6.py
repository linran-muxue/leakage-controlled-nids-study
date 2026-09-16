"""Dataset coverage matrix (supplementary item S25)."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results_review_v5"
OUT.mkdir(exist_ok=True)

ROWS = [
    ["dimension", "CIC-IDS2017", "NSL-KDD", "UNSW-NB15"],
    ["capture era", "2017", "1998 lineage (KDD CUP 99)", "2015"],
    ["testbed", "enterprise-like B-profile with HTTP/HTTPS/FTP/SSH/email",
     "simulated DARPA evaluation network", "IXIA PerfectStorm synthetic traffic generator"],
    ["feature extractor", "CICFlowMeter, 78 features", "KDD connection records, 41 features",
     "Argus and Bro derived, 49 features"],
    ["rows used", "2,830,743 raw; 53,237 audited research population",
     "125,973 train / 22,544 test", "175,341 train / 82,332 test"],
    ["native label space", "15 raw labels, 5 retained", "5 classes", "10 attack categories"],
    ["minority classes", "Web Attack 1.26%, Bot 3.66%", "R2L and U2R", "Analysis, Backdoor, Worms"],
    ["known defects", "duplicate flows, 133 cross-label conflicts, 12 constant columns",
     "redundancy inherited from KDD CUP 99", "largely synthetic attacks, cross-split feature overlap"],
    ["role in this study", "primary protocol and two populations", "independent native-label benchmark",
     "independent native-label benchmark"],
    ["what a fourth dataset would add", "an IoT or OT deployment, a different capture vantage point, "
     "or a temporally separated capture from the same testbed", "", ""],
]


def main() -> None:
    path = OUT / "dataset_coverage_matrix.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        csv.writer(handle).writerows(ROWS)
    print(f"COVERAGE_MATRIX={path}")


if __name__ == "__main__":
    main()
