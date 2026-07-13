# Dopagent · 架构快照

## 完成度总览

```
自我学习闭环     ████████████████░░░░  80%
 ① 检测          ████████             correction 信号 ✅
 ② 诊断          ████████             纠正模板已 pin ✅
 ③ 写入          ████████             Hindsight retain ✅
 ④ 检索          ████████             Alaya 管道 ✅
 ⑤ 泛化          ██░░░░░░             等数据量（需 50+ 纠正记录）
 ⑥ 元学习        ░░░░░░░░             研究级

三层记忆         ██████████████░░░░  70%
 热存储          ████████             hot_memory.md + hotness.py ✅
 温存储          ██░░░░░░             hot→warm 提炼逻辑（设计完成，待实现）
 冷存储          ████████             Hindsight + Alaya ✅

Dopagent         ██████░░░░░░░░░░░░  30%
 profiles        ████░░░░             四个 profile 参数定义（设计中）
 signals         ████░░░░             correction ✅, engagement/surfacing 待实现
 propose         ██░░░░░░             提议模板（设计中）
 decision_fn     ░░░░░░░░             dopamine_score 函数（待实现）
```

## 文件清单

```
dopagent/
├── README.md              ← 人说读（待写）
├── SKILL.md               ← Agent 入口（待写）
├── install.py             ← 一键 Bootstrap（待写）
├── ROADMAP.md             ← 本文件
│
├── scripts/               ← ✅ 全部就绪
│   ├── alaya_rerank.py    ← Alaya 公式引擎
│   ├── alaya_recall.py    ← recall + 重排一体
│   └── hotness.py         ← 热存储调度器
│
├── dopagent/              ← 🚧 设计中
│   ├── profiles/
│   │   ├── creative.md    ← 创意模式参数
│   │   ├── execution.md   ← 执行模式参数
│   │   ├── exploration.md ← 探索模式参数
│   │   └── recovery.md    ← 低能模式参数
│   ├── signals/
│   │   ├── correction.md  ← User 纠正检测（✅ 已 pin 为 instinct）
│   │   ├── engagement.md  ← 话题粘性检测（待实现）
│   │   └── surfacing.md   ← 反思/感悟检测（待实现）
│   └── propose.md         ← 提议模板（待写）
│
├── templates/
│   └── hot_memory.md      ← 热存储模板 ✅
│
└── patches/
    └── hindsight-hermes.py ← skill 增量修改（待写）
```

## 下一步优先级

1. ~~SKILL.md + install.py~~ ✅ L1 完成
2. ~~快照脱敏~~ ✅ 零个人标识
3. ~~L3：propose + profile 切换~~ ✅
4. ~~README + config 层~~ ✅ 新用户可自举
5. 纠正验证（optional，已设计）
6. Engagement 信号（optional，已设计）
7. 温存储提炼逻辑
8. ~~L5 设计规范~~ ✅ L5_SPEC.md（符号蒸馏 + 审计引擎 + 安全栅 + 成本约束）
9. 泛化 — 积累 50+ 纠正后跑 reflect
