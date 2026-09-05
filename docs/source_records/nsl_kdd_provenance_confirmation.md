# NSL-KDD 来源确认

## 结论

本项目本地 `KDDTrain+.txt` 与 `KDDTest+.txt` 的实际下载来源确认采用：

`https://github.com/defcom17/NSL_KDD`

## 证据链

1. 用户此前提供的 PowerShell 下载记录中，`Invoke-WebRequest` 的 URL 明确为：
   - `https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTrain%2B.txt`
   - `https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTest%2B.txt`
2. 本地文件位置为：
   - `E:\论文\data\external\NSL-KDD\KDDTrain+.txt`
   - `E:\论文\data\external\NSL-KDD\KDDTest+.txt`
3. 本地文件哈希与审计记录一致：
   - KDDTrain+ SHA-256：`1b86d2f957b33082081bba410fe129b475efebcc13c9014c3f447c8271aadf95`
   - KDDTest+ SHA-256：`fa46b0935342616aa83b7c2578db355b6a7aaabbc492248172c7a1e8b7ab8f84`
4. 另一张截图显示 `Jehuty4949/NSL_KDD`，但没有本地下载命令或完整文件哈希，不能作为本地文件来源证明。

## 论文写法

正文使用：

> NSL-KDD files were downloaded from the public `defcom17/NSL_KDD` mirror using the raw file URLs recorded in the experiment log. The exact commit was not preserved; therefore, the source is reported as a mirror snapshot and the file SHA-256 values are provided for reproducibility.

不应写成：

- `Jehuty4949/NSL_KDD` 是本实验实际来源；
- NSL-KDD 官方网站；
- 某个未经证实的许可证或具体版本号。
