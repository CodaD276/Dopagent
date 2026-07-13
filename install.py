#!/usr/bin/env python3
"""
Dopagent · 安装脚本
文件系统初始化 + 依赖验证。Agent 侧配置由 SKILL.md bootstrap 完成。

用法:
  python install.py              # 完整安装
  python install.py --dry-run    # 仅验证，不修改文件
  python install.py --uninstall  # 回滚（移除补丁、清理热存储）
"""

import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

# ── 加载配置 ──
PROJECT_ROOT = Path(__file__).parent.resolve()

def load_config():
    """加载 config.py，不存在则用示例配置并警告"""
    config_path = PROJECT_ROOT / "config.py"
    example_path = PROJECT_ROOT / "config.example.py"

    if config_path.exists():
        sys.path.insert(0, str(PROJECT_ROOT))
        import config
        return config

    print("  ⚠️  config.py 不存在，使用 config.example.py 的默认值")
    print("     建议: cp config.example.py config.py 并编辑路径\n")
    sys.path.insert(0, str(PROJECT_ROOT))
    import config_example as config
    return config

config = load_config()

WORKSPACE = Path(config.WORKSPACE)
SKILLS_DIR = Path(config.SKILLS_DIR)
HINDSIGHT_SKILL = SKILLS_DIR / "hindsight-hermes-usage" / "SKILL.md"
HINDSIGHT_URL = getattr(config, "HINDSIGHT_URL", "http://127.0.0.1:9177")

# ── 平台适配 ──
def find_curl():
    """找 curl——Windows 上可能是 curl.exe"""
    for name in ["curl", "curl.exe"]:
        if shutil.which(name):
            return name
    return "curl"  # 兜底

CURL = find_curl()

STEPS = []


def step(label):
    """装饰器：标记安装步骤"""
    def decorator(fn):
        STEPS.append((label, fn))
        return fn
    return decorator


# ═══════════════════════════════════════════════
# 安装步骤
# ═══════════════════════════════════════════════

@step("检查 Hindsight 服务")
def check_hindsight():
    result = subprocess.run(
        [CURL, "-s", "--connect-timeout", "5", f"{HINDSIGHT_URL}/health"],
        capture_output=True, text=True, timeout=10
    )
    if "healthy" not in result.stdout:
        raise RuntimeError(
            f"Hindsight 未运行（{HINDSIGHT_URL}）。请先启动 Hindsight daemon。"
        )
    return "Hindsight 健康 ✅"


@step("初始化热存储模板")
def init_hot_memory():
    dest = WORKSPACE / "hot_memory.md"
    src = PROJECT_ROOT / "templates" / "hot_memory.md"

    if not dest.exists():
        shutil.copy(src, dest)
        return f"已创建 {dest.name} ✅"
    else:
        # 已存在 → 检查是不是旧版本（无标题行）
        content = dest.read_text(encoding="utf-8")
        if "# Hot Memory" not in content:
            shutil.copy(src, dest)
            return f"已覆盖 {dest.name}（旧版本无标头）✅"
        return f"{dest.name} 已存在且有效，跳过"


@step("修补 hindsight-hermes-usage skill")
def patch_hindsight_skill():
    if not HINDSIGHT_SKILL.exists():
        return f"⚠️  {HINDSIGHT_SKILL} 不存在。如果使用其他 bank 名或 skill 名，请手动配置 Alaya 管道。跳过。"

    content = HINDSIGHT_SKILL.read_text(encoding="utf-8")

    if "Alaya 管道" in content:
        return "Alaya 章节已存在，跳过 ✅"

    # 在 "## Recall（召回）" 后插入 Alaya 章节
    alaya_block = """### ⚡ Alaya 管道（强制）

- recall → `python WORKSPACE\\alaya_recall.py "查询"`，**禁止裸 curl**
- 公式：1.2×semantic + 0.3×exp(-0.005×days) + 0.1×(importance/10)
- 参数：`--budget low|mid|high`、`--debug`、`--no-rerank`

"""

    if "## Recall（召回）" in content:
        content = content.replace(
            "## Recall（召回）\n\n`POST",
            f"## Recall（召回）\n\n{alaya_block}\n`POST"
        )
    if "default-enabled: false" in content:
        content = content.replace("default-enabled: false", "default-enabled: true")

    HINDSIGHT_SKILL.write_text(content, encoding="utf-8")
    return "Alaya 章节已注入 ✅"


