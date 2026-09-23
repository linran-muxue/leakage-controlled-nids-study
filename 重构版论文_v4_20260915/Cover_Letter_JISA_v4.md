# Cover letter

**To:** The Editor-in-Chief, *Journal of Information Security and Applications*

**Subject:** Submission of a research article — "Protocol Sensitivity Dominates Aggregation-Rule Differences in Flow-Based Network Intrusion Detection: A Leakage-Controlled Study of Conditional Ensemble Weighting"

---

Dear Editor,

We submit for your consideration a research article on the evaluation methodology of machine-learning network intrusion detection. The manuscript is original, has not been published elsewhere, and is not under consideration by another journal.

**What the paper asks.** Reported performance differences between intrusion-detection models are highly sensitive to duplicate flows, conflicting labels, feature-selection leakage, class priors and tuning budgets. We test a widely adopted but rarely validated assumption — that fusing several forest experts with sample-specific reliability weights is reliably better than equal voting — under a single leakage-controlled protocol on CIC-IDS2017, with NSL-KDD and UNSW-NB15 as independent native-label benchmarks.

**What we find.** Across ten seeds the conditional mechanism and an equal-weight chi-square forest differ by -0.000456 Macro-F1, with the per-seed sign split five to five. The headline ordering concerns the aggregation rule: its effect is an order of magnitude below the protocol effects we measure (class prior 0.0725, tuning budget 0.0078, deduplication order up to 0.0060). Model-family differences are larger still, and the paper says so - the multilayer perceptron trails the forests by 0.0916 Macro-F1 and extremely randomised trees by 0.0318. Both the seed-level 90% interval and the test-row paired bootstrap interval lie inside pre-specified equivalence margins of 0.005 and 0.01 Macro-F1, so the paper can assert equivalence rather than merely failing to reject a null. Because that population is a capped subset, we also rebuild it 7.8 times larger (413,209 flows) and repeat the ten-seed comparison there: the equivalence holds at both margins, with the point estimate now slightly favouring the control. Removing the cap entirely (1,093,278 deduplicated flows, ten seeds) reproduces the same picture: -0.005533 Macro-F1, 90% interval [-0.007179, -0.003886], TOST 0.005 边界不等价、0.01 边界等价, at a 175x training-cost penalty. A fourth dataset from a different domain (N-BaIoT: consumer-IoT botnet traffic, 180,000 flows) is saturated for every flow-feature classifier, which is precisely the regime our Condition 1 predicts. The four experts disagree on no test row; the learned weights have a normalised entropy of 0.99998; and 99.91% of test rows are *provably* immune to the weighting under an explicit perturbation bound, with a median decision margin 3,469 to 5,038 times that bound. A search over all 108 gate hyper-parameter configurations yields only six distinct validation scores, which excludes insufficient tuning as an explanation [4]. A reverse experiment shows the gain is governed by expert diversity: expert sets with 0.20-0.36% pairwise disagreement gain exactly zero in six of six runs, while deliberately decorrelated sets gain positively in nine of nine.

**Why it fits JISA.** The journal publishes work on the security and dependability of information systems, and a recurring practical question in that space is how much of a published detection improvement survives when the evaluation protocol is controlled. Our contribution is directly usable by other authors: a reusable leakage-controlled protocol, three falsifiable identifiability conditions (one of which becomes a row-wise computable bound), a quantitative map showing that protocol choices exceed aggregation-rule differences by an order of magnitude, while model-family differences remain larger still, and eight concrete reporting recommendations.

**Honesty about the boundary.** The paper does not claim a new state-of-the-art classifier, and it says so explicitly. It also states that the CIC populations are audited research subsets (53,237 of 2,668,729 physically valid records), that file-level experiments are not temporal holdouts, that the external datasets are independent benchmarks rather than transfer tests, and that latency excludes packet capture and feature extraction. The conditional mechanism is shown to be 4.1 times larger and 4.6 times lower in throughput than a single forest while offering no cost-sensitive advantage across false-negative to false-positive cost ratios from 1 to 100.

**Reproducibility.** Code, per-row predictions, audit intermediates, the ten-seed run, the gate search, the identifiability analysis and the expert-diversity suite are released at https://github.com/linran-muxue/leakage-controlled-nids-study (release v1.11.0, tag v1.11.0). Raw datasets are not redistributed; provenance, retrieval dates and SHA-256 checksums are recorded. A 118-test suite runs in continuous integration.

**Declarations.** All DOIs were verified against Crossref. The work used only public datasets and generated no scanning, probing or live attack traffic. Generative AI tools assisted language editing and software drafting; the author verified all code, data, citations and numerical claims. Funding and competing-interest statements are provided in the manuscript.

We would be glad to suggest reviewers on request, and we thank you for considering the manuscript.

Yours sincerely,

*(Author name, affiliation, e-mail and ORCID to be inserted before submission.)*
