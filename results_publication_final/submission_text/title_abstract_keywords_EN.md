## Title

Protocol Sensitivity Dominates Aggregation-Rule Differences in Flow-Based Network Intrusion Detection: A Leakage-Controlled Study of Conditional Ensemble Weighting

## Abstract

Reported differences between intrusion-detection models are sensitive to duplicate flows, conflicting labels, feature leakage and class priors. We test a widely adopted but rarely validated assumption: that fusing random-forest experts with sample-specific reliability weights (RCCF) beats equal voting. Under one leakage-controlled protocol we build a 53,237-flow natural-prior population and a 3,365-flow balanced control from CIC-IDS2017, add NSL-KDD, UNSW-NB15 and an IoT corpus, and compare four feature views over ten seeds. The two models differ by -0.000456 Macro-F1 (five up, five down); the seed-level 90% and paired bootstrap intervals lie inside the 0.005 and 0.01 equivalence margins. Over the same four experts it changes one label in 79,860 predictions. Experts never disagree; weight entropy is 0.99998; class prior and dedup order move Macro-F1 by +0.0725 and +0.0060. Three identifiability conditions are derived, one a row-wise bound: 99.91% of the 23,958 test rows are provably invariant, with a median margin 3,469-5,038 times it. 108 gate configurations yield six distinct scores; across fifteen configurations the gain co-varies with expert diversity (slope 0.0646, r = 0.749; association, not intervention). The equivalence reproduces on a population 7.8 times larger but not on the uncapped 2,429,503-flow corpus, where it becomes a consistent deficit (-0.005533, all ten seeds) at a 175-fold cost; the IoT corpus saturates. The mechanism is 4.1 times larger and 4.6 times slower (S22), without cost-sensitive advantage. We contribute a leakage-controlled protocol, an identifiability boundary and a map separating protocol from aggregation-rule effects; the evidence supports neither superiority nor production readiness.

## Keywords

network intrusion detection; ensemble learning; conditional weighting; data leakage; identifiability; reproducibility; CIC-IDS2017

---
abstract 247 words (limit 250); 7 keywords
