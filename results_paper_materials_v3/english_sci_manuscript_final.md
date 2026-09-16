# Risk-Calibrated Conformal Forests for Auditable Network Intrusion Detection: A Leakage-Controlled Multi-Dataset Evaluation

## Abstract

Performance claims for network intrusion detection are sensitive to duplicate flows, label conflicts, class priors, feature-selection leakage, and public split construction. We present Risk-Calibrated Conformal Forest (RCCF), a bounded sample-conditional reliability layer for random forests, and evaluate it under a pre-specified, leakage-controlled protocol. RCCF trains four forest experts (full, chi-square, mutual-information, and ANOVA views), learns risk models from cross-fitted training predictions, calibrates probabilities on a disjoint validation partition, and reports conformal rejection without using final test labels for fitting. The strict primary CIC protocol retains the observed class prior after global deduplication, physical-range screening, and a 20,000-per-class cap (53,237 flows; 37,265/7,986/7,986 train/validation/test). RCCF reaches Macro-F1 0.889955 across three fixed seeds, versus 0.887960 for a full-feature equal RF and 0.888870 for a chi-square RF. A 3,365-flow balanced subset is retained as a control protocol, where RCCF reaches 0.961807; this score is not interpreted as natural-prevalence performance. RCCF incurs higher inference cost and does not dominate ExtraTrees or the strongest external baselines. Native-label NSL-KDD and UNSW-NB15 experiments are independent benchmarks, not transfer tests, and expose minority-class and calibration limitations. The contribution is methodological: a reproducible protocol that quantifies how class priors, deduplication, conditional weighting, probability quality, rejection, and cost alter conclusions. The evidence does not support a universal-superiority or production-readiness claim.

**Keywords:** network intrusion detection; random forest; risk calibration; conformal prediction; leakage control; reproducibility; open-set evaluation

## 1. Introduction

### 1.1 Motivation and scope

Public intrusion-detection datasets contain repeated feature vectors, conflicting labels, strong class imbalance, and dataset-specific artefacts. A random split can place near-identical flows in both training and test sets; fitting a scaler or selector before splitting can leak distributional information; and accuracy can hide failure on rare attack families. We study closed-set multiclass flow classification and treat unknown-family rejection, probability quality, robustness, and latency as separate diagnostic estimands.

### 1.2 Research questions and hypotheses

RQ1 asks whether training-only feature filtering reduces dimensionality without material Macro-F1 loss. RQ2 asks whether a cross-fitted risk gate produces a stable gain over equal voting. RQ3 asks how deduplication, class priors, unknown families, and split construction affect conclusions. RQ4 asks whether observations persist across independent datasets and repeated partitions. H1-H4 were declared directionally before interpreting the final numbers. H2 is supported only if the paired difference is stable, practically meaningful, and statistically credible.

### 1.3 Contributions and evidence hierarchy

The study contributes (i) an auditable CIC-IDS2017 curation record, (ii) an implementation of RCCF with explicit training, calibration, and test boundaries, (iii) paired uncertainty, calibration, robustness, latency, and coverage analyses, and (iv) independent native-label checks on NSL-KDD and UNSW-NB15. Locked CIC results are primary; repeated and strong-baseline results are stability checks; external datasets are pressure tests. Scores are never pooled across incompatible label spaces.

### 1.4 Estimands and decision rules

Let $P_{CIC}^{nat}$ denote the deduplicated, capped population with observed class proportions and let $P_{CIC}^{bal}$ denote the 3,365-flow balanced control population. The primary estimand is test Macro-F1 on $P_{CIC}^{nat}$ under a stratified 70/15/15 split, averaged over seeds 42, 2024, and 3407. The balanced protocol is a secondary control estimand on a balanced research subset. Secondary estimands are paired RCCF--equal-RF differences, log loss, Brier score, ECE/MCE, selective risk, unknown-family rejection, perturbation degradation, and single-row latency percentiles. A small point estimate without paired support is not treated as an algorithmic advantage. Table 1 and Figure 1 summarize the primary and control comparisons.

## 2. Related Work and Positioning

Classical trees, support-vector machines, random forests, and boosting remain attractive for heterogeneous flow statistics. Filter selectors such as chi-square, mutual information, and ANOVA are inexpensive but must be fitted within the training boundary. Random forests use equal tree voting; RCCF tests whether a sample-conditional reliability layer can improve that aggregation. ExtraTrees and XGBoost are strong controls. Open-set recognition methods based on OpenMax, EVT, prototypes, or deep representations are dataset-dependent; RCCF is not positioned as a universal replacement.

