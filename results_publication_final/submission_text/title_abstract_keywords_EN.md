## Title

Protocol Sensitivity Dominates Aggregation-Rule Differences in Flow-Based Network Intrusion Detection: A Leakage-Controlled Study of Conditional Ensemble Weighting

## Abstract

Reported differences between intrusion-detection models are sensitive to duplicate flows, conflicting labels, feature leakage and class priors. We test a widely adopted but rarely validated assumption: that fusing random-forest experts with sample-specific reliability weights (RCCF) beats equal voting. Under one leakage-controlled protocol we build a 53,237-flow natural-prior population and a 3,365-flow balanced control from CIC-IDS2017, add NSL-KDD, UNSW-NB15 and an IoT corpus, and compare four feature views over ten seeds. The two models differ by -0.000456 Macro-F1 (five up, five down); the seed-level 90% and test-row paired bootstrap intervals both lie inside equivalence margins of 0.005 and 0.01. The four experts disagree on no test row, weight entropy is 0.99998, and class prior and deduplication order move Macro-F1 by +0.0725 and +0.0060. Three identifiability conditions are derived, one a row-wise bound: 99.91% of the 23,958 test rows are provably invariant, with a median decision margin 3,469-5,038 times it. All 108 gate configurations yield six distinct validation scores; the gain is governed by expert diversity (slope 0.0646, r = 0.749). The equivalence reproduces on a population 7.8 times larger but not on the uncapped 2,429,503-flow corpus, where it becomes a small, consistent deficit (-0.005533, all ten seeds) at a 175-fold training cost; the IoT corpus saturates for every model. The mechanism is 4.1 times larger and 4.6 times slower than one forest, without cost-sensitive advantage. We contribute a reusable leakage-controlled protocol, an identifiability boundary and a map separating protocol from aggregation-rule effects; the evidence supports neither superiority nor production readiness.

## Keywords

network intrusion detection; ensemble learning; conditional weighting; data leakage; identifiability; reproducibility; CIC-IDS2017

---
abstract 249 words (limit 250); 7 keywords
