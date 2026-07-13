# L5 · 元学习引擎 · 设计规范

## 定位

L0-L4 让 Agent 从错误中学习。L5 让 Agent 从**学习过程中**学习——不是"学到了什么"，是"学习方式好不好"。

L5 的输出不是教训，是**对框架自身的优化提案**，通过 User 确认后应用。

---

## 一、符号蒸馏记法

L5 的核心创新——用结构化符号取代自然语言本能，实现跨会话统一理解。

### 规则符号

| 符号 | 含义 | 示例 |
|---|---|---|
| `⟹` | 强制路由（must use） | `bedroom:precool ⟹ SHT30` |
| `∦` | 互斥约束（must not） | `bedroom:precool ∦ xiaomi_living` |
| `⤳` | 状态转移 | `creative ⤳ execution` |
| `⚠️` | 风险模式（附概率） | `⚠️overdesign(p=0.7)` |
| `✓` | 已验证模式（附天数） | `✓pattern[21d]` |
| `↺` | 复发计数 | `↺2` |
| `∩` | 条件组合 | `[深夜] ∩ [好奇心]` |

### 时序符号

```
[creative] ⤳ [exploration] ⤳ [execution]
→ "User 的创新周期：创意 → 调研 → 落地"
```

### 蒸馏管道

```
原材料（~200 tok）
  ↓ 本能蒸馏
本能（~15 tok）
  ↓ L5 检测：同一本能出现 3+ 次
  ↓ 符号蒸馏
符号（~8 tok）
  ↓ 写入心智模型，附带验证计数 + 时间窗口
```

---

## 二、审计引擎

### 2.1 学习速率自评

每 20 条纠正 → 跑一次：

| 指标 | 计算方法 | 低值含义 |
|---|---|---|
| 转化率 | 产出的教训 / 总纠正 | 诊断格式太宽松 |
| 行为延迟 | 纠正后 N 轮不再犯 | instinct 注入方式有问题 |
| 复发率 | 同类错误出现 >1 次 | 适用场景字段太窄 |

### 2.2 信号质量审计

每种信号追踪产出质量：

| 信号 | 追踪指标 | 低质量响应 |
|---|---|---|
| correction | 被回访次数、提炼成模式的比率 | 收紧模板 |
| engagement | 提议接受率、深潜完成率 | 提高触发阈值 |
| surfacing | 镜像复述被确认的比率 | 降低检测灵敏度 |

### 2.3 Profile 效力追踪

| Profile | 核心指标 |
|---|---|
| creative | 每会话"后来被 remember 的内容"数量 |
| execution | 微步骤准确率、User 完成率 |
| exploration | 下一轮是否进入 creative/execution |
| recovery | 提议后 User 情绪是否回升（语义判断） |

### 2.4 跨会话模式挖掘

```
示例发现：
  会话 A（周一 22:00）→ creative，产出 3 设计文档
  会话 B（周三 02:00）→ execution，落地 A 的一个设计
  会话 C（周五 21:00）→ exploration，调研社区方案

  L5 输出：
    "User 的创新周期 = creative ⤳ exploration ⤳ execution
     平均间隔 3-5 天。creative 后期可主动提议探索。"
```

---

## 三、安全栅

### 3.1 沙盒提案

L5 不直接改写框架。生成 `.patch` 文件，附带：

```
改动内容：
改动理由：
预期效果：
风险等级：（低/中/高）
ROI：（token 成本 vs 预期节省）
```

User 说 yes → 应用。说 no → 归档提案 + 否决理由。

### 3.2 可回滚

每次框架自改 = git commit。改坏 → `git revert` 一条命令。

### 3.3 自动熔断

框架自改后 5 轮内出现新纠正 → 自动回滚 + 标记：

> "刚改的规则立刻被纠正——可能改错了。已回滚。请手动审核。"

---

## 四、稳定性防护

### 4.1 冷启动基线

前 30 天不优化，只记录。建立基线分布。30 天后 → 任一指标偏离 2σ → 触发审计。

### 4.2 过拟合防护

优化建议基于最近 30 天数据，但必须在 30 天前随机样本上也成立。只在最近数据上成立 → 标记过拟合，不自动应用。

### 4.3 漂移检测

旧模式不再匹配最近行为 → 标记为漂移。不删除旧规则——归档为"过去的 User 是这样的"。

---

## 五、成本约束

每次 L5 审计带 ROI 报告：

```
"本次审计消耗 1,200 tok ($0.0002)。
 发现 1 个优化——纠正模板简化可节省 ~30 tok/纠正。
 回收周期：13 会话。通过成本审查，建议应用。"

ROI 为负的建议 → 搁置，不自动应用。
```

---

## 六、L4 → L5 数据采集规范

L4 每条产出必须附带以下元数据，L5 审计时直接消费，无需回溯对话：

```yaml
# L4 产出元数据（嵌入 Hindsight retain 的 tags 和 content）
source_signal: correction | engagement | surfacing | manual
source_profile: creative | execution | exploration | recovery
discovery_latency: 3           # 纠正发生 → 教训 retain 之间的轮数
recurrence_flag: false         # 这条教训之前出现过类似吗
profile_sequence: [exploration, creative, execution]  # 本轮会话的 profile 轨迹
session_duration_min: 245      # 会话持续时间
outcome_sentiment: positive    # 会话结束时 User 的情绪基调（语义判断）
```
