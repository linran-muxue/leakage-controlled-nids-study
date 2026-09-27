"""Re-derive every cell of Tables 4, 5 and 7 from the released artefacts.

Table 6 has been covered since Round 20p; the three tables that carry the main
result were not, and the first pass over them found a defect: the Train (s)
column of Table 4(b) printed 0.451 / 0.299 / 0.494 for the three forest rows
while the released balanced-control run gives 0.249586 / 0.235422 / 0.130834 for
the same models over the same three seeds - and every other cell of those rows
does match that run.

Every printed cell is read back out of the manuscript and must equal its source
rounded to that cell's own precision, so a cell edited without re-deriving its
source fails the gate.  The two panels of Table 4 are parsed separately: they
reuse the same row labels, and a parser that merges them compares panel (b)
against panel (a) sources.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN = (BASE / "English_SCI_Manuscript_v4.md").read_text(encoding="utf-8")
passed = mismatches = 0
CELL = re.compile(r"-?\d+(?:\.\d+)?")
COLUMNS = ("accuracy", "balanced_accuracy", "macro_f1", "log_loss", "brier", "ece",
           "train_seconds", "predict_seconds")


def rows_between(start: str, stop: str, occurrence: int = 0) -> dict[str, list[str]]:
    """Markdown table rows between two markers."""
    lines = EN.splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith(start)]
    if len(starts) <= occurrence:
        raise SystemExit(f"table start not found: {start}")
    first = starts[occurrence]
    stops = [i for i in range(first + 1, len(lines)) if lines[i].startswith(stop)]
    if not stops:
        raise SystemExit(f"table stop not found after {start}: {stop}")
    rows: dict[str, list[str]] = {}
    for line in lines[first:stops[0]]:
        if not line.startswith("|") or set(line) <= set("|-: "):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells[0] in ("Model", "Comparison", "Population"):
            continue
        rows[cells[0]] = cells[1:]
    return rows


def cell(value: float, printed: str, label: str) -> None:
    global passed, mismatches
    cleaned = printed.replace("**", "").replace("*", "").replace("+", "")
    found = CELL.search(cleaned)
    if not found:
        raise SystemExit(f"no number in cell {printed!r}")
    text = found.group(0)
    digits = len(text.split(".")[1]) if "." in text else 0
    rendered = f"{float(value):.{digits}f}"
    if rendered == text:
        passed += 1
        print(f"OK    {label:<56}{text}")
    else:
        mismatches += 1
        print(f"ISSUE {label:<56}printed {text}, source rounds to {rendered}")


def interval(value: float, printed: str, label: str, first: bool) -> None:
    parts = printed.split(",")
    cell(value, parts[0] if first else parts[1], label)


def whole(value: float, printed: str, label: str) -> None:
    global passed, mismatches
    target = int(round(value))
    cleaned = re.sub(r"[, ]", "", printed.replace("**", ""))
    if cleaned == str(target):
        passed += 1
        print(f"OK    {label:<56}{printed}")
    else:
        mismatches += 1
        print(f"ISSUE {label:<56}printed {printed}, source {target}")


def verdict(flag: bool, printed: str, label: str) -> None:
    global passed, mismatches
    expected = "equivalent" if flag else "not equivalent"
    if expected == printed.replace("**", ""):
        passed += 1
        print(f"OK    {label:<56}{expected}")
    else:
        mismatches += 1
        print(f"ISSUE {label:<56}printed {printed}, source {expected}")


def main() -> int:
    ten = pd.read_csv(ROOT / "results_seeds10_v5" / "table4a_10seeds.csv").set_index("model")
    mlp = pd.read_csv(ROOT / "results_mlp_final_v5" / "metrics_aggregate.csv").iloc[0]
    mlp_paired = json.loads((ROOT / "results_mlp_final_v5" /
                             "mlp_vs_rccf_summary.json").read_text(encoding="utf-8"))

    print("== Table 4(a) natural-prior population (ten seeds) ==")
    natural = {
        "RCCF": ["rccf"],
        "Equal RF (chi-square, k = 60)": ["equal_rf_chi2"],
        "Equal RF (full features)": ["equal_rf_all"],
        "ExtraTrees (chi-square)": ["extra_trees_chi2"],
    }
    rows = rows_between("**Table 4.", "(b) Balanced")
    for label, (model,) in natural.items():
        for name, printed in zip(COLUMNS, rows[label]):
            cell(float(ten.loc[model, name]), printed, f"4a {label[:26]} {name}")
    mlp_values = [mlp.accuracy_mean, mlp_paired["mlp_balanced_accuracy_mean"], mlp.macro_f1_mean,
                  mlp.log_loss_mean, mlp.brier_macro_mean, mlp.ece_mean,
                  mlp.train_seconds_mean, mlp.predict_seconds_mean]
    for name, value, printed in zip(COLUMNS, mlp_values, rows["MLP (128 hidden units, k = 60)"]):
        cell(float(value), printed, f"4a MLP {name}")

    print()
    print("== Table 4(b) balanced control population (three seeds) ==")
    balanced_rccf = pd.read_csv(ROOT / "results_rccf_cic_balanced_v3b" /
                                "metrics_aggregate.csv").iloc[0]
    baseline = pd.read_csv(ROOT / "results_cic_balanced_baselines_v3b" /
                           "metrics_aggregate_flat.csv").set_index("model")
    strong = pd.read_csv(ROOT / "results_cfrg_strong_baselines_v2_verified" /
                         "summary.csv", header=[0, 1])
    strong = strong.set_index(strong.columns[0])
    # the balanced files name the Brier column brier_macro_mean
    balanced_names = ("accuracy_mean", "balanced_accuracy_mean", "macro_f1_mean",
                      "log_loss_mean", "brier_macro_mean", "ece_mean",
                      "train_seconds_mean", "predict_seconds_mean")
    rows = rows_between("**Table 4.", "**First")
    # the RCCF run names the same column brier_mean; the baseline run brier_macro_mean
    rccf_names = ("accuracy_mean", "balanced_accuracy_mean", "macro_f1_mean",
                  "log_loss_mean", "brier_mean", "ece_mean",
                  "train_seconds_mean", "predict_seconds_mean")
    rccf_values = [float(getattr(balanced_rccf, name)) for name in rccf_names]
    for name, value, printed in zip(COLUMNS, rccf_values, rows["RCCF"]):
        cell(value, printed, f"4b RCCF {name}")
    for label, model in (("Equal RF (chi-square)", "equal_rf_chi2"),
                         ("Equal RF (full features)", "equal_rf_all"),
                         ("ExtraTrees (chi-square)", "extra_trees_chi2")):
        for name, source, printed in zip(COLUMNS, balanced_names, rows[label]):
            cell(float(baseline.loc[model, source]), printed, f"4b {label[:26]} {name}")
    strong_names = {"brier": "brier_macro"}
    for name, printed in zip(COLUMNS,
                             rows["XGBoost (independently tuned, validation-selected)"]):
        column = strong_names.get(name, name)
        cell(float(strong.loc["xgboost", (column, "mean")]), printed, f"4b XGBoost {name}")

    print()
    print("== Table 5 paired statistics (ten seeds) ==")
    power = pd.read_csv(ROOT / "results_seeds10_v5" / "power_analysis.csv").set_index("comparison")
    effects = pd.read_csv(ROOT / "results_seeds10_v5" / "effect_sizes.csv").set_index("comparison")
    holm = pd.read_csv(ROOT / "results_seeds10_v5" / "signflip_holm.csv").set_index("comparison")
    comparisons = {
        "RCCF - equal RF (chi-square)": "rccf_minus_equal_rf_chi2",
        "RCCF - equal RF (all features)": "rccf_minus_equal_rf_all",
        "RCCF - ExtraTrees (chi-square)": "rccf_minus_extra_trees_chi2",
    }
    rows = rows_between("**Table 5.", "**Table 6")
    for label, key in comparisons.items():
        row, stats = rows[label], power.loc[key]
        cell(float(stats.mean_difference), row[0], f"5 {label[:26]} mean")
        cell(float(stats.sd_difference), row[1], f"5 {label[:26]} sd")
        interval(float(stats.ci95_low), row[2], f"5 {label[:26]} 95% low", True)
        interval(float(stats.ci95_high), row[2], f"5 {label[:26]} 95% high", False)
        interval(float(stats.ci90_low), row[3], f"5 {label[:26]} 90% low", True)
        interval(float(stats.ci90_high), row[3], f"5 {label[:26]} 90% high", False)
        verdict(bool(stats["tost_equivalent_at_0.005"]), row[4], f"5 {label[:26]} TOST 0.005")
        verdict(bool(stats["tost_equivalent_at_0.01"]), row[5], f"5 {label[:26]} TOST 0.01")
        cell(float(stats.min_detectable_effect_80pct), row[6], f"5 {label[:26]} MDE 80%")
        cell(float(effects.loc[key, "cohens_dz"]), row[7], f"5 {label[:26]} Cohen d_z")
        cell(float(holm.loc[key, "holm_adjusted_p"]), row[8], f"5 {label[:26]} Holm p")
        split = f"{int(effects.loc[key, 'seeds_favouring_rccf'])}/" \
                f"{int(effects.loc[key, 'seeds_favouring_baseline'])}"
        printed_split = re.sub(r"\s", "", row[9]).replace("**", "")
        global passed, mismatches
        if printed_split == split:
            passed += 1
            print(f"OK    {'5 ' + label[:26] + ' sign split':<56}{printed_split}")
        else:
            mismatches += 1
            print(f"ISSUE {'5 ' + label[:26] + ' sign split':<56}"
                  f"printed {printed_split}, source {split}")

    print()
    print("== Table 7 scale ladder ==")
    scale = pd.read_csv(ROOT / "results_scale_sensitivity_v46" / "metrics_aggregate.csv",
                        header=[0, 1])
    scale = scale.set_index(scale.columns[0])
    # the two-row header leaves a NaN row and the literal "model" row behind
    scale = scale[scale.index.notna() & (scale.index != "model")]
    scale_summary = json.loads((ROOT / "results_scale_sensitivity_v46" /
                                "scale_sensitivity_summary.json").read_text(encoding="utf-8"))
    full = pd.read_csv(ROOT / "results_full_corpus_v49" / "metrics_aggregate.csv", header=[0, 1])
    full = full.set_index(full.columns[0])
    full = full[full.index.notna() & (full.index != "model")]
    # both runs release the baseline side and the conditional side separately
    scale_rccf = pd.read_csv(ROOT / "results_rccf_cic_natural_v4_scale200k" /
                             "metrics_aggregate.csv").iloc[0]
    full_rccf = pd.read_csv(ROOT / "results_rccf_cic_natural_v4_full" /
                            "metrics_aggregate.csv").iloc[0]
    full_summary = json.loads((ROOT / "results_full_corpus_v49" /
                               "full_corpus_summary.json").read_text(encoding="utf-8"))
    ladder = {
        "Capped, 20,000 per class":
            (53237, 7986, float(ten.loc["rccf", "macro_f1"]),
             float(ten.loc["equal_rf_chi2", "macro_f1"]), True, True),
        "Capped, 200,000 per class":
            (413209, scale_summary["population_rows"],
             float(scale_rccf.macro_f1_mean),
             float(scale.loc["equal_rf_chi2", ("macro_f1", "mean")]),
             bool(scale_summary["tost"]["0.005"]["equivalent"]),
             bool(scale_summary["tost"]["0.01"]["equivalent"])),
        "Uncapped (full deduplicated corpus)":
            (2429503, full_summary["test_rows"],
             float(full_rccf.macro_f1_mean),
             float(full.loc["equal_rf_chi2", ("macro_f1", "mean")]),
             bool(full_summary["tost"]["0.005"]["equivalent"]),
             bool(full_summary["tost"]["0.01"]["equivalent"])),
    }
    rows = rows_between("**Table 7.", "### 6")
    for label, (flows, test_rows, rccf, control, eq005, eq01) in ladder.items():
        row = rows[label]
        whole(flows, row[0], f"7 {label[:24]} flows")
        whole(test_rows, row[1], f"7 {label[:24]} test rows")
        cell(rccf, row[2], f"7 {label[:24]} RCCF")
        cell(control, row[3], f"7 {label[:24]} equal RF")
        cell(rccf - control, row[4], f"7 {label[:24]} difference")
        verdict(eq005, row[5], f"7 {label[:24]} TOST 0.005")
        verdict(eq01, row[6], f"7 {label[:24]} TOST 0.01")

    print()
    print(f"assertions passed {passed} | mismatches {mismatches}")
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
