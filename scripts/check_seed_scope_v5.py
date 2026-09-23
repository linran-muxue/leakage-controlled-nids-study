"""Guard the seed scope of every quoted number (Round 20d).

The ten-seed upgrade rewrote Table 4(a) and its text, but the neural-baseline
row (three seeds), its paragraph and Figure 4 (three seeds) kept the old run
while the captions claimed ten seeds. This check recomputes both scopes from
their source files and asserts that the manuscripts, the captions and the two
figure builders label them correctly.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
MLP = ROOT / "results_mlp_final_v5"
TEN = ROOT / "results_seeds10_v5"
SHARED_SEEDS = [42, 2024, 3407]
problems: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    if not ok:
        problems.append(f"{label}: {detail}")


def function_body(source: str, name: str) -> str:
    start = source.index(f"def {name}(")
    end = source.find("\ndef ", start + 1)
    return source[start:] if end == -1 else source[start:end]


def main() -> int:
    en = (BASE / "English_SCI_Manuscript_v4.md").read_text(encoding="utf-8")
    zh = (BASE / "中文SCI论文_v4_重构版.md").read_text(encoding="utf-8")
    en_builder = (ROOT / "scripts" / "build_figures_en_v5.py").read_text(encoding="utf-8")
    zh_builder = (ROOT / "scripts" / "build_restructured_figures_v4.py").read_text(encoding="utf-8")

    # ---- source scopes -------------------------------------------------
    mlp_by_seed = pd.read_csv(MLP / "metrics_by_seed.csv")
    mlp_agg = pd.read_csv(MLP / "metrics_aggregate.csv").iloc[0]
    ten = pd.read_csv(TEN / "table4a_10seeds.csv").set_index("model")
    ten_by_seed = pd.read_csv(TEN / "metrics_by_seed.csv")
    rccf3 = pd.read_csv(ROOT / "results_rccf_cic_natural_v3b" / "metrics_aggregate.csv").iloc[0]

    mlp_seeds = sorted(int(s) for s in mlp_by_seed["seed"])
    check("MLP per-seed rows", len(mlp_seeds) == 3, f"{mlp_seeds}")
    check("MLP seeds are the shared three", mlp_seeds == SHARED_SEEDS, f"{mlp_seeds}")
    ten_seeds = sorted(int(s) for s in ten_by_seed["seed"].unique())
    check("ten-seed source rows", len(ten_seeds) == 10, f"{ten_seeds}")

    mlp_bal = float(np.mean([
        balanced_accuracy_score(
            (pred := pd.read_csv(MLP / f"predictions_seed{s}.csv"))["true_label"],
            pred["predicted_label"])
        for s in SHARED_SEEDS]))

    # ---- the MLP row is the three-seed mean in both manuscripts --------
    row_en = (f"| MLP (128 hidden units, k = 60) | {mlp_agg.accuracy_mean:.5f} | {mlp_bal:.5f} | "
              f"{mlp_agg.macro_f1_mean:.6f} | {mlp_agg.log_loss_mean:.5f} | "
              f"{mlp_agg.brier_macro_mean:.6f} | {mlp_agg.ece_mean:.6f} | "
              f"{mlp_agg.train_seconds_mean:.2f} | {mlp_agg.predict_seconds_mean:.4f} |")
    row_zh = row_en.replace("MLP (128 hidden units, k = 60)", "MLP（128 隐单元，k = 60）")
    check("EN MLP row is the three-seed mean", row_en in en, row_en)
    check("ZH MLP row is the three-seed mean", row_zh in zh, row_zh)

    # ---- the caveats are written down ----------------------------------
    for label, text, needle in (
        ("EN table head", en, "mean of ten seeds (MLP row: three seeds common to both runs)"),
        ("EN paragraph scope", en,
         "Every comparison in this paragraph is computed on the three seeds common to both runs"),
        ("EN figure caption", en, "the MLP bar uses the three seeds common to both runs"),
        ("ZH table head", zh, "十种子均值（MLP 行为两次运行共有的三个种子）"),
        ("ZH paragraph scope", zh, "本段所有对照均在两次运行共有的三个种子"),
        ("ZH figure note", zh, "（MLP 柱为两次运行共有的三个种子）"),
    ):
        check(label, needle in text, needle)

    # ---- the paragraph's RCCF reference values are the three-seed ones --
    ref = {
        "accuracy": f"{rccf3.accuracy_mean:.5f}",
        "macro_f1": f"{rccf3.macro_f1_mean:.6f}",
        "balanced_accuracy": f"{rccf3.balanced_accuracy_mean:.5f}",
        "brier": f"{rccf3.brier_mean:.6f}",
    }
    check("EN quotes RCCF three-seed macro-F1", f"against {ref['macro_f1']}" in en, ref["macro_f1"])
    check("ZH quotes RCCF three-seed macro-F1", f"对 RCCF 的 {ref['macro_f1']}" in zh, ref["macro_f1"])
    check("EN quotes RCCF three-seed balanced accuracy",
          f"against {ref['balanced_accuracy']}" in en, ref["balanced_accuracy"])
    check("EN quotes RCCF three-seed Brier", f"against {ref['brier']}" in en, ref["brier"])
    check("ZH quotes RCCF three-seed balanced accuracy",
          f"对 {ref['balanced_accuracy']}" in zh, ref["balanced_accuracy"])
    check("ZH quotes RCCF three-seed Brier", f"对 {ref['brier']}" in zh, ref["brier"])

    # ---- Figure 4 is drawn from the ten-seed run ------------------------
    en_fig4 = function_body(en_builder, "fig4")
    zh_fig4 = function_body(zh_builder, "_natural_table") + function_body(zh_builder, "fig4")
    for label, body in (("EN", en_fig4), ("ZH", zh_fig4)):
        check(f"{label} fig4 uses the ten-seed table", 'table4a_10seeds.csv' in body)
        check(f"{label} fig4 uses the ten-seed bootstrap", 'tost_results.csv' in body)
    check("EN fig4 labels the MLP bar", "MLP (3 seeds)" in en_fig4)
    check("ZH fig4 labels the MLP bar", "MLP（三种子）" in zh_fig4)

    # ---- the ten-seed values the figure plots are the ones in Table 4(a)
    for model, token in (("rccf", "0.889278"), ("equal_rf_chi2", "0.889734")):
        value = f"{ten.loc[model, 'macro_f1']:.6f}"
        check(f"ten-seed {model} macro-F1", value == token, value)
        check(f"manuscripts carry {token}", token in en and token in zh, token)

    if problems:
        for problem in problems:
            print(f"ISSUE {problem}")
        print("SEED_SCOPE_FAILED")
        return 1
    print(f"seed scopes OK: MLP {mlp_seeds}, primary {len(ten_seeds)} seeds; "
          f"figure 4 redrawn from the ten-seed run")
    print("SEED_SCOPE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
