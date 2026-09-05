# Leakage-Controlled Feature Selection and Random-Forest Ensembles for Network Intrusion Detection: A Reproducible Multi-Dataset Study

## Abstract

Reliable comparison of network intrusion detectors is difficult when feature selection, duplicate handling, class balancing, and train/test boundaries are inconsistently reported. This study presents a leakage-controlled, coverage-aware evaluation protocol. CIC-IDS2017 is the primary benchmark. After label mapping, invalid-record removal, global duplicate screening, and cross-label conflict handling, we construct a five-class balanced research subset of 3,365 flows. Stage-wise audit counts and source-file label fractions are reported, so the subset is not treated as a population estimate. Normalization, feature scoring, and model selection use training data only. With 60 chi-square-ranked features, 100 trees, and `min_samples_leaf=2`, the chi-square random forest obtains 95.78% ± 0.11% accuracy and 95.79% ± 0.11% macro-F1 across three seeds; the full-feature forest is essentially identical. Ten repeated stratified splits show no reliable macro-F1 advantage (paired sign-flip p=0.969). Validation-weighted and equal-voting forests produce identical predictions and are therefore interpreted as an applicability comparison. Independent NSL-KDD and UNSW-NB15 benchmarks expose class-imbalance and public-split effects. In UNSW-NB15, 10.37% of test rows match normalized training feature keys, and removing matches changes macro-F1. Held-out CIC attack families show family-dependent unknown rejection. The evidence supports reproducible protocol design and explicit validity boundaries, not universal superiority, complete temporal generalization, or real-gateway deployment.

**Keywords:** network intrusion detection; CIC-IDS2017; feature selection; random forest; leakage control; reproducibility; open-set recognition

## 1. Introduction

Machine-learning intrusion detection systems are often compared using a single accuracy value, although preprocessing, duplicate records, class priors, and split construction can materially alter that value. Public datasets make reproducible evaluation possible, but they also contain dataset-specific artifacts and incomplete metadata. Reviews of machine-learning methods for cybersecurity (Buczak and Guven, 2016) and network intrusion-detection datasets (Ring et al., 2019; Khraisat et al., 2019) have emphasized the impact of dataset construction and duplicated or near-duplicated records on reported conclusions. Concept drift and open-set recognition further motivate evaluation beyond random in-distribution splits (Lu et al., 2019; Geng et al., 2021). A rigorous study should therefore report not only predictive performance, but also the provenance of the data, the scope of preprocessing, the treatment of repeated records, the support of each class, and the uncertainty of the comparison.

This paper studies a controlled workflow for network-flow classification rather than claiming a universally optimal classifier. The workflow combines (i) staged data auditing, (ii) training-only preprocessing and feature selection, (iii) locked and independently tuned baselines, (iv) repeated-split and bootstrap uncertainty estimates, (v) probability and latency measurements, and (vi) independent-label benchmarks on NSL-KDD and UNSW-NB15. The study asks three questions:

1. Can chi-square filtering reduce the input dimension while preserving random-forest performance?
2. Does validation-based tree weighting produce a stable improvement over equal voting?
3. How do class imbalance, public split construction, unknown attack families, and measurement protocol affect the conclusions?

The contributions are deliberately evidence-bounded. We provide an auditable evaluation chain and quantify when common claims do or do not hold. The proposed weighting rule is retained as a reproducible ablation, not presented as a statistically validated state-of-the-art method. Before analysis, we defined three estimands: (H1) the paired difference in test Macro-F1 between chi-square and full-feature RF under repeated stratified splits; (H2) the paired disagreement rate between weighted and equal voting on the same test rows; and (H3) the change in class-balanced performance when the public data protocol is altered. H1 and H2 are inferential comparisons; H3 is a protocol-sensitivity estimand and is interpreted descriptively. This design treats model ranking, probability quality, and protocol sensitivity as distinct estimands rather than collapsing them into one score.

## 2. Datasets and provenance

### 2.1 CIC-IDS2017

CIC-IDS2017 was obtained from the Canadian Institute for Cybersecurity source page (Canadian Institute for Cybersecurity, n.d.) at <https://www.unb.ca/cic/datasets/ids-2017.html> and is used with the accompanying dataset description (Sharafaldin et al., 2018). The local `MachineLearningCSV` archive contained eight CSV files and 2,830,743 raw rows. The archive is identified by its SHA-256 checksum (`c3f26274b36c837ccf28ffd2dbf4582941c30b3ee70a635c6e5b2f87c4727928`) rather than by an invented numeric release version. The saved source record does not display a standard SPDX license identifier; use is therefore described as research use under the source-page terms.

