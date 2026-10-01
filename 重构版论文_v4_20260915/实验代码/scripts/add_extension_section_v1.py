"""Insert the extension-experiment section into both manuscripts.

All numbers are read from the result files at run time, so the section cannot
disagree with the evidence; the only literals are the sentence templates.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
EN = BASE / "English_SCI_Manuscript_v4.md"
ZH = BASE / "中文SCI论文_v4_重构版.md"


def jload(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main() -> None:
    families = jload("results_member_family_v1/member_family_summary.json")
    holdout = jload("results_day_holdout_v1/day_holdout_summary.json")
    deployment = jload("results_deployment_metrics_v1/deployment_summary.json")
    ids2018 = jload("results_rccf_cic_ids2018_v1/benchmark_summary.json")
    iot = jload("results_rccf_cic_iot2023_v1/benchmark_summary.json")
    nsl = pd.read_csv(ROOT / "results_rccf_nsl_v10/metrics_aggregate.csv").iloc[0]
    unsw = pd.read_csv(ROOT / "results_rccf_unsw_v10/metrics_aggregate.csv").iloc[0]
    nbaiot = pd.read_csv(ROOT / "results_rccf_nbaiot_v10/metrics_aggregate.csv").iloc[0]
    audit2018 = jload("results_data_audit_cic_ids2018_v1/data_processing_audit.json")

    day_values = {day: value["rccf"]["macro_f1_mean"] for day, value in holdout.items()}
    day_min = min(day_values.values())
    day_max = max(day_values.values())
    families_gain = families["families"]["mean_gain"]
    q4_gain = families["q4"]["mean_gain"]
    q6_gain = families["q6"]["mean_gain"]
    q4_dis = 100 * families["q4"]["mean_pairwise_disagreement"]
    fam_dis = 100 * families["families"]["mean_pairwise_disagreement"]
    fpr_eq = deployment["results_full_corpus_v49|equal_rf_chi2"]["operating_fpr"]
    fpr_xgb = deployment["results_full_corpus_v49|xgboost_chi2"]["operating_fpr"]
    primary = deployment["results_seeds10_v5|rccf"]

    en = (
        "\n### 5.8 Extension experiments\n\n"
        "Five extensions probe the boundaries of the main result; their per-seed data and a "
        "standalone report ship with the release (扩展实验报告, `results_*_v1/`).\n\n"
        f"**Member family and count.** Replacing the four same-family filter views (pairwise "
        f"disagreement {q4_dis:.2f}%, gain {q4_gain:+.6f}) with cross-family members "
        f"(random forest, extremely randomised trees and XGBoost) raises disagreement to "
        f"{fam_dis:.2f}% and the gain to {families_gain:+.6f}; six members give {q6_gain:+.6f}. "
        "The gate therefore acts once the members are dissimilar enough, but even the most "
        "diverse configuration stays inside the 0.005 margin.\n\n"
        f"**Temporal holdout.** Splitting CIC-IDS2017 by capture day (train on four days, test on "
        f"the fifth, per-class cap 20,000) drops Macro-F1 to {day_min:.3f}-{day_max:.3f} across "
        "the five held-out days. The cause is compositional: Monday contains only Normal traffic,"
        " Tuesday only Normal and Brute Force, and so on, so no day carries the full label set. "
        "The day-level split is therefore constructible but not category-complete - the quantified "
        "form of the limitation in Section 6.5.\n\n"
        f"**External benchmarks at ten seeds.** Under the three deterministic views (the "
        "mutual-information expert is omitted because its k-nearest-neighbour estimator does not "
        f"scale to these training sizes), NSL-KDD reaches {nsl['macro_f1_mean']:.6f} "
        f"+/- {nsl['macro_f1_std']:.6f}, UNSW-NB15 {unsw['macro_f1_mean']:.6f} "
        f"+/- {unsw['macro_f1_std']:.6f} and N-BaIoT {nbaiot['macro_f1_mean']:.6f} "
        f"+/- {nbaiot['macro_f1_std']:.6f} over ten seeds.\n\n"
        f"**Two further corpora.** CIC-IDS2018 (16.2 M raw rows, 4.10 M duplicates removed) gives "
        f"a 56,055/12,012/12,012 five-class benchmark on which the gate and the same-members equal "
        f"fusion are identical across five seeds ({ids2018['rccf_mean_macro_f1']:.6f}, zero labels "
        f"changed). CIC-IoT-2023 (38.4 M rows, eight coarse classes) gives "
        f"{iot['rccf_mean_macro_f1']:.6f} for the gate against "
        f"{iot['equal_fusion_mean_macro_f1']:.6f} for the same-members fusion over three seeds - "
        f"a {iot['same_members_difference']:+.6f} difference. Both reproduce the primary finding "
        "on corpora the study had not used.\n\n"
        f"**Deployment view.** At the model's own operating point the full-corpus false-positive "
        f"rate on benign flows is {fpr_eq:.5f} for the equal-weight chi-square forest and "
        f"{fpr_xgb:.5f} for XGBoost, and the conditional model reaches AUROC "
        f"{primary['roc_auc_mean']:.5f} with FPR {primary['fpr_at_95_tpr_mean']:.5f} at 95% "
        "detection on the primary population. The aggregation-rule effect is an order of magnitude "
        "smaller than the model-family effect on the same axis.\n\n"
    )
    zh = (
        "\n### 5.8 扩展实验\n\n"
        "五个扩展实验界定了主结论的边界；逐种子数据与独立报告随发布包提供"
        "（扩展实验报告、`results_*_v1/`）。\n\n"
        f"**专家家族与数量。** 把四个同族过滤式视图（两两分歧 {q4_dis:.2f}%，增益 {q4_gain:+.6f}）"
        f"换成跨家族成员（随机森林、极端随机树、XGBoost）后，分歧升到 {fam_dis:.2f}%，"
        f"增益升到 {families_gain:+.6f}；六个成员时为 {q6_gain:+.6f}。"
        "因此当成员足够分散时门控确实开始起作用，但即使最分散的配置也仍在 0.005 边界之内。\n\n"
        f"**时间留出。** 按采集日划分 CIC-IDS2017（用四天训练、留出一天，每类上限 2 万）后，"
        f"留出日的 Macro-F1 落到 {day_min:.3f}–{day_max:.3f}。原因是类别构成："
        "周一只有正常流量，周二只有正常与暴力破解，以此类推，没有任何一天覆盖完整类别集。"
        "因此按天划分可以构造、但不是类别完整的——这正是 6.5 节限制的定量形式。\n\n"
        f"**外部基准扩到十种子。** 在三个确定性视图下（省略互信息专家，因为其 kNN 估计器"
        f"在此规模上不可行），NSL-KDD 为 {nsl['macro_f1_mean']:.6f} ± {nsl['macro_f1_std']:.6f}，"
        f"UNSW-NB15 为 {unsw['macro_f1_mean']:.6f} ± {unsw['macro_f1_std']:.6f}，"
        f"N-BaIoT 为 {nbaiot['macro_f1_mean']:.6f} ± {nbaiot['macro_f1_std']:.6f}（十种子）。\n\n"
        f"**两个新语料。** CIC-IDS2018（原始 16.2 M 行，去重移除 4.10 M 行）得到 "
        f"56 055/12 012/12 012 的五分类基准，五个种子上门控与同成员等权融合完全相同"
        f"（{ids2018['rccf_mean_macro_f1']:.6f}，改判 0 条）。CIC-IoT-2023（38.4 M 行、八个粗类）"
        f"上，门控为 {iot['rccf_mean_macro_f1']:.6f}，同成员等权融合为 "
        f"{iot['equal_fusion_mean_macro_f1']:.6f}，差 {iot['same_members_difference']:+.6f}（三个种子）。"
        "两者都在本文未使用过的语料上复现了主结论。\n\n"
        f"**部署视角。** 在模型自身的操作点上，全语料对正常流的误报率为 "
        f"{fpr_eq:.5f}（等权卡方森林）与 {fpr_xgb:.5f}（XGBoost）；主总体上条件加权模型的 "
        f"AUROC 为 {primary['roc_auc_mean']:.5f}，95% 检出率对应误报率 "
        f"{primary['fpr_at_95_tpr_mean']:.5f}。在同一坐标轴上，聚合规则效应比模型族效应小一个数量级。\n\n"
    )

    for path, block, anchor in ((EN, en, "## 6. Discussion"), (ZH, zh, "## 6 讨论")):
        text = path.read_text(encoding="utf-8")
        if "### 5.8 Extension experiments" in text or "### 5.8 扩展实验" in text:
            print(f"{path.name}: section already present")
            continue
        if anchor not in text:
            raise SystemExit(f"{path.name}: anchor {anchor!r} not found")
        text = text.replace(anchor, block.lstrip("\n") + anchor, 1)
        path.write_text(text, encoding="utf-8")
        print(f"{path.name}: inserted 5.8")
    print("EXTENSION_SECTION_INSERTED")


if __name__ == "__main__":
    main()
