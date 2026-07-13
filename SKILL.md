---
name: dopagent
description: >-
  User 个人助理的自我学习框架。Alaya 检索重排 + 三层记忆 + 纠正自动学习 + Dopagent 动机引擎。
  MANDATORY TRIGGERS:
  你记不记得, 回忆一下, 之前聊过, 之前是不是, 纠正, 你错了, do you remember, recall, remember when, wrong, you are wrong, no that is not.
  SKIP:
  纯闲聊无信息增量, 临时性操作指令, casual chat.
default-enabled: true
---

# Dopagent

## Bootstrap（首次激活）

如果是本 skill 第一次加载：

1. Pin 以下 instincts（如果尚不存在）：
   - `Hindsight recall → python $WORKSPACE/alaya_recall.py "查询"（禁止裸 curl）。公式: 1.2×semantic + 0.3×exp(-0.005×days) + 0.1×(importance/10)，importance 默认 5。`
   - `被 User 纠正时：提取教训 → 填纠正模板 → retain 到 Hindsight (imp:8) → 回复中展示模板。`

2. 检查 `hot_memory.md` 是否在 WORKSPACE。不存在 → 提示 User 运行 `python install.py`。

3. 汇报就绪："纠正我 → 自动学习。'你记不记得' → Alaya 重排。热存储管理中。"

---

## 核心行为

### 记忆检索
- User 说"你记不记得""之前聊过""do you remember""recall" → `python $WORKSPACE/alaya_recall.py "查询" --budget mid`
- 裸 curl 仅限调试

### 纠正学习
- User 说"不对""不是""应该是...""wrong""no" → 填纠正模板 → Hindsight retain (imp:8) + 热存储新增
- 模板：User说了什么 / Agent错在哪 / 正确理解 / 适用场景（下次遇到X→应Y） / 元模式（可选）

### 热存储
- 每轮回复前 → `python $WORKSPACE/hotness.py sort`
- 会话结束 → `python $WORKSPACE/hotness.py check`
- λ 监控 → `python $WORKSPACE/hotness.py tune`（条目≥5时跑）

### Dopagent Check（每轮回复前）

推理步骤，LLM 尽力执行，无程序级强制保障。

```
1. 最近 3 轮 → User 状态？（兴奋/好奇/疲惫/焦虑/反思/想开干）
2. 匹配 profile → creative / execution / exploration / recovery
3. 行动 → 推（用 propose 模板）/ 等 / 换
4. 重大决策 → 写入热存储
```

**四个 Profile**：
- creative：探索语气，不催。"这个方向有意思..."
- execution：拆微步骤，报进度。"第二步 ✓，还剩两步"
- exploration：广度优先，一次 3-5 选项。"哪个让你觉得好玩？"
- recovery：不推任务，<5min 微选项，被拒绝 → 不追。"不急，要不去冲杯抹茶？"

**Propose 模板**："[任务]，而且 [为什么现在是好时机]。看了 [热存储]，[历史证据]。[预估耗时]，[爽感理由]。"
不用"你需要..."——命令式破坏多巴胺循环。

---

## 工具速查

| 触发 | 命令 |
|---|---|
| recall | `python $WORKSPACE/alaya_recall.py "查询" --budget mid` |
| 热存储 sort | `python $WORKSPACE/hotness.py sort` |
| 热存储 check | `python $WORKSPACE/hotness.py check` |
| 热存储 add | `python $WORKSPACE/hotness.py add` |
| λ 监控 | `python $WORKSPACE/hotness.py tune` |
| 纠正 | 填模板 → Hindsight retain (imp:8) → 热存储 add |

## 记忆分层

- **热**（hot_memory.md）：常浮起的高频短期记忆
- **温**（模式层）：多次验证的规律（待积累）
- **冷**（Hindsight）：固化心智模型

---

## 可选增强（默认关闭）

- **Session Retro**：说"记一下今晚的" / "retain session" → 提取触发/状态轨迹/产出/洞察/情绪弧线 → retain imp:7
- **纠正验证**：说"开启纠正验证" / "enable correction verify" → 纠正后调廉价 LLM 检查提取是否准确。Agent 决定何时启用
- **Engagement 检测**：说"开启 engagement 检测" / "enable engagement detection" → 同一话题 ≥3 轮 → 等空隙提议深潜

→ 完整设计文档：[ROADMAP.md](https://github.com/CodaD276/Dopagent/blob/main/ROADMAP.md) · [L5_SPEC.md](https://github.com/CodaD276/Dopagent/blob/main/L5_SPEC.md)
