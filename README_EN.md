# Dopagent

An AI agent that learns from your corrections — Alaya retrieval rerank, 3-tier memory, correction autolearn, and ADHD-optimized motivation engine.

[简体中文](README.md) · [繁體中文](README_ZH-TW.md)

---

## What This Skill Does

Every time you correct your AI agent, it extracts the lesson, stores it in long-term memory, and surfaces it the next time it's relevant. Not by chance — by a retrieval algorithm that weights semantic similarity, recency, and importance.

Memory alone isn't enough. The agent also needs to know **when to nudge you and when to stay quiet**. Dopagent runs four profiles — creative, execution, exploration, recovery — and switches between them based on your conversational state. Deep in architecture discussion at 2 AM? Creative mode. Said "I don't feel like doing anything" three times in a row? Recovery mode — a single 30-second micro-option, zero pressure.

Everything runs locally. Python stdlib, zero external dependencies. The learning pipeline starts spinning the moment you correct the agent.

## Why "Dopagent"

I have ADHD.

Dopamine is my operating system. A task doesn't get started because it's important — it gets started because it's *interesting*. The boring stuff sinks. The stimulating stuff floats. It's not laziness. It's a different scheduling algorithm.

This framework's motivation engine is built on exactly that logic:

- **Hot storage** = your brain's workbench. Interesting things float to the top. Uninteresting things slowly cool down and sink. They're not deleted — just not in your face right now.
- **Cold storage** = long-term memory. The truly important stuff crystallizes there, uncontaminated by whatever feels fun in the moment.
- **Correction as learning** = when you say "no, it should be X not Y" — that's the strongest learning signal there is. No need to explicitly say "remember this." The correction *is* the "remember this."
- **Four profiles** = ADHD is not one state. Late-night hyperfocus and scattered daytime attention are completely different cognitive modes. The agent has to learn the difference.

Put simply: I gave my agent an external prefrontal cortex. It won't cure ADHD. But it remembers things when I forget, recognizes when I'm stuck and need to pivot, and puts the most important task in front of me when I'm actually ready to do it.

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

**Dev & Test Environment**: Windows 11 · HanaAgent · Hindsight

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
