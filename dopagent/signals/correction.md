# Correction Signal
# 检测 "User 在纠正 Agent"

## 触发模式

- "不对" "不是" "你说错了" "其实是..." "应该是..."
- User 在回复中给出了与 Agent 前一回复相矛盾的信息
- User 显式指出 Agent 的错误假设

## 响应流程（已 pin 为 instinct）

1. 识别纠正
2. 填纠正模板（User说了什么 / Agent错在哪 / 正确理解 / 适用场景 / 元模式）
3. `python hotness.py add` → 写入热存储
4. Hindsight retain（imp:8）
5. 回复中展示模板

## 状态
✅ 已实现为 pinned memory instinct
✅ 已验证（2026-07-13：记忆三层架构纠正）
