# Dopagent

AI 助手自我学习框架。Alaya 检索重排 + 三层记忆 + 纠正自动学习 + Dopagent 动机引擎。

## 前置条件

| 依赖 | 必需 | 说明 |
|---|---|---|
| Python 3.10+ | ✅ | 全部标准库，无需 pip install |
| curl | ✅ | HTTP 调用 Hindsight API |
| Hindsight daemon | ✅ | 长期记忆存储，默认 :9177 |
| HanaAgent | ✅ | Skill 加载 + Pinned Memory + Agent 宿主 |
| 5 分钟 | ✅ | 改两个路径 + 跑一条命令 |

各脚本的依赖清单：

```
scripts/
  alaya_rerank.py   → json, math, datetime, sys      (stdlib only)
  alaya_recall.py   → json, subprocess, tempfile, sys  (stdlib only)
  hotness.py        → json, pathlib, re, datetime, sys (stdlib only)

系统工具: curl（调用 Hindsight HTTP API）
```

## 快速开始

```bash
# 1. 编辑配置——只需改两个路径
cp config.example.py config.py
# 打开 config.py，设置 WORKSPACE 和 SKILLS_DIR

# 2. 安装
python install.py

# 3. 引导 Agent
# 在 HanaAgent 新会话中说：
# "加载 dopagent skill"
#
# Agent 会自动完成 bootstrap——pin instincts、验证管道。
```

## 包含什么

```
安装后 Agent 获得三项新能力：

· 纠正我 → 自动提取教训，存入长期记忆，下次不再犯
· "你记不记得" → Alaya 公式重排，最相关的记忆排最前面
· 热存储 → 短期高频记忆自动管理，该浮的浮、该沉的沉

Dopagent 动机引擎（可选激活）：
· 四个模式自动切换——创意 / 执行 / 探索 / 恢复
· Agent 感知你的状态，决定该推、该等、还是该换方向
```

## 架构

```
scripts/        可运行工具
  alaya_rerank.py    Alaya 检索重排引擎
  alaya_recall.py    recall + 重排一体
  hotness.py         热存储调度器（sort/check/tune）

dopagent/       动机引擎（设计文档）
  profiles/         创意/执行/探索/恢复 四个模式
  signals/          纠正/粘性/反思 三个检测器
  propose.md        吸引力提议模板

templates/      数据模板
  hot_memory.md     热存储模板（安装时自动初始化）

patches/         集成补丁（安装时自动应用）
```

## 许可

MIT

## 致谢

- **Alaya 检索公式**（1.2×semantic + 0.3×time_decay + 0.1×emotion）  
  源自 [moeru-ai/airi](https://github.com/moeru-ai/airi) 项目（MIT）的  
  [Alaya 记忆层提案](https://github.com/moeru-ai/airi/issues/879)（@lvy010, 2026-01-05）
- **Dopagent 动机引擎** — Instincts 概念启发自 [ECC](https://github.com/affaan-m/ECC)（MIT）
- **符号蒸馏记法** — 参考 [TencentDB Agent Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory) 的符号化压缩思路
- **Hindsight** — 长期记忆后端（MIT）
- **Alaya 命名** — 梵语 *ālaya-vijñāna*（阿赖耶识），亦见于 [SecurityRonin/alaya](https://github.com/SecurityRonin/alaya)（MIT）

→ [移植到其他平台](PORTING.md)
→ [架构快照](ROADMAP.md)
