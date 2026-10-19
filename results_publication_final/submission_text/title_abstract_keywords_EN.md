## Title

Where Equivalence Ends: Population Construction, Not the Aggregation Rule, Determines Reported Ensemble Gains in Flow-Based Network Intrusion Detection

## Abstract

Reported performance differences between intrusion-detection models are usually attributed to the models, while the population is treated as neutral. We show that this assumption fails systematically. Under one leakage-controlled audit of CIC-IDS2017 we build a three-rung scale ladder - 53,237 flows (20,000 per class), 413,209 (200,000 per class) and the complete deduplicated corpus of 2,429,503 - and repeat a paired comparison between sample-conditional forest fusion (RCCF) and an equal-weight chi-square forest on every rung with ten seeds. On the first two rungs the models are equivalent: -0.000456 and -0.001137 Macro-F1, both inside a pre-specified 0.005 margin. On the third, equivalence breaks: -0.005533 (SD 0.002840; 90% interval [-0.007179, -0.003886]), all ten seeds negative, at 175-fold training cost. The reversal is not the gate: it changes one label in 79,860 predictions, weight entropy is 0.99998, and 99.91% of 23,958 test rows are provably invariant. It is caused by member-quality dispersion that capping removes: the full-feature view trails the chi-square view by 0.021397, and one such member in a four-way average predicts the deficit (0.005349). A constructive follow-up forces the views apart: the gain returns (+0.00736 under quality matching, +0.09768 on the full corpus, ten seeds each). The pattern is not a law of scale: modern corpora reaching 14,250,000 rows differ by 0.000009. Class prior (+0.0725), tuning budget (+0.0078) and deduplication order (+0.0060) exceed the aggregation effect (0.0005). On the full corpus, accuracy stays at 0.9958-0.9993 while Macro-F1 is 0.754007-0.800255. An equivalence claim about ensemble aggregation is therefore a claim about a population.

## Keywords

network intrusion detection; ensemble learning; conditional weighting; population construction; equivalence testing; data leakage; reproducibility

---
abstract 250 words (limit 250); 7 keywords
