"""Build probability confidence intervals, Macro-F1 paired intervals and feature frequencies."""
from pathlib import Path
import argparse
import sys
import numpy as np
import pandas as pd
from sklearn.feature_selection import chi2
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import MinMaxScaler
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.publication_additional import bootstrap_probability_metrics, paired_bootstrap_delta

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--data-dir',type=Path,required=True); ap.add_argument('--additional-dir',type=Path,required=True); ap.add_argument('--main-dir',type=Path,required=True); ap.add_argument('--output-dir',type=Path,required=True); args=ap.parse_args(); args.output_dir.mkdir(parents=True,exist_ok=True)
    rows=[]
    for path in sorted(args.additional_dir.glob('predictions_*_seed*.csv')):
        parts=path.stem.split('_seed'); method=parts[0].replace('predictions_',''); seed=int(parts[1]); p=pd.read_csv(path); prob_cols=[c for c in p.columns if c.startswith('proba_')]; classes=np.array([c[6:] for c in prob_cols]); out=bootstrap_probability_metrics(p.y_true.to_numpy(),p[prob_cols].to_numpy(),classes,n_bootstrap=3000,seed=seed)
        for metric,(low,point,high) in out.items(): rows.append({'method':method,'seed':seed,'metric':metric,'low':low,'point':point,'high':high,'n_bootstrap':3000,'confidence':.95})
    pd.DataFrame(rows).to_csv(args.output_dir/'probability_metric_bootstrap_ci.csv',index=False,encoding='utf-8-sig')
    pair_rows=[]
    for seed in [42,2024,3407]:
        base=pd.read_csv(args.main_dir/f'predictions_random_forest_chi2_seed{seed}.csv')
        for other in ['random_forest_all','weighted_rf_chi2','extra_trees_chi2']:
            cand=pd.read_csv(args.main_dir/f'predictions_{other}_seed{seed}.csv'); r=paired_bootstrap_delta(base.y_true,cand.y_pred,base.y_pred,n_bootstrap=3000,seed=seed)
            pair_rows.append({'seed':seed,'comparison':f'{other}_minus_random_forest_chi2_macro_f1','low':r['low'],'point':r['point'],'high':r['high'],'n_bootstrap':3000,'confidence':.95})
    pd.DataFrame(pair_rows).to_csv(args.output_dir/'paired_macro_f1_bootstrap_ci.csv',index=False,encoding='utf-8-sig')
    tr=pd.read_csv(args.data_dir/'train.csv',low_memory=False); names=[c for c in tr.columns if c!='target']; X=MinMaxScaler().fit_transform(tr[names]); y=tr.target.to_numpy(); rec=[]; skf=StratifiedKFold(n_splits=5,shuffle=True,random_state=42)
    for fold,(fit,_) in enumerate(skf.split(X,y)):
        scores,_=chi2(X[fit],y[fit]); idx=np.argsort(-np.nan_to_num(scores,nan=0,posinf=np.finfo(float).max),kind='stable')[:60]
        for rank,i in enumerate(idx,1): rec.append({'fold':fold,'k':60,'feature':names[i],'rank':rank,'chi2_score':float(scores[i])})
    rec=pd.DataFrame(rec); rec.to_csv(args.output_dir/'feature_selection_frequency_records.csv',index=False,encoding='utf-8-sig'); freq=rec.groupby('feature',as_index=False).agg(selection_count=('feature','size'),mean_rank=('rank','mean'),mean_chi2_score=('chi2_score','mean')).sort_values(['selection_count','mean_rank'],ascending=[False,True]); freq['selection_rate']=freq.selection_count/5; freq.to_csv(args.output_dir/'feature_selection_frequency.csv',index=False,encoding='utf-8-sig')
    # Natural-distribution CIC class-level predicted counts.
    imb = Path(args.main_dir).parent / 'results_imbalanced_v3'
    pred_path = imb / 'predictions_random_forest_chi2_seed42.csv'
    if pred_path.exists():
        pred = pd.read_csv(pred_path); labels = sorted(set(pred.y_true) | set(pred.y_pred)); cm = pd.crosstab(pred.y_true, pred.y_pred).reindex(index=labels, columns=labels, fill_value=0)
        counts = pd.DataFrame({'true_class': labels, 'test_support': [int((pred.y_true == c).sum()) for c in labels], 'predicted_total': [int((pred.y_pred == c).sum()) for c in labels], 'predicted_as_normal': [int(cm.loc[c].get('Normal', 0)) for c in labels]})
        counts['predicted_as_normal_rate'] = counts['predicted_as_normal'] / counts['test_support'].replace(0, np.nan)
        counts.to_csv(args.output_dir/'imbalanced_predicted_class_counts.csv', index=False, encoding='utf-8-sig')
    print(freq.head(20).to_string(index=False))
if __name__=='__main__': main()
