"""Rebuild canonical CFRG figures from versioned result artifacts."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "results_publication_final" / "figures"

def main():
    cic = pd.read_csv(ROOT / "results_cfrg_cic_v2_verified" / "metrics_aggregate_flat.csv")
    strong = pd.read_csv(ROOT / "results_cfrg_strong_baselines_v2_verified" / "summary.csv", header=[0, 1])
    strong.columns = ["_".join(str(x) for x in c if str(x) != "nan").strip("_") for c in strong.columns]
    # Normalize model names and combine the locked CIC and strong-baseline artifacts.
    rows = []
    for _, r in cic.iterrows():
        rows.append({"model": r["model"], "Accuracy": 100*r["accuracy_mean"], "Macro-F1": 100*r["macro_f1_mean"]})
    if "macro_f1_mean" in strong.columns:
        for _, r in strong.iterrows():
            if str(r.get("model", "")).lower() == "xgboost":
                rows.append({"model": "xgboost", "Accuracy": 100*float(r["accuracy_mean"]), "Macro-F1": 100*float(r["macro_f1_mean"])})
    frame = pd.DataFrame(rows).drop_duplicates("model")
    # Strong-baseline artifact uses simplified names; map them to the locked
    # labels while avoiding duplicate CFRG/RF entries.
    for m, canonical in [("equal_rf", "equal_rf_chi2"), ("cfrg_forest", "cfrg_forest_chi2"), ("extra_trees", "extra_trees_chi2")]:
        if m in frame["model"].values:
            frame.loc[frame["model"] == m, "model"] = canonical
    order = ["equal_rf_all", "equal_rf_chi2", "cfrg_forest_chi2", "extra_trees_chi2", "xgboost"]
    frame["order"] = frame["model"].map({m:i for i,m in enumerate(order)})
    frame = frame.sort_values("order").dropna(subset=["order"])
    labels = {"equal_rf_all":"Equal RF (all)", "equal_rf_chi2":"Equal RF (χ²-60)", "cfrg_forest_chi2":"CFRG-Forest (χ²-60)", "extra_trees_chi2":"ExtraTrees (χ²-60)", "xgboost":"XGBoost (χ²-60)"}
    x = range(len(frame)); width = 0.36
    fig, ax = plt.subplots(figsize=(10, 5.6), dpi=180)
    ax.bar([i-width/2 for i in x], frame["Accuracy"], width, label="Accuracy")
    ax.bar([i+width/2 for i in x], frame["Macro-F1"], width, label="Macro-F1")
    ax.set_xticks(list(x), [labels[m] for m in frame["model"]], rotation=18, ha="right")
    ax.set_ylabel("Score (%)")
    ax.set_ylim(90, 97)
    ax.set_title("Locked CIC-IDS2017 comparison on the balanced research subset")
    ax.grid(axis="y", alpha=.3); ax.legend(frameon=True)
    fig.tight_layout(); FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / "fig_v2_model_performance.png", bbox_inches="tight"); plt.close(fig)
    print(f"FIGURE_WRITTEN={FIG / 'fig_v2_model_performance.png'}")

if __name__ == "__main__":
    main()
