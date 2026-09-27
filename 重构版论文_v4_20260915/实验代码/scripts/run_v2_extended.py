from pathlib import Path
import argparse
import json
import sys
import time
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.feature_selection import chi2
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import MinMaxScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.experiment_components import WeightedRandomForest, compute_metrics
from src.statistical_analysis import bootstrap_metric_ci, paired_permutation_accuracy
from src.paired_tests import mcnemar_exact

def select_idx(X, y, k):
    scores, _ = chi2(np.asarray(X, dtype=float), np.asarray(y))
    return np.argsort(-np.nan_to_num(scores, nan=0.0, posinf=np.finfo(float).max))[:k]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--processed-dir', type=Path, required=True)
    ap.add_argument('--output-dir', type=Path, required=True)
    ap.add_argument('--seeds', type=int, nargs='+', default=[42, 2024, 3407])
    args = ap.parse_args(); args.output_dir.mkdir(parents=True, exist_ok=True)
    tr = pd.read_csv(args.processed_dir/'train.csv', low_memory=False)
    va = pd.read_csv(args.processed_dir/'validation.csv', low_memory=False)
    te = pd.read_csv(args.processed_dir/'test.csv', low_memory=False)
    names = [c for c in tr.columns if c != 'target']
    scaler = MinMaxScaler()
    X = scaler.fit_transform(tr[names].apply(pd.to_numeric, errors='raise'))
    Xv = scaler.transform(va[names].apply(pd.to_numeric, errors='raise'))
    Xt = scaler.transform(te[names].apply(pd.to_numeric, errors='raise'))
    y, yv, yt = tr.target.to_numpy(), va.target.to_numpy(), te.target.to_numpy()
    chi_idx = select_idx(X, y, 60)
    labels = sorted(np.unique(np.concatenate([y, yt])))
    out_pred = args.output_dir/'predictions'; out_pred.mkdir(exist_ok=True)
    rows = []
    configs = {
        'tuned_random_forest': ('rf_all', lambda seed: RandomForestClassifier(n_estimators=300, n_jobs=-1, class_weight='balanced_subsample', random_state=seed), np.arange(X.shape[1])),
        'tuned_decision_tree': ('dt_chi2', lambda seed: __import__('sklearn.tree', fromlist=['DecisionTreeClassifier']).DecisionTreeClassifier(max_depth=10, class_weight='balanced', random_state=seed), chi_idx),
        'tuned_svm': ('svm_all', lambda seed: __import__('sklearn.svm', fromlist=['SVC']).SVC(C=100, kernel='rbf', gamma='scale', class_weight='balanced'), np.arange(X.shape[1])),
        'tuned_extra_trees': ('extra_all', lambda seed: ExtraTreesClassifier(n_estimators=300, n_jobs=-1, class_weight='balanced', random_state=seed), np.arange(X.shape[1])),
    }
    for seed in args.seeds:
        for name, (_, factory, idx) in configs.items():
            model = factory(seed); start=time.perf_counter(); model.fit(X[:,idx], y); train_s=time.perf_counter()-start
            start=time.perf_counter(); pred=model.predict(Xt[:,idx]); pred_s=time.perf_counter()-start
            m=compute_metrics(yt,pred); rows.append({'model':name,'seed':seed,**m,'train_seconds':train_s,'predict_seconds':pred_s,'feature_count':len(idx),'test_samples':len(yt)})
            prefix=f'{name}_seed{seed}'
            pd.DataFrame({'y_true':yt,'y_pred':pred}).to_csv(out_pred/f'{prefix}.csv',index=False,encoding='utf-8-sig')
            pd.DataFrame(classification_report(yt,pred,labels=labels,output_dict=True,zero_division=0)).T.to_csv(args.output_dir/f'classification_report_{prefix}.csv',encoding='utf-8-sig')
            pd.DataFrame(confusion_matrix(yt,pred,labels=labels),index=labels,columns=labels).to_csv(args.output_dir/f'confusion_matrix_{prefix}.csv',encoding='utf-8-sig')
        weighted=WeightedRandomForest(n_estimators=300,random_state=seed,weight_metric='balanced_accuracy')
        start=time.perf_counter(); weighted.fit(X[:,chi_idx],y,Xv[:,chi_idx],yv); train_s=time.perf_counter()-start
        start=time.perf_counter(); pred=weighted.predict(Xt[:,chi_idx]); pred_s=time.perf_counter()-start
        m=compute_metrics(yt,pred); rows.append({'model':'weighted_rf_chi2','seed':seed,**m,'train_seconds':train_s,'predict_seconds':pred_s,'feature_count':len(chi_idx),'test_samples':len(yt)})
        prefix=f'weighted_rf_chi2_seed{seed}'
        pd.DataFrame({'y_true':yt,'y_pred':pred}).to_csv(out_pred/f'{prefix}.csv',index=False,encoding='utf-8-sig')
        pd.DataFrame({'tree_score':weighted.tree_scores_,'tree_weight':weighted.tree_weights_}).to_csv(args.output_dir/f'tree_weights_seed{seed}.csv',index=False,encoding='utf-8-sig')
        pd.DataFrame(classification_report(yt,pred,labels=labels,output_dict=True,zero_division=0)).T.to_csv(args.output_dir/f'classification_report_{prefix}.csv',encoding='utf-8-sig')
        pd.DataFrame(confusion_matrix(yt,pred,labels=labels),index=labels,columns=labels).to_csv(args.output_dir/f'confusion_matrix_{prefix}.csv',encoding='utf-8-sig')
    metrics=pd.DataFrame(rows); metrics.to_csv(args.output_dir/'metrics_3seeds.csv',index=False,encoding='utf-8-sig')
    metrics.groupby('model')[['accuracy','macro_precision','macro_recall','macro_f1','train_seconds','predict_seconds']].agg(['mean','std']).reset_index().to_csv(args.output_dir/'metrics_aggregate.csv',index=False,encoding='utf-8-sig')

    # Bootstrap intervals and paired tests use the actual row-level predictions.
    ci_rows=[]; test_rows=[]
    for model in metrics.model.unique():
        for seed in args.seeds:
            pred=pd.read_csv(out_pred/f'{model}_seed{seed}.csv')
            alo,a,ahi=bootstrap_metric_ci(pred.y_true,pred.y_pred,'accuracy',n_bootstrap=3000,seed=seed)
            flo,f, fhi=bootstrap_metric_ci(pred.y_true,pred.y_pred,'macro_f1',n_bootstrap=3000,seed=seed+100)
            ci_rows.append({'model':model,'seed':seed,'accuracy':a,'accuracy_ci_low':alo,'accuracy_ci_high':ahi,'macro_f1':f,'macro_f1_ci_low':flo,'macro_f1_ci_high':fhi,'test_samples':len(pred)})
    pd.DataFrame(ci_rows).to_csv(args.output_dir/'bootstrap_confidence_intervals.csv',index=False,encoding='utf-8-sig')
    for seed in args.seeds:
        base=pd.read_csv(out_pred/f'tuned_random_forest_seed{seed}.csv')
        for other in ['weighted_rf_chi2','tuned_extra_trees']:
            cand=pd.read_csv(out_pred/f'{other}_seed{seed}.csv')
            mc=mcnemar_exact(base.y_true,base.y_pred,cand.y_pred)
            delta,p=paired_permutation_accuracy(base.y_true,base.y_pred,cand.y_pred,n_permutations=20000,seed=seed)
            test_rows.append({'seed':seed,'comparison':f'{other}_vs_tuned_random_forest',**mc,'accuracy_delta_b_minus_a':delta,'permutation_p_value':p})
    pd.DataFrame(test_rows).to_csv(args.output_dir/'paired_significance_tests.csv',index=False,encoding='utf-8-sig')

    # Weight-strategy ablation on the same v2 split and chi-square-60 features.
    ablation_rows = []
    for metric in ['balanced_accuracy', 'accuracy', 'macro_f1']:
        for seed in args.seeds:
            model = WeightedRandomForest(n_estimators=300, random_state=seed, weight_metric=metric)
            model.fit(X[:, chi_idx], y, Xv[:, chi_idx], yv)
            pred = model.predict(Xt[:, chi_idx])
            ablation_rows.append({'weight_metric': metric, 'seed': seed, **compute_metrics(yt, pred)})
    pd.DataFrame(ablation_rows).to_csv(args.output_dir/'weight_ablation.csv', index=False, encoding='utf-8-sig')
    pd.DataFrame(ablation_rows).groupby('weight_metric')[['accuracy','macro_precision','macro_recall','macro_f1']].agg(['mean','std']).reset_index().to_csv(args.output_dir/'weight_ablation_summary.csv', index=False, encoding='utf-8-sig')

    # Deployment/robustness benchmark on seed 42 models.
    dep_out=args.output_dir/'deployment'; dep_out.mkdir(exist_ok=True)
    deploy_models={
      'rf_all': (RandomForestClassifier(n_estimators=300,n_jobs=-1,class_weight='balanced_subsample',random_state=42), X, Xt),
      'extra_trees_all': (ExtraTreesClassifier(n_estimators=300,n_jobs=-1,class_weight='balanced',random_state=42), X, Xt),
      'weighted_rf_chi2': (WeightedRandomForest(n_estimators=300,random_state=42,weight_metric='balanced_accuracy').fit(X[:,chi_idx],y,Xv[:,chi_idx],yv), X[:,chi_idx], Xt[:,chi_idx]),
    }
    dep_rows=[]; rob_rows=[]; rng=np.random.default_rng(42)
    for name,(model,xtr,xte) in deploy_models.items():
        if name!='weighted_rf_chi2': model.fit(xtr,y)
        joblib.dump(model,dep_out/f'{name}.joblib',compress=3); size=(dep_out/f'{name}.joblib').stat().st_size
        for batch in [1,32,128,512]:
            start=time.perf_counter()
            for i in range(0,len(xte),batch): model.predict(xte[i:i+batch])
            elapsed=time.perf_counter()-start
            dep_rows.append({'model':name,'batch_size':batch,'total_seconds':elapsed,'latency_ms_per_sample':elapsed/len(xte)*1000,'samples_per_second':len(xte)/elapsed,'model_bytes':size})
        base=model.predict(xte); rob_rows.append({'model':name,'condition':'clean',**compute_metrics(yt,base)})
        scale=np.maximum(np.std(xtr,axis=0),1e-6)
        for noise in [0.01,0.05]:
            vals=[compute_metrics(yt,model.predict(np.clip(xte+rng.normal(0,noise*scale,xte.shape),0,1))) for _ in range(10)]
            rob_rows.append({'model':name,'condition':f'gaussian_noise_{int(noise*100)}pct_mean',**{k:float(np.mean([v[k] for v in vals])) for k in ['accuracy','macro_precision','macro_recall','macro_f1']}})
        for mask in [0.01,0.05]:
            vals=[]
            for _ in range(10):
                z=xte.copy(); cols=rng.choice(z.shape[1],max(1,int(z.shape[1]*mask)),replace=False); z[:,cols]=0; vals.append(compute_metrics(yt,model.predict(z)))
            rob_rows.append({'model':name,'condition':f'feature_mask_{int(mask*100)}pct_mean',**{k:float(np.mean([v[k] for v in vals])) for k in ['accuracy','macro_precision','macro_recall','macro_f1']}})
    pd.DataFrame(dep_rows).to_csv(dep_out/'deployment_benchmark.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(rob_rows).to_csv(dep_out/'robustness_metrics.csv',index=False,encoding='utf-8-sig')
    print(metrics.to_string(index=False))

if __name__=='__main__': main()
