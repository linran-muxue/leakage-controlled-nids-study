from pathlib import Path
import argparse, json, time
import numpy as np, pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_selection import chi2
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.metrics import accuracy_score, f1_score

ROOT=Path(__file__).resolve().parents[1]
def select_idx(X,y,k):
    scores,_=chi2(np.asarray(X,dtype=float),np.asarray(y)); return np.argsort(-np.nan_to_num(scores,nan=0.0,posinf=np.finfo(float).max))[:k]

def build_model(model_name, params, seed):
    if model_name=='decision_tree': return DecisionTreeClassifier(max_depth=params.get('max_depth'),class_weight='balanced',random_state=seed)
    if model_name=='svm': return SVC(C=params['C'],kernel='rbf',gamma='scale',class_weight='balanced')
    if model_name=='random_forest': return RandomForestClassifier(n_estimators=params['n_estimators'],min_samples_leaf=params.get('min_samples_leaf',1),n_jobs=-1,class_weight='balanced_subsample',random_state=seed)
    if model_name=='extra_trees': return ExtraTreesClassifier(n_estimators=params['n_estimators'],min_samples_leaf=params.get('min_samples_leaf',1),n_jobs=-1,class_weight='balanced',random_state=seed)
    raise ValueError(f'unknown model family: {model_name}')

def json_safe_config(row):
    result = {}
    for key, value in row.items():
        if pd.isna(value):
            result[key] = None
        elif isinstance(value, (np.integer,)):
            result[key] = int(value)
        elif isinstance(value, (np.floating,)):
            result[key] = float(value)
        else:
            result[key] = value
    return result

def evaluate_config_cv(X,y,model_name,mode,k,params,seed=42):
    skf=StratifiedKFold(n_splits=5,shuffle=True,random_state=seed); f1s=[]; accs=[]
    for ti,vi in skf.split(X,y):
        scaler=MinMaxScaler(); Xfit=scaler.fit_transform(X[ti]); Xvalid=scaler.transform(X[vi])
        idx=np.arange(X.shape[1]) if mode=='all' else select_idx(Xfit,y[ti],k)
        m=build_model(model_name,params,seed); m.fit(Xfit[:,idx],y[ti]); p=m.predict(Xvalid[:,idx])
        f1s.append(f1_score(y[vi],p,average='macro',zero_division=0)); accs.append(accuracy_score(y[vi],p))
    return float(np.mean(f1s)),float(np.mean(accs))
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--processed-dir',type=Path,required=True); ap.add_argument('--output-dir',type=Path,required=True); ap.add_argument('--seed',type=int,default=42); a=ap.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True)
    tr=pd.read_csv(a.processed_dir/'train.csv'); te=pd.read_csv(a.processed_dir/'test.csv'); names=[c for c in tr.columns if c!='target']; X=tr[names].apply(pd.to_numeric,errors='raise').to_numpy(dtype=float); Xt=te[names].apply(pd.to_numeric,errors='raise').to_numpy(dtype=float); y=tr.target.to_numpy(); yt=te.target.to_numpy(); rows=[]
    configs=[]
    for mode in ['all','chi2']:
      for k in ([len(names)] if mode=='all' else [20,40,60]):
       configs += [('decision_tree',mode,k,{'max_depth':d}) for d in [None,10,20,30]]
       configs += [('svm',mode,k,{'C':c}) for c in [1,10,100]]
       configs += [('random_forest',mode,k,{'n_estimators':n,'min_samples_leaf':leaf}) for n in [100,200,300] for leaf in [1,2,4]]
       configs += [('extra_trees',mode,k,{'n_estimators':n,'min_samples_leaf':leaf}) for n in [100,200,300] for leaf in [1,2,4]]
    for model_name,mode,k,params in configs:
        cv_f1,cv_acc=evaluate_config_cv(X,y,model_name,mode,k,params,a.seed)
        rows.append({'model':model_name,'feature_mode':mode,'k':k,**params,'cv_macro_f1':cv_f1,'cv_accuracy':cv_acc,'complexity':sum(v for v in params.values() if isinstance(v,int))})
    table=pd.DataFrame(rows); table.to_csv(a.output_dir/'cv_results.csv',index=False,encoding='utf-8-sig'); selected={}
    for family in ['decision_tree','svm','random_forest','extra_trees']:
        selected[family]=json_safe_config(table[table.model==family].sort_values(['cv_macro_f1','cv_accuracy','complexity'],ascending=[False,False,True]).iloc[0].to_dict())
    (a.output_dir/'selected_configs_by_model.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8-sig')
    # Evaluate one best configuration per model family on untouched test set.
    finals=[]
    scaler=MinMaxScaler(); Xs=scaler.fit_transform(X); Xts=scaler.transform(Xt)
    for family in ['decision_tree','svm','random_forest','extra_trees']:
        sub=selected[family]; mode=sub['feature_mode']; k=int(sub['k']); idx=np.arange(X.shape[1]) if mode=='all' else select_idx(Xs,y,k); params={key:(int(sub[key]) if key in ['max_depth','n_estimators','min_samples_leaf'] else float(sub[key])) for key in ['max_depth','C','n_estimators','min_samples_leaf'] if key in sub and not pd.isna(sub[key])}; m=build_model(family,params,a.seed)
        s=time.perf_counter(); m.fit(Xs[:,idx],y); train_s=time.perf_counter()-s; s=time.perf_counter(); p=m.predict(Xts[:,idx]); pred_s=time.perf_counter()-s; finals.append({'model':'tuned_'+family,'accuracy':accuracy_score(yt,p),'macro_f1':f1_score(yt,p,average='macro',zero_division=0),'train_seconds':train_s,'predict_seconds':pred_s,'feature_mode':mode,'k':k,**params}); pd.DataFrame({'y_true':yt,'y_pred':p}).to_csv(a.output_dir/f'predictions_tuned_{family}.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(finals).to_csv(a.output_dir/'test_metrics.csv',index=False,encoding='utf-8-sig'); print(pd.DataFrame(finals).to_string(index=False))
if __name__=='__main__': main()
