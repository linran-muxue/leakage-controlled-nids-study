# 来源截图核验记录（2026-09-05）

## CIC-IDS2017

- 文件：`cic_ids2017_source_2026-09-05.png`
- 页面标题可见：`Intrusion detection evaluation dataset (CIC-IDS2017)`。
- 页面可见内容说明该数据集包含正常流量、常见攻击，以及基于 CICFlowMeter 生成的标注流量 CSV。
- 截图未显示明确的 SPDX 许可证、数字版本号或完整使用条款。

## NSL-KDD

- 文件：`nsl_kdd_mirror_2026-09-05.png`
- 截图显示的仓库是 `Jehuty4949/NSL_KDD`，分支为 `master`，页面显示 `1 Commit`，可见提交短标识为 `27bbbdf`。
- 截图未显示完整 commit SHA，也未显示 LICENSE 文件或明确许可证文本。
- 重要一致性问题：截图显示 `Jehuty4949/NSL_KDD`，但项目下载记录和此前下载命令使用 `defcom17/NSL_KDD`。当前元数据仍以实际下载来源 `defcom17/NSL_KDD` 为准；该截图只能作为“同名公开镜像存在”的旁证，不能作为本地文件来源证明。由于截图未显示完整 commit，当前记录为 mirror snapshot，不声称精确 commit。
- 来源确认依据：用户此前提供的 PowerShell 下载记录明确调用 `https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTrain%2B.txt` 和对应的 `KDDTest%2B.txt`。因此本项目将 `defcom17/NSL_KDD` 作为实际下载来源；截图中的 `Jehuty4949/NSL_KDD` 不改变该结论。

## UNSW-NB15

- 文件：`unsw_nb15_source_2026-09-05.png`
- 页面标题可见：`The UNSW-NB15 Dataset`。
- 页面说明源文件可下载，并指出数据由 IXIA PerfectStorm、tcpdump、Argus 和 Bro-IDS 等工具生成；页面列出九类攻击、49个特征和官方训练/测试划分（175,341 / 82,332）。
- 页面红色提示明确要求学术/公开使用者引用相关论文。
- 截图未显示明确的 SPDX 许可证或数字版本号；正文应写“按项目页面说明使用并引用原始论文”，不要自行填写 CC-BY/MIT 等许可证。
