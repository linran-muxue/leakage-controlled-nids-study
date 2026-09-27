"""Fair official-split NSL-KDD benchmark (weighted RF excluded from main table)."""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.feature_selection import chi2
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import MinMaxScaler
from sklearn.tree import DecisionTreeClassifier
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.experiment_components import compute_metrics

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--processed-dir',type=Path,required=True); ap.add_argument('--output-dir',type=Path,required=True); ap.add_argument('--chi2-k',type=int,default=60); ap.add_argument('--n-estimators',type=int,default=100); ap.add_argument('--min-samples-leaf',type=int,default=2); ap.add_argument('--seed',type=int,default=42); a=ap.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True)
    tr=pd.read_csv(a.processed_dir/'train.csv',low_memory=False); te=pd.read_csv(a.processed_dir/'test.csv',low_memory=False); names=[c for c in tr.columns if c!='target']; Xr=tr[names].apply(pd.to_numeric,errors='raise').to_numpy(float); Xtr=te[names].apply(pd.to_numeric,errors='raise').to_numpy(float); y=tr.target.to_numpy(); yt=te.target.to_numpy(); sc=MinMaxScaler(); X=sc.fit_transform(Xr); Xt=sc.transform(Xtr)
    scores,pvals=chi2(X,y); scores=np.nan_to_num(scores,nan=0.0,posinf=np.finfo(float).max,neginf=0.0); pvals=np.nan_to_num(pvals,nan=1.0,posinf=1.0,neginf=0.0); idx=np.argsort(-scores,kind='stable')[:min(a.chi2_k,X.shape[1])]; fs=pd.DataFrame({'feature':names,'chi2':scores,'p_value':pvals}).sort_values(['chi2','feature'],ascending=[False,True],kind='mergesort'); fs['rank']=np.arange(1,len(fs)+1); fs.to_csv(a.output_dir/'feature_scores_training_only.csv',index=False,encoding='utf-8-sig'); selected=[names[i] for i in idx]
    (a.output_dir/'final_config.json').write_text(json.dumps({'dataset':'NSL-KDD','train_file':'KDDTrain+','test_file':'KDDTest+','comparison_protocol':'all_models_fit_on_complete_official_training_split','chi2_k':len(idx),'n_estimators':a.n_estimators,'min_samples_leaf':a.min_samples_leaf,'decision_tree_max_depth':10,'seed':a.seed,'feature_count_all':len(names),'feature_count_chi2':len(idx),'selected_features':selected,'weighted_rf_in_main_comparison':False},ensure_ascii=False,indent=2),encoding='utf-8')
    labels=sorted(np.unique(np.concatenate([y,yt]))); models={'rf_all':(RandomForestClassifier(n_estimators=a.n_estimators,min_samples_leaf=a.min_samples_leaf,n_jobs=-1,class_weight='balanced_subsample',random_state=a.seed),np.arange(X.shape[1])),'rf_chi2':(RandomForestClassifier(n_estimators=a.n_estimators,min_samples_leaf=a.min_samples_leaf,n_jobs=-1,class_weight='balanced_subsample',random_state=a.seed),idx),'extra_trees_chi2':(ExtraTreesClassifier(n_estimators=a.n_estimators,min_samples_leaf=a.min_samples_leaf,n_jobs=-1,class_weight='balanced',random_state=a.seed),idx),'decision_tree_chi2':(DecisionTreeClassifier(max_depth=10,min_samples_leaf=a.min_samples_leaf,class_weight='balanced',random_state=a.seed),idx)}; rows=[]
    for name,(model,cols) in models.items():
        t=time.perf_counter(); model.fit(X[:,cols],y); train_s=time.perf_counter()-t; t=time.perf_counter(); pred=model.predict(Xt[:,cols]); pred_s=time.perf_counter()-t
        report = pd.DataFrame(classification_report(yt,pred,labels=labels,output_dict=True,zero_division=0)).T
        cm = pd.DataFrame(confusion_matrix(yt,pred,labels=labels),index=labels,columns=labels)
        metrics = compute_metrics(yt,pred)
        rows.append({'model':name,**metrics,'train_seconds':train_s,'predict_seconds':pred_s,'feature_count':len(cols),'n_estimators':a.n_estimators if name!='decision_tree_chi2' else None,'min_samples_leaf':a.min_samples_leaf,'test_samples':len(yt)})
        pd.DataFrame({'y_true':yt,'y_pred':pred}).to_csv(a.output_dir/f'predictions_{name}.csv',index=False,encoding='utf-8-sig')
        report.to_csv(a.output_dir/f'classification_report_{name}.csv',encoding='utf-8-sig')
        cm.to_csv(a.output_dir/f'confusion_matrix_{name}.csv',encoding='utf-8-sig')
        minority = report.reindex(['R2L','U2R']).copy()
        minority.insert(0, 'model', name)
        minority.insert(1, 'test_support_total', [int((yt == c).sum()) for c in minority.index])
        minority['predicted_as_normal_rate'] = [float(((yt == c) & (pred == 'Normal')).sum() / max(1, (yt == c).sum())) for c in minority.index]
        minority.reset_index(names='class').to_csv(a.output_dir/f'minority_analysis_{name}.csv',index=False,encoding='utf-8-sig')
    result=pd.DataFrame(rows); result.to_csv(a.output_dir/'metrics.csv',index=False,encoding='utf-8-sig')
    class_counts = pd.DataFrame({'split':['train']*len(labels)+['test']*len(labels), 'class':labels*2, 'count':[int((y==c).sum()) for c in labels]+[int((yt==c).sum()) for c in labels]})
    class_counts.to_csv(a.output_dir/'class_counts.csv',index=False,encoding='utf-8-sig')
    minority_all=[]
    for name in models:
        p=pd.read_csv(a.output_dir/f'minority_analysis_{name}.csv'); minority_all.append(p)
    pd.concat(minority_all,ignore_index=True).to_csv(a.output_dir/'minority_analysis_summary.csv',index=False,encoding='utf-8-sig')
    (a.output_dir/'README.md').write_text('公平版 NSL-KDD 外部基准：所有主比较模型均使用完整 KDDTrain+ 训练、官方 KDDTest+ 测试、相同预处理和固定模型配置。加权随机森林因需要额外验证集，不纳入主比较。报告Accuracy、Balanced Accuracy、宏平均指标，并单独分析R2L/U2R少数类及其误判为Normal的比例。NSL-KDD的Normal、DoS、Probe、R2L、U2R标签体系与CIC-IDS2017不同，仅作为独立公开基准。\n',encoding='utf-8'); print(result.to_string(index=False))
if __name__=='__main__': main()
