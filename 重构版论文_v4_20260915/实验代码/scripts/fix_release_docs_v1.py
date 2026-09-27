"""Bring the three released metadata documents back in line with the paper.

The repository grew from three datasets and one population to four datasets and
four populations (53,237 / 3,365 / 413,209 / 2,429,503), and the manuscript
itself moved from the old JISA layout to ``重构版论文_v4_20260915/``.  The three
documents that describe the archive were never updated:

* ``README.md`` (shipped inside the submission bundle) still listed three
  datasets in its redistribution statement, and its artifact map pointed at the
  superseded ``results_paper_materials_v3/`` manuscripts while never mentioning
  the current manuscript directory or the two large populations.
* ``MODEL_CARD.md`` said all experiments use three datasets, and attributed the
  4.6x factor to per-row latency when it is the whole-batch throughput factor -
  the exact conflation the manuscript warns about (single-row P50 ratio 4.9).
* ``DATA_CARD.md`` described only the CIC-IDS2017 populations and omitted the
  N-BaIoT benchmark entirely.

No experimental number changes; the corrections are cross-references and one
mis-attributed ratio.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]


def fix(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise SystemExit(f"anchor not found exactly once in {path.name}: {text.count(old)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"updated {path.name}")


README_DATASETS_OLD = ("It does **not** redistribute the original CIC-IDS2017, NSL-KDD, or "
                       "UNSW-NB15 files.")
README_DATASETS_NEW = ("It does **not** redistribute the original CIC-IDS2017, NSL-KDD, "
                       "UNSW-NB15 or N-BaIoT files.")

README_ARTIFACTS_OLD = ("- `results_paper_materials_v3/`: manuscript, figures, Highlights, "
                        "Graphical Abstract, and supplementary index.")
README_ARTIFACTS_NEW = (
    "- `重构版论文_v4_20260915/`: **the current manuscript** (English and Chinese), its figures, "
    "the `S01-S29` supplementary bundle, the cover letter and the Highlights.\n"
    "- `results_paper_materials_v3/`: the earlier JISA-layout materials (superseded manuscripts, "
    "`Highlights_JISA`, `Graphical_Abstract_JISA` and the provenance tables). The submitted "
    "manuscript is the one under `重构版论文_v4_20260915/`; nothing here should be quoted as "
    "the final text.\n"
    "- `data_processed_cic_natural_v4_scale200k/`, `data_processed_cic_natural_v4_full/`: the "
    "413,209-flow and 2,429,503-flow populations behind the scale-sensitivity analyses "
    "(supplementary S27 and S29).\n"
    "- `superseded/`: files kept only for provenance; they are not the source of any number in "
    "the manuscript.")

README_PROTOCOL_OLD = ("The locked CIC-IDS2017 publication protocol is **v3b**.  "
                       "`data_processed_cic_natural_v3b`\n"
                       "is the primary capped natural-prior research population, while\n"
                       "`data_processed_cic_balanced_v3b` is a secondary balanced control subset.")
README_PROTOCOL_NEW = ("The locked CIC-IDS2017 publication protocol is **v3b**.  "
                       "`data_processed_cic_natural_v3b`\n"
                       "is the primary capped natural-prior research population, while\n"
                       "`data_processed_cic_balanced_v3b` is a secondary balanced control subset.  "
                       "The same\n"
                       "audit is then re-run with a 200,000-per-class cap "
                       "(`data_processed_cic_natural_v4_scale200k`,\n"
                       "413,209 flows) and with the cap removed entirely "
                       "(`data_processed_cic_natural_v4_full`,\n"
                       "2,429,503 flows); those two populations are reported in Section 5.7 and "
                       "in supplementary\n"
                       "S27 and S29, and they are where the aggregation-rule difference stops "
                       "being equivalent.")

MODEL_DATASETS_OLD = ("- **Not** validated on live traffic. All experiments use three public "
                      "research datasets.")
MODEL_DATASETS_NEW = ("- **Not** validated on live traffic. All experiments use four public "
                      "research datasets: CIC-IDS2017, NSL-KDD, UNSW-NB15 and N-BaIoT.")

MODEL_SIZE_OLD = ("The mechanism is 4.1 times larger and 4.6 times slower per row than a single "
                  "forest,")
MODEL_SIZE_NEW = ("The mechanism is 4.1 times larger than a single equal-weight forest, and its "
                  "whole-batch throughput is 4.6 times lower; the single-row P50 latency ratio is "
                  "4.9, a different quantity that must not be conflated with it,")

DATA_DATASETS_OLD = ("| UNSW-NB15 | UNSW Canberra Cyber (official project page) | Official "
                     "training and testing CSV | 2026-09-04 | Page requires citation of the "
                     "original paper; no SPDX identifier displayed |")
DATA_DATASETS_NEW = DATA_DATASETS_OLD + (
    "\n| N-BaIoT | UCI Machine Learning Repository, dataset 442 (official archive) | "
    "N-BaIoT.zip, 9 device folders / 90 CSVs after extraction, DOI 10.24432/C5RC8J, as "
    "published 2018 | 2026-09-19 | CC BY 4.0 stated on the dataset page (verified) |")

DATA_POPULATIONS_OLD = "| balanced control | 3,365 | 673 rows per class |"
DATA_POPULATIONS_NEW = (
    "| balanced control | 3,365 | 673 rows per class |\n"
    "| deduplicated, capped at 200,000 per class | 413,209 | scale-sensitivity population "
    "(supplementary S27) |\n"
    "| deduplicated, no cap | 2,429,503 | full corpus, train 1,700,652 / validation 364,425 / "
    "test 364,426 (supplementary S29) |\n"
    "| N-BaIoT audit and benchmark | 180,000 | 60,000 rows per class (Benign, Gafgyt, Mirai); "
    "near-duplicates removed before splitting (supplementary S28) |")


def main() -> None:
    readme = ROOT / "README.md"
    model = ROOT / "MODEL_CARD.md"
    data = ROOT / "DATA_CARD.md"
    fix(readme, README_PROTOCOL_OLD, README_PROTOCOL_NEW)
    fix(readme, README_DATASETS_OLD, README_DATASETS_NEW)
    fix(readme, README_ARTIFACTS_OLD, README_ARTIFACTS_NEW)
    fix(model, MODEL_DATASETS_OLD, MODEL_DATASETS_NEW)
    fix(model, MODEL_SIZE_OLD, MODEL_SIZE_NEW)
    fix(data, DATA_DATASETS_OLD, DATA_DATASETS_NEW)
    fix(data, DATA_POPULATIONS_OLD, DATA_POPULATIONS_NEW)
    print("RELEASE_DOCS_FIXED")


if __name__ == "__main__":
    main()