### 2.1 Study family comparison

| Family | Strength | Main validity risk | Treatment here |
|---|---|---|---|
| Classical IDS models | Low cost | Prior-dominated accuracy | Macro-F1, balanced accuracy, class reports |
| Filter-selected forests | Compact features | Selector leakage | Training-only selectors |
| Boosting/ExtraTrees | Strong nonlinear controls | Unequal tuning budget | Same locked feature budget |
| OOB risk gating | Conditional reliability | Correlated OOB rows | Cross-fitted risk models and paired tests |
| Open-set rejection | Explicit unknown output | Threshold leakage | Known-only calibration and conformal diagnostics |

Table 1a compares representative recent studies by task, method family, and evaluation boundary. The table is a scope comparison rather than a ranking of reported accuracy.

| Study family | Typical data/task | Fitting boundary | Primary outcome | Limitation relevant here |
|---|---|---|---|---|
| OpenMax/EVT and prototype methods | Closed plus unknown attacks | Threshold dependent | Unknown rejection | Openness sensitivity |
| VAE/GAN representations | IoT or CIC flows | Joint representation/classifier | Unknown detection | Higher cost |
| Bayesian/ensemble uncertainty | Multi-dataset diagnostics | Uncertainty model fit with predictor | Calibration/OoD | Calibration assumptions |
| Leakage and cross-dataset studies | Public IDS datasets | Protocol as treatment | Ranking change | Usually no conditional forest gate |
| This study | CIC primary; NSL/UNSW independent | OOB gate and training-only transforms | Paired labels, probabilities, rejection | Bounded mechanism; no universal gain |

## 3. Data and Provenance

### 3.1 CIC-IDS2017

CIC-IDS2017 follows Sharafaldin et al. (2018). The local MachineLearningCSV archive contains eight CSV files and 2,830,743 raw rows. BENIGN is mapped to Normal; DDoS and DoS families to DoS/DDoS; FTP-Patator, SSH-Patator and Web Attack Brute Force to Brute Force; XSS and SQL Injection to Web Attack; and Bot remains Bot. PortScan, Infiltration, and Heartbleed are excluded from the closed-set task and reserved for diagnostics.

The audit records 2,671,766 mapped rows, 2,741 non-finite rows, and 2,669,025 finite rows. A separate physical-range audit removes 296 additional records with impossible negative duration, rate, header-length, or segment-size values; CICFlowMeter's documented -1 unavailable sentinels for initial-window and undefined inter-arrival fields are retained. The strict protocol therefore contains 2,668,729 physically valid mapped rows before deduplication. It records 239,093 duplicate occurrences, 4,524 cross-label mismatch occurrences, 5,048 rows in affected conflict groups, and 133 conflicting feature vectors removed before capping. A 20,000-per-class cap leaves 53,237 candidates with proportions Normal 37.57%, DoS/DDoS 37.56%, Brute Force 19.95%, Bot 3.66%, and Web Attack 1.26%. The primary natural-prior protocol retains all 53,237 candidates; the 3,365-flow equal-per-class sample is a secondary control. Neither protocol is full-corpus performance or a production prevalence estimate.

| Stage | Rows | Interpretation |
|---|---:|---|
| Raw archive | 2,830,743 | Eight local CSV files |
| Label mapped | 2,671,766 | Assigned to retained/reserved families |
| Finite numeric | 2,669,025 | NaN/infinite/non-finite rows removed |
| Physical-range valid | 2,668,729 | 296 impossible negative duration/rate/length records removed |
| Duplicate occurrences | 239,101 | Repeated feature-vector occurrences |
| Conflict groups removed | 133 | Unique conflicting vectors |
| Capped candidates | 53,237 | Up to 20,000 per retained class |
| Capped natural-prior population | 53,237 | 20,000-per-class cap; observed proportions retained |
| Balanced control subset | 3,365 | 673 per class |

### 3.2 NSL-KDD

NSL-KDD follows Tavallaee et al. (2009) and retains the public KDDTrain+/KDDTest+ boundary with native Normal, DoS, Probe, R2L, and U2R labels. The repository records the mirror URL, access metadata, file hashes, row counts, and native class counts. Because the mirror snapshot does not provide a verified SPDX license, no license is inferred. NSL-KDD is an independent native-label benchmark, not direct evidence of cross-dataset transfer and not as direct evidence of cross-dataset transfer as a paired migration experiment.

