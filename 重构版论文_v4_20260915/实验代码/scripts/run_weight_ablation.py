from pathlib import Path
import sys
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.experiment_components import WeightedRandomForest, compute_metrics, select_chi2_features

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = Path(r"E:\论文\data\processed_dedup")
OUT = ROOT / "results_weight_ablation"

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tr = pd.read_csv(PROCESSED / "train.csv", low_memory=False)
    va = pd.read_csv(PROCESSED / "validation.csv", low_memory=False)
    te = pd.read_csv(PROCESSED / "test.csv", low_memory=False)
    names = [c for c in tr.columns if c != "target"]
    scaler = MinMaxScaler()
    Xtr = scaler.fit_transform(tr[names].apply(pd.to_numeric, errors="raise")); Xv = scaler.transform(va[names].apply(pd.to_numeric, errors="raise")); Xte = scaler.transform(te[names].apply(pd.to_numeric, errors="raise"))
    ytr, yv, yte = tr.target.to_numpy(), va.target.to_numpy(), te.target.to_numpy()
    selected, ranking = select_chi2_features(pd.DataFrame(Xtr, columns=names), ytr, k=60)
    idx = [names.index(x) for x in selected]
    rows=[]
    for metric in ["balanced_accuracy", "accuracy", "macro_f1"]:
        for seed in [42,2024,3407]:
            model=WeightedRandomForest(n_estimators=200,random_state=seed,weight_metric=metric)
            model.fit(Xtr[:,idx], ytr, Xv[:,idx], yv); pred=model.predict(Xte[:,idx]); m=compute_metrics(yte,pred)
            rows.append({"weight_metric":metric,"seed":seed,**m})
            pd.DataFrame({"tree_score":model.tree_scores_,"tree_weight":model.tree_weights_}).to_csv(OUT/f"tree_weights_{metric}_seed{seed}.csv",index=False,encoding="utf-8-sig")
            pd.DataFrame({"y_true":yte,"y_pred":pred}).to_csv(OUT/f"predictions_{metric}_seed{seed}.csv",index=False,encoding="utf-8-sig")
    result=pd.DataFrame(rows); result.to_csv(OUT/"weight_strategy_metrics.csv",index=False,encoding="utf-8-sig"); result.groupby("weight_metric",as_index=False)[["accuracy","macro_precision","macro_recall","macro_f1"]].mean().to_csv(OUT/"weight_strategy_summary.csv",index=False,encoding="utf-8-sig"); print(result.to_string(index=False))
if __name__ == "__main__": main()
