"""One-shot finaliser for the full-corpus experiment.
Run after the ten-seed full-corpus RCCF batch finishes: it computes the paired
statistics, writes the Section 5.7 paragraph into both manuscripts with the
measured numbers, registers the new supplementary item, and rebuilds the
deliverables.
"""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import f1_score

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
PY = sys.executable
RCCF_DIR = ROOT / "results_rccf_cic_natural_v4_full"
CONTROL_DIR = ROOT / "results_full_corpus_v49"
SEEDS = [42, 2024, 3407, 7, 13, 101, 202, 303, 404, 505]
CONSOLIDATE = ROOT / "scripts" / "consolidate_rccf_full_metrics_v1.py"


def rebuild_aggregates() -> None:
    """Rebuild RCCF aggregate files from every per-seed file.

    The batch is normally resumed across several invocations (2.3 h per seed),
    and each invocation overwrites ``metrics_by_seed.csv`` with only the seeds
    it handled.  Consolidating here keeps the artefact referenced by S29 honest.
    """
    result = subprocess.run([PY, str(CONSOLIDATE), "--rccf-dir", str(RCCF_DIR)],
                            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                            errors="replace")
    sys.stdout.write(result.stdout)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise SystemExit("aggregate consolidation failed")


def training_cost() -> dict:
    """Mean training seconds per seed for RCCF and for the equal-weight control.

    The cost gap is the one quantity in this comparison that is not uncertain,
    so it is reported alongside the accuracy difference.
    """
    rccf = []
    for seed in SEEDS:
        path = RCCF_DIR / f"metrics_seed{seed}.csv"
        if path.exists():
            rccf.append(float(pd.read_csv(path)["train_seconds"].iloc[0]))
    control = float("nan")
    by_seed = CONTROL_DIR / "metrics_by_seed.csv"
    if by_seed.exists():
        frame = pd.read_csv(by_seed)
        subset = frame.loc[frame["model"] == "equal_rf_chi2", "train_seconds"]
        if len(subset):
            control = float(subset.mean())
    return {
        "rccf_mean_train_seconds": float(np.mean(rccf)) if rccf else float("nan"),
        "control_mean_train_seconds": control,
        "train_slowdown": (float(np.mean(rccf)) / control) if rccf and control else float("nan"),
    }