### 3.3 UNSW-NB15

UNSW-NB15 follows Moustafa and Slay (2015) and uses the official training/testing files and native ten-class `attack_cat` labels. The binary label and identifier are excluded; categorical variables are encoded from the training side. SHA-256 values are recorded for both files. This experiment is independent native-label validation, not pooled performance or transfer learning.

### 3.4 Data populations and why two CIC protocols are required

The raw CIC corpus is not treated as a single exchangeable population. We define two explicit estimands from the same globally deduplicated source: $P_{CIC}^{nat}$ retains observed class proportions after a transparent 20,000-per-class cap, whereas $P_{CIC}^{bal}$ draws 673 rows per class for a balanced control. The former is primary because it preserves prevalence information; the latter isolates class-balanced discrimination. The cap is a computational and reproducibility constraint, not a claim that the resulting proportions equal real-world prevalence.

## 4. Methodology

### 4.1 Leakage-controlled protocol

Corpus-level duplicate and conflict curation is completed before splitting and reported as a population-definition choice. For each seed, the balanced population is split 70/15/15. Scalers and feature selectors are fitted on training rows only. RCCF risk models use cross-fitted training predictions; temperature and conformal parameters use the validation partition; final test labels are used only for diagnostics.

### 4.2 RCCF mechanism

Four experts are trained: full features, chi-square Top-$k$, mutual-information Top-$k$, and ANOVA Top-$k$. For expert $e$, OOF probabilities produce confidence, normalized entropy, and top-two margin descriptors. A logistic risk model estimates $r_e(x)$ from the concatenated OOF probabilities and descriptors. The conditional weights are

$$w_e(x)=\frac{\exp[-r_e(x)]}{\sum_j\exp[-r_j(x)]}, \qquad p(y\mid x)=\sum_e w_e(x)p_e(y\mid x).$$

Temperature scaling is fitted on validation probabilities only. Mondrian conformal p-values provide a selective `unknown` output at alpha=0.1. The mechanism changes probabilities first; a hard-label change is possible only when the fused argmax changes.

### 4.3 Training and inference algorithm

Algorithm 1 makes the information boundary explicit. For each cross-fitting fold, every expert is trained without the fold's validation rows, and its out-of-fold probabilities are stored. Risk models are then fitted to those out-of-fold descriptors. Only after this step are the four experts refitted on the complete training partition. The validation partition is used once for temperature and conformal calibration; it is never used to fit the risk gate. At inference, the four probability vectors and descriptors are passed through the already-fitted risk models, normalized by a row-wise softmax, and fused.

**Algorithm 1. Leakage-controlled RCCF training and inference.**

```text
Input: training matrix X_tr, labels y_tr; validation matrix X_va, labels y_va;
       feature budget k, forest size T, folds K, conformal level alpha.
1. Split (X_tr, y_tr) into K stratified folds.
2. For each fold and each expert q in {full, chi2, mutual-information, ANOVA}:
      fit the scaler and selector on the fold's training rows;
      fit a T-tree forest; predict the held-out fold;
      store out-of-fold probabilities and uncertainty descriptors.
3. Fit one logistic risk model r_q on the complete out-of-fold table for each q.
4. Refit all four expert forests on all training rows; retain their scalers/selectors.
5. Predict X_va with the fused experts; fit temperature and Mondrian calibration.
6. For a new row x, transform x through each expert, obtain p_q(x),
      estimate r_q(x), set w_q(x)=exp(-r_q(x))/sum_j exp(-r_j(x)),
      and return p(x)=sum_q w_q(x)p_q(x) and the conformal decision.
Output: calibrated probabilities, class prediction, and optional unknown label.
```

### 4.4 Complexity and reproducibility

Let $n$ be the number of training rows, $d$ the original feature count, $k$ the selected feature count, $T$ the number of trees, $K$ the cross-fitting folds, and $Q=4$ the number of experts. The dominant training cost is approximately $O(QK T n\\log n)$ for the cross-fitted forests plus $O(QT n\\log n)$ for the final refits; feature selection contributes $O(Qnd)$ for the filter scores. Inference evaluates all four forests and the gate, giving approximately $O(QT\\log n)$ per row for tree traversal, excluding feature extraction. Thus RCCF is intentionally more expensive than a single equal-voting forest. The implementation fixes the random state of the stochastic mutual-information selector, stores SHA-256 hashes for processed splits and external files, and emits per-row probabilities so every reported aggregate can be recomputed.

