"""
Dopagent · 用户配置
复制为 config.py 并修改路径。
"""

# 工作区目录——hot_memory.md 和脚本存放位置
WORKSPACE = r"C:\Users\PC\Desktop\OH-WorkSpace"

# HanaAgent skill 目录
SKILLS_DIR = r"C:\Users\PC\.hanako\skills"

# ──────────────────────────────────────
# 以下通常不需要修改
# ──────────────────────────────────────

# Hindsight 服务地址
HINDSIGHT_URL = "http://127.0.0.1:9177"

# Hindsight bank 名称
HINDSIGHT_BANK = "hermes"

# 热存储文件名
HOT_MEMORY_FILE = "hot_memory.md"

# 热存储大小上限（字节）
HOT_MEMORY_MAX_SIZE = 50 * 1024  # 50 KB

# 时间衰减系数（/小时）
# 0.03 → ~24h 到 50%，~3 天到 10%
HOTNESS_LAMBDA = 0.03
