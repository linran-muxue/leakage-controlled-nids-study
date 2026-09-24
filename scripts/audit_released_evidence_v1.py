"""Recompute the released metrics from the released per-row predictions.

Every supplementary item ships predictions next to the metric tables derived
from them, but nothing verified that the two agree: a metrics file could be
stale, truncated, or produced from a different prediction file and every other
check would still pass.  This audit recomputes accuracy and Macro-F1 from the
predictions themselves and compares them with the stored values, over the
directories the supplementary bundle actually ships.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, f1_score

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
TOL = 1e-9
problems: list[str] = []
checked = 0


def compare(label: str, recomputed: float, stored: float) -> None:
    global checked
    checked += 1
    if abs(recomputed - stored) > TOL:
        problems.append("%s: prediction says %.6f, metrics file says %.6f"
                        % (label, recomputed, stored))


def check_rccf(directory: Path) -> None:
    combined = directory / "metrics_by_seed.csv"
    combined_rows = pd.read_csv(combined) if combined.exists() else None
    for path in sorted(directory.glob("predictions_seed*.csv")):
        seed = int(re.search(r"predictions_seed(\d+)\.csv$", path.name).group(1))
        metrics = directory / ("metrics_seed%d.csv" % seed)
        if metrics.exists():
            row = pd.read_csv(metrics).iloc[0]
        elif combined_rows is not None and "seed" in combined_rows.columns:
            # Some runs publish one combined table instead of per-seed files.
            candidates = combined_rows[combined_rows["seed"] == seed]
            if "model" in candidates.columns and len(candidates) > 1:
                named = [m for m in candidates["model"].unique()
                         if str(m) in directory.name]
                if named:
                    candidates = candidates[candidates["model"] == named[0]]
                elif "rccf" in set(candidates["model"]):
                    candidates = candidates[candidates["model"] == "rccf"]
            if candidates.empty:
                problems.append("%s/seed%d: no metrics row" % (directory.name, seed))
                continue
            row = candidates.iloc[0]
        else:
            problems.append("%s/seed%d: no metrics file" % (directory.name, seed))
            continue
        frame = pd.read_csv(path, usecols=["true_label", "predicted_label"])
        y, pred = frame["true_label"], frame["predicted_label"]
        compare("%s/seed%d macro_f1" % (directory.name, seed),
                f1_score(y, pred, average="macro", zero_division=0), float(row["macro_f1"]))
        compare("%s/seed%d accuracy" % (directory.name, seed),
                accuracy_score(y, pred), float(row["accuracy"]))


def check_baselines(directory: Path) -> None:
    aggregate = directory / "metrics_by_seed.csv"
    if not aggregate.exists():
        return
    stored = pd.read_csv(aggregate)
    for path in sorted(directory.glob("predictions_*_seed*.csv")):
        match = re.match(r"predictions_(.+)_seed(\d+)\.csv$", path.name)
        if not match:
            continue
        model, seed = match.group(1), int(match.group(2))
        rows = stored[(stored["model"] == model) & (stored["seed"] == seed)]
        if rows.empty:
            continue
        frame = pd.read_csv(path, usecols=["y_true", "y_pred"])
        row = rows.iloc[0]
        compare("%s/%s/seed%d macro_f1" % (directory.name, model, seed),
                f1_score(frame["y_true"], frame["y_pred"], average="macro", zero_division=0),
                float(row["macro_f1"]))
        compare("%s/%s/seed%d accuracy" % (directory.name, model, seed),
                accuracy_score(frame["y_true"], frame["y_pred"]), float(row["accuracy"]))


def main() -> int:
    spec = importlib.util.spec_from_file_location(
        "assembler", ROOT / "scripts" / "assemble_supplementary_v5.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    directories = sorted({ROOT / Path(source).parent
                          for _, sources in module.ITEMS.values() for source in sources})
    absent = [d.name for d in directories if not d.is_dir()]
    for directory in directories:
        if not directory.is_dir():
            continue
        before = len(problems)
        check_rccf(directory)
        check_baselines(directory)
        print("  %-46s%s" % (directory.name, "ok" if len(problems) == before else "MISMATCH"))
    print()
    print("recomputed %d metric value(s) from the released predictions" % checked)
    if absent:
        # Say what was not covered: three of the supplementary sources live in the
        # processed populations, which the archive does not redistribute, so a
        # fresh clone verifies fewer values than a full checkout does.
        print("not covered (folder absent, not redistributed): %s" % ", ".join(absent))
    if problems:
        for problem in problems:
            print("ISSUE " + problem)
        print("RELEASED_EVIDENCE_FAILED")
        return 1
    print("RELEASED_EVIDENCE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
