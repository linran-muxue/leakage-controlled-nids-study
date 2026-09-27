"""Second tidy-up pass: leftover fixtures, scratch files and loose run logs.

The first pass quarantined 46 unrelated files; this one covers what it missed.
``tmp_test_unsw/`` still held two three-line UNSW-NB15 fixtures left over from
an integration test and referenced by no code, three scratch files sat at the
repository root (a search-engine dump, a translation helper and a temporary
patch probe), and eleven ``results_*.err`` run logs were tracked where the first
pass had only caught ``results_*.log``.  The loose local drafts that were never
tracked are moved out of the working root at the same time.

Nothing is deleted: tracked files go to ``.quarantine/unrelated_material/``,
local drafts to ``.quarantine/local_material/``, and every move is recorded in
``superseded/unrelated_material_manifest_v2.json`` so it stays auditable.
``check_release_hygiene_v1.py`` fails if any of them is tracked again.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
QUARANTINE = ROOT / ".quarantine" / "unrelated_material"
LOCAL = ROOT / ".quarantine" / "local_material"
MANIFEST = ROOT / "superseded" / "unrelated_material_manifest_v2.json"

# tracked path -> (reason, marker that must appear in the file's first 4 KiB)
TRACKED: dict[str, tuple[str, str]] = {
    "tmp_test_unsw/UNSW-NB15_training-set.csv":
        ("leftover integration-test fixture (three lines), referenced by no code",
         "id,proto,attack_cat"),
    "tmp_test_unsw/UNSW-NB15_testing-set.csv":
        ("leftover integration-test fixture (three lines), referenced by no code",
         "id,proto,attack_cat"),
    "search_result.json": ("search-engine output unrelated to the study", "{"),
    "translate_papers.py": ("scratch translation helper", "import"),
    "tmp_patch_probe.txt": ("temporary patch probe", ""),
}

# local, never-tracked material -> (reason)
LOCAL_FILES: dict[str, str] = {
    "论文草稿_基于卡方特征选择与随机森林的CIC-IDS2017入侵检测研究.docx": "最早期草稿（2026-09-03）",
    "论文投稿草稿_v2_统一无泄漏实验结果.docx": "早期草稿（2026-09-03）",
    "论文完整正文_v3_无泄漏实验统一稿.docx": "早期正文版本（2026-09-04）",
    "论文完整正文_v4_期刊优化稿.docx": "早期正文版本（2026-09-04）",
    "论文完整正文_v5_UNSW类别分析稿.docx": "早期正文版本（2026-09-05）",
    "论文完整正文_v6_数据处理完善稿.docx": "早期正文版本（2026-09-05）",
    "三篇论文中文翻译.docx": "外部论文翻译草稿",
    "CIC-IDS2017入侵检测论文项目任务单.docx": "项目启动任务单",
    "inspect_rollout_calls.py": "会话排查脚本",
    "repair_cross_thread_message.py": "会话修复脚本",
    "repair_current_cross_thread_message.py": "会话修复脚本",
    ".cross-thread-repair.err.log": "会话修复日志",
    ".cross-thread-repair.out.log": "会话修复日志",
    ".cross-thread-repair-v2.err.log": "会话修复日志",
    ".cross-thread-repair-v2.out.log": "会话修复日志",
}


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 22), b""):
            hasher.update(block)
    return hasher.hexdigest()


def tracked_files() -> set[str]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True)
    return set(out.stdout.splitlines())


def main() -> None:
    tracked = tracked_files()
    entries = []
    for relative in list(TRACKED) + sorted(p for p in tracked
                                           if p.startswith("results_") and p.endswith(".err")):
        path = ROOT / relative
        if not path.exists():
            continue
        reason, marker = TRACKED.get(relative, ("loose run log from a finished run", ""))
        if marker and marker not in path.read_bytes()[:4096].decode("utf-8", errors="replace"):
            raise SystemExit(f"{relative}: expected marker {marker!r} is absent; wrong file?")
        name = Path(relative).name
        QUARANTINE.mkdir(parents=True, exist_ok=True)
        target = QUARANTINE / name
        shutil.move(str(path), str(target))
        if relative in tracked:
            subprocess.run(["git", "rm", "--cached", "--quiet", relative], cwd=ROOT, check=True)
        entries.append({"file": relative, "bytes": target.stat().st_size,
                        "sha256": digest(target), "reason": reason,
                        "moved_to": str(target.relative_to(ROOT))})
        print(f"  moved {relative} ({target.stat().st_size:,} bytes) - {reason}")

    for relative, reason in LOCAL_FILES.items():
        path = ROOT / relative
        if not path.exists():
            continue
        LOCAL.mkdir(parents=True, exist_ok=True)
        target = LOCAL / Path(relative).name
        shutil.move(str(path), str(target))
        entries.append({"file": relative, "bytes": target.stat().st_size,
                        "sha256": digest(target), "reason": reason,
                        "moved_to": str(target.relative_to(ROOT))})
        print(f"  moved {relative} ({target.stat().st_size:,} bytes) - {reason}")

    empty = [path for path in (ROOT / "tmp_test_unsw").glob("*")] if (ROOT / "tmp_test_unsw").exists() else []
    if (ROOT / "tmp_test_unsw").exists() and not empty:
        (ROOT / "tmp_test_unsw").rmdir()
        print("  removed the now-empty tmp_test_unsw/ directory")

    MANIFEST.write_text(json.dumps(
        {"note": "Second tidy-up pass; files moved out of the release tree and kept locally.",
         "count": len(entries), "files": entries}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print(f"MANIFEST={MANIFEST.relative_to(ROOT)} count={len(entries)}")


if __name__ == "__main__":
    main()
