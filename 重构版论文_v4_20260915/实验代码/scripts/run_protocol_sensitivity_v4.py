"""Compare the locked global-dedup protocol with a split-first/training-only-dedup protocol."""
from pathlib import Path
import argparse, json, time
import numpy as np, pandas as pd
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_selection import chi2
from src.data_pipeline import map_attack_label
from src.experiment_components import compute_metrics

def raw_capped_balanced(raw_dir, cap=20000, per_class=673):
    buckets={}
    for path in sorted(raw_dir.rglob('*.csv')):
        for ch in pd.read_csv(path,chunksize=100000,low_memory=False,encoding_errors='replace'):
            ch.columns=[str(c).strip() for c in ch.columns]; lc=next(c for c in ch.columns if c.lower()=='label')
            mp=ch[lc].map(lambda x:map_attack_label(x,False)); keep=mp.notna(); ch=ch.loc[keep].copy(); mp=mp.loc[keep]
            names=[c for c in ch.columns if c not in {lc,'Flow ID','Timestamp'}]
            num=ch[names].apply(pd.to_numeric,errors='coerce').replace([np.inf,-np.inf],np.nan); valid=num.notna().all(axis=1)
            num=num.loc[valid].copy(); mp=mp.loc[valid]
            num['target']=mp.to_numpy()
            for label,g in num.groupby('target'):
                buckets.setdefault(label,[]).append(g)
    out=[]
    for label,parts in buckets.items():
        g=pd.concat(parts,ignore_index=True)
        if len(g)>cap: g=g.sample(cap,random_state=42)
        if len(g)>per_class: g=g.sample(per_class,random_state=42)
        out.append(g)
    return pd.concat(out,ignore_index=True).sample(frac=1,random_state=42).reset_index(drop=True)

def evaluate(frame, seed, training_dedup=False):
    tr, rest=train_test_split(frame,test_size=.30,stratify=frame.target,random_state=seed); va,te=train_test_split(rest,test_size=.50,stratify=rest.target,random_state=seed)
    names=[c for c in frame.columns if c!='target'];
    if training_dedup:
        tr=tr.drop_duplicates(subset=names).reset_index(drop=True)
    sc=MinMaxScaler(); X=sc.fit_transform(tr[names]); Xt=sc.transform(te[names]); y=tr.target.to_numpy(); yt=te.target.to_numpy(); scores,_=chi2(X,y); idx=np.sort(np.argsort(-np.nan_to_num(scores,nan=0),kind='stable')[:60])
    m=RandomForestClassifier(n_estimators=100,min_samples_leaf=2,class_weight='balanced_subsample',n_jobs=-1,random_state=seed); start=time.perf_counter(); m.fit(X[:,idx],y); train_s=time.perf_counter()-start; pred=m.predict(Xt[:,idx]); return {'seed':seed,'train_rows':len(tr),'test_rows':len(te),'training_only_dedup':training_dedup,**compute_metrics(yt,pred),'train_seconds':train_s}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--raw-dir',type=Path,required=True); ap.add_argument('--canonical-dir',type=Path,required=True); ap.add_argument('--output-dir',type=Path,required=True); args=ap.parse_args(); args.output_dir.mkdir(parents=True,exist_ok=True)
    canonical=pd.concat([pd.read_csv(args.canonical_dir/f'{s}.csv',low_memory=False) for s in ['train','validation','test']],ignore_index=True); raw=raw_capped_balanced(args.raw_dir)
    rows=[]
    for seed in [42,2024,3407]: rows += [dict(protocol='global_dedup_before_split',**evaluate(canonical,seed,False)),dict(protocol='split_first_training_only_dedup',**evaluate(raw,seed,True))]
    pd.DataFrame(rows).to_csv(args.output_dir/'protocol_sensitivity_metrics.csv',index=False,encoding='utf-8-sig'); (args.output_dir/'protocol.json').write_text(json.dumps({'global_protocol':'canonical dedup-balanced frame','sensitivity_protocol':'raw mapped/capped/balanced frame; deduplicate training split only','seeds':[42,2024,3407]},ensure_ascii=False,indent=2),encoding='utf-8'); print(pd.DataFrame(rows).to_string(index=False))
if __name__=='__main__': main()
