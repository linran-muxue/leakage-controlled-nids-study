"""Reproduce the offline latency percentile protocol without rerunning all evidence."""
from pathlib import Path
import argparse
import time
import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import chi2
from sklearn.preprocessing import MinMaxScaler
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.additional_metrics import percentile_latency

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--processed-dir', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--k', type=int, default=60)
    ap.add_argument('--n-estimators', type=int, default=100)
    ap.add_argument('--min-samples-leaf', type=int, default=2)
    args = ap.parse_args()
    tr = pd.read_csv(args.processed_dir/'train.csv', low_memory=False)
    te = pd.read_csv(args.processed_dir/'test.csv', low_memory=False)
    names = [c for c in tr.columns if c != 'target']
    scaler = MinMaxScaler(); x = scaler.fit_transform(tr[names]); xt = scaler.transform(te[names])
    y = tr.target.to_numpy()
    scores, _ = chi2(x, y)
    scores = np.nan_to_num(scores, nan=0.0, posinf=np.finfo(float).max)
    cols = np.argsort(-scores, kind='stable')[:args.k]
    rows=[]
    for method, indices in [('all', np.arange(x.shape[1])), ('chi2', cols)]:
        model = RandomForestClassifier(n_estimators=args.n_estimators, min_samples_leaf=args.min_samples_leaf,
            class_weight='balanced_subsample', n_jobs=1, random_state=42).fit(x[:, indices], y)
        xte = xt[:, indices]
        for n_jobs in [1, -1]:
            model.set_params(n_jobs=n_jobs)
            for batch in [1, 32, 128, 512]:
                for _ in range(3):
                    model.predict(xte[:min(batch, len(xte))])
                values=[]
                for _ in range(30):
                    start=time.perf_counter()
                    for i in range(0, len(xte), batch): model.predict(xte[i:i+batch])
                    values.append((time.perf_counter()-start)/len(xte)*1000)
                rows.append({'method':method,'n_jobs':n_jobs,'batch_size':batch,**percentile_latency(values),'mean_ms':float(np.mean(values))})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.output,index=False,encoding='utf-8-sig')
    print(pd.DataFrame(rows).to_string(index=False))

if __name__ == '__main__': main()
