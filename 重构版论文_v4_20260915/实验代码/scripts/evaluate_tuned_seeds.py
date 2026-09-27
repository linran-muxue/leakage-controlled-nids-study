from pathlib import Path
import json, time, sys
import numpy as np, pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_selection import chi2
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.metrics import accuracy_score, f1_score

ROOT=Path(__file__).resolve().parents[1]
def idx_for(X,y,k):
    s,_=chi2(X,y); return np.argsort(-np.nan_to_num(s,nan=0.0))[:k]
def main():
    ap=__import__('argparse').ArgumentParser(); ap.add_argument('--processed-dir',type=Path,required=True); ap.add_argument('--config-file',type=Path,required=True); ap.add_argument('--output-dir',type=Path,required=True); a=ap.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True)
    tr=pd.read_csv(a.processed_dir/'train.csv'); te=pd.read_csv(a.processed_dir/'test.csv'); names=[c for c in tr.columns if c!='target']; sc=MinMaxScaler(); X=sc.fit_transform(tr[names].apply(pd.to_numeric,errors='raise')); Xt=sc.transform(te[names].apply(pd.to_numeric,errors='raise')); y=tr.target.to_numpy(); yt=te.target.to_numpy(); cfg=pd.read_csv(a.config_file) if a.config_file.suffix=='.csv' else None
    cv=pd.read_csv(a.output_dir.parent/'results_tuned_all'/'cv_results.csv') if cfg is None else cfg
    rows=[]
    for family in ['decision_tree','svm','random_forest','extra_trees']:
        sub=cv[cv.model==family].sort_values(['cv_macro_f1','cv_accuracy','complexity'],ascending=[False,False,True]).iloc[0].to_dict()
        for seed in [42,2024,3407]:
            k=int(sub['k']); idx=np.arange(X.shape[1]) if sub['feature_mode']=='all' else idx_for(X,y,k); kw={x:sub[x] for x in ['max_depth','C','n_estimators'] if x in sub and not pd.isna(sub[x])}
            if family=='decision_tree': m=DecisionTreeClassifier(max_depth=None if 'max_depth' not in kw else int(kw['max_depth']),class_weight='balanced',random_state=seed)
            elif family=='svm': m=SVC(C=float(kw['C']),kernel='rbf',gamma='scale',class_weight='balanced')
            elif family=='random_forest': m=RandomForestClassifier(n_estimators=int(kw['n_estimators']),n_jobs=-1,class_weight='balanced_subsample',random_state=seed)
            else: m=ExtraTreesClassifier(n_estimators=int(kw['n_estimators']),n_jobs=-1,class_weight='balanced',random_state=seed)
            s=time.perf_counter(); m.fit(X[:,idx],y); ts=time.perf_counter()-s; s=time.perf_counter(); p=m.predict(Xt[:,idx]); ps=time.perf_counter()-s; rows.append({'model':'tuned_'+family,'seed':seed,'accuracy':accuracy_score(yt,p),'macro_f1':f1_score(yt,p,average='macro',zero_division=0),'train_seconds':ts,'predict_seconds':ps,'feature_mode':sub['feature_mode'],'k':k,**kw}); pd.DataFrame({'y_true':yt,'y_pred':p}).to_csv(a.output_dir/f'predictions_tuned_{family}_seed{seed}.csv',index=False,encoding='utf-8-sig')
    result=pd.DataFrame(rows); result.to_csv(a.output_dir/'test_metrics_3seeds.csv',index=False,encoding='utf-8-sig'); result.groupby('model',as_index=False)[['accuracy','macro_f1','train_seconds','predict_seconds']].agg(['mean','std']).reset_index().to_csv(a.output_dir/'test_metrics_aggregate.csv',index=False,encoding='utf-8-sig'); print(result.to_string(index=False))
if __name__=='__main__': main()
