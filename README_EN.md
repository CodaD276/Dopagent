# Dopagent

An AI agent that learns from your corrections — Alaya retrieval rerank, 3-tier memory, correction autolearn, and ADHD-optimized motivation engine.

[中文版](README.md)

## Prerequisites

| Dependency | Required | Notes |
|---|---|---|
| Python 3.10+ | ✅ | stdlib only — no pip install needed |
| curl | ✅ | HTTP calls to Hindsight API |
| Hindsight daemon | ✅ | Long-term memory backend, default :9177 |
| HanaAgent | ✅ | Skill loading + Pinned Memory + Agent runtime |
| 5 minutes | ✅ | Edit two paths + run one command |

Zero external Python dependencies:

```
scripts/
  alaya_rerank.py   → json, math, datetime, sys      (stdlib only)
  alaya_recall.py   → json, subprocess, tempfile, sys  (stdlib only)
  hotness.py        → json, pathlib, re, datetime, sys (stdlib only)

System: curl (Hindsight HTTP API)
```

## Quick Start

```bash
# 1. Configure — just two paths to edit
cp config_example.py config.py
# Open config.py, set WORKSPACE and SKILLS_DIR

# 2. Install
python install.py

# 3. Bootstrap the Agent
# In a new HanaAgent session, say:
# "load dopagent skill"
#
# The Agent will self-bootstrap — pin instincts, verify the pipeline.
```

## What You Get

```
Three new Agent capabilities:

· Correct the Agent → lessons auto-extracted, stored in long-term memory
· "Do you remember..." → Alaya rerank surfaces the most relevant memories
· Hot storage → short-term high-frequency memory auto-managed (float / sink)

Dopagent motivation engine (opt-in):
· Four profiles — creative / execution / exploration / recovery
· Agent senses your state, decides whether to push, wait, or pivot
```

## Architecture

```
scripts/        Runnable tools
  alaya_rerank.py    Alaya retrieval rerank engine
  alaya_recall.py    recall + rerank in one
  hotness.py         Hot storage scheduler (sort / check / tune)

dopagent/       Motivation engine (design docs)
  profiles/         creative / execution / exploration / recovery
  signals/          correction / engagement / surfacing
  propose.md        Attractive proposal template

templates/      Data templates
  hot_memory.md     Hot storage template (auto-initialized on install)

patches/        Integration patches (auto-applied on install)
```

## Portability

→ [Porting to other platforms](PORTING.md) — Claude Code, Cursor, Copilot, Codex, Windsurf, OpenClaw

## Roadmap

→ [Architecture overview](ROADMAP.md) — completion status and next priorities

## License

MIT

## Acknowledgments

- **Alaya retrieval formula** (1.2×semantic + 0.3×time_decay + 0.1×emotion)  
  From [moeru-ai/airi](https://github.com/moeru-ai/airi) (MIT) —  
  [Alaya memory layer proposal](https://github.com/moeru-ai/airi/issues/879) by @lvy010 (2026-01-05)
- **Dopagent motivation engine** — Instincts concept inspired by [ECC](https://github.com/affaan-m/ECC) (MIT)
- **Symbolic distillation notation** — Adapted from [TencentDB Agent Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory)
- **Hindsight** — Long-term memory backend (MIT)
- **Alaya naming** — Sanskrit *ālaya-vijñāna* (storehouse consciousness), also used by [SecurityRonin/alaya](https://github.com/SecurityRonin/alaya) (MIT)