### 4.5 Statistical analysis and estimand hierarchy

The primary comparison is the paired difference in test Macro-F1 on the same 505 rows for each seed. We report the point estimate, exact McNemar test for paired hard-label disagreements, a seed-level sign-flip test, and a paired bootstrap interval. No p-value is interpreted without the corresponding effect size. For probability quality, Log Loss and Brier are evaluated on the same rows; ECE and MCE use ten fixed confidence bins. Robustness is reported as absolute and relative Macro-F1 degradation under identical perturbation masks. Latency uses the median, 95th, and 99th percentiles over repeated single-row calls, separately for `n_jobs=1` and the library default. These analyses are secondary unless explicitly identified as diagnostics.

### 4.6 Confirmatory versus diagnostic analyses

Locked CIC comparison and paired RCCF/equal-RF tests are confirmatory. Feature stability, calibration, robustness, latency, file-label coverage, open-set rejection, natural-prior sensitivity, and external datasets are diagnostic. This distinction prevents favorable sensitivity results from replacing the primary estimand.

### 4.7 When can the gate change a prediction?

The gate can change a prediction only if expert probability vectors disagree near an argmax boundary and the estimated risks differ enough to move the fused maximum. If descriptors are concentrated and tree errors are correlated, weights approach uniformity; the normalized weight entropy then approaches its maximum, indicating little effective specialization. This is a limiting condition, not a guarantee of improvement. The practical decision criterion is cost-sensitive: a gate must justify its added training and inference cost through a stable downstream benefit.

### 4.8 Gate identifiability, limiting propositions, and cost–benefit criterion

If all expert probabilities are identical, any convex weighting gives the same prediction. If risk scores are equal, RCCF reduces exactly to equal averaging. If the argmax margin exceeds the maximum possible weighted perturbation, the hard label is unchanged. These propositions explain why a sophisticated gate can be statistically inert on a homogeneous benchmark.

## 5. Results

### 5.1 Primary CIC comparison under observed class priors

Under the strict 53,237-flow capped natural-prior protocol, RCCF obtains mean Macro-F1 0.889955, compared with 0.887960 for full-feature equal RF and 0.888870 for chi-square RF. The absolute RCCF--full-RF difference is 0.001995 Macro-F1, while RCCF requires approximately 61.1 s of training and 0.152 s of test prediction versus 0.80 s and 0.041 s for full RF. This is a small observed difference with a clear cost trade-off, not evidence of universal superiority. The natural-prior test support is 292 Bot, 1,593 Brute Force, 3,000 DoS/DDoS, 3,000 Normal, and 101 Web Attack rows. RCCF Macro-F1 is therefore driven by both majority and rare-class behavior; class-level reports remain primary, while accuracy is secondary.

### 5.2 Balanced control CIC comparison

On the strict balanced control protocol, RCCF obtains Macro-F1 0.961807, balanced accuracy 0.961716, log loss 0.124100, Brier score 0.012751, and ECE 0.024483 across the three locked seeds. The equal-voting chi-square forest obtains mean Macro-F1 0.963215 and the full-feature equal RF 0.961000. The paired McNemar and seed-level tests do not support stable superiority. Thus RQ2 and H2 are not supported as stable superiority claims. This protocol is a balanced control and is not interpreted as natural-prevalence performance.

| Model | Macro-F1 | Balanced accuracy | Log loss | Brier | ECE | Train s | Predict s |
|---|---:|---:|---:|---:|---:|---:|---:|
| RCCF | 0.961807 | 0.961716 | 0.124100 | 0.012751 | 0.024483 | 9.130 | 0.119 |
| Equal RF chi-square | 0.963215 | -- | -- | -- | -- | -- | -- |
| ExtraTrees chi-square | 0.948976 | -- | -- | -- | -- | -- | -- |

The observed RCCF point difference is approximately 0.00066 Macro-F1. A gain of this size, with no significant paired evidence and higher cost, is not an algorithmic breakthrough. The result is informative because it exposes a null or near-null mechanism under a controlled protocol.

### 5.3 Repeated stability, feature selection, and strong controls

Across the locked seeds, RCCF wins two comparisons by tie and one by approximately 0.002 Macro-F1; the direction is not stable enough to establish H2. Chi-square is retained as a compact selector for interpretability, not because it is universally optimal. Mutual information and ANOVA are mandatory controls in the feature-quality tables. XGBoost and ExtraTrees remain strong alternative baselines.

