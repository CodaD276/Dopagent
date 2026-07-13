"""
Dopagent · User Configuration
Copy to config.py and edit the paths below.
复制为 config.py 并修改以下路径。
"""

# Workspace directory — where hot_memory.md and scripts live
# 工作区目录 — hot_memory.md 和脚本存放位置
WORKSPACE = r"C:\Users\PC\Desktop\OH-WorkSpace"

# HanaAgent skills directory
# HanaAgent skill 目录
SKILLS_DIR = r"C:\Users\PC\.hanako\skills"

# ──────────────────────────────────────
# Below this line usually doesn't need changes
# 以下通常不需要修改
# ──────────────────────────────────────

# Hindsight server URL
# Hindsight 服务地址
HINDSIGHT_URL = "http://127.0.0.1:9177"

# Hindsight bank name
# Hindsight bank 名称
HINDSIGHT_BANK = "hermes"

# Hot memory filename
# 热存储文件名
HOT_MEMORY_FILE = "hot_memory.md"

# Hot memory max size (bytes)
# 热存储大小上限（字节）
HOT_MEMORY_MAX_SIZE = 50 * 1024  # 50 KB

# Time decay coefficient (per hour)
# 0.03 → ~24h to 50%, ~3 days to 10%
# 时间衰减系数（/小时）
# 0.03 → ~24h 到 50%，~3 天到 10%
HOTNESS_LAMBDA = 0.03
