"""Audit raw-file by attack-label coverage without constructing a file-wise model split."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data_pipeline import map_attack_label

LABELS = ["Normal", "DoS/DDoS", "Brute Force", "Web Attack", "Bot", "PortScan", "Infiltration", "Heartbleed", "Other"]

def map_extended(value):
    mapped = map_attack_label(value, include_other=False)
    if mapped is not None:
        return mapped
    raw = str(value).strip().lower()
    if raw == "portscan": return "PortScan"
    if raw == "infiltration": return "Infiltration"
    if raw == "heartbleed": return "Heartbleed"
    return "Other"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--chunksize", type=int, default=100_000)
    args = ap.parse_args(); args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for path in sorted(args.raw_dir.rglob("*.csv")):
        counts = {label: 0 for label in LABELS}; total = 0
        for chunk in pd.read_csv(path, chunksize=args.chunksize, low_memory=False, encoding_errors="replace"):
            label_col = next(c for c in chunk.columns if str(c).strip().lower() == "label")
            mapped = chunk[label_col].map(map_extended)
            vc = mapped.value_counts()
            for label, count in vc.items(): counts[label] += int(count)
            total += len(chunk)
        row = {"file": str(path.relative_to(args.raw_dir)), "raw_rows": total, **counts}
        row["present_main_classes"] = sum(row[x] > 0 for x in LABELS[:5])
        row["present_all_audited_classes"] = sum(row[x] > 0 for x in LABELS)
        rows.append(row)
    table = pd.DataFrame(rows)
    table.to_csv(args.output_dir / "file_label_counts.csv", index=False, encoding="utf-8-sig")
    matrix = table.set_index("file")[LABELS]
    matrix.to_csv(args.output_dir / "file_label_matrix.csv", encoding="utf-8-sig")
    summary = {
        "raw_dir": str(args.raw_dir),
        "file_count": int(len(table)),
        "labels": LABELS,
        "files_with_all_five_main_classes": int((table.present_main_classes == 5).sum()),
        "files_missing_at_least_one_main_class": int((table.present_main_classes < 5).sum()),
        "note": "File-level split is reported as coverage audit only; no incomplete five-class file-wise test result is claimed."
    }
    (args.output_dir / "file_label_coverage_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(table.to_string(index=False)); print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__": main()
