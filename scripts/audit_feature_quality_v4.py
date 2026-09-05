"""Audit feature degeneracy, redundancy and split overlap for CIC v4 data."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--processed-dir', type=Path, required=True)
    ap.add_argument('--output-dir', type=Path, required=True)
    ap.add_argument('--near-zero-threshold', type=float, default=0.001)
    ap.add_argument('--high-correlation-threshold', type=float, default=0.99)
    args = ap.parse_args(); args.output_dir.mkdir(parents=True, exist_ok=True)
    train = pd.read_csv(args.processed_dir/'train.csv', low_memory=False)
    valid = pd.read_csv(args.processed_dir/'validation.csv', low_memory=False)
    test = pd.read_csv(args.processed_dir/'test.csv', low_memory=False)
    names = [c for c in train.columns if c != 'target']
    x = train[names].apply(pd.to_numeric, errors='raise')
    nunique = x.nunique(dropna=False)
    summary = pd.DataFrame({'feature': names, 'nunique': [int(nunique[c]) for c in names], 'unique_ratio': [float(nunique[c]/len(x)) for c in names], 'missing_count': [int(x[c].isna().sum()) for c in names]})
    summary['is_constant'] = summary['nunique'] == 1
    summary['is_near_zero_variance'] = summary.unique_ratio < args.near_zero_threshold
    summary.to_csv(args.output_dir/'feature_quality_summary.csv', index=False, encoding='utf-8-sig')
    corr = x.corr().abs(); upper = corr.where(np.triu(np.ones(corr.shape), 1).astype(bool)); pairs=[]
    for col in upper.columns:
        for row in upper.index:
            value = upper.loc[row, col]
            if pd.notna(value) and value >= args.high_correlation_threshold:
                pairs.append({'feature_a': row, 'feature_b': col, 'abs_correlation': float(value)})
    pd.DataFrame(pairs).sort_values('abs_correlation', ascending=False).to_csv(args.output_dir/'high_correlation_pairs.csv', index=False, encoding='utf-8-sig')
    hashes = {}
    for name, frame in [('train',train),('validation',valid),('test',test)]:
        hashes[name] = set(pd.util.hash_pandas_object(frame[names], index=False))
    overlap = {'train_validation': len(hashes['train'] & hashes['validation']), 'train_test': len(hashes['train'] & hashes['test']), 'validation_test': len(hashes['validation'] & hashes['test'])}
    result = {'processed_dir': str(args.processed_dir), 'train_rows': len(train), 'validation_rows': len(valid), 'test_rows': len(test), 'feature_count': len(names), 'constant_feature_count': int(summary.is_constant.sum()), 'constant_features': summary.loc[summary.is_constant,'feature'].tolist(), 'near_zero_variance_count': int(summary.is_near_zero_variance.sum()), 'near_zero_variance_features': summary.loc[summary.is_near_zero_variance,'feature'].tolist(), 'high_correlation_threshold': args.high_correlation_threshold, 'high_correlation_pair_count': len(pairs), 'cross_split_exact_feature_overlaps': overlap, 'recommendation': 'Treat constant and near-zero-variance features as an audit/ablation condition; do not silently change the locked main protocol.'}
    (args.output_dir/'feature_quality_audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__': main()
