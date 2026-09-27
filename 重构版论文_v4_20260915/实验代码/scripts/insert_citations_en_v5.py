"""Insert numeric in-text citations into the English manuscript (audit finding F1)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "重构版论文_v4_20260915" / "English_SCI_Manuscript_v4.md"

# (unique anchor, text to insert immediately after the anchor, label)
INSERTS = [
    ("CIC-IDS2017, NSL-KDD and UNSW-NB15 dominate this literature",
     " [14-16]", "intro-datasets"),
    ("and thousands of papers report that one model outperforms another on them.",
     " The corresponding research area is surveyed in [22,23].", "intro-surveys"),
    ("Several recent studies show that leakage and preprocessing order alone can reverse conclusions in intrusion detection.",
     " [18-20]", "intro-leakage"),
    ("CIC-IDS2017 was released by Sharafaldin et al. in 2018",
     " [14]", "2.1-cic"),
    ("NSL-KDD is a refined version of KDD CUP 99 with five native labels (Normal, DoS, Probe, R2L, U2R).",
     " [15]", "2.1-nsl"),
    ("UNSW-NB15, released by Moustafa and Slay in 2015, provides official training and testing files with nine attack categories.",
     " [16]", "2.1-unsw"),
    ("Several structural defects are documented.",
     " [17]", "2.1-defects"),
    ("Engelen and Timmerman, and Liu et al., show that preprocessing order and splitting choices alone can materially change reported performance.",
     " [18,19]", "2.1-order"),
    ("These findings motivate H3: if protocol choices change conclusions, the protocol itself must become a reported and tested object.",
     " This position is part of a wider methodological critique of machine learning in security [20,21,24].", "2.1-critique"),
    ("The chi-square statistic measures dependence between a discretised feature and the label",
     " [12]", "2.2-chi2"),
    ("mutual information (MI) captures non-linear dependence, and analysis of variance (ANOVA) compares between-class with within-class variance.",
     " [13]", "2.2-mi-anova"),
    ("Such leakage is common and hard to detect from a methods paragraph.",
     " [20]", "2.2-leakage"),
    ("Breiman's random forest combines bootstrapped trees through equal voting or probability averaging",
     " [1,2]", "2.3-rf"),
    ("Implementations in the literature include validation-accuracy tree weighting, out-of-bag error weighting, meta-learners that predict sample-dependent weights, confidence-based weighting after probability calibration, and uncertainty-driven weighting in deep ensembles.",
     " [8-11,29]", "2.3-implementations"),
    ("Recent open-set work adds extreme-value theory, prototype learning or autoencoder reconstruction error to construct rejection mechanisms.",
     " [25,26,40,41]", "2.3-openset"),
    ("For alert ranking, risk scoring and human-in-the-loop triage, Log Loss, the Brier score and expected calibration error (ECE) matter more.",
     " [27]", "2.4-metrics"),
    ("Two models with identical hard labels can differ substantially in calibration, so discriminative and probabilistic metrics must be reported separately.",
     " [28,29]", "2.4-calibration"),
    ("Three public datasets are used, all obtained from official or public sources.",
     " [14-16]", "3.1-datasets"),
    ("and a Mondrian (class-conditional) conformal predictor provides an optional `unknown` output at significance level alpha = 0.1.",
     " [30-33]", "3.4-conformal"),
    ("(i) exact McNemar tests for hard-label disagreement",
     " [34]", "3.5-mcnemar"),
    ("(ii) a seed-level sign-flip test for directional stability",
     " [35,36]", "3.5-signflip"),
    ("(iii) stratified paired bootstrap for interval estimation of Macro-F1 differences",
     " [38]", "3.5-bootstrap"),
    ("(iv) Holm correction for multiple comparisons",
     " [37]", "3.5-holm"),
    ("(v) equivalence testing (TOST), which compares the paired bootstrap 90% interval",
     " [39]", "3.5-tost"),
    ("an equal-weight random forest (RF) on each view, extremely randomised trees, XGBoost and a multilayer perceptron (MLP).",
     " Tree-ensemble and boosting references are [1-8].", "4.1-learners"),
    ("Fused probabilities are then temperature-scaled on the validation partition",
     " [27]", "4.2-temperature"),
    ("The reported timings are single-machine measurements and are not portability claims.",
     " The software stack is documented in [42-45].", "4.4-software"),
    ("without controlling duplicates, transform leakage, class priors and tuning budgets, an observed \"weighting gain\" has at least four competing explanations",
     " [18-20]", "6.2-attribution"),
    ("so that the evaluation protocol itself becomes a verifiable object.",
     " The recommendations extend those of [20].", "7-recommendations"),
]


def main() -> None:
    text = MD.read_text(encoding="utf-8")
    applied, skipped = 0, []
    for anchor, insert, label in INSERTS:
        if anchor not in text:
            skipped.append(label)
            continue
        if insert.strip() and insert.strip() in text[max(0, text.find(anchor) - 5):text.find(anchor) + len(anchor) + 40]:
            continue
        text = text.replace(anchor, anchor + insert, 1)
        applied += 1
    MD.write_text(text, encoding="utf-8")
    print(f"EN_CITATIONS_APPLIED={applied}")
    if skipped:
        print("anchors not found:", skipped)


if __name__ == "__main__":
    main()