The main task maps labels to Normal, DoS/DDoS, Brute Force, Web Attack, and Bot. PortScan, Infiltration, and Heartbleed are excluded from the closed-set task and reused only in the open-set analysis. After invalid-value cleaning, global duplicate screening, and removal of cross-label conflict groups, 53,237 capped candidate rows remain. Equal sampling across the five classes produces 3,365 flows (673 per class), split into 2,355 training, 505 validation, and 505 test rows. This is a controlled balanced research subset, not the full CIC-IDS2017 population. Because curation precedes splitting, the paper reports this as a dataset-level protocol choice and does not claim a completely untouched test corpus.

### 2.2 NSL-KDD

The NSL-KDD files were downloaded from the public `defcom17/NSL_KDD` mirror (defcom17, n.d.) (defcom17, n.d.) (defcom17, n.d.) using raw URLs recorded in the experiment log. The exact commit was not preserved, so the source is reported as a mirror snapshot and the file checksums are provided. The dataset choice follows the original KDD'99 analysis (Tavallaee et al., 2009). The local SHA-256 values are `1b86d2f957b33082081bba410fe129b475efebcc13c9014c3f447c8271aadf95` for `KDDTrain+.txt` and `fa46b0935342616aa83b7c2578db355b6a7aaabbc492248172c7a1e8b7ab8f84` for `KDDTest+.txt`. The task retains the public Normal, DoS, Probe, R2L, and U2R label system and the original train/test boundary. NSL-KDD is an independent benchmark, not a cross-dataset transfer test.

### 2.3 UNSW-NB15

UNSW-NB15 was obtained from the UNSW Canberra Cyber project page (UNSW Canberra Cyber, n.d.) at <https://research.unsw.edu.au/projects/unsw-nb15-dataset>. The study retains `UNSW-NB15_training-set.csv` (175,341 rows) and `UNSW-NB15_testing-set.csv` (82,332 rows), each with 45 columns and `attack_cat` as the target. The training and testing SHA-256 values are `bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa` and `734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559`, respectively. The project page requires academic/public users to cite the associated dataset paper; no standard SPDX license or numeric version is asserted here.

An audit excluding `id`, `label`, and `attack_cat` found 1,302 common normalized feature keys across the official files, covering 8,541 test rows (10.37%). This property is treated as a dataset limitation and is examined through split-sensitivity protocols.

## 3. Leakage-controlled methodology

All operations that estimate model or transformation parameters are restricted to the training partition or training fold. Numeric invalid values are removed before modeling. The CIC duplicate screen uses a two-order 128-bit composite fingerprint as a candidate locator, followed by full-vector checks for retained records. This global duplicate/conflict audit is a dataset-level curation step performed before the final split; it is not a fitted model transform, but it does use the available corpus and is therefore reported explicitly as a protocol choice rather than as a claim of untouched-test preprocessing. Min-max scaling, categorical encoding, chi-square scoring, mutual-information scoring, ANOVA scoring, and hyperparameter selection are fitted without access to validation or test labels. Source filename, row index, timestamp, and raw label are retained in provenance sidecars and excluded from model features.

The primary locked configuration uses 60 selected features, 100 trees, `min_samples_leaf=2`, and `class_weight=balanced_subsample`. Baselines include a decision tree, SVM, ExtraTrees (Geurts et al., 2006), full-feature random forest (Breiman, 2001), chi-square random forest (Liu and Setiono, 1995), and validation-based weighted random forest. Independently tuned configurations are reported separately from the controlled ablation; they are not mixed in the same performance claim. All reported model comparisons use the same rows, feature matrix, class order, and random seeds within each comparison family. The test set is accessed only once for the locked evaluation; model-selection results are reported from a separate nested cross-validation control.

For the weighted forest, tree (i) receives a validation balanced-accuracy score (b_i) and weight

\[
w_i=\frac{b_i+\varepsilon}{\sum_{j=1}^{T}(b_j+\varepsilon)}.
\]

The weighted class probability is defined as \(p_w(c\mid x)=\sum_i w_i p_i(c\mid x)\). Equal voting, accuracy weighting, and macro-F1 weighting are included as ablations. Classification metrics are accuracy, balanced accuracy, macro-precision, macro-recall, and macro-F1. Probability quality is assessed with log loss, macro-averaged Brier score, and expected calibration error; these metrics are reported separately from hard-label metrics because probability ranking and minority-class recall can move in different directions. Bootstrap intervals use test-row resampling and are reported as percentile 95% intervals (Efron and Tibshirani, 1997). McNemar's test is restricted to paired prediction disagreements (McNemar, 1947); paired sign-flip tests are reported for repeated-split metric differences. For multiple model contrasts, p-values are adjusted with Holm's step-down procedure within the pre-defined comparison family (Demšar, 2006). Alongside p-values, we report the paired effect estimate and its bootstrap interval; statistical significance is not interpreted as practical importance.

