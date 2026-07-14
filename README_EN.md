## What This Skill Does

Your AI agent automatically extracts lessons from every correction and stores them in long-term memory. Next time a similar scenario comes up, the most relevant experience surfaces — not by luck, by a retrieval algorithm.

Memory alone isn't enough. The agent also needs to know **when to nudge you and when to stay quiet**. Dopagent runs four profiles — creative, execution, exploration, recovery — switching based on your state.

Everything runs locally. Python stdlib, zero external dependencies.

> ⚠️ Dopagent Check is an LLM reasoning step — the agent makes a best effort each turn, but there is no program-level enforcement. The framework's reliability comes from the correction loop (correct→retain→Alaya recall). The motivation engine is an assistive layer.


## Quick Start

```bash
# 1. Configure — just two paths to edit
cp config_example.py config.py
# Open config.py, set WORKSPACE and SKILLS_DIR

# 2. Install
python install.py

# 3. Bootstrap the Agent
# In a HanaAgent chat, type:
# "load dopagent skill"
#
# (HanaAgent loads skills via chat commands —
#  it will read SKILL.md and run the bootstrap.)
```

### Verify Installation

30-second smoke test:

```
1. Tell the Agent something obviously wrong, e.g. "Toronto is in Quebec"
2. After it corrects you, say "do you remember what I just corrected?"
3. The Agent should recall the correction
```

Correction → memory → retrieval — one loop, 30 seconds.

## 5-Minute Walkthrough

After install, try this — see all four circuits in action:

```
👤 User:   "Toronto is in Ontario, not Quebec."
           (← a correction, but you didn't say "remember this")

🤖 Agent:  Detects correction signal → auto-fills template:

           Correction Template:
           · I was wrong: confused province
           · Correct: Toronto = Ontario
           · Next time: verify Canadian geography first

           → retain to Hindsight (imp:8)
           → add to Hot Storage [correction]
           → hotness.py sort → floats to ACTIVE top

👤 User:   (3 days later) "Did I correct you about geography before?"

🤖 Agent:  python alaya_recall.py "geography correction"
           → Alaya formula: semantic + time decay + importance
           → "Toronto in Ontario" ranks #1
           → "Yes, on July 13 you corrected me about Toronto."
```

Four circuits, one flow: correction → storage → retrieval → hot storage lifecycle.

---

## Prerequisites

| Dependency | Required | Notes |
|---|---|---|
| Python 3.10+ | ✅ | stdlib only — no pip install |
| curl | ✅ | HTTP calls to Hindsight API |
| Hindsight daemon | ✅ | Long-term memory backend, default :9177 |
| Agent Platform | 🟨 | HanaAgent native. Others via [Porting Guide](PORTING.md) |
| 5 minutes | ✅ | Edit two paths + run one command |

```
scripts/
  alaya_rerank.py   → json, math, datetime, sys      (stdlib only)
  alaya_recall.py   → json, subprocess, tempfile, sys  (stdlib only)
  hotness.py        → json, pathlib, re, datetime, sys (stdlib only)

System: curl (Hindsight HTTP API)
```

**Dev & Test Environment**: Windows 11 · HanaAgent · Hindsight

## Architecture Layers / 架构层次

After installation you're at **L1**. L0-L3 run automatically. L4-L5 activate when enough data accumulates.

| Layer | Name | Status | Trigger |
|---|---|---|---|
| **L0** | Infrastructure · Alaya + Hot/Cold Storage | ✅ Auto | Runs on install |
| **L1** | Bootstrap · install.py + 6-platform porting | ✅ Auto | `python install.py` |
| **L2** | Dopagent Check · State sensing + λ monitor | ✅ Auto | Every response |
| **L3** | Execution · 4 profiles + Propose | ✅ Auto | Triggered by L2 |
| **L4** | Pattern Extraction · Lesson → Generalization | 🚧 Needs data | Auto after 50+ corrections |
| **L5** | Meta-Learning · Symbolic Distill + Audit | 📐 Spec ready | Auto after L4 output |

L4-L5 are not missing features — the framework is in place. Data accumulates through daily use. No manual trigger needed.

**Optional** (manual opt-in):

| Feature | Description | How to enable |
|---|---|---|
| Correction Verify | Cheap LLM double-checks extracted lessons | Say "开启纠正验证" / "enable correction verify" |
| Engagement Signal | Detects sustained interest in a topic | Say "开启 engagement 检测" / "enable engagement detection" |

→ [Full topology + completion status](ROADMAP.md)

---

