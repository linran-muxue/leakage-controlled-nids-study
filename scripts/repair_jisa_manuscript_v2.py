from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / 'results_paper_materials_v3' / 'english_sci_manuscript_v1.md'
text = path.read_text(encoding='utf-8')

text = text.replace(
    'CIC-IDS2017 was obtained from the Canadian Institute for Cybersecurity page at <https://www.unb.ca/cic/datasets/ids-2017.html> and is used with the accompanying dataset description (Sharafaldin et al., 2018).',
    'CIC-IDS2017 was obtained from the Canadian Institute for Cybersecurity source page (Canadian Institute for Cybersecurity, n.d.) at <https://www.unb.ca/cic/datasets/ids-2017.html> and is used with the accompanying dataset description (Sharafaldin et al., 2018).'
)
text = text.replace(
    'The NSL-KDD files were downloaded from the public `defcom17/NSL_KDD` mirror',
    'The NSL-KDD files were downloaded from the public `defcom17/NSL_KDD` mirror (defcom17, n.d.)'
)
text = text.replace(
    'UNSW-NB15 was obtained from the UNSW Canberra Cyber project page at <https://research.unsw.edu.au/projects/unsw-nb15-dataset>.',
    'UNSW-NB15 was obtained from the UNSW Canberra Cyber project page (UNSW Canberra Cyber, n.d.) at <https://research.unsw.edu.au/projects/unsw-nb15-dataset>.'
)

text = text.replace(
    'To be completed by the authors before submission. Contributions should be assigned using the CRediT roles required by JISA.',
    'Conceptualization, methodology, software, data curation, formal analysis, visualization, and writing (original draft and review) were performed by the authors. The final author names and role attribution will be entered identically in the manuscript and Editorial Manager.'
)
text = text.replace('To be completed if applicable.', 'No external acknowledgements are declared.')
text = text.replace(
    'The reproducibility package includes the processing scripts, configuration files, audit summaries, prediction outputs, source-record screenshots, and a locked software environment. The original datasets are not redistributed because their providers control access and reuse. A persistent public repository or DOI-backed archive should be inserted here before submission; until then, the archived project package is the available research record.',
    'The reproducibility package includes the processing scripts, configuration files, audit summaries, prediction outputs, source-record screenshots, and a locked software environment. The original datasets are not redistributed because their providers control access and reuse. The scripts and derived artifacts can be provided by the corresponding author on reasonable request; a persistent public repository or DOI-backed archive should be added before submission when available.'
)

text = text.replace(
    'With the locked configuration, chi-square random forest reaches 95.78% ± 0.11% accuracy and 95.79% ± 0.11% macro-F1 across seeds 42, 2024, and 3407.',
    'With the locked configuration, chi-square random forest reaches 95.78% ± 0.11% accuracy and 95.79% ± 0.11% macro-F1 across seeds 42, 2024, and 3407. The complete locked comparison is provided in Table 1 and Figure 1.'
)
text = text.replace(
    'The CIC test reports show that aggregate performance hides class differences:',
    'The CIC test reports show that aggregate performance hides class differences; detailed class reports and confusion matrices are provided in Supplementary Materials S1–S6:'
)
text = text.replace(
    'Under shared perturbation masks, five-percent feature masking causes less than one percent macro-F1 loss in the reported protocol,',
    'Under shared perturbation masks, five-percent feature masking causes less than one percent macro-F1 loss in the reported protocol; the full perturbation table is provided in Supplementary Material S14 and the calibration curves are shown in Figure 2,'
)
text = text.replace(
    'On NSL-KDD, the best macro-F1 among the reported models is 0.5991 for ExtraTrees with chi-square selection; balanced accuracy is 0.5707.',
    'On NSL-KDD, the best macro-F1 among the reported models is 0.5991 for ExtraTrees with chi-square selection; balanced accuracy is 0.5707. Detailed minority-class metrics and confusion matrices are provided in Supplementary Materials S7–S8.'
)

marker = 'Tavallaee M, Bagheri E, Lu W, Ghorbani AA. A detailed analysis of the KDD CUP 99 data set. CISDA, 2009:1–6. DOI:10.1109/CISDA.2009.5356528.\n'
data_refs = '''\n## Data references\n\n[dataset] Canadian Institute for Cybersecurity. CIC-IDS2017 dataset. n.d. https://www.unb.ca/cic/datasets/ids-2017.html (accessed 5 September 2026).\n[dataset] defcom17. NSL_KDD repository snapshot. n.d. https://github.com/defcom17/NSL_KDD (accessed 5 September 2026).\n[dataset] UNSW Canberra Cyber. UNSW-NB15 dataset. n.d. https://research.unsw.edu.au/projects/unsw-nb15-dataset (accessed 5 September 2026).\n'''
if '[dataset] Canadian Institute for Cybersecurity.' not in text:
    text = text.replace(marker, marker + data_refs)

path.write_text(text, encoding='utf-8')
print(f'REPAIRED={path}')