## 4. Experimental results

### 4.1 CIC-IDS2017 controlled comparison

With the locked configuration, chi-square random forest reaches 95.78% ± 0.11% accuracy and 95.79% ± 0.11% macro-F1 across seeds 42, 2024, and 3407. The complete locked comparison is provided in Table 1 and Figure 1. The complete locked comparison is provided in Table 1 and Figure 1. The full-feature random forest reaches 95.78% ± 0.23% accuracy and 95.79% ± 0.23% macro-F1. Thus, reducing 78 input features to 60 preserves the observed performance but does not establish a reliable improvement. Ten repeated stratified splits give macro-F1 values of 95.72% ± 1.11% for chi-square RF and 95.70% ± 1.05% for full-feature RF; the paired sign-flip p-value is 0.969.

The validation-balanced-accuracy weighted forest and equal-voting forest produce identical test predictions in the locked experiment. McNemar's discordant pair count is zero and p=1.0. The result is consistent with concentrated single-tree validation scores and near-uniform normalized weights. The weighting rule is therefore an interpretable applicability analysis with additional validation cost, not a demonstrated accuracy gain.

The inferential conclusion is unchanged after effect-size framing: the weighted-minus-equal Macro-F1 difference is 0.0000 on every locked seed, with no discordant test pair and a McNemar p-value of 1.0. Thus, the null result is not merely a failure to reach a threshold; the observed effect is exactly zero under this protocol.

### 4.2 Class-level, probability, and robustness evidence

The CIC test reports show that aggregate performance hides class differences; detailed class reports and confusion matrices are provided in Supplementary Materials S1–S6: in the representative chi-square RF run, Bot has F1=1.000, whereas Brute Force and Web Attack are the more difficult classes (F1=0.924 and 0.913 in the cited run). In the natural-distribution sensitivity set, accuracy remains around 97.8% while macro-F1 decreases to approximately 89.1–89.4%; Web Attack has F1=0.546 in the seed-42 report. These results motivate reporting balanced accuracy and class-level support together with accuracy.

Under shared perturbation masks, five-percent feature masking causes less than one percent macro-F1 loss in the reported protocol; the full perturbation table is provided in Supplementary Material S14 and the calibration curves are shown in Figure 2, whereas one-percent Gaussian noise produces an approximately 30% relative macro-F1 decrease. These measurements apply to already extracted features and do not constitute an end-to-end robustness or gateway deployment test. Offline latency is reported with P50, P95, and P99. For chi-square RF at batch size one, single-thread latency is 9.459, 11.809, and 12.352 ms per sample for P50/P95/P99; multi-thread latency is 35.726, 45.128, and 292.883 ms. The long multi-thread tail is treated as a measurement limitation rather than a deployment guarantee.

### 4.3 Open-set analysis

PortScan, Infiltration, and Heartbleed are held out as unknown families. The threshold is fitted from known-class validation scores only. Following the closed-set/open-set distinction in the open-set recognition literature (Geng et al., 2021), the threshold is never fitted on unknown test rows. When all three families are held out, AUROC is 0.9587, AUPR is 0.9097, FPR at 95% TPR is 0.0588, and unknown recall is 0.7488. Performance is family-dependent: Heartbleed alone has AUROC 0.9944 and unknown recall 1.0000 with only 11 unknown samples, whereas Infiltration alone has unknown recall 0.3889. The evidence supports attack-family-dependent rejection potential, not a solved open-set detector.

### 4.4 Independent benchmarks

On NSL-KDD, the best macro-F1 among the reported models is 0.5991 for ExtraTrees with chi-square selection; balanced accuracy is 0.5707. Detailed minority-class metrics and confusion matrices are provided in Supplementary Materials S7–S8. Detailed minority-class metrics and confusion matrices are provided in Supplementary Materials S7–S8. R2L and U2R remain difficult minority classes, with low recall and frequent confusion with Normal. On UNSW-NB15 (Moustafa and Slay, 2015), after excluding `id`, binary `label`, and target `attack_cat`, the 42 raw predictors are encoded into 197 training-derived numeric features. The three-seed full-feature RF obtains accuracy 0.7038, balanced accuracy 0.5677, and macro-F1 0.4824; the 60-feature chi-square RF obtains 0.7083, 0.5415, and 0.4673, respectively. XGBoost (Chen and Guestrin, 2016) has higher accuracy (0.7680) and better probability metrics, but lower balanced accuracy (0.5254) than full-feature RF. The official UNSW protocol yields macro-F1 0.4570 in the split-sensitivity experiment; removing test-side feature-key matches changes it to 0.4851, while removing matches on both sides yields 0.4770. These values should be read as protocol sensitivity, not as direct evidence of cross-dataset transfer.

