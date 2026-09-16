# Open-set unknown attack experiment (v1)

Known training labels are Normal, DoS/DDoS, Brute Force, Web Attack and Bot. PortScan, Infiltration and Heartbleed are held out as unknown attack families and are never used for model fitting or χ² feature selection.

Using a controlled cap of 1,000 rows per known/unknown group, the first run obtained:

- Unknown AUROC: 0.9494
- Unknown recall at the validation-derived threshold: 0.3687
- Known-class Macro-F1 on the known validation subset: 0.8015
- Coverage after rejection: 0.7815

The experiment demonstrates that unknown rejection is a meaningful additional research problem, but the threshold and sampling protocol must be expanded to multiple unknown-family combinations before it can support a strong SCI claim.
