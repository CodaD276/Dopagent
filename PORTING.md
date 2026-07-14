# Porting Guide / 移植指南

Dopagent's core is platform-agnostic — reasoning templates (Dopagent Check, correction template, Propose) are pure Markdown, and Python scripts use only stdlib. Only **loading mechanism** and **persistent context** need per-platform adaptation.

Dopagent 的核心与平台无关——推理模板（Dopagent Check、纠正模板、Propose）是纯 Markdown，Python 脚本是纯标准库。只有**加载方式**和**常驻上下文机制**需要适配。

**HanaAgent 跨平台**：macOS / Windows / Linux 均支持。skills 目录统一为 `~/.hanako/skills/`，路径格式分别为 `/Users/用户名/.hanako/`（macOS）、`C:\Users\用户名\.hanako\`（Windows）、`/home/用户名/.hanako/`（Linux）。config_example.py 已注释三平台示例。

---

## Compatibility Matrix / 适配矩阵

| Platform | SKILL.md → | Persistent Context | Trigger | Difficulty |
|---|---|---|---|---|
| **Claude Code** | CLAUDE.md | MEMORY.md | Auto-load | ★☆☆☆☆ |
| **Cursor** | `.cursorrules` | `.cursorrules` | Auto-load | ★☆☆☆☆ |
| **GitHub Copilot** | `.github/copilot-instructions.md` | same file | Auto-load | ★☆☆☆☆ |
| **Codex CLI** | `AGENTS.md` | `AGENTS.md` | Auto-load | ★★☆☆☆ |
| **Windsurf** | `.windsurf/rules/` | `.windsurf/rules/` | Auto-load | ★★☆☆☆ |
| **OpenClaw** | `skills/` directory | `MEMORY.md` | skill system | ★★★☆☆ |

---

## Platform Steps / 各平台步骤

### Claude Code (easiest / 最简)

```bash
# Strip YAML frontmatter, append to CLAUDE.md
# 去掉 YAML 头，追加到 CLAUDE.md
sed '/^---$/,/^---$/d' SKILL.md >> CLAUDE.md

# Write instincts to MEMORY.md
# 把 instincts 写进 MEMORY.md
echo "Hindsight recall → python $WORKSPACE/alaya_recall.py" >> MEMORY.md
echo "On correction → fill template → retain imp:8" >> MEMORY.md

python install.py
```

Zero code changes. Claude Code loads CLAUDE.md automatically. MEMORY.md = HanaAgent's pinned memory.

零代码改动。Claude Code 自动加载 CLAUDE.md。MEMORY.md 相当于 HanaAgent 的 pinned memory。

### Cursor

```bash
cp SKILL.md .cursorrules
# Manually delete YAML frontmatter (between --- and ---)
# 手动删掉 YAML 头
# Write instincts at top of file / instincts 写在文件顶部
python install.py
```

### GitHub Copilot

```bash
# Copy body to .github/copilot-instructions.md
# 正文 → .github/copilot-instructions.md
# Write instincts at top / instincts 写在顶部
python install.py
```

### Codex CLI

```bash
# Body → AGENTS.md or .codex/instructions.md
# 正文 → AGENTS.md 或 .codex/instructions.md
# Instincts → same file / 同文件
python install.py
```

Codex doesn't support MANDATORY TRIGGERS. Replace with: "When user says X, Agent judges for itself."

Codex 不支持 MANDATORY TRIGGERS。改为"用户说 X 时 Agent 自行判断"。

### OpenClaw / Hermes Agent

```bash
# Place SKILL.md in skills/ (keep YAML header — OpenClaw is compatible)
# 把 SKILL.md 放入 skills/ 目录（保留 YAML 头——OpenClaw 兼容此格式）
# Instincts → MEMORY.md
python install.py
```

---

## Effort Breakdown / 工作量拆解

```
Total effort = strip YAML header (30s) + move instincts (1min) + python install.py (30s)

All platforms:     reasoning templates → zero changes
All platforms:     Python scripts → zero changes
All platforms:     hot_memory.md → zero changes
Differences:       only ① filename convention + ② persistent context location

总工作量 = 删 YAML 头 (30s) + 迁移 instincts (1min) + python install.py (30s)

所有平台：推理模板 → 零改动
所有平台：Python 脚本 → 零改动
所有平台：hot_memory.md → 零改动
各平台差异：只有 ① 文件名约定 + ② 常驻上下文位置
```

**Core principle**: the framework's brain and muscles are platform-independent. HanaAgent is just the first adapted host.

**核心设计原则**：框架的大脑和肌肉不依赖任何平台。HanaAgent 只是第一个适配的宿主。
