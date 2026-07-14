#!/usr/bin/env python3
"""
hotness — 热存储调度器
管理 hot_memory.md 的排序、浮沉、提炼。

用法:
  python hotness.py sort      # 按 hotness 重排，裁剪超限条目
  python hotness.py check     # 检查阈值：ACTIVE→WARM→COOLING
  python hotness.py promote   # 扫描 WARM 条目，建议 retain 到 Hindsight
  python hotness.py add       # 交互式添加条目
"""

import re
import sys
from datetime import datetime, timezone
from math import exp
from pathlib import Path

HOT_FILE = Path(__file__).parent / "hot_memory.md"
MAX_SIZE = 50 * 1024  # 50KB 上限

# ══════════════════════════════════════
# hotness 公式
# ══════════════════════════════════════
TYPE_BONUS = {
    "correction": 1.0,
    "decision": 0.8,
    "insight": 0.7,
    "engagement": 0.5,
}
W_RECENCY = 0.40
W_FREQ = 0.25
W_TYPE = 0.25
W_IMP = 0.10


def parse_hot_file():
    """解析 hot_memory.md，返回 (header, sections)"""
    text = HOT_FILE.read_text(encoding="utf-8")
    # 切分段落：以 ### [ 开头的条目
    entries = []
    header_parts = []
    current = []
    in_entry = False

    for line in text.split("\n"):
        if line.startswith("### ["):
            if in_entry and current:
                entries.append("\n".join(current))
            current = [line]
            in_entry = True
        elif in_entry:
            if line.startswith("---") or line.startswith("## "):
                entries.append("\n".join(current))
                current = []
                in_entry = False
                header_parts.append(line)
            else:
                current.append(line)
        else:
            header_parts.append(line)

    if in_entry and current:
        entries.append("\n".join(current))

    return "\n".join(header_parts), entries


def extract_meta(entry):
    """从条目 footer 提取元数据"""
    m = re.search(r"_hotness:\s*([\d.]+)", entry)
    hotness = float(m.group(1)) if m else 0.5
    m = re.search(r"imp:\s*(\d+)", entry)
    importance = int(m.group(1)) if m else 5
    m = re.search(r"acc:\s*(\d+)", entry)
    access_count = int(m.group(1)) if m else 1
    m = re.search(r"last:\s*(\S+)", entry)
    last_access = m.group(1) if m else "unknown"
    m = re.search(r"id:\s*(\S+)", entry)
    entry_id = m.group(1) if m else "unknown"

    # 类型
    etype = "engagement"
    m = re.match(r"### \[(\w+)\]", entry)
    if m:
        etype = m.group(1)

    return {
        "hotness": hotness,
        "importance": importance,
        "access_count": access_count,
        "last_access": last_access,
        "id": entry_id,
        "type": etype,
    }


def compute_hotness(meta, now=None):
    """计算 hotness 分数"""
    if now is None:
        now = datetime.now(timezone.utc)

    # 新鲜度衰减（容忍多种日期格式）
    last_str = meta.get("last_access", "")
    last = None
    # fromisoformat 对短字符串不可靠（"07-13" → 公元7年）
    if len(last_str) >= 10:
        try:
            last = datetime.fromisoformat(last_str)
        except (ValueError, TypeError):
            pass
    if last is None:
        try:
            # 尝试 MM-DDTHH:MM 或 MM-DD，补全当前年份
            date_part = last_str.split("T")[0]
            time_part = last_str.split("T")[1] if "T" in last_str else "00:00"
            last = datetime.strptime(f"{now.year}-{date_part}T{time_part}", "%Y-%m-%dT%H:%M")
            last = last.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            hours = 720  # 未知时间视为 30 天前
            last = None
    if last:
        hours = max(0, (now - last).total_seconds() / 3600)
    else:
        hours = 720
    recency = exp(-0.03 * hours)  # ~24h到50%，~3天到10%

    # 频率
    freq = min(meta["access_count"] / 5.0, 1.0)

    # 类型
    type_b = TYPE_BONUS.get(meta["type"], 0.5)

    # 重要性
    imp = meta["importance"] / 10.0

    return round(
        W_RECENCY * recency + W_FREQ * freq + W_TYPE * type_b + W_IMP * imp, 4
    )


