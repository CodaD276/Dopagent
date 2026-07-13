# Dopagent · Architecture Overview / 架构快照

## Completion Status / 完成度总览

```
Self-Learning Loop / 自我学习闭环      ████████████████░░░░  80%
 ① Detect / 检测                      ████████   correction signal ✅
 ② Diagnose / 诊断                    ████████   correction template pinned ✅
 ③ Write / 写入                       ████████   Hindsight retain ✅
 ④ Retrieve / 检索                    ████████   Alaya pipeline ✅
 ⑤ Generalize / 泛化                  ██░░░░░░   needs 50+ corrections
 ⑥ Meta-learn / 元学习                ░░░░░░░░   research phase

3-Tier Memory / 三层记忆              ██████████████░░░░  70%
 Hot / 热存储                         ████████   hot_memory.md + hotness.py ✅
 Warm / 温存储                        ██░░░░░░   hot→warm promotion (designed)
 Cold / 冷存储                        ████████   Hindsight + Alaya ✅

Dopagent Engine / 动机引擎             ██████░░░░░░░░░░░░  30%
 profiles                              ████░░░░   designed
 signals                               ████░░░░   correction ✅, engagement/surfacing pending
 propose                                ██░░░░░░   template designed
 decision_fn                            ░░░░░░░░   pending
```

## File Tree / 文件清单

```
dopagent/
├── README.md / README_EN.md / README_ZH-TW.md
├── SKILL.md               ← Agent entry / Agent 入口
├── install.py             ← One-command bootstrap / 一键部署
├── ROADMAP.md             ← This file / 本文件
├── PORTING.md             ← Platform porting guide / 平台移植
├── L5_SPEC.md             ← Meta-learning spec / 元学习规范
│
├── scripts/               ✅ All ready
│   ├── alaya_rerank.py    ← Alaya formula engine
│   ├── alaya_recall.py    ← recall + rerank
│   └── hotness.py         ← hot storage scheduler
│
├── dopagent/              📐 Designed
│   ├── profiles/          creative / execution / exploration / recovery
│   ├── signals/           correction ✅ · engagement 🚧 · surfacing 🚧
│   └── propose.md         attractive proposal template
│
├── templates/
│   └── hot_memory.md      ← clean template / 空模板
│
└── patches/
    └── .gitkeep           ← integration patches / 集成补丁
```

## Next Steps / 下一步

1. ~~Bootstrap (SKILL.md + install.py)~~ ✅
2. ~~Sanitization~~ ✅ zero personal identifiers
3. ~~L3: Propose + Profile switching~~ ✅
4. ~~README + config layer~~ ✅ self-bootstrapping
5. Correction verification (optional, designed / 已设计)
6. Engagement signal (optional, designed / 已设计)
7. Warm storage promotion logic / 温存储提炼逻辑
8. ~~L5 spec~~ ✅ L5_SPEC.md (symbolic distillation + audit + safety + cost)
9. Generalization — needs 50+ corrections / 泛化 · 等 50+ 纠正记录
