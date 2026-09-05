from pathlib import Path
import sys
import argparse,time,joblib,os
import numpy as np,pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestClassifier,ExtraTreesClassifier
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.experiment_components import WeightedRandomForest,compute_metrics,select_chi2_features

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--processed-dir',type=Path,required=True); ap.add_argument('--output-dir',type=Path,required=True); a=ap.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True); tr=pd.read_csv(a.processed_dir/'train.csv'); va=pd.read_csv(a.processed_dir/'validation.csv'); te=pd.read_csv(a.processed_dir/'test.csv'); names=[c for c in tr.columns if c!='target']; sc=MinMaxScaler(); X=sc.fit_transform(tr[names]); Xv=sc.transform(va[names]); Xt=sc.transform(te[names]); y=tr.target.to_numpy(); yv=va.target.to_numpy(); yt=te.target.to_numpy(); sel,_=select_chi2_features(pd.DataFrame(X,columns=names),y,60); idx=[names.index(s) for s in sel]
 models={}; models['rf_all']=(RandomForestClassifier(n_estimators=300,max_depth=20,min_samples_leaf=2,n_jobs=-1,class_weight='balanced_subsample',random_state=42),X,Xt); models['rf_chi2']=(RandomForestClassifier(n_estimators=300,max_depth=20,min_samples_leaf=2,n_jobs=-1,class_weight='balanced_subsample',random_state=42),X[:,idx],Xt[:,idx]); models['extra_trees_chi2']=(ExtraTreesClassifier(n_estimators=300,n_jobs=-1,class_weight='balanced',random_state=42),X[:,idx],Xt[:,idx]); w=WeightedRandomForest(n_estimators=300,random_state=42,weight_metric='balanced_accuracy'); w.fit(X[:,idx],y,Xv[:,idx],yv); models['weighted_rf_chi2']=(w,None,Xt[:,idx])
 rows=[]; robust=[]
 for name,(m,xtr,xte) in models.items():
  if xtr is not None: m.fit(xtr,y)
  path=a.output_dir/f'{name}.joblib'; joblib.dump(m,path,compress=3); size=path.stat().st_size
  for batch in [1,32,128,512]:
   reps=max(1,int(np.ceil(len(xte)/batch))); s=time.perf_counter();
   for i in range(reps): m.predict(xte[i*batch:(i+1)*batch])
   elapsed=time.perf_counter()-s; rows.append({'model':name,'batch_size':batch,'total_seconds':elapsed,'latency_ms_per_sample':elapsed/len(xte)*1000,'samples_per_second':len(xte)/elapsed,'model_bytes':size})
  base=m.predict(xte); robust.append({'model':name,'condition':'clean',**compute_metrics(yt,base)})
  rng=np.random.default_rng(42); feature_scale=np.maximum(np.std(xtr,axis=0) if xtr is not None else np.std(xte,axis=0),1e-6)
  for noise in [0.01,0.05]:
   scores=[compute_metrics(yt,m.predict(np.clip(xte+rng.normal(0,noise*feature_scale,xte.shape),0,1))) for _ in range(10)]
   robust.append({'model':name,'condition':f'gaussian_noise_{int(noise*100)}pct_mean',**{k:float(np.mean([s[k] for s in scores])) for k in ['accuracy','macro_precision','macro_recall','macro_f1']}})
  for mask in [0.01,0.05]:
   scores=[]
   for _ in range(10):
    z=xte.copy(); cols=rng.choice(z.shape[1],max(1,int(z.shape[1]*mask)),replace=False); z[:,cols]=0; scores.append(compute_metrics(yt,m.predict(z)))
   robust.append({'model':name,'condition':f'feature_mask_{int(mask*100)}pct_mean',**{k:float(np.mean([s[k] for s in scores])) for k in ['accuracy','macro_precision','macro_recall','macro_f1']}})
 pd.DataFrame(rows).to_csv(a.output_dir/'deployment_benchmark.csv',index=False,encoding='utf-8-sig'); pd.DataFrame(robust).to_csv(a.output_dir/'robustness_metrics.csv',index=False,encoding='utf-8-sig'); print('DEPLOYMENT_AND_ROBUSTNESS_DONE')
if __name__=='__main__': main()
