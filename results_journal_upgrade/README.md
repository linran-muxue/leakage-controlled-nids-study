# 期刊升级实验

本目录记录在不使用测试集选参的前提下进行的升级实验。

- `cv_hyperparameter_results.csv`：训练集内5折分层交叉验证的配置搜索结果
- `selected_hyperparameters.json`：按Macro-F1、Accuracy和复杂度确定的最优配置
- `tuned_test_metrics.csv`：固定配置在独立测试集上的三种子结果

最优配置：k=60、n_estimators=300、max_depth=20、min_samples_leaf=2。

训练集交叉验证Macro-F1为0.9630，独立测试集Accuracy和Macro-F1均为0.9564。该结果相较原固定参数有小幅改善，不应表述为突破性提升。
