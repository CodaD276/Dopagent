## 移植指南

dopagent 的核心与平台无关——推理模板（Dopagent Check、纠正模板、Propose）
是纯 Markdown，Python 脚本是纯标准库。只有 **加载方式** 和 **常驻上下文机制** 需要适配。

## 适配矩阵

| 平台 | SKILL.md 正文 | 常驻上下文 | 触发机制 | 整体难度 |
|---|---|---|---|---|
| **Claude Code** | 改名 CLAUDE.md | MEMORY.md | `/skill` 或 CLAUDE.md 自动加载 | ★☆☆☆☆ |
| **Cursor** | `.cursorrules` | `.cursorrules` | 自动加载 | ★☆☆☆☆ |
| **GitHub Copilot** | `.github/copilot-instructions.md` | 同上 | 自动加载 | ★☆☆☆☆ |
| **Codex CLI** | `AGENTS.md` | `AGENTS.md` | 自动加载 | ★★☆☆☆ |
| **Windsurf** | `.windsurf/rules/` | `.windsurf/rules/` | 自动加载 | ★★☆☆☆ |
| **OpenClaw** | `skills/` 目录 | `MEMORY.md` | skill 系统 | ★★★☆☆ |

## 各平台适配步骤

### Claude Code（最简）

```bash
# 1. 把 SKILL.md 正文（去掉 YAML 头）追加到 CLAUDE.md
cat SKILL.md | sed '/^---$/,/^---$/d' >> CLAUDE.md

# 2. 把 instincts 写进 MEMORY.md
echo "Hindsight recall → python $WORKSPACE/alaya_recall.py" >> MEMORY.md
echo "纠正时 → 填模板 → retain imp:8" >> MEMORY.md

# 3. 安装
python install.py
```

改动量：零代码。Claude Code 自动加载 CLAUDE.md，不需要触发词配置。MEMORY.md = HanaAgent 的 pinned memory。

### Cursor

```bash
# 1. 复制正文到 .cursorrules
cp SKILL.md .cursorrules
# 手动删掉 YAML 头（--- 之间的部分）

# 2. instincts 写进同一文件（顶部）
# 3. python install.py
```

改动量：删 YAML 头。`.cursorrules` 每个会话自动加载。

### GitHub Copilot

```bash
# 1. 正文 → .github/copilot-instructions.md
# 2. instincts → 同文件顶部
# 3. python install.py
```

改动量：删 YAML 头。Copilot 自动读取 `.github/` 下的指令文件。

### Codex CLI

```bash
# 1. 正文 → AGENTS.md 或 .codex/instructions.md
# 2. instincts → 同文件
# 3. python install.py
```

变动量：删 YAML 头 + 调整触发逻辑（Codex 不支持 MANDATORY TRIGGERS，改为"用户说 X 时 Agent 自行判断"）。

### OpenClaw / Hermes Agent

```bash
# 1. 把 SKILL.md 放入 skills/ 目录（保留 YAML 头——OpenClaw 兼容此格式）
# 2. instincts 写进 MEMORY.md
# 3. python install.py
```

变动量：几乎为零。OpenClaw 的 skill 格式与 HanaAgent 高度兼容。

## 移植工作量拆解

```
总工作量 = 删 YAML 头 (30s) + 移动 instincts (1min) + python install.py (30s)

所有平台：     推理模板 → 零改动
所有平台：     Python 脚本 → 零改动
所有平台：     hot_memory.md → 零改动
各平台差异：   只有 ① 文件名约定 + ② 常驻上下文位置
```

**核心设计原则**：框架的大脑和肌肉不依赖任何平台。HanaAgent 只是第一个适配的宿主。
