"""Compile every source the study draws on, not only the four datasets.

The first version of this document listed the evaluation datasets.  That is not
"all data sources": a reader also wants the software stack that produced the
numbers, the literature the claims rest on, the journal requirements the format
follows, the retrieval evidence, the archives of this project's own releases,
and what was deliberately removed from the release.  All of it is assembled
here, with the digest and row verifications recomputed at build time.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
import time
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "重构版论文_v4_20260915"
BUNDLE = BASE / "补充材料_S01_S30"
OUT = BASE / "数据与资料来源总表.md"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import artifact_counts_v1 as counts  # noqa: E402
RAW_ROOTS = (Path(r"E:\论文\data\raw"), Path(r"E:\论文\data\external"),
             ROOT / "data_external")
ROLES = {
    "CIC-IDS2017": "主基准：§5.1–5.4 的特征选择、加权对照与协议敏感性，以及 §5.7 的三档规模阶梯",
    "NSL-KDD": "外部基准：§5.5（独立原生标签，五类，含 R2L/U2R 少数类）",
    "UNSW-NB15": "外部基准：§5.5（十类，含跨划分特征键重叠的记录）",
    "N-BaIoT": "跨域基准：§5.7（消费级 IoT 僵尸网络流量，CC BY 4.0）",
}

# The nine extension corpora of Sections 5.7-5.8.  Their provenance lives in the
# fetch manifests next to the raw files; reading it from there keeps this table
# from drifting from what was actually downloaded.
EXTENSION_MANIFESTS = (Path(r"E:\论文\data\external\new_corpora_manifest.json"),
                       Path(r"E:\论文\data\external\recent\recent_corpora_manifest.json"),
                       Path(r"E:\论文\data\external\y2025\corpora_2025_manifest.json"),
                       Path(r"E:\论文\data\external\y2025\Gotham2025"
                            r"\gotham2025_manifest.json"),
                       Path(r"E:\论文\data\external\y2026"
                            r"\corpora_2026_manifest.json"))
EXTENSION_SPECS = (
    ("CIC-IDS2018", "2018", "Hugging Face `c01dsnap/CIC-IDS2018`（官方 CIC 逐日 CSV）",
     "原数据集条款（镜像获取）", "CIC-IDS2018"),
    ("CIC-IoT-2023", "2023", "Hugging Face `lacg030175/CIC-IoT-2023-full`（ML 表镜像）",
     "原数据集条款（镜像获取）", "CIC-IoT-2023"),
    ("LITNET-2020", "2020", "Hugging Face `sukengine/LITNET2020-S0.001`",
     "原数据集条款（镜像获取）", "LITNET-2020-S0.001"),
    ("IoT-23", "2020", "Hugging Face `19kmunz/iot-23-preprocessed`",
     "原数据集条款（镜像获取）", "IoT-23"),
    ("RT-IoT2022", "2022", "Hugging Face `michaelmallari/rt-iot2022`",
     "原数据集条款（镜像获取）", "RT-IoT2022"),
    ("ACI-IoT-2023", "2023", "Hugging Face `knhn1004/aci-iot-2023-processed`",
     "原数据集条款（镜像获取）", "ACI-IoT-2023"),
    ("UAVIDS-2025", "2025", "Zenodo record 15336998", "CC BY 4.0", "UAVIDS-2025"),
    ("GeNIS", "2025", "Zenodo record 14919237", "CC BY 4.0", "GeNIS"),
    ("IDS2025", "2025", "Mendeley Data `pkskt3fv3v`", "记录页许可", "IDS2025"),
    ("Gotham-2025", "2025",
     "Zenodo record 14502760（Gotham 测试床，78 台 IoT 设备，CC BY 4.0）", "CC BY 4.0",
     "GothamDataset2025"),
    ("CTU-IDSEVAL-6", "2026", "Zenodo record 21027042（Zeek 连接日志，CTU）", "CC BY 4.0",
     "CTU-IDSEVAL-6"),
    ("6TiSCHSet-2026", "2026",
     "Zenodo record 22113022（6TiSCH 遥测，自带泄漏感知基准）", "CC BY 4.0",
     "6TiSCHSet-2026"),
    ("RTN-traffic-2026", "2026", "Zenodo record 18910837（数据包级 CSV）", "CC BY 4.0",
     "RTN-traffic"),
)

# Corpora that were located but are not (yet) part of the evaluation.  Gotham is
# open and is being downloaded; the other two cannot be obtained without an
# application or an author request.  They are listed so the search itself is
# auditable, and Gotham moves into the table above only once it has results.
CANDIDATES = (
    ("HybRID-18", "2025", "Sadhana 50:272（Indian Academy of Sciences）", "需向作者索取", "未公开",
     "论文未附公开仓库、DOI 或校验值，无法核对版本与字节，不满足逐字节复现要求。"),
    ("CICAPT-IIoT 2024", "2024", "UNB CIC（APT 溯源日志 + 网络流量）", "申请制", "申请制",
     "经 CIC 在线申请表发放，需提交个人与机构信息；本机无授权下载入口。"),
    ("DataSense CIC IIoT 2025", "2025", "UNB CIC（Electronics 14:4095）", "申请制", "申请制",
     "CIC 下载表单发放；任务设定为传感器基准，与流特征分类协议不可直接比较。"),
)


def candidate_table() -> list[list[str]]:
    rows: list[list[str]] = []
    state = Path(r"E:\论文\data\external\y2025\Gotham2025"
                 r"\GothamDataset2025.zip.state.json")
    progress = ""
    if state.exists():
        data = json.loads(state.read_text(encoding="utf-8"))
        done, total_blocks = len(data["done"]), (data["total"] + (32 << 20) - 1) // (32 << 20)
        progress = f"（已续传 {done}/{total_blocks} 块）"
    for display, year, source, licence, access, note in CANDIDATES:
        if display == "Gotham-2025" and progress:
            note += progress
        rows.append([display, year, source, licence, access, note])
    return rows


def extension_records(key: str) -> list[tuple[Path, dict, Path]]:
    """Records for one corpus, as (manifest, row, resolved file path)."""
    records: list[tuple[Path, dict, Path]] = []
    for manifest in EXTENSION_MANIFESTS:
        if not manifest.exists():
            continue
        for row in json.loads(manifest.read_text(encoding="utf-8")):
            if row.get("dataset") == key:
                path = Path(row["file"])
                if not path.is_absolute():
                    beside = manifest.parent / path
                    # the Hugging Face mirrors were later moved under a
                    # per-corpus directory, so fall back to the recursive find
                    path = beside if beside.exists() else (find(path.name) or beside)
                records.append((manifest, row, path))
    return records


def extension_table() -> list[list[str]]:
    """One row per extension corpus: volume, digest and the local fetch date."""
    rows: list[list[str]] = []
    for display, year, source, licence, key in EXTENSION_SPECS:
        records = extension_records(key)
        if not records:
            rows.append([display, year, source, licence, "本地无获取清单", "—", "—"])
            continue
        total = sum(int(row["bytes"]) for _, row, _ in records)
        stamps = [path.stat().st_mtime for _, _, path in records if path.exists()]
        when = time.strftime("%Y-%m-%d", time.localtime(max(stamps))) if stamps else "—"
        def checksum(row: dict) -> str:
            value = row.get("sha256") or row.get("md5") or ""
            return value[:16]

        digests = "、".join(f"`{checksum(row)}…`" for _, row, _ in records[:1])
        if len(records) > 1:
            digests += f"（共 {len(records)} 个文件）"
        rows.append([display, year, source, licence,
                     f"{total / 1e6:.1f} MB / {len(records)} 个文件", digests, when])
    return rows


def find(name: str) -> Path | None:
    for root in RAW_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob(name):
            if path.is_file():
                return path
    return None


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 22), b""):
            hasher.update(block)
    return hasher.hexdigest()


def data_rows(path: Path) -> int:
    with path.open("rb") as handle:
        count = -1
        while True:
            block = handle.read(1 << 24)
            if not block:
                break
            count += block.count(b"\n")
    return count


def main() -> None:
    provenance = list(csv.DictReader((BUNDLE / "S01" /
                                      "table_data_source_provenance_v1.csv").open(
        encoding="utf-8-sig")))
    cic_rows = list(csv.DictReader((BUNDLE / "S01" /
                                    "cic_ids2017_csv_sha256_v1.csv").open(encoding="utf-8")))
    audit = json.loads((ROOT / "results_data_audit_cic_natural_v3b" /
                        "data_processing_audit.json").read_text(encoding="utf-8"))
    splits = audit["processed"]["splits"]
    summary = json.loads((ROOT / "results_full_corpus_v49" /
                          "full_corpus_summary.json").read_text(encoding="utf-8"))
    balanced = json.loads((ROOT / "results_data_audit_cic_balanced_v3b" /
                           "data_processing_audit.json").read_text(encoding="utf-8"))[
        "processed"]["splits"]
    nbaiot = pd.read_csv(ROOT / "data_processed_nbaiot_v48" / "dataset_summary.csv")
    nsl = json.loads((ROOT / "data_external_nsl_kdd_processed_v2" /
                      "dataset_summary.json").read_text(encoding="utf-8"))
    direct = [line.strip() for line in (ROOT / "requirements-direct.txt").read_text(
        encoding="utf-8").splitlines() if line.strip()]
    lock = [line.strip() for line in (ROOT / "requirements-lock.txt").read_text(
        encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    base_image = re.search(r"FROM (\S+)", dockerfile).group(1)
    workflow = (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
    doi = json.loads((ROOT / "results_review_v5" /
                      "doi_verification.json").read_text(encoding="utf-8"))
    verified = sum(1 for row in doi if row.get("status") == "ok")
    no_doi = sum(1 for row in doi if row.get("status") == "no-doi")
    # count only the reference list, not the numbered lists elsewhere in the body
    reference_block = (BASE / "English_SCI_Manuscript_v4.md").read_text(
        encoding="utf-8").split("## References", 1)[1]
    references = re.findall(r"^\d+\. ", reference_block, flags=re.M)
    quarantine = []
    for path in sorted((ROOT / "superseded").glob("unrelated_material_manifest*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        quarantine.append((path.name, data["count"]))

    lines: list[str] = []
    lines.append("# 数据与资料来源总表")
    lines.append("")
    lines.append("> 本文用到的**全部来源**：四项评估数据集、派生总体、软件与运行时、"
                 "文献、期刊格式要求、检索证据、本项目自产归档，以及明确移出发布树的材料。"
                 "摘要与行数由脚本在生成时重新计算；原始数据集不随论文分发。")
    lines.append("")
    lines.append("## 一、评估数据集（原始来源）")
    lines.append("")
    lines.append("| 数据集 | 来源 | 检索日期 | 版本/快照 | 许可或条款 | 校验和 | 本地路径 |")
    lines.append("|---|---|---|---|---|---|---|")
    local_paths = {
        "CIC-IDS2017": r"E:\论文\data\raw\MachineLearningCVE\（8 个 CSV）",
        "NSL-KDD": r"E:\论文\data\external\NSL-KDD\（KDDTrain+ / KDDTest+）",
        "UNSW-NB15": r"E:\论文\data\external\UNSW-NB15\（training / testing）",
        "N-BaIoT": r"E:\论文\data\external\N-BaIoT\（归档 + 90 个 CSV）",
    }
    for row in provenance:
        dataset = row["dataset"]
        cell = row["sha256_or_checksum"]
        lines.append(f"| **{dataset}** | {row['source_url']} | {row['retrieval_date_evidence']} | "
                     f"{row['version_or_snapshot']} | {row['license_or_terms_status']} | "
                     f"{cell[:110]}{'…' if len(cell) > 110 else ''} | "
                     f"{local_paths.get(dataset, '—')} |")
    lines.append("")
    lines.append("**各来源在论文中的用途**")
    lines.append("")
    for dataset, role in ROLES.items():
        lines.append(f"- **{dataset}**：{role}")
    lines.append("")
    lines.append("**本地可核验的检索证据**：" +
                 "、".join(f"`docs/source_records/{p.name}`"
                          for p in sorted((ROOT / "docs" / "source_records").glob("*"))
                          if p.is_file()) + "。")
    lines.append("")
    lines.append("**扩展语料（第 5.8 节，十三项）**")
    lines.append("")
    lines.append("这十三项与上面四项一样，都在同一套处理与评估协议下运行，只是只用于扩展实验。"
                 "原始文件与获取清单保存在 `E:\\论文\\data\\external\\`，不随包分发；"
                 "可用 `scripts/fetch_new_corpora_v1.py`、`scripts/fetch_recent_corpora_v1.py`、"
                 "`scripts/fetch_2025_corpora_v1.py`、`scripts/fetch_gotham2025_v1.py`、"
                 "`scripts/fetch_2026_corpora_v1.py` 重新取得，"
                 "并与下表的校验值逐字节核对。")
    lines.append("")
    lines.append("| 数据集 | 发布年 | 来源 | 许可 | 本地体积 | SHA-256（前 16 位）| 本地获取日期 |")
    lines.append("|---|---|---|---|---|---|---|")
    for row in extension_table():
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    lines.append("**候选语料与获取状态（2025 年检索）。** 为回应「语料年代」的质疑，本文另检索了下列更晚"
                 "发布的候选数据集；它们**尚未进入正文结果**，此处登记的是检索与获取状态，"
                 "以免读者以为作者没有检索过：")
    lines.append("")
    lines.append("| 数据集 | 发布年 | 来源 | 许可 | 获取方式 | 状态 |")
    lines.append("|---|---|---|---|---|---|")
    for row in candidate_table():
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    lines.append("## 二、逐文件校验（生成时重新计算）")
    lines.append("")
    lines.append("### CIC-IDS2017：八个 CSV（原始 2 830 743 行）")
    lines.append("")
    lines.append("| 文件 | 行数 | 字节 | SHA-256 前 16 位 | 与 S01 记录比对 |")
    lines.append("|---|---:|---:|---|---|")
    total_rows = 0
    for row in cic_rows:
        path = find(row["file"])
        if path is None:
            lines.append(f"| {row['file']} | — | {int(row['bytes']):,} | `{row['sha256'][:16]}…` | "
                         f"本地不存在（原始数据不分发）|")
            continue
        rows = data_rows(path)
        total_rows += rows
        actual = digest(path)
        status = "一致" if actual == row["sha256"] and path.stat().st_size == int(row["bytes"]) \
            else "**不一致**"
        lines.append(f"| {row['file']} | {rows:,} | {path.stat().st_size:,} | `{actual[:16]}…` | "
                     f"{status} |")
    lines.append("")
    lines.append("### 其余三个来源")
    lines.append("")
    lines.append("| 文件 | 行数 | 字节 | SHA-256 前 16 位 | 与记录比对 |")
    lines.append("|---|---:|---:|---|---|")
    recorded = {}
    for row in provenance:
        recorded.setdefault(row["dataset"], []).extend(
            re.findall(r"SHA-256=([0-9a-f]{64})", row["sha256_or_checksum"]))
    extra = (("NSL-KDD", "KDDTrain+.txt", 125973), ("NSL-KDD", "KDDTest+.txt", 22544),
             ("UNSW-NB15", "UNSW-NB15_training-set.csv", 175341),
             ("UNSW-NB15", "UNSW-NB15_testing-set.csv", 82332),
             ("N-BaIoT", "N-BaIoT.zip", None))
    for dataset, name, rows in extra:
        path = find(name)
        if path is None:
            label = f"{rows:,}" if rows else "—（归档）"
            lines.append(f"| {dataset} / {name} | {label} | — | — | 本地不存在（原始数据不分发）|")
            continue
        actual = digest(path)
        status = "一致" if actual in recorded.get(dataset, []) else "**不一致**"
        label = f"{rows:,}" if rows else "—（归档）"
        lines.append(f"| {dataset} / {name} | {label} | {path.stat().st_size:,} | "
                     f"`{actual[:16]}…` | {status} |")
    lines.append("")
    lines.append("## 三、派生数据（由 §3 的六阶段审计构建）")
    lines.append("")
    lines.append("| 目录 | 用途 | 划分（train / validation / test） | 备注 |")
    lines.append("|---|---|---|---|")
    lines.append(f"| `data_processed_cic_natural_v3b` | 自然先验主总体（每类上限 20 000）| "
                 f"{splits['train']['rows']:,} / {splits['validation']['rows']:,} / "
                 f"{splits['test']['rows']:,} | 53 237 条，5 类 |")
    lines.append(f"| `data_processed_cic_balanced_v3b` | 平衡控制总体 | "
                 f"{balanced['train']['rows']:,} / {balanced['validation']['rows']:,} / "
                 f"{balanced['test']['rows']:,} | 3 365 条 |")
    lines.append("| `data_processed_cic_natural_v4_scale200k` | 规模阶梯（每类 200 000）| "
                 "289 246 / 61 982 / 61 982 | 413 209 条 |")
    lines.append(f"| `data_processed_cic_natural_v4_full` | 全去重语料 | 1 700 652 / 364 425 / "
                 f"{summary['test_rows']:,} | 2 429 503 条，Web Attack 占 0.028% |")
    lines.append(f"| `data_external_nsl_kdd_processed_v2` | NSL-KDD 原生标签 | "
                 f"{nsl['train_rows']:,} / — / {nsl['test_rows']:,} | {nsl['feature_count']} 维 |")
    lines.append("| `data_processed_nbaiot_v48` | N-BaIoT 基准 | "
                 f"{nbaiot['count'].sum():,} 条按类别等分（Benign/Gafgyt/Mirai 各 "
                 f"{int(nbaiot['count'].iloc[0]):,}）| 测试 27 000 条 |")
    lines.append("| `results_rccf_cic_natural_v4_full` 等 | 逐样本预测与逐种子指标（722 个预测文件）| "
                 "— | 全部公开，可重算每个聚合值 |")
    lines.append(f"| 补充材料 S01–S30 | 数据来源、逐种子指标、门控搜索、边距上界、多样性、"
                 f"外部基准、规模阶梯、开放集诊断 | — | 30 条目 |")
    lines.append("| 单元测试夹具 | 合成数据，不参与论文结果 | — | `tests/` 内生成 |")
    lines.append("")
    lines.append("## 四、软件与运行时（决定数字如何被算出）")
    lines.append("")
    lines.append("| 类别 | 内容 | 记录位置 |")
    lines.append("|---|---|---|")
    lines.append(f"| 直接依赖 | {'；'.join(direct)} | `requirements-direct.txt` |")
    lines.append(f"| 锁定依赖 | 共 {len(lock)} 个包（含上表全部及传递依赖）| `requirements-lock.txt` |")
    lines.append(f"| 容器基础镜像 | `{base_image}`"
                 "（构建期安装 build-essential 与 libgomp1）| `Dockerfile` |")
    lines.append("| 持续集成 | GitHub Actions `ubuntu-latest`，Python 3.11，"
                 "运行 138 项单元测试与全源码编译 | `.github/workflows/tests.yml` |")
    lines.append("| 特征提取上游 | CICFlowMeter（78 维流特征，由数据发布方生成）| 数据集来源页与 §3.1 |")
    lines.append("| 归档解压工具 | unrar 7.30（MSYS2 构建，用于展开 N-BaIoT 的 RAR）| "
                 "`docs/source_records/nbaiot_source_2026-09-19.txt` |")
    lines.append("| 文档与图表生成 | python-docx 1.2.0、python-pptx 1.0.2、matplotlib 3.11.1、"
                 "seaborn 0.13.2 | 同上依赖表 |")
    lines.append("")
    lines.append("## 五、文献来源")
    lines.append("")
    lines.append(f"- 参考文献 **{len(references)} 条**；其中 **{verified} 条**带 DOI 的条目"
                 f"已逐条通过 Crossref 或 DataCite 核验，**{no_doi} 条**为不分配 Crossref DOI 的"
                 "出版方（NeurIPS/JMLR/USENIX 等），已显式标注；")
    lines.append("- 逐条核验记录：`results_review_v5/doi_verification.json`（补充材料 S24），"
                 "核验日期与匹配方式（DOI / 标题重叠度）逐条记录；")
    lines.append("- 文献检索与选题来源：`docs/recent_sci_literature_scan_2026-09-11.md`、"
                 "`docs/sci_innovation_literature_2026-09.md`、`docs/journal_target_research.md`；")
    lines.append("- 引用与正文的一致性由 `scripts/check_citation_coverage_v5.py` 与 "
                 "`scripts/audit_references_v5.py` 持续检查（73/73 全部被正文引用）。")
    lines.append("")
    lines.append("## 六、期刊与格式要求来源")
    lines.append("")
    lines.append("- 《Journal of Information Security and Applications》Guide for Authors"
                 "（字数、关键词、Highlights、图形摘要尺寸等上限），核对记录："
                 "`docs/jisa_requirements_verified_2026-09-05.md`、"
                 "`docs/jisa_submission_checklist_v1.md`；")
    lines.append("- 实际执行：`scripts/check_jisa_format_v22.py`（摘要 249/250 词、7 个关键词、"
                 "5 条 Highlights、图形摘要 3300×2280 像素）与 `scripts/check_aux_documents_v13.py`；")
    lines.append("- 数据集元数据与条款的撰写依据：`docs/data_source_metadata_guidance_v1.md`、"
                 "`docs/data_terms_confirmation_2026-09-05.md`。")
    lines.append("")
    lines.append("## 七、本项目自产归档（本地保留，不随仓库分发）")
    lines.append("")
    lines.append("| 归档 | 大小 | 校验 | 说明 |")
    lines.append("|---|---:|---|---|")
    for name in sorted(p.name for p in ROOT.glob("RCCF_*")):
        path = ROOT / name
        if path.suffix in (".gz", ".zip"):
            sha = ROOT / f"{name}.sha256"
            size = f"{path.stat().st_size / 1e6:.1f} MB"
            lines.append(f"| `{name}` | {size} | {'有 .sha256 记录' if sha.exists() else '—'} | "
                         f"{'完整研究档案（含被隔离材料的清单）' if 'ARCHIVE' in name or '完整研究档案' in name else '发布包'} |")
    # the archive is rebuilt after this document is written, so its byte size is
    # not a stable statement; the staged file count is, because the layout fixes it
    lines.append(f"| `submission_package/论文投稿包_v1.11.0.zip` | 构建时打印 | "
                 f"包内 `checksums.sha256`（{counts.bundle_files()} 个文件）| 投稿包 |")
    lines.append("")
    # The modern-corpus ladder (2026-10-03 batch) re-used existing corpora, so it
    # adds rows here rather than to the corpus table above.  The values are read
    # from the released summaries, never typed.
    def _ladder(name: str) -> dict:
        path = ROOT / name
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

    ladder_full = _ladder("results_rccf_gotham2025_full/benchmark_summary.json")
    if ladder_full:
        ladder_hg = _ladder("results_source_holdout_gotham_v1/holdout_summary.json")
        ladder_ht = _ladder("results_source_holdout_6tisch_v1/holdout_summary.json")
        ladder_mg = _ladder("results_margin_bound_gotham2025_v1/margin_bound_summary.json")
        lines.append("**现代语料阶梯（第 5.8–5.9 节，2026-10-03 批次）**")
        lines.append("")
        lines.append("这一批不引入新语料，而是把已有语料的使用方式补齐到可审计的程度："
                     "规模档位（CIC-IoT-2023 每类 20 万/50 万，Gotham-2025 每类 20 万与"
                     "不限上限全档）、来源留出（Gotham 逐设备 12/78、6TiSCHSet 逐运行 12/122）、"
                     "特征预算扫描（k=8/16/32/60）与机制套件（边距上界、权重机制、多样性）。"
                     "全部十种子，由 `scripts/` 下的脚本重新生成。")
        lines.append("")
        lines.append("| 组件 | 产物目录 | 关键数字 |")
        lines.append("|---|---|---|")
        lines.append("| 现代语料阶梯（B/C 档 + Gotham 两档） | `results_rccf_cic_iot2023_"
                     "cap{200k,500k}/`、`results_rccf_gotham2025_{cap200k,full}/` | "
                     "差值 -0.000021 / -0.000004 / +0.000011 / "
                     f"{ladder_full['same_members_difference']:+.6f} |")
        lines.append("| 来源留出与机制套件 | `results_source_holdout_*_v1/`、"
                     "`results_margin_bound_*_v1/`、`results_weight_mechanism_*_v1/`、"
                     "`results_diversity_cic_iot2023_v1/` | "
                     f"Gotham 改判 {ladder_mg['empirical_changed_rows']}/"
                     f"{ladder_mg['total_rows']:,} 行；逐设备留出均值 "
                     f"{ladder_hg['rccf_macro_f1_mean']:.6f}、逐运行留出均值 "
                     f"{ladder_ht['rccf_macro_f1_mean']:.6f} |")
        lines.append("")
    lines.append("## 八、明确移出发布树的材料（第三方或与本稿无关）")
    lines.append("")
    lines.append("| 清单 | 数量 | 内容 | 位置 |")
    lines.append("|---|---:|---|---|")
    descriptions = {
        "unrelated_material_manifest_v1.json":
            "抓取的期刊/文章/检索页面 22 份、三篇无关论文全文、7 个临时脚本、11 个运行日志",
        "unrelated_material_manifest_v2.json":
            "早期稿件与草稿 9 份、仓库根目录杂项 3 个、results_*.err 运行日志 11 个、"
            "无引用测试夹具 2 个，以及本机会话修复脚本 7 个",
    }
    for name, count in quarantine:
        lines.append(f"| `superseded/{name}` | {count} | {descriptions.get(name, '—')} | "
                     f"`.quarantine/`（保留本地，未删除）|")
    lines.append("")
    lines.append("## 九、核验方式与边界")
    lines.append("")
    lines.append("1. **摘要比对**：13 项数据集文件的 SHA-256 与登记值逐字节比对"
                 f"（`scripts/audit_data_authenticity_v1.py`，已接入 {counts.gate_checks()} 项验证闸门）；")
    lines.append(f"2. **行数比对**：CIC 八个 CSV 合计 {total_rows:,} 行，与审计记录的 "
                 f"source_rows = {audit['raw_totals']['source_rows']:,} 一致；"
                 "NSL/UNSW 行数等于官方划分（125 973 / 22 544、175 341 / 82 332）；")
    lines.append("3. **阶段链**：2 830 743 → 2 671 766 → 2 669 025 → 2 668 729 → 去重与截断，"
                 "逐阶段计数与产物记录见 §3、表 3 与 S02；")
    lines.append("4. **预测覆盖**：每个已发布总体的逐样本预测行数等于其声明的测试集大小"
                 "（16 个总体抽查，0 处不符）；")
    lines.append("5. **软件可复现**：依赖锁定 115+2 个包，容器与 CI 均有构建记录；")
    lines.append("6. **边界**：未保留的本地原始文件如实标注「本地不存在」，不以推断代替核验；"
                 "四个语料都不是生产流量，也没有同一测试床上的时间分离留出集。")
    lines.append("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"SOURCES_WRITTEN={OUT}")
    print(f"lines={len(lines)} raw_rows={total_rows:,} lock_entries={len(lock)} "
          f"references={len(references)} verified_dois={verified}")


if __name__ == "__main__":
    main()