def update_footer(entry, hotness, access_count, now_str=None):
    """更新条目 footer"""
    if now_str is None:
        now_str = datetime.now(timezone.utc).strftime("%m-%d")
    # 替换或追加 footer
    if "_hotness:" in entry:
        entry = re.sub(r"_hotness:\s*[\d.]+", f"_hotness: {hotness}", entry)
        entry = re.sub(r"acc:\s*\d+", f"acc: {access_count}", entry)
        entry = re.sub(r"last:\s*\S+", f"last: {now_str}", entry)
    else:
        entry = entry.rstrip() + f"\n_hotness: {hotness} | acc: {access_count} | last: {now_str}"
    return entry


def classify(hotness):
    if hotness > 0.5:
        return "ACTIVE"
    elif hotness > 0.2:
        return "WARM"
    return "COOLING"


def cmd_sort():
    """重排条目：ACTIVE(按hotness降序) → WARM → COOLING"""
    header, entries = parse_hot_file()
    now = datetime.now(timezone.utc)
    now_str = now.strftime("%m-%dT%H:%M")

    scored = []
    for e in entries:
        meta = extract_meta(e)
        h = compute_hotness(meta, now)
        meta["hotness"] = h
        meta["access_count"] += 0  # sort 不改变访问计数
        scored.append((h, meta, e))

    scored.sort(key=lambda x: x[0], reverse=True)

    # 分组
    active, warm, cooling = [], [], []
    for h, meta, entry in scored:
        tier = classify(h)
        entry = update_footer(entry, h, meta["access_count"], now_str)
        if tier == "ACTIVE":
            active.append(entry)
        elif tier == "WARM":
            warm.append(entry)
        else:
            cooling.append(entry)

    # 组装
    lines = [f"# Hot Memory", f"_last sorted: {now.isoformat()}_", ""]
    lines.append("---")
    lines.append("")
    lines.append("## 🔴 ACTIVE")
    lines.append("<!-- hotness > 0.5 — 每轮回复自动注入 -->")
    lines.append("")
    for e in active:
        lines.append(e)
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 🟡 WARM")
    lines.append("<!-- hotness 0.2–0.5 — 等待更多验证 -->")
    lines.append("")
    for e in warm:
        lines.append(e)
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## ⚪ COOLING → 归档")
    lines.append("<!-- hotness < 0.2，下次排序时移除 -->")
    lines.append("")
    for e in cooling:
        lines.append(e)
        lines.append("")

    full = "\n".join(lines)

    # 裁剪
    if len(full.encode("utf-8")) > MAX_SIZE:
        # 优先保留 ACTIVE，裁剪 COOLING 和 WARM
        trunc = "\n".join(lines[: len(lines) - len(cooling) * 2 - len(warm) * 2])
        full = trunc

    HOT_FILE.write_text(full, encoding="utf-8")
    print(f"排序完成: {len(active)} ACTIVE, {len(warm)} WARM, {len(cooling)} COOLING")
    for h, meta, _ in scored[:5]:
        print(f"  {meta['hotness']:.4f}  [{meta['type']}]  {meta['id']}")


def cmd_check():
    """检查阈值，标记降级条目"""
    header, entries = parse_hot_file()
    now = datetime.now(timezone.utc)

    for e in entries:
        meta = extract_meta(e)
        h = compute_hotness(meta, now)
        old_tier = classify(meta["hotness"])
        new_tier = classify(h)
        if old_tier != new_tier:
            print(f"[{meta['type']}] {meta['id']}: {old_tier} → {new_tier} (hotness: {meta['hotness']:.4f} → {h:.4f})")

    # 重写文件
    cmd_sort()


def cmd_promote():
    """扫描条目，access ≥ 3 的自动 retain 到 Hindsight"""
    header, entries = parse_hot_file()

    HINDSIGHT_URL = "http://127.0.0.1:9177/v1/default/banks/hermes/memories"
    promoted = 0

    for e in entries:
        meta = extract_meta(e)
        if meta["access_count"] >= 3 and meta["hotness"] > 0.3:
            # 提取条目的核心文本（跳过 footer 行）
            lines = [l for l in e.split("\n") if not l.startswith("_hotness:")]
            text = "\n".join(lines).strip()

            etype = meta.get("type", "insight")
            payload = {
                "items": [{
                    "content": f"[promoted from hot storage] {text}",
                    "context": f"hotness.py promote — {etype} promoted after {meta['access_count']} accesses",
                    "tags": ["promoted", etype],
                }],
                "async": True,
            }

            import tempfile, subprocess
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
                json.dump(payload, f, ensure_ascii=False)
                tmp = f.name

            result = subprocess.run(
                ["curl", "-s", "-X", "POST", HINDSIGHT_URL,
                 "-H", "Content-Type: application/json",
                 "--data-binary", f"@{tmp}", "--max-time", "10"],
                capture_output=True, text=True, timeout=15
            )
            os.unlink(tmp)

            if '"success":true' in result.stdout:
                print(f"  ✅ retained: {meta['id']}")
                promoted += 1
            else:
                print(f"  ❌ retain failed: {meta['id']} — {result.stdout[:100]}")

    if promoted == 0:
        print("  无条目符合 promote 条件（需 access ≥3 且 hotness > 0.3）")
    else:
        print(f"\n  {promoted} 条已 retain 到 Hindsight")


