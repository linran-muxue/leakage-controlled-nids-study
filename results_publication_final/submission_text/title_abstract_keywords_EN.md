## Title

Protocol Sensitivity Dominates Aggregation-Rule Differences in Flow-Based Network Intrusion Detection: A Leakage-Controlled Study of Conditional Ensemble Weighting

## Abstract

Reported differences between intrusion-detection models are sensitive to duplicate flows, conflicting labels, feature leakage and class priors. We test a widely adopted but rarely validated assumption: that fusing random-forest experts with sample-specific reliability weights (RCCF) beats equal voting. We build a 53,237-flow natural-prior population and a 3,365-flow balanced control from CIC-IDS2017, add NSL-KDD, UNSW-NB15 and an IoT corpus, and compare four feature views over ten seeds. The two models differ by -0.000456 Macro-F1 (five up, five down); both intervals lie inside the 0.005 and 0.01 equivalence margins, and over the same four experts the gate changes one label in 79,860 predictions although the experts disagree on 0.15%-0.66% of test rows; weight entropy is 0.99998; class prior and dedup order move Macro-F1 by +0.0725 and +0.0060. Three identifiability conditions are derived, one a row-wise bound: 99.91% of 23,958 test rows are provably invariant, with a median margin 3,469-5,038 times it. Across fifteen configurations the gain co-varies with expert diversity (r = 0.749). The equivalence reproduces on a 7.8-times-larger population but not on the uncapped 2,429,503-flow corpus, where it becomes a consistent deficit (-0.005533) at 175-fold cost. On a 2025 packet corpus with 18 classes the gate gains +0.0063 at eight of sixteen features (all ten seeds), while at the full budget its three views coincide. The mechanism is 4.1 times larger and 4.6 times slower (S22). We contribute a leakage-controlled protocol, an identifiability boundary and a map separating protocol from aggregation-rule effects; the evidence supports neither general superiority nor production readiness.

## Keywords

network intrusion detection; ensemble learning; conditional weighting; data leakage; identifiability; reproducibility; CIC-IDS2017

---
abstract 250 words (limit 250); 7 keywords
