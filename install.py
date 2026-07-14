#!/usr/bin/env python3
"""
Dopagent · Install script / 安装脚本
File system init + dependency verification. Agent-side config via SKILL.md bootstrap.
文件系统初始化 + 依赖验证。Agent 侧配置由 SKILL.md bootstrap 完成。

Usage / 用法:
  python install.py              # Full install / 完整安装
  python install.py --dry-run    # Verify without modifying / 仅验证，不修改
  python install.py --check      # Environment health check / 环境健康检查
  python install.py --uninstall  # Rollback / 回滚
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
            f"Hindsight 未运行（{HINDSIGHT_URL}）。\n"
            f"  启动命令（取决于安装方式）：\n"
            f"  · HanaAgent 自带：在 HanaAgent 设置中检查 Hindsight 状态\n"
            f"  · 独立安装：hindsight-embed start\n"
            f"  验证：curl {HINDSIGHT_URL}/health\n"
            f"  排查：参考 hindsight-docs skill"
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

    print("\n  ⚠️  将修改 {HINDSIGHT_SKILL.name} 以注入 Alaya 管道。原文件备份为 .bak。按 Ctrl+C 跳过。")
    bak = HINDSIGHT_SKILL.with_suffix('.md.bak')
    shutil.copy(HINDSIGHT_SKILL, bak)

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
        return f"⏭  Non-HanaAgent platform, skipped. See PORTING.md. / 非 HanaAgent 平台，跳过。参考 PORTING.md。"
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

    # 替换 SKILL.md 中的 $WORKSPACE 占位符为实际路径（仅在安装目标）
    installed_skill = SKILLS_DIR / "dopagent" / "SKILL.md"
    if installed_skill.exists():
        content = installed_skill.read_text(encoding="utf-8")
        workspace_str = str(WORKSPACE)
        content = content.replace("$WORKSPACE", workspace_str)
        installed_skill.write_text(content, encoding="utf-8")
        synced.append("SKILL.md (路径已注入)")

    return f"已同步 {', '.join(synced)} ✅"


# ═══════════════════════════════════════════════
# 卸载
# ═══════════════════════════════════════════════

# ═══════════════════════════════════════════════
# 环境检查
# ═══════════════════════════════════════════════

def check_environment():
    """Pre-install health check — reports what's missing without modifying anything.
    安装前健康检查——报告缺失项，不修改任何文件。"""
    print("=" * 56)
    print("  Dopagent · Environment Check / 环境检查")
    print("=" * 56)
    print()

    results = []
    all_ok = True

    # 1. Python version
    py_ver = sys.version_info
    if py_ver >= (3, 10):
        results.append(("Python 3.10+", "OK", f"{py_ver.major}.{py_ver.minor}.{py_ver.micro}"))
    else:
        results.append(("Python 3.10+", "FAIL", f"{py_ver.major}.{py_ver.minor} detected, upgrade required"))
        all_ok = False

    # 2. curl
    if shutil.which(CURL):
        results.append(("curl", "OK", shutil.which(CURL)))
    else:
        results.append(("curl", "FAIL", "not found in PATH"))
        all_ok = False

    # 3. Hindsight
    try:
        r = subprocess.run(
            [CURL, "-s", "--connect-timeout", "5", f"{HINDSIGHT_URL}/health"],
            capture_output=True, text=True, timeout=10
        )
        if "healthy" in r.stdout:
            results.append(("Hindsight", "OK", HINDSIGHT_URL))
        else:
            results.append(("Hindsight", "WARN", f"{HINDSIGHT_URL} reachable but unhealthy"))
    except Exception:
        results.append(("Hindsight", "WARN", f"{HINDSIGHT_URL} unreachable — start the daemon before install"))

    # 4. Workspace writable
    if WORKSPACE.exists():
        test_file = WORKSPACE / ".dopagent_test"
        try:
            test_file.write_text("test")
            test_file.unlink()
            results.append(("Workspace", "OK", str(WORKSPACE)))
        except (OSError, PermissionError):
            results.append(("Workspace", "FAIL", f"{WORKSPACE} not writable"))
            all_ok = False
    else:
        try:
            WORKSPACE.mkdir(parents=True, exist_ok=True)
            results.append(("Workspace", "OK", f"{WORKSPACE} (created)"))
        except (OSError, PermissionError):
            results.append(("Workspace", "FAIL", f"{WORKSPACE} cannot be created"))
            all_ok = False

    # 5. Skills directory
    if SKILLS_DIR.exists():
        results.append(("Skills dir", "OK", str(SKILLS_DIR)))
    else:
        results.append(("Skills dir", "WARN", f"{SKILLS_DIR} not found — skill auto-install will skip"))

    # 6. Config
    config_path = PROJECT_ROOT / "config.py"
    if config_path.exists():
        results.append(("config.py", "OK", str(config_path)))
    else:
        results.append(("config.py", "WARN", f"not found — copy config_example.py to config.py first"))

    # Print results
    print(f"  {'Item':20s} {'Status':6s} {'Detail'}")
    print(f"  {'-'*20} {'-'*6} {'-'*30}")
    for item, status, detail in results:
        sym = "✅" if status == "OK" else "⚠️ " if status == "WARN" else "❌"
        print(f"  {item:20s} {sym:6s} {detail}")

    print()
    if all_ok:
        print("  All checks passed. Ready to install: python install.py")
        print("  所有检查通过。可以安装：python install.py")
    else:
        print("  Fix items marked FAIL before installing.")
        print("  修复标记为 FAIL 的项目后重新安装。")
    print()
    return all_ok


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

    if "--check" in sys.argv:
        check_environment()
        return

    dry_run = "--dry-run" in sys.argv
    print("=" * 60)
    print("  Dopagent · Install / 安装")
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