### 5.4 Calibration, robustness, and latency

All models use the same held-out test rows and seed-specific perturbation masks. RCCF probabilities are saved for every row, enabling Log Loss, Brier, ECE, MCE, and bootstrap intervals. Shared 1% Gaussian noise and 5% feature masking are evaluated as relative Macro-F1 drops. Single-row P50, P95, and P99 latency is measured with one worker and the library default worker setting; the measurement begins after numerical feature extraction and is not end-to-end gateway latency. RCCF is materially slower than equal RF, especially under multi-worker overhead on small batches. Figure 2 shows the test-set calibration curve, while Figures 3–6 report robustness, latency, coverage, and confusion diagnostics.

Quantitatively, the shared perturbation audit gives mean relative Macro-F1 drops of 43.30% for RCCF and 42.64% for equal RF under 1% Gaussian noise; under 5% feature masking, the corresponding drops are 1.23% and 1.27%. The result supports a narrow statement: RCCF is less sensitive than equal RF in this particular perturbation protocol, but neither model is robust to the chosen continuous-noise magnitude. Single-thread mean P50/P95/P99 latency is 14.62/15.77/16.12 ms for RCCF versus 2.96/3.61/4.18 ms for equal RF; these are classifier-stage measurements, not deployment service-level objectives.

### 5.5 Open-set diagnostics

PortScan, Infiltration, and Heartbleed are reserved as unknown families. Unknown-family AUROC and recall are reported separately by attack family and threshold protocol. These diagnostics do not show that RCCF solves open-set recognition; performance depends on which family is held out and on calibration assumptions.

### 5.6 Independent native-label benchmarks

On NSL-KDD, RCCF reaches Accuracy 0.747960, Balanced Accuracy 0.492837, and Macro-F1 0.514697 (mean over three seeds). R2L and U2R remain minority classes with low recall and F1, despite acceptable aggregate accuracy. On UNSW-NB15, RCCF reaches Accuracy 0.715340, Balanced Accuracy 0.566753, and Macro-F1 0.493310 (mean over three seeds). These are independent native-label results; they are not cross-dataset transfer successes and are not averaged with CIC scores.

| Dataset / model | Accuracy | Balanced accuracy | Macro-F1 |
|---|---:|---:|---:|
| NSL-KDD RCCF | 0.747960 | 0.492837 | 0.514697 |
| UNSW-NB15 RCCF | 0.715340 | 0.566753 | 0.493310 |

The class reports show why aggregate accuracy is insufficient. On NSL-KDD, the seed-2024 R2L and U2R recalls are 0.108 and 0.025, respectively, with F1 scores 0.195 and 0.047. On UNSW-NB15, the same seed has very low F1 for Analysis (0.013), Backdoor (0.064), and DoS (0.277), while Generic reaches 0.981 and Normal 0.805. These minority-class failures are not implementation noise; they are the principal reason that balanced accuracy and class-level reports are retained beside accuracy.

### 5.7 Reviewer-facing synthesis: claim, evidence, and boundary

| Claim | Evidence | Defensible interpretation |
|---|---|---|
| RCCF is more accurate | Small locked point difference; McNemar p=1.0 | Observed difference, not stable superiority |
| Feature selection solves redundancy | Selector rankings and ablations | Protocol choice, not universal improvement |
| RCCF detects unknown attacks | Attack-family-dependent rejection | Open-set ability remains conditional |
| Results transfer across datasets | Native-label external benchmarks | Independent pressure tests only |
| Latency is deployment ready | Post-feature-extraction timing | Classifier-stage offline cost only |

## 6. Discussion

### 6.1 Hard labels and probability quality

Hard-label equality does not imply probability equality. RCCF can move probability mass while retaining the same argmax. Conversely, a small hard-label gain can coexist with worse log loss. For alert ranking and risk scoring, calibration should be reported independently from Macro-F1.

### 6.2 Practical decision matrix

For highest closed-set CIC Macro-F1 under the locked protocol, XGBoost or a tuned equal forest should be considered before RCCF. For an auditable reliability layer, RCCF is useful as an experimental mechanism when its cost is acceptable and its selective output is evaluated. No single model is recommended for all objectives.

### 6.3 What the evidence does and does not identify