def cmd_add():
    """交互式添加条目"""
    print("类型 [correction/decision/insight/engagement]: ", end="")
    etype = sys.stdin.readline().strip() or "insight"
    print("摘要 (一行): ", end="")
    summary = sys.stdin.readline().strip()
    print("详细内容 (多行, 空行结束): ")
    lines = []
    while True:
        line = sys.stdin.readline()
        if not line or line == "\n":
            break
        lines.append(line.rstrip())
    full = "\n".join(lines)
    print("重要性 [1-10, 默认 7]: ", end="")
    imp_str = sys.stdin.readline().strip()
    importance = int(imp_str) if imp_str.isdigit() else 7

    now = datetime.now(timezone.utc)
    now_str = now.strftime("%m-%dT%H:%M")
    eid = f"{etype[:4]}-{now.strftime('%Y%m%d')}-{summary[:20].replace(' ','-')}"

    entry = f"""### [{etype}] {summary}
{full}
_hotness: 0.90 | imp: {importance} | acc: 1 | last: {now_str} | id: {eid}_
"""

    with HOT_FILE.open("a", encoding="utf-8") as f:
        f.write("\n" + entry + "\n")

    print(f"已添加: {eid}")
    cmd_sort()


def cmd_tune():
    """λ 监控——统计条目衰减情况，建议调整 λ"""
    _, entries = parse_hot_file()
    now = datetime.now(timezone.utc)

    tiers = {"ACTIVE": [], "WARM": [], "COOLING": []}
    for e in entries:
        meta = extract_meta(e)
        h = compute_hotness(meta, now)
        tier = classify(h)
        tiers[tier].append((h, meta))

    print(f"{'='*50}")
    print(f"  λ 监控 · {now.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*50}\n")

    total = sum(len(v) for v in tiers.values())
    if total == 0:
        print("  热存储为空，无需调整。")
        return

    for tier_name, items in tiers.items():
        pct = len(items) / total * 100
        print(f"  {tier_name:10s}  {len(items):>3} 条 ({pct:5.1f}%)")
        if items:
            avg_h = sum(h for h, _ in items) / len(items)
            print(f"            平均 hotness: {avg_h:.4f}")

    print()

    # λ 建议
    active_count = len(tiers["ACTIVE"])
    warm_count = len(tiers["WARM"])

    if total < 5:
        print("  → 条目少于 5 条，数据不足。积累后重试。")
    elif active_count == 0 and warm_count > 0:
        print("  ⚠️  无 ACTIVE 条目——衰减可能过快。")
        print("     建议: λ 从 0.03 降至 0.015，让条目在 ACTIVE 停留更久。")
        print("     编辑 hotness.py 第 126 行: exp(-0.03 * hours) → exp(-0.015 * hours)")
    elif active_count > warm_count * 3:
        print("  ⚠️  ACTIVE 堆积——衰减可能过慢。")
        print("     建议: λ 从 0.03 升至 0.06，加快降级节奏。")
        print("     编辑 hotness.py 第 126 行: exp(-0.03 * hours) → exp(-0.06 * hours)")
    else:
        print("  ✅ λ 表现正常，无需调整。")

    print()
    print("  注意: tune 只给建议，不自作主张改 λ。")


if __name__ == "__main__":
    cmds = {"sort": cmd_sort, "check": cmd_check, "promote": cmd_promote, "add": cmd_add, "tune": cmd_tune}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print("用法: python hotness.py [sort|check|promote|add]")
        sys.exit(1)
    cmds[sys.argv[1]]()