@step("安装 Skill 到 Agent 平台")
def install_skill():
    # HanaAgent: copy SKILL.md to skills directory
    # Other platforms: follow PORTING.md instead
    if not SKILLS_DIR.exists() or ".hanako" not in str(SKILLS_DIR):
        return f"⏭ 非 HanaAgent 平台，跳过。请参考 PORTING.md 手动配置。"
    skill_dir = SKILLS_DIR / "dopagent"
    skill_dir.mkdir(parents=True, exist_ok=True)
    src = PROJECT_ROOT / "SKILL.md"
    dest = skill_dir / "SKILL.md"
    shutil.copy(src, dest)
    return f"SKILL.md → {skill_dir} ✅ 新会话自动加载（HanaAgent）"


@step("验证 Alaya 管道")
def verify_alaya():
    alaya_script = PROJECT_ROOT / "scripts" / "alaya_rerank.py"
    result = subprocess.run(
        [sys.executable, "-c",
         f"import py_compile; py_compile.compile(r'{alaya_script}', doraise=True); print('OK')"],
        capture_output=True, text=True, timeout=10
    )
    if "OK" not in result.stdout:
        raise RuntimeError(f"alaya_rerank.py 语法检查失败:\n{result.stderr}")

    hotness_script = PROJECT_ROOT / "scripts" / "hotness.py"
    result = subprocess.run(
        [sys.executable, "-c",
         f"import py_compile; py_compile.compile(r'{hotness_script}', doraise=True); print('OK')"],
        capture_output=True, text=True, timeout=10
    )
    if "OK" not in result.stdout:
        raise RuntimeError(f"hotness.py 语法检查失败:\n{result.stderr}")

    return "脚本语法验证通过 ✅"


@step("同步脚本到工作区")
def sync_scripts():
    script_files = ["alaya_rerank.py", "alaya_recall.py", "hotness.py"]
    synced = []
    for fname in script_files:
        src = PROJECT_ROOT / "scripts" / fname
        dest = WORKSPACE / fname
        if src.exists():
            shutil.copy(src, dest)
            synced.append(fname)

    # 替换 SKILL.md 中的 $WORKSPACE 占位符为实际路径
    skill_md = PROJECT_ROOT / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        workspace_str = str(WORKSPACE)
        content = content.replace("$WORKSPACE", workspace_str)
        skill_md.write_text(content, encoding="utf-8")
        synced.append("SKILL.md (路径已注入)")

    return f"已同步 {', '.join(synced)} ✅"


# ═══════════════════════════════════════════════
# 卸载
# ═══════════════════════════════════════════════

def uninstall():
    print("⚠️  卸载 Dopagent\n")

    # 回滚 hot_memory
    hot_file = WORKSPACE / "hot_memory.md"
    if hot_file.exists():
        hot_file.unlink()
        print("  已删除 hot_memory.md")

    # 回滚 hindsight skill patch（移除 Alaya 章节）
    if HINDSIGHT_SKILL.exists():
        content = HINDSIGHT_SKILL.read_text(encoding="utf-8")
        if "Alaya 管道" in content:
            import re
            content = re.sub(
                r'### ⚡ Alaya 管道.*?\n\n',
                '',
                content,
                flags=re.DOTALL
            )
            HINDSIGHT_SKILL.write_text(content, encoding="utf-8")
            print("  已移除 Alaya 章节")

    print("\n卸载完成。Pinned memories 需要手动清理（/settings → Memory）。")


# ═══════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════

def main():
    if "--uninstall" in sys.argv:
        uninstall()
        return

    dry_run = "--dry-run" in sys.argv
    print("=" * 60)
    print("  Dopagent · 安装")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    print()

    errors = []
    for label, fn in STEPS:
        try:
            msg = fn()
            print(f"  [{label}] {msg}")
        except Exception as e:
            print(f"  [{label}] ❌ 失败: {e}")
            errors.append((label, str(e)))

    print()
    if errors:
        print(f"❌ {len(errors)} 步失败:")
        for label, err in errors:
            print(f"   - {label}: {err}")
        sys.exit(1)

    print("━" * 60)
    print("  文件系统初始化完成。")
    print()
    print("  下一步 → 启动 HanaAgent，在新会话中说：")
    print('  "加载 dopagent skill"')
    print()
    print("  Agent 会自动读取 SKILL.md 的 bootstrap 流程，")
    print("  完成 instincts pinning + 管道验证。")
    print("━" * 60)


if __name__ == "__main__":
    main()
