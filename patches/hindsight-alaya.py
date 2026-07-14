#!/usr/bin/env python3
"""
patches/hindsight-alaya.py — 独立补丁脚本
往 hindsight-hermes-usage/SKILL.md 注入 Alaya 管道章节。

用法:
  python patches/hindsight-alaya.py [--dry-run] [--restore]
"""
import sys
import shutil
from pathlib import Path

SKILLS_DIR = Path.home() / ".hanako" / "skills"
HINDSIGHT_SKILL = SKILLS_DIR / "hindsight-hermes-usage" / "SKILL.md"

ALAYA_BLOCK = """### ⚡ Alaya 管道（强制）

- recall → `python $WORKSPACE/alaya_recall.py "查询"`，**禁止裸 curl**
- 公式：1.2×semantic + 0.3×exp(-0.005×days) + 0.1×(importance/10)
- 参数：`--budget low|mid|high`、`--debug`、`--no-rerank`

"""


def apply(dry_run=False):
    if not HINDSIGHT_SKILL.exists():
        print(f"⚠️  {HINDSIGHT_SKILL} 不存在，跳过")
        return

    content = HINDSIGHT_SKILL.read_text(encoding="utf-8")

    if "Alaya 管道" in content:
        print("✅ Alaya 章节已存在")
        return

    bak = HINDSIGHT_SKILL.with_suffix(".md.bak")
    if not dry_run:
        shutil.copy(HINDSIGHT_SKILL, bak)

    if "## Recall（召回）" in content:
        content = content.replace(
            "## Recall（召回）\n\n`POST",
            f"## Recall（召回）\n\n{ALAYA_BLOCK}\n`POST"
        )
    if "default-enabled: false" in content:
        content = content.replace("default-enabled: false", "default-enabled: true")

    if not dry_run:
        HINDSIGHT_SKILL.write_text(content, encoding="utf-8")
        print(f"✅ Alaya 注入完成（备份: {bak}）")
    else:
        print("🔍 dry-run: 检查通过，未修改文件")


def restore():
    bak = HINDSIGHT_SKILL.with_suffix(".md.bak")
    if bak.exists():
        shutil.copy(bak, HINDSIGHT_SKILL)
        bak.unlink()
        print(f"✅ 已从备份恢复")
    else:
        print(f"⚠️  备份文件不存在: {bak}")


if __name__ == "__main__":
    if "--restore" in sys.argv:
        restore()
    else:
        apply("--dry-run" in sys.argv)