## Why "Dopagent"

I have ADHD. Dopamine is my operating system. A task doesn't get started because it's important — it gets started because it's *interesting*. The boring stuff sinks. The stimulating stuff floats.

- **Hot storage** = your brain's workbench. Interesting floats; uninteresting sinks
- **Cold storage** = long-term memory. Important stays; fun-of-the-moment doesn't pollute it
- **Correction as learning** = "No, it should be X not Y" — the strongest learning signal
- **Four profiles** = ADHD is not one state. Late-night hyperfocus ≠ scattered daytime attention

Put simply: an external prefrontal cortex for your AI assistant.

## Architecture

```mermaid
graph LR
    U["👤 User"] <-->|correct · query · state| A["🤖 Agent"]

    A -->|"wrong"| CT["📝 Correction<br/>Template"]
    CT -->|"retain imp:8"| H["❄️ Hindsight"]
    CT -->|"add"| HOT["🔥 Hot Storage"]

    A -->|"remember?"| AL["🔍 Alaya Pipeline<br/>1.2×sem+0.3×decay+0.1×imp"]
    AL -->|"query"| H
    AL -->|"rerank"| A

    A -->|"each turn"| PM["🧠 Profile Matcher<br/>creative/execution/explore/recover"]
    PM --> DEC["Push · Wait · Switch"]
    DEC -.->|"feedback"| A

    HS["⚙️ Hotness<br/>Scheduler"] -->|sort/check| HOT
    HOT -->|"promotion"| WARM["🌤️ Warm"] -->|"consolidation"| H

    A --> RETRO["📋 Session Retro"]
    RETRO -->|"retain imp:7"| H
    RETRO -->|"insight"| HOT

    style H fill:#4c1d95,stroke:#a78bfa,color:#e2e8f0
    style HOT fill:#b45309,stroke:#fbbf24,color:#fef3c7
    style WARM fill:#c2410c,stroke:#fb923c,color:#fed7aa
    style CT fill:#9f1239,stroke:#fb7185,color:#fecdd3
    style AL fill:#065f46,stroke:#34d399,color:#d1fae5
    style PM fill:#1e3a5f,stroke:#60a5fa,color:#bfdbfe
```

→ [Porting to other platforms](PORTING.md)
→ [Architecture overview](ROADMAP.md)

## Glossary

| Term | One-liner |
|---|---|
| Hindsight | Local long-term memory service (port 9177). Stores corrections and mental models |
| Alaya | Retrieval rerank script — ranks memories by semantic similarity + time decay + importance |
| Hot Storage | `hot_memory.md` — short-term high-frequency memory, auto floats and sinks |
| Warm Storage | Repeatedly validated patterns, auto-promoted via `hotness.py promote` |
| λ (lambda) | Time decay coefficient, controls memory cooldown speed |

## FAQ

**Q: Nothing happens after install?**  
A: Check Hindsight is running: `curl http://127.0.0.1:9177/health`. Start the Hindsight daemon if it's not.

**Q: Recall times out?**  
A: Hindsight's local embedding model is slow on first query (30-90s). Subsequent queries are faster. If it keeps timing out, check if Hindsight is overloaded by other processes.

**Q: Do I need to understand Hindsight or Alaya?**  
A: No. Correct the agent → auto-learning. The internals are transparent in daily use.

**Q: When will correction verify / engagement detection be available?**  
A: Engagement detection is available now (✅). Correction verify requires VERIFY_LLM_API_KEY in config.py (⚙️).

**Q: What if Hindsight goes down — will corrections be lost?**  
A: No. Corrections are auto-saved to hot storage and synced when Hindsight recovers. Agent replies are never blocked waiting for Hindsight (>10s auto-skip).

**Q: How do I set up the correction verify API key?**  
A: Edit config.py, uncomment and fill in:
```python
VERIFY_LLM_API_KEY = "sk-your-key"
VERIFY_LLM_ENDPOINT = "https://api.openai.com/v1/chat/completions"  # or compatible API
VERIFY_LLM_MODEL = "gpt-3.5-turbo"  # cheaper is better, verification only
```

## Planned

| Feature | Status |
|---|---|
| Warm storage promotion (hot→warm) | ✅ `hotness.py promote` auto-retains to Hindsight |
| Correction verify (verify.py) | ⚙️ requires VERIFY_LLM_API_KEY |
| Engagement signal | ✅ embedded in SKILL.md, LLM-native detection |
| Cross-platform install scripts | ✅ `cross-install.py` supports 6 platforms |

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
