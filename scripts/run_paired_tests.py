from pathlib import Path
import sys
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.paired_tests import mcnemar_exact
from src.statistical_analysis import paired_permutation_accuracy

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "results_journal_full"
OUT = ROOT / "results_paper_materials" / "tables"

def load(name, seed):
    return pd.read_csv(EXP / f"predictions_{name}_seed{seed}.csv")

def main():
    rows=[]
    for seed in [42,2024,3407]:
        a=load("random_forest_all",seed); b=load("random_forest_chi2",seed); c=load("weighted_rf_chi2",seed)
        for name,x,y in [("rf_chi2_vs_rf_all",a,b),("weighted_rf_chi2_vs_rf_all",a,c),("extra_trees_chi2_vs_rf_all",a,load("extra_trees_chi2",seed))]:
            mc=mcnemar_exact(a.y_true,x.y_pred,y.y_pred)
            delta,p=paired_permutation_accuracy(a.y_true,x.y_pred,y.y_pred,n_permutations=20000,seed=seed)
            rows.append({"seed":seed,"comparison":name,**mc,"accuracy_delta_b_minus_a":delta,"permutation_p_value":p})
    pd.DataFrame(rows).to_csv(OUT/"table_paired_significance_tests.csv",index=False,encoding="utf-8-sig")
    print(pd.DataFrame(rows).to_string(index=False))
if __name__ == "__main__": main()
