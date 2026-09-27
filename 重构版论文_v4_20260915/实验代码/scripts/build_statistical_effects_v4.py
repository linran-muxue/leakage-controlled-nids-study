"""Derive paired-test effect sizes and Holm-adjusted p-values from saved results."""
from pathlib import Path
import pandas as pd
import numpy as np
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.additional_metrics import holm_adjust

def main():
    src = ROOT / 'results_publication_final' / 'paired_significance_tests.csv'
    out = ROOT / 'results_additional_evidence_v4' / 'statistical_effects_holm.csv'
    df = pd.read_csv(src)
    n = 505
    df['n_test'] = n
    df['net_accuracy_effect'] = (df['b_only_correct'] - df['a_only_correct']) / n
    df['discordant_pairs'] = df['a_only_correct'] + df['b_only_correct']
    df['mcnemar_odds_ratio_cc'] = (df['b_only_correct'] + 0.5) / (df['a_only_correct'] + 0.5)
    df['holm_p_value'] = holm_adjust(df['p_value'].tolist())
    df['holm_permutation_p_value'] = holm_adjust(df['permutation_p_value'].tolist())
    df['significant_holm_0_05'] = (df['holm_p_value'] < 0.05) | (df['holm_permutation_p_value'] < 0.05)
    cols = ['seed','comparison','a_only_correct','b_only_correct','discordant_pairs','accuracy_delta_b_minus_a','net_accuracy_effect','mcnemar_odds_ratio_cc','p_value','holm_p_value','permutation_p_value','holm_permutation_p_value','significant_holm_0_05']
    out.parent.mkdir(parents=True, exist_ok=True)
    df[cols].to_csv(out, index=False, encoding='utf-8-sig')
    print(df[cols].to_string(index=False))

if __name__ == '__main__': main()
