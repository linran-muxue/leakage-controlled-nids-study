"""Attach raw-file provenance to the already locked processed CIC splits.

The model files remain feature-only; provenance is stored in sidecar CSVs so
source metadata cannot accidentally enter the feature matrix.
"""
from pathlib import Path
import argparse
import hashlib
import json
import pandas as pd
import numpy as np
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data_pipeline import map_attack_label

def fp(values):
    a = pd.DataFrame([values])
    f = int(pd.util.hash_pandas_object(a, index=False).iloc[0])
    b = int(pd.util.hash_pandas_object(a[a.columns[::-1]], index=False).iloc[0])
    return f, b

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--raw-dir',type=Path,required=True); ap.add_argument('--processed-dir',type=Path,required=True); ap.add_argument('--output-dir',type=Path,required=True)
    args=ap.parse_args(); args.output_dir.mkdir(parents=True,exist_ok=True)
    splits={s:pd.read_csv(args.processed_dir/f'{s}.csv',low_memory=False) for s in ['train','validation','test']}
    names=[c for c in splits['train'].columns if c!='target']; wanted={}
    for s,df in splits.items():
        for i,row in df.iterrows(): wanted.setdefault(fp(row[names].to_numpy()), []).append((s,int(i),str(row['target'])))
    found={k:[] for k in splits}
    for path in sorted(args.raw_dir.rglob('*.csv')):
        for chunk in pd.read_csv(path,chunksize=100000,low_memory=False,encoding_errors='replace'):
            chunk.columns=[str(c).strip() for c in chunk.columns]
            label_col=next(c for c in chunk.columns if c.lower()=='label')
            mapped=chunk[label_col].map(lambda x: map_attack_label(x,include_other=False))
            feature_names=[c for c in names if c in chunk.columns]
            numeric=chunk[feature_names].apply(pd.to_numeric,errors='coerce').replace([np.inf,-np.inf],np.nan)
            valid=numeric.notna().all(axis=1)
            for local_idx,(idx,row) in enumerate(numeric.loc[valid].iterrows()):
                label=mapped.loc[idx]
                if pd.isna(label): continue
                key=fp(row.to_numpy())
                if key not in wanted: continue
                for split,processed_idx,target in wanted[key]:
                    if target==label and not any(x['processed_row_id']==processed_idx for x in found[split]):
                        found[split].append({'processed_row_id':processed_idx,'source_file':path.name,'source_path':str(path),'source_row_id':int(idx),'source_label':str(chunk.loc[idx,label_col]).strip(),'mapped_target':str(label)})
    for s,df in splits.items():
        out=pd.DataFrame(found[s]).sort_values('processed_row_id') if found[s] else pd.DataFrame(columns=['processed_row_id','source_file','source_path','source_row_id','source_label','mapped_target'])
        out.to_csv(args.output_dir/f'{s}_source_provenance.csv',index=False,encoding='utf-8-sig')
        print(s, len(out), 'of', len(df))
    (args.output_dir/'README.json').write_text(json.dumps({'raw_dir':str(args.raw_dir),'processed_dir':str(args.processed_dir),'feature_columns':names,'metadata_kept_out_of_model_features':True},ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__': main()