### 4.5 Nested model-selection control

The nested comparison follows the multiple-classifier evaluation principles of Demšar (2006).

The nested model-wise experiment uses five outer folds and inner tuning restricted to each outer-training partition. The outer-fold macro-F1 means are 0.9544 ± 0.0059 for random forest, 0.9480 ± 0.0067 for ExtraTrees, and 0.9622 ± 0.0059 for XGBoost. The paired XGBoost-versus-random-forest macro-F1 difference is 0.0078 with a 95% interval of [0.0044, 0.0105], while the fold-level permutation p-value is 0.0625. This control analysis indicates that model selection can change the ranking observed under a locked configuration, but the present five-fold sample does not justify a statistically significant superiority claim at the 0.05 level. Because only five outer folds are available, the p-value has a discrete resolution of 1/16; it should be treated as a small-sample sensitivity result rather than as definitive evidence for or against superiority.

### 4.6 Protocol sensitivity and evidence hierarchy

The results are reported in an explicit evidence hierarchy. The locked CIC experiment is the primary within-dataset comparison; repeated stratified splits quantify split sensitivity; nested cross-validation controls model-selection optimism; open-set and file-level analyses probe distribution shift; and NSL-KDD and UNSW-NB15 are independent-label benchmarks. These layers answer different questions and are not pooled into a single grand average. The balanced CIC subset estimates performance under a controlled class prior, whereas the natural-distribution and external-dataset analyses estimate sensitivity to class prior and dataset construction. This separation prevents a high score in one protocol from being used as evidence for a stronger claim in another.

For practical interpretation, relative degradation is defined as \(\Delta_{rel}=100(M_{clean}-M_{perturbed})/M_{clean}\), where \(M\) is Macro-F1 or balanced accuracy. A degradation percentage is accompanied by the clean and perturbed values, the common perturbation seed, and the number of repeated measurements. The same rule is used for protocol-sensitivity comparisons, with the reference protocol stated explicitly.

## 5. Limitations and reproducibility

The main CIC result is based on a 3,365-row balanced research subset and cannot be extrapolated to the full archive or to a production traffic prior. The global curation step is performed before splitting and is therefore a dataset-level protocol choice rather than a claim of a pristine untouched test corpus. File-level CIC experiments are coverage audits because no individual source file contains all five main classes; they do not prove complete temporal generalization. NSL-KDD is based on a public mirror snapshot without a preserved commit. UNSW-NB15 has measurable cross-split feature-key overlap, and its official test score is therefore not treated as an unbiased external generalization estimate. Offline latency excludes packet capture, flow construction, network I/O, and alert handling. The source screenshots, checksums, processing scripts, configuration files, predictions, and audit summaries are stored with the project materials. Raw datasets are not redistributed.

## 6. Conclusion

The experiments show that a leakage-controlled and provenance-aware protocol can preserve reproducibility while exposing important evaluation boundaries. The nested analysis provides a model-selection-bias control and yields a higher point estimate for tuned XGBoost, but its fold-level permutation result does not cross the 0.05 threshold. On the controlled CIC subset, chi-square selection reduces the input dimension with nearly unchanged random-forest macro-F1. The validation-weighted forest does not differ from equal voting under the present configuration. Independent benchmarks reveal strong class-prior and split-construction effects, while open-set performance varies across unknown attack families. The appropriate conclusion is therefore methodological: reliable intrusion-detection comparisons require explicit data auditing, training-only preprocessing, class-level and probability metrics, repeated uncertainty estimates, and transparent limitations. The results do not establish universal classifier superiority, complete time-external generalization, or real-gateway deployment.

## Declarations

### CRediT authorship contribution statement

Conceptualization, methodology, software, data curation, formal analysis, visualization, and writing (original draft and review) were performed by the authors. The final author names and role attribution will be entered identically in the manuscript and Editorial Manager.

### Funding

This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.

### Declaration of competing interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

### Acknowledgements

No external acknowledgements are declared.

## Data and code availability