The locked CIC experiment identifies a near-null hard-label effect under a balanced, deduplicated population; it does not identify a universally better classifier. The gate can still be useful for probability-aware ranking or selective review, but the present evidence does not show a favorable joint operating point across Macro-F1, calibration, open-set rejection, and latency. The appropriate scientific conclusion is therefore mechanism-level: conditional weighting is identifiable and reproducible, while its practical benefit is dataset- and perturbation-dependent.

## 7. Limitations and Validity Threats

The CIC estimands are conditional on strict deduplicated, capped research populations and cannot be generalized to full-corpus prevalence or production traffic. File-level coverage is not a category-complete temporal holdout and cannot establish full time-out generalization. NSL-KDD and UNSW-NB15 use different native label spaces and are independent benchmarks, not transfer tests. Unknown-family support is small for some attacks. Latency excludes packet capture, flow construction, feature extraction, alert transport, and drift monitoring. Bootstrap intervals quantify test-row resampling uncertainty, not new-network uncertainty.

## 8. Conclusion

RCCF provides a transparent implementation of cross-fitted risk calibration and conformal rejection for forest experts. Under a leakage-controlled, deduplicated CIC protocol, it produces a near-null hard-label difference relative to equal voting, no significant paired advantage, higher computational cost, and mixed probability quality. External native-label benchmarks expose minority-class and calibration failures. The principal contribution is an auditable way to identify these boundaries, not a claim of universal algorithmic superiority.

## Data and code availability

Code, manifests, predictions, figures, and supplementary tables are released at https://github.com/linran-muxue/leakage-controlled-nids-study (release v1.0.2). Raw datasets are not redistributed; source URLs, access metadata, and SHA-256 values are recorded in the repository.

## Funding

No funding statement is asserted until the author confirms that no grant, institutional, scholarship, equipment, or in-kind support contributed to the work.

## Declaration of competing interest

The author should confirm whether any financial or personal relationship could have influenced the work.

## Declaration of Generative AI

Generative AI tools assisted language editing and software drafting. The author is responsible for verifying code, data, citations, and the submitted manuscript.

## CRediT authorship contribution statement

To be completed by the author based on actual contributions.

## References

Breiman L. Random forests. Machine Learning, 2001, 45(1):5–32. DOI:10.1023/A:1010933404324.

Buczak A L, Guven E. A survey of data mining and machine learning methods for cyber security intrusion detection. IEEE Communications Surveys & Tutorials, 2016, 18(2):1153–1176. DOI:10.1109/COMST.2015.2494502.

Chen T, Guestrin C. XGBoost: A scalable tree boosting system. KDD, 2016:785–794. DOI:10.1145/2939672.2939785.

Geng C, Huang S H, Chen S. Recent advances in open set recognition: A survey. IEEE TPAMI, 2021, 43(10):3614–3631. DOI:10.1109/TPAMI.2020.2981604.

Geurts P, Ernst D, Wehenkel L. Extremely randomized trees. Machine Learning, 2006, 63:3–42. DOI:10.1007/s10994-006-6226-1.

Guolou P, Ye X. Open-set intrusion detection with MinMax autoencoder and pseudo extreme value machine. IJCNN, 2022. DOI:10.1109/IJCNN55064.2022.9892858.

Han S, Kim Y, Lee S. Improvement of the classification performance of an intrusion detection model for rare and unknown attack traffic. Electronics, 2021, 10(18):2268. DOI:10.3390/electronics10182268.

Khraisat A, Gondal I, Vamplew P, Kamruzzaman J. Survey of intrusion detection systems: Techniques, datasets and challenges. Cybersecurity, 2019, 2:20. DOI:10.1186/s42400-019-0038-7.

Liu H, Setiono R. Chi2: Feature selection and discretization of numeric attributes. ICTAI, 1995:388–391. DOI:10.1109/TAI.1995.479783.

Moustafa N, Slay J. UNSW-NB15: A comprehensive data set for network intrusion detection systems. MilCIS, 2015:1–6. DOI:10.1109/MilCIS.2015.7348942.

Sharafaldin I, Lashkari A H, Ghorbani A A. Toward generating a new intrusion detection dataset and intrusion traffic characterization. ICISSP, 2018:108–116. DOI:10.5220/0006639801080116.

Tavallaee M, Bagheri E, Lu W, Ghorbani A A. A detailed analysis of the KDD CUP 99 data set. CISDA, 2009:1–6. DOI:10.1109/CISDA.2009.5356528.
