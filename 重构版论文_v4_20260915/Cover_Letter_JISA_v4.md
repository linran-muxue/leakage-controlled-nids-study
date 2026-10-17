# Cover letter

**To:** The Editor-in-Chief, *Journal of Information Security and Applications*

JISA has already published work of exactly this kind - Layeghy and Portmann's "Benchmarking the benchmark" (2024) compares synthetic and real-world NIDS datasets - which is why an evaluation-methodology contribution fits the journal's scope.

**Subject:** Submission of a research article — "Where Equivalence Ends: Population Construction, Not the Aggregation Rule, Determines Reported Ensemble Gains in Flow-Based Network Intrusion Detection"

---

Dear Editor,

We submit for your consideration a research article on the evaluation methodology of machine-learning network intrusion detection. The manuscript is original, has not been published elsewhere, and is not under consideration by another journal.

**What the paper asks.** Reported performance differences between intrusion-detection models are highly sensitive to duplicate flows, conflicting labels, feature-selection leakage, class priors and tuning budgets. We test a widely adopted but rarely validated assumption — that fusing several forest experts with sample-specific reliability weights is reliably better than equal voting — under a single leakage-controlled protocol on CIC-IDS2017, with NSL-KDD and UNSW-NB15 as independent native-label benchmarks.

**What we find — a scale ladder, not a single verdict.** We hold the audit, the estimator pair, the feature views, the tuning budget and the ten seeds fixed, and vary one reported dimension only: the per-class cap. At 53,237 flows the conditional mechanism and the equal-weight chi-square forest differ by -0.000456 Macro-F1, with the per-seed sign split five to five; both the seed-level 90% interval and the test-row paired bootstrap interval lie inside pre-specified equivalence margins of 0.005 and 0.01. Raising the cap to 200,000 per class (413,209 flows) reproduces the equivalence: -0.001137, 90% interval [-0.002966, +0.000692]. Removing the cap entirely (2,429,503 deduplicated flows, ten seeds) ends it: -0.005533 Macro-F1, 90% interval [-0.007179, -0.003886], all ten seeds negative, not equivalent at 0.005, at a 175x training-cost penalty. The same estimator pair therefore supports opposite conclusions depending on a preprocessing choice that is rarely reported as a design decision. That ladder is the paper's headline contribution.

**Why the reversal happens.** It is not the gate. Over the same four experts the gate changes one label in 79,860 predictions; normalised weight entropy is 0.99998; and 99.91% of 23,958 test rows are *provably* immune to the weighting under an explicit margin-to-perturbation bound. What changes along the ladder is member-quality dispersion: the full-feature view trails the chi-square view by 0.002068, 0.004249 and 0.021397 on the three rungs, and dividing each gap by the four members predicts 0.000517, 0.001062 and 0.005349 against measured differences of -0.000456, -0.001137 and -0.005533 - within 14% across a 46-fold range. A reverse experiment points the same way: expert sets with 0.20-0.36% pairwise disagreement gain exactly zero in six of six runs, while deliberately decorrelated sets (1.76-6.44%) gain positively in nine of nine (slope 0.0646, r = 0.749). A search over all 108 gate hyper-parameter configurations yields only six distinct validation scores, which excludes insufficient tuning.

**The wider map.** Class prior moves Macro-F1 by +0.0725, tuning budget by +0.0078 and deduplication order by up to +0.0060, against 0.0005 for the aggregation rule; the 200,000-per-class to uncapped step moves the between-arm difference by 0.004396. Model-family differences are larger still, and the paper says so - the multilayer perceptron trails the forests by 0.0916 Macro-F1 and extremely randomised trees by 0.0318. A fourth dataset from a different domain (N-BaIoT: consumer-IoT botnet traffic, 180,000 flows) is saturated for every flow-feature classifier, which is precisely the regime our Condition 1 predicts.

**Why it fits JISA.** The journal publishes work on the security and dependability of information systems, and a recurring practical question in that space is how much of a published detection improvement survives when the evaluation protocol is controlled. Our contribution is directly usable by other authors: a three-rung scale ladder that makes the population dependence of an equivalence claim visible, a reusable leakage-controlled protocol, three falsifiable identifiability conditions (one of which becomes a row-wise computable bound), a quantitative map showing that protocol choices exceed aggregation-rule differences by an order of magnitude while model-family differences remain larger still, and nine concrete reporting recommendations - the first of which is that every headline comparison state its rung.

**Honesty about the boundary.** The paper does not claim a new state-of-the-art classifier, and it says so explicitly. It also states that the CIC populations are audited research subsets (53,237 of 2,668,729 physically valid records), that file-level experiments are not temporal holdouts, that the external datasets are independent benchmarks rather than transfer tests, and that latency excludes packet capture and feature extraction. The conditional mechanism is shown to be 4.1 times larger and 4.6 times lower in throughput than a single forest while offering no cost-sensitive advantage across false-negative to false-positive cost ratios from 1 to 100.

**Reproducibility.** Code, per-row predictions, audit intermediates, the ten-seed run, the gate search, the identifiability analysis and the expert-diversity suite are released at https://github.com/linran-muxue/leakage-controlled-nids-study (release v1.11.0, tag v1.11.0). Raw datasets are not redistributed; provenance, retrieval dates and SHA-256 checksums are recorded. A 138-test suite runs in continuous integration.

**Declarations.** All DOIs were verified against Crossref. The work used only public datasets and generated no scanning, probing or live attack traffic. Generative AI tools assisted language editing and software drafting; the author verified all code, data, citations and numerical claims. Funding and competing-interest statements are provided in the manuscript.

We would be glad to suggest reviewers on request, and we thank you for considering the manuscript.

Yours sincerely,

*(Author name, affiliation, e-mail and ORCID to be inserted before submission.)*