The project stores preprocessing scripts, audit summaries, model configurations, predictions, statistical outputs, and source-record screenshots. A supplementary-material index maps each manuscript table identifier to its canonical machine-readable file and generating protocol. CIC-IDS2017, NSL-KDD, and UNSW-NB15 were obtained from their respective public distribution pages. The files are used for offline research in accordance with the terms stated by the respective providers or repositories; no standard SPDX license is asserted where the source does not state one. Raw datasets are not redistributed. The reproducibility package includes the processing scripts, configuration files, audit summaries, prediction outputs, source-record screenshots, and a locked software environment. The original datasets are not redistributed because their providers control access and reuse. The scripts and derived artifacts are publicly archived at https://github.com/linran-muxue/leakage-controlled-nids-study (release `v1.0.0`). The repository excludes the original datasets and records the processing scripts, derived artifacts, source evidence, and locked software environment.


## Declaration of Generative AI and AI-assisted technologies in the manuscript preparation process

During the preparation of this manuscript, the authors used ChatGPT to assist with language editing, document organization, code documentation, and the presentation of reproducibility materials. The authors reviewed and edited all assisted content, verified the reported data and references, and take full responsibility for the final published version.

## References

Breiman L. Random forests. Machine Learning, 2001, 45(1):5–32. DOI:10.1023/A:1010933404324.
Buczak AL, Guven E. A survey of data mining and machine learning methods for cyber security intrusion detection. IEEE Communications Surveys & Tutorials, 2016, 18(2):1153–1176. DOI:10.1109/COMST.2015.2494502.
Chen T, Guestrin C. XGBoost: A scalable tree boosting system. Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 2016:785–794. DOI:10.1145/2939672.2939785.
Demšar J. Statistical comparisons of classifiers over multiple data sets. Journal of Machine Learning Research, 2006, 7:1–30.
Efron B, Tibshirani RJ. Improvements on cross-validation: The .632+ bootstrap method. Journal of the American Statistical Association, 1997, 92(438):548–560. DOI:10.2307/2965703.
Geng C, Huang SH, Chen S. Recent advances in open set recognition: A survey. IEEE Transactions on Pattern Analysis and Machine Intelligence, 2021, 43(10):3614–3631. DOI:10.1109/TPAMI.2020.2981604.
Geurts P, Ernst D, Wehenkel L. Extremely randomized trees. Machine Learning, 2006, 63:3–42. DOI:10.1007/s10994-006-6226-1.
Khraisat A, Gondal I, Vamplew P, Kamruzzaman J. Survey of intrusion detection systems: Techniques, datasets and challenges. Cybersecurity, 2019, 2:20. DOI:10.1186/s42400-019-0038-7.
Liu H, Setiono R. Chi2: Feature selection and discretization of numeric attributes. ICTAI, 1995, 388–391. DOI:10.1109/TAI.1995.479783.
Lu J, Liu A, Dong F, Gu F, Gama J, Zhang G. Learning under concept drift: A review. IEEE Transactions on Knowledge and Data Engineering, 2019, 31(12):2346–2363. DOI:10.1109/TKDE.2018.2876857.
McNemar Q. Note on the sampling error of the difference between correlated proportions or percentages. Psychometrika, 1947, 12:153–157. DOI:10.1007/BF02295996.
Moustafa N, Slay J. UNSW-NB15: A comprehensive data set for network intrusion detection systems. MilCIS, 2015:1–6. DOI:10.1109/MilCIS.2015.7348942.
Ring M, Wunderlich S, Grüdl D, Landes D, Hotho A. A survey of network-based intrusion detection data sets. Computers & Security, 2019, 86:147–167. DOI:10.1016/j.cose.2019.06.005.
Sharafaldin I, Lashkari AH, Ghorbani AA. Toward generating a new intrusion detection dataset and intrusion traffic characterization. ICISSP, 2018:108–116. DOI:10.5220/0006639801080116.
Tavallaee M, Bagheri E, Lu W, Ghorbani AA. A detailed analysis of the KDD CUP 99 data set. CISDA, 2009:1–6. DOI:10.1109/CISDA.2009.5356528.

## Data references

[dataset] Canadian Institute for Cybersecurity. CIC-IDS2017 dataset. n.d. https://www.unb.ca/cic/datasets/ids-2017.html (accessed 5 September 2026).
[dataset] defcom17. NSL_KDD repository snapshot. n.d. https://github.com/defcom17/NSL_KDD (accessed 5 September 2026).
[dataset] UNSW Canberra Cyber. UNSW-NB15 dataset. n.d. https://research.unsw.edu.au/projects/unsw-nb15-dataset (accessed 5 September 2026).