def paired_stats() -> dict:
    rows = []
    for seed in SEEDS:
        left_path = RCCF_DIR / f"predictions_seed{seed}.csv"
        right_path = CONTROL_DIR / f"predictions_equal_rf_chi2_seed{seed}.csv"
        if not (left_path.exists() and right_path.exists()):
            continue
        left = pd.read_csv(left_path)
        right = pd.read_csv(right_path)
        if not (left["true_label"].to_numpy() == right["y_true"].to_numpy()).all():
            raise SystemExit(f"row misalignment at seed {seed}")
        y_true = left["true_label"].to_numpy()
        a = left["predicted_label"].to_numpy()
        b = right["y_pred"].to_numpy()
        rows.append({
            "seed": seed,
            "rccf_macro_f1": f1_score(y_true, a, average="macro", zero_division=0),
            "control_macro_f1": f1_score(y_true, b, average="macro", zero_division=0),
            "disagreements": int((a != b).sum()),
            "rows": int(len(y_true)),
        })
    frame = pd.DataFrame(rows)
    frame["difference"] = frame["rccf_macro_f1"] - frame["control_macro_f1"]
    frame.to_csv(CONTROL_DIR / "full_corpus_paired_by_seed.csv", index=False, encoding="utf-8-sig")
    values = frame["difference"].to_numpy()
    n = len(values)
    mean = float(values.mean())
    sd = float(values.std(ddof=1)) if n > 1 else float("nan")
    sem = sd / np.sqrt(n) if n > 1 else float("nan")
    t90 = stats.t.ppf(0.95, n - 1) if n > 1 else float("nan")
    tost = {}
    if n > 1:
        for margin in (0.005, 0.01):
            lo = stats.ttest_1samp(values, -margin, alternative="greater").pvalue
            hi = stats.ttest_1samp(values, margin, alternative="less").pvalue
            tost[str(margin)] = {"p_low": float(lo), "p_high": float(hi),
                                 "equivalent": bool(lo < 0.05 and hi < 0.05)}
    summary = {
        "seeds": frame["seed"].tolist(), "n_seeds": n,
        "test_rows": int(frame["rows"].iloc[0]),
        "rccf_mean_macro_f1": float(frame["rccf_macro_f1"].mean()),
        "control_mean_macro_f1": float(frame["control_macro_f1"].mean()),
        "mean_difference": mean, "sd": sd,
        "seed_level_90_interval": [mean - t90 * sem, mean + t90 * sem],
        "tost": tost,
        "mean_disagreements": float(frame["disagreements"].mean()),
        "max_disagreements": int(frame["disagreements"].max()),
    }
    summary.update(training_cost())
    (CONTROL_DIR / "full_corpus_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def paragraph_en(s: dict) -> str:
    lo, hi = s["seed_level_90_interval"]
    tost = ("equivalent at both pre-specified margins"
            if s["tost"] and all(v["equivalent"] for v in s["tost"].values())
            else "not evaluable or not equivalent at one margin")
    cost = ""
    if np.isfinite(s.get("rccf_mean_train_seconds", float("nan"))):
        cost = (f" The cost asymmetry is at its most extreme here: {s['rccf_mean_train_seconds']:.0f} s to train "
                f"RCCF per seed against {s['control_mean_train_seconds']:.0f} s for the equal-weight forest "
                f"({s['train_slowdown']:.0f}x), at a quality difference of {s['mean_difference']:.6f}.")
    return (
        "**The full deduplicated corpus.** Removing the per-class cap entirely yields 2,429,503 flows "
        "(train 1,700,651 / validation 364,426 / test 364,426) - the complete deduplicated CIC-IDS2017 "
        "corpus, in which Web Attack contributes 0.028% of the rows. A single RCCF fit takes about 2.3 "
        f"hours at this scale, so the comparison was run as a batch over the same ten seeds: RCCF averages "
        f"{s['rccf_mean_macro_f1']:.6f} Macro-F1 against {s['control_mean_macro_f1']:.6f} for the equal-weight "
        f"chi-square forest, a mean paired difference of {s['mean_difference']:.6f} "
        f"(SD {s['sd']:.6f}; seed-level 90% interval [{lo:.6f}, {hi:.6f}]), which is {tost}. The two arms "
        f"disagree on {s['mean_disagreements']:.0f} of {s['test_rows']:,} test rows per seed on average "
        "(at most {max_d}) - the same order as on the capped populations. The context baselines separate more "
        "sharply here than anywhere else in the study: XGBoost reaches 0.800255 Macro-F1, the equal-weight "
        "full-feature forest 0.738143, extremely randomised trees 0.696629 and a depth-limited decision tree "
        "0.595653, so the model-family gap between XGBoost and the equal-weight chi-square forest (0.041) "
        "exceeds every protocol effect measured here except the class prior. Accuracy, by contrast, is 0.9993 "
        "for XGBoost and 0.9958 for the equal-weight forest - the clearest illustration in this study of how "
        "much accuracy hides on an imbalanced corpus.".replace("{max_d}", str(s["max_disagreements"]))
        + cost
    )


def paragraph_zh(s: dict) -> str:
    lo, hi = s["seed_level_90_interval"]
    tost = ("在两个预设边界上均等价"
            if s["tost"] and all(v["equivalent"] for v in s["tost"].values())
            else "无法判定或在其中一个边界上不等价")
    cost = ""
    if np.isfinite(s.get("rccf_mean_train_seconds", float("nan"))):
        cost = (f"该规模下代价不对称也最极端：RCCF 每个种子训练 {s['rccf_mean_train_seconds']:.0f} 秒，"
                f"等权森林仅需 {s['control_mean_train_seconds']:.0f} 秒（{s['train_slowdown']:.0f} 倍），"
                f"而质量差为 {s['mean_difference']:.6f}。")
    return (
        "**完整去重语料。** 完全取消每类上限后得到 2 429 503 条（训练 1 700 651 / 验证 364 426 / 测试 364 426），"
        "即去重后的 CIC-IDS2017 全语料，其中 Web Attack 仅占 0.028%。该规模下单次 RCCF 训练约需 2.3 小时，"
        f"因此按同样的十个种子批量运行：RCCF 平均 Macro-F1 为 {s['rccf_mean_macro_f1']:.6f}，等权卡方森林为 "
        f"{s['control_mean_macro_f1']:.6f}，平均配对差 {s['mean_difference']:.6f}（标准差 {s['sd']:.6f}；"
        f"种子级 90% 区间 [{lo:.6f}, {hi:.6f}]），{tost}。两个分支平均每个种子在 {s['test_rows']:,} 条测试样本中"
        f"分歧 {s['mean_disagreements']:.0f} 条（最多 {s['max_disagreements']} 条），与截断总体同量级。"
        "其余基线在全语料上的分化比本研究的任何其他设置都更剧烈：XGBoost 达 0.800255，全特征等权森林 0.738143，"
        "极端随机树 0.696629，限深决策树 0.595653；XGBoost 相对等权卡方森林的模型族差距（0.041）超过本研究测得的"
        "除类别先验以外的全部协议效应。而准确率上 XGBoost 为 0.9993、等权森林为 0.9958——这是全文最能说明"
        "「准确率在不平衡语料上会掩盖多少问题」的一处证据。" + cost
    )


def insert_into_manuscript(name: str, paragraph: str, anchor: str) -> bool:
    path = BASE / name
    text = path.read_text(encoding="utf-8")
    if "The full deduplicated corpus" in text or "完整去重语料" in text:
        print(f"{name}: full-corpus paragraph already present")
        return False
    if anchor not in text:
        print(f"{name}: anchor not found, paragraph not inserted")
        return False
    path.write_text(text.replace(anchor, paragraph + "\n\n" + anchor, 1), encoding="utf-8")
    print(f"{name}: full-corpus paragraph inserted")
    return True


def main() -> None:
    rebuild_aggregates()
    summary = paired_stats()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if summary["n_seeds"] < 10:
        # Guard: inserting a partial result would trip the "already present"
        # check on the next run and silently freeze a one-seed paragraph into
        # the manuscript.  Statistics and JSON are still written for inspection.
        print(f"only {summary['n_seeds']} seed(s) available; manuscript left untouched")
        return
    insert_into_manuscript("English_SCI_Manuscript_v4.md", paragraph_en(summary),
                           "**A fourth dataset from a different domain.**")
    insert_into_manuscript("中文SCI论文_v4_重构版.md", paragraph_zh(summary),
                           "**不同领域的第四个数据集。**")


if __name__ == "__main__":
    main()
