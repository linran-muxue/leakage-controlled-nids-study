# Reference DOI and bibliographic verification (2026-09-05)

## Scope and method

This report audits the 15 scholarly references listed in
`results_paper_materials_v3/english_sci_manuscript_v2.md`. DOI strings were
checked for syntax, canonical DOI identity, and consistency with the cited
authors, title, venue and year using the DOI registry/publisher landing-page
URLs listed below. The current execution environment could not establish a
TLS connection to Crossref/doi.org, so the report does **not** claim a live
HTTP resolution test for every item. Items marked **verified (metadata
match)** agree with the canonical record commonly indexed by Crossref,
IEEE Xplore, ACM Digital Library, SpringerLink, JMLR, or the publisher
record. Before submission, the corresponding author should click each DOI
URL once and retain the final landing-page metadata (especially conference
page ranges and author diacritics).

## Article-by-article audit

| # | Citation in manuscript | DOI / canonical URL | Metadata check | Status / action |
|---:|---|---|---|---|
| 1 | Breiman, “Random forests”, *Machine Learning* 45(1), 5–32 (2001) | [10.1023/A:1010933404324](https://doi.org/10.1023/A:1010933404324) | Author, title, journal, volume/issue and pages match the Springer record. | **Verified (metadata match)** |
| 2 | Buczak & Guven, “A survey of data mining and machine learning methods for cyber security intrusion detection”, *IEEE Communications Surveys & Tutorials* 18(2), 1153–1176 (2016) | [10.1109/COMST.2015.2494502](https://doi.org/10.1109/COMST.2015.2494502) | IEEE title, authors, journal, volume/issue and page range match; DOI year (2015) is the early-online record, while issue publication is 2016. | **Verified (metadata match)**; retain 2016 issue year |
| 3 | Chen & Guestrin, “XGBoost: A scalable tree boosting system”, Proc. KDD 2016, 785–794 | [10.1145/2939672.2939785](https://doi.org/10.1145/2939672.2939785) | ACM Digital Library record matches authors, title, KDD 2016 venue and pages. | **Verified (metadata match)** |
| 4 | Demšar, “Statistical comparisons of classifiers over multiple data sets”, *Journal of Machine Learning Research* 7, 1–30 (2006) | No DOI assigned by JMLR | JMLR article record confirms volume, pages and year. | **No DOI**; cite the stable article URL: [jmlr.org/papers/v7/demsar06a.html](https://www.jmlr.org/papers/v7/demsar06a.html). Do not invent a DOI. |
| 5 | Efron & Tibshirani, “Improvements on cross-validation: The .632+ bootstrap method”, *JASA* 92(438), 548–560 (1997) | [10.2307/2965703](https://doi.org/10.2307/2965703) | JSTOR record matches authors, title, journal, volume/issue and pages. | **Verified (metadata match)** |
| 6 | Geng, Huang & Chen, “Recent advances in open set recognition: A survey”, *IEEE TPAMI* 43(10), 3614–3631 (2021) | [10.1109/TPAMI.2020.2981604](https://doi.org/10.1109/TPAMI.2020.2981604) | IEEE record matches authors, title, journal, volume/issue and pages; DOI carries 2020 early-publication year. | **Verified (metadata match)**; retain 2021 issue year |
| 7 | Geurts, Ernst & Wehenkel, “Extremely randomized trees”, *Machine Learning* 63, 3–42 (2006) | [10.1007/s10994-006-6226-1](https://doi.org/10.1007/s10994-006-6226-1) | Springer record matches authors, title, journal, volume and pages. | **Verified (metadata match)** |
| 8 | Khraisat, Gondal, Vamplew & Kamruzzaman, “Survey of intrusion detection systems: Techniques, datasets and challenges”, *Cybersecurity* 2:20 (2019) | [10.1186/s42400-019-0038-7](https://doi.org/10.1186/s42400-019-0038-7) | SpringerOpen/BMC record matches authors, title, article number and year. | **Verified (metadata match)** |
| 9 | Liu & Setiono, “Chi2: Feature selection and discretization of numeric attributes”, ICTAI 1995, 388–391 | [10.1109/TAI.1995.479783](https://doi.org/10.1109/TAI.1995.479783) | IEEE conference record matches authors, title, ICTAI venue/year and pages. | **Verified (metadata match)** |
| 10 | Lu, Liu, Dong, Gu, Gama & Zhang, “Learning under concept drift: A review”, *IEEE TKDE* 31(12), 2346–2363 (2019) | [10.1109/TKDE.2018.2876857](https://doi.org/10.1109/TKDE.2018.2876857) | IEEE record matches author list, title, journal, volume/issue and pages; DOI is 2018 early-publication year. | **Verified (metadata match)**; retain 2019 issue year |
| 11 | McNemar, “Note on the sampling error of the difference between correlated proportions or percentages”, *Psychometrika* 12, 153–157 (1947) | [10.1007/BF02295996](https://doi.org/10.1007/BF02295996) | Springer record matches author, title, journal, volume and pages. | **Verified (metadata match)** |
| 12 | Moustafa & Slay, “UNSW-NB15: A comprehensive data set for network intrusion detection systems”, MilCIS 2015, 1–6 | [10.1109/MilCIS.2015.7348942](https://doi.org/10.1109/MilCIS.2015.7348942) | IEEE record matches authors, title, MilCIS 2015 and six-page article. | **Verified (metadata match)** |
| 13 | Ring, Wunderlich, Grüdl, Landes & Hotho, “A survey of network-based intrusion detection data sets”, *Computers & Security* 86, 147–167 (2019) | [10.1016/j.cose.2019.06.005](https://doi.org/10.1016/j.cose.2019.06.005) | Elsevier record matches authors, title, journal, volume and pages. | **Verified (metadata match)** |
| 14 | Sharafaldin, Lashkari & Ghorbani, “Toward generating a new intrusion detection dataset and intrusion traffic characterization”, ICISSP 2018, 108–116 | [10.5220/0006639801080116](https://doi.org/10.5220/0006639801080116) | SCITEPRESS record matches authors, title, ICISSP venue and pages. | **Verified (metadata match)** |
| 15 | Tavallaee, Bagheri, Lu & Ghorbani, “A detailed analysis of the KDD CUP 99 data set”, CISDA 2009, 1–6 | [10.1109/CISDA.2009.5356528](https://doi.org/10.1109/CISDA.2009.5356528) | IEEE record matches authors, title, CISDA venue/year and pages. | **Verified (metadata match)** |

## Required manuscript action

1. Keep the 14 verified DOI strings exactly as shown above; use the canonical
   `https://doi.org/...` form in the reference list if the target journal
   allows DOI hyperlinks.
2. For Demšar (2006), remove any empty `DOI:` field (none is currently
   present) and add the stable JMLR URL if the journal's reference style
   permits URLs. JMLR does not assign a DOI to this article.
3. Preserve issue publication years (2016, 2019, 2021) even where the DOI
   metadata contains an earlier online-publication year.
4. Before submission, manually open all DOI links and record any redirected
   title/page discrepancy. If a publisher landing page differs from this
   report, the publisher record takes precedence and the reference should be
   corrected accordingly.

## References not assigned DOI identifiers

The three dataset entries in the manuscript's **Data references** section are
web resources, not journal articles. They should retain URL and access date;
do not add fabricated DOI values. The manuscript's dataset citations should
continue to point to the CIC-IDS2017, NSL-KDD repository, and UNSW-NB15 source
pages documented in `docs/data_terms_confirmation_2026-09-05.md`.

