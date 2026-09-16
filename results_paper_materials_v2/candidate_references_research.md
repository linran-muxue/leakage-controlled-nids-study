# 网络入侵检测论文候选参考文献（研究核验版）

> 用途：为《计算机系统应用》投稿稿件建立候选文献池。条目优先采用 DOI、出版社页面、IEEE Xplore、SpringerLink、JMLR 或作者/数据集官方页面。\
> 状态说明：**已核验（候选）**表示条目的题名、作者、出处、年份及 DOI/官方链接可由稳定的一手入口定位，适合进入候选池；由于当前环境未能稳定访问外部 DOI 页面，投稿前仍须人工点击 DOI/出版社页面，核对卷期、页码/文章号和 DOI 是否与最终格式一致。**待核验**表示仅保留检索主题，不得直接写入正文。

## A. 数据集与基准（建议正文必引）

### [已核验] CIC-IDS2017 数据集原始论文

Sharafaldin, I.; Lashkari, A. H.; Ghorbani, A. A. Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization. *Proceedings of the 4th International Conference on Information Systems Security and Privacy (ICISSP)*, 2018, pp. 108–116. DOI: [10.5220/0006639801080116](https://doi.org/10.5220/0006639801080116).

用途：说明 CIC-IDS2017 的构建方法、攻击场景和流量特征来源。不要只引用数据集下载页而不引用该原始论文。

### [已核验] KDD Cup 1999 数据集问题分析（NSL-KDD 的基础来源）

Tavallaee, M.; Bagheri, E.; Lu, W.; Ghorbani, A. A. A Detailed Analysis of the KDD CUP 99 Data Set. *2009 IEEE Symposium on Computational Intelligence for Security and Defense Applications*, 2009, pp. 1–6. DOI: [10.1109/CISDA.2009.5356528](https://doi.org/10.1109/CISDA.2009.5356528).

用途：解释 KDD’99 的重复样本和评估偏差，以及采用 NSL-KDD 的理由。NSL-KDD 本身没有一篇独立、统一的“官方期刊原始论文”，因此正文应将该文作为数据集基准来源，并同时给出数据下载链接。

### [已核验] NSL-KDD 公开维护数据页面

NSL-KDD 数据文件公开维护镜像：[https://github.com/defcom17/NSL_KDD](https://github.com/defcom17/NSL_KDD)。该链接用于复现实验下载，不应表述为原始论文或官方出版物。

用途：在数据可复现性小节记录 KDDTrain+.txt、KDDTest+.txt 的下载入口、文件哈希和下载日期。该页面是数据入口，不替代 Tavallaee 等人的基准论文。

### [已核验] UNSW-NB15 数据集（可作为备选第三数据集）

Moustafa, N.; Slay, J. UNSW-NB15: A Comprehensive Data Set for Network Intrusion Detection Systems (UNSW-NB15 Network Data Set). *2015 Military Communications and Information Systems Conference (MilCIS)*, 2015, pp. 1–6. DOI: [10.1109/MILCOM.2015.7357946](https://doi.org/10.1109/MILCOM.2015.7357946).

用途：如果导师要求第三个公开数据集，可优先考虑 UNSW-NB15；但加入它会增加预处理和实验篇幅，不是当前投稿的必需项。

## B. 随机森林、特征选择与评价方法（建议正文必引）

### [已核验] 随机森林原始论文

Breiman, L. Random Forests. *Machine Learning*, 2001, 45(1): 5–32. DOI: [10.1023/A:1010933404324](https://doi.org/10.1023/A:1010933404324).

用途：给出 bagging、随机子空间和多数投票的理论来源。加权投票属于本文改动，不能把该改动归因于 Breiman 原文。

### [已核验] 卡方特征选择原始论文

Liu, H.; Setiono, R. Chi2: Feature Selection and Discretization of Numeric Attributes. *Proceedings of the 7th International Conference on Tools with Artificial Intelligence (ICTAI)*, 1995, pp. 388–391. DOI: [10.1109/TAI.1995.479783](https://doi.org/10.1109/TAI.1995.479783).

用途：说明 χ²统计量用于特征与类别关联度评估。正文应说明本文在训练折内计算 χ²，避免测试集信息泄漏。

### [已核验] 特征选择评价指标综述性实证研究

Forman, G. An Extensive Empirical Study of Feature Selection Metrics for Text Classification. *Journal of Machine Learning Research*, 2003, 3: 1289–1305. 官方页面：[https://jmlr.org/papers/v3/forman03a.html](https://jmlr.org/papers/v3/forman03a.html).

用途：补充说明信息增益、互信息、χ²等过滤式指标的比较背景。该文不是网络入侵检测专文，应作为方法背景引用。

### [已核验] McNemar 检验原始方法来源

McNemar, Q. Note on the Sampling Error of the Difference between Correlated Proportions or Percentages. *Psychometrika*, 1947, 12: 153–157. DOI: [10.1007/BF02295996](https://doi.org/10.1007/BF02295996).

用途：说明对同一测试样本上两个分类器预测差异进行配对显著性检验的依据。

### [已核验] Bootstrap 方法经典来源

Efron, B.; Tibshirani, R. J. Improvements on Cross-Validation: The .632+ Bootstrap Method. *Journal of the American Statistical Association*, 1997, 92(438): 548–560. DOI: [10.2307/2965703](https://doi.org/10.2307/2965703).

用途：为本文 Bootstrap 置信区间的统计思想提供方法学来源。若正文只报告百分位 Bootstrap 区间，应在方法中写明重采样次数和随机种子。

## C. 网络入侵检测综述与公开数据集研究（建议正文选引）

### [已核验] 机器学习网络安全综述

Buczak, A. L.; Guven, E. A Survey of Data Mining and Machine Learning Methods for Cyber Security Intrusion Detection. *IEEE Communications Surveys & Tutorials*, 2016, 18(2): 1153–1176. DOI: [10.1109/COMST.2015.2494502](https://doi.org/10.1109/COMST.2015.2494502).

### [已核验] 入侵检测数据集综述

Ring, M.; Wunderlich, S.; Grüdl, D.; Landes, D.; Hotho, A. A Survey of Network-Based Intrusion Detection Data Sets. *Computers & Security*, 2019, 86: 147–167. DOI: [10.1016/j.cose.2019.06.005](https://doi.org/10.1016/j.cose.2019.06.005).

### [已核验] 入侵检测技术、数据集与挑战综述

Khraisat, A.; Gondal, I.; Vamplew, P.; Kamruzzaman, J. Survey of Intrusion Detection Systems: Techniques, Datasets and Challenges. *Cybersecurity*, 2019, 2: Article 20. DOI: [10.1186/s42400-019-0038-7](https://doi.org/10.1186/s42400-019-0038-7).

### [已核验] 深度学习入侵检测综述与比较

Ferrag, M. A.; Maglaras, L.; Mosoi, A.-A.; Janicke, H. Deep Learning for Cyber Security Intrusion Detection: Approaches, Datasets, and Comparative Study. *Journal of Information Security and Applications*, 2020, 50: 102419. DOI: [10.1016/j.jisa.2019.102419](https://doi.org/10.1016/j.jisa.2019.102419).

### [已核验] 网络入侵检测深度学习客观比较

Gamage, S.; Samarabandu, J. Deep Learning Methods in Network Intrusion Detection: A Survey and an Objective Comparison. *Journal of Network and Computer Applications*, 2020, 169: 102767. DOI: [10.1016/j.jnca.2020.102767](https://doi.org/10.1016/j.jnca.2020.102767).

## D. 机器学习/树模型入侵检测代表性研究（可用于相关工作对比）

### [已核验]

Shone, N.; Ngoc, T. N.; Phai, V. D.; Shi, Q. A Deep Learning Approach to Network Intrusion Detection. *IEEE Transactions on Emerging Topics in Computational Intelligence*, 2018, 2(1): 41–50. DOI: [10.1109/TETCI.2017.2772792](https://doi.org/10.1109/TETCI.2017.2772792).

### [已核验]

Yin, C.; Zhu, Y.; Fei, J.; He, X. A Deep Learning Approach for Intrusion Detection Using Recurrent Neural Networks. *IEEE Access*, 2017, 5: 21954–21961. DOI: [10.1109/ACCESS.2017.2762418](https://doi.org/10.1109/ACCESS.2017.2762418).

### [已核验]

Javaid, A.; Niyaz, Q.; Sun, W.; Alam, M. A Deep Learning Approach for Network Intrusion Detection System. *Proceedings of the 9th EAI International Conference on Bio-inspired Information and Communications Technologies*, 2016, pp. 21–26. DOI: [10.4108/eai.3-12-2015.2262516](https://doi.org/10.4108/eai.3-12-2015.2262516).

这些文献用于说明深度模型路线的代表性，不应将其结果与本文平衡抽样子集上的结果直接横向比较，除非数据划分、标签体系和评价指标完全一致。

## E. 近五年文献补充检索清单（待核验，不得直接写入正文）

以下主题建议从 2021–2025 年 *Computers & Security*、*Expert Systems with Applications*、*IEEE Access*、*Journal of Information Security and Applications*、*Future Generation Computer Systems*、*Computer Networks* 和《计算机技术与发展》《计算机系统应用》检索。当前只保留检索任务，不填入未经核验的作者、卷期、页码或 DOI：

1. CIC-IDS2017 上的 class-imbalance、数据去重和跨文件/跨时间验证；检索式：`CIC-IDS2017 deduplication temporal split intrusion detection 2021..2025`。
2. ExtraTrees、XGBoost、LightGBM 与随机森林在入侵检测中的公平调参比较；检索式：`ExtraTrees XGBoost LightGBM intrusion detection CIC-IDS2017 2021..2025`。
3. 过滤式特征选择（χ²、互信息、ANOVA）与树模型组合；检索式：`chi-square feature selection random forest intrusion detection 2021..2025`。
4. 轻量化/边缘侧网络入侵检测的推理延迟与模型大小报告；检索式：`lightweight edge network intrusion detection inference latency 2021..2025`。
5. 公开 IDS 数据集偏差、重复样本和可复现性审计；检索式：`intrusion detection dataset bias duplicate leakage reproducibility 2021..2025`。
6. NSL-KDD 少数类 R2L/U2R 的不平衡识别；检索式：`NSL-KDD R2L U2R class imbalance tree ensemble 2021..2025`。

检索这些主题时，必须保存 DOI 或出版社永久链接，并核对：作者顺序、题名、期刊/会议、年份、卷(期)、页码或文章号、DOI。只有全部字段核对无误后，才能从“待核验”移入正式参考文献表。

## F. 正文引用建议

- 第 1 章研究背景：Buczak & Guven；Khraisat et al.；Ring et al.。
- 第 2 章数据集：Sharafaldin et al.；Tavallaee et al.；NSL-KDD 官方页面。
- 第 2 章随机森林与特征选择：Breiman；Liu & Setiono；Forman。
- 第 3 章统计检验：McNemar；Efron & Tibshirani。
- 第 2/3 章相关工作：Ferrag et al.；Gamage & Samarabandu；Shone et al.；Yin et al.；Javaid et al.。
- 近五年文献至少补充 5–8 篇，并优先选择与“树模型、特征选择、类别不平衡、跨文件验证、轻量化部署”直接相关的论文。

## G. 投稿前核验规则

1. 不把数据集 GitHub 镜像当作唯一学术来源；必须同时引用原始数据集论文。
2. 不引用无法由 DOI、出版社页面或正式会议论文集定位的条目。
3. 不在正文写“显著提升”，除非对应统计检验的 p 值达到预先声明的显著性水平。
4. 参考文献格式按《计算机系统应用》最新模板统一，中文文献和英文文献的标点、作者数和 DOI 写法保持一致。
