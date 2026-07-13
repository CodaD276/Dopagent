#!/usr/bin/env python3
"""
Alaya Rerank — Hindsight recall 后处理排序
公式: 1.2 × semantic_sim + 0.3 × time_decay + 0.1 × (importance/10)

用法:
  python alaya_rerank.py recall_output.json          # 从文件读
  curl ... | python alaya_rerank.py                   # 从 stdin 读
  python alaya_rerank.py recall_output.json --debug   # 打印排名变化对比
"""

import json
import sys
import re
from datetime import datetime, timezone
from math import exp

# ═══════════════════════════════════════════════
# 可调参数
# ═══════════════════════════════════════════════
LAMBDA = 0.005           # 时间衰减系数（越大衰减越快）
W_SEMANTIC = 1.2         # 语义相似度权重
W_TIME = 0.3             # 时间衰减权重
W_IMPORTANCE = 0.1       # 重要性权重
DEFAULT_IMPORTANCE = 5   # 无标注记忆的默认重要性（0-10）


def parse_importance(text: str, metadata: dict) -> int:
    """从 metadata.importance 或 content 前缀提取重要性"""
    # 优先读 metadata
    if isinstance(metadata, dict):
        imp = metadata.get('importance')
        if isinstance(imp, (int, float)):
            return max(0, min(10, int(imp)))
    # 兜底: content 中的 [imp:8] 或 [重要性:8]
    if text:
        m = re.search(r'\[imp(?:ortance)?[:：]\s*(\d+)\]', text, re.IGNORECASE)
        if m:
            return max(0, min(10, int(m.group(1))))
    return DEFAULT_IMPORTANCE


def days_ago(timestamp_str: str) -> float:
    """计算距今天数，无时间戳默认 365"""
    if not timestamp_str:
        return 365.0
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        return (now - dt).total_seconds() / 86400.0
    except (ValueError, TypeError):
        return 365.0


def rerank(results: list) -> tuple:
    """对 recall 结果应用 Alaya 公式，返回 (重排结果, 分数列表)"""
    scored = []
    for r in results:
        semantic = r.get('scores', {}).get('semantic', 0)
        mentioned = r.get('mentioned_at', '')
        metadata = r.get('metadata', {})
        text = r.get('text', '')

        importance = parse_importance(text, metadata)
        days = days_ago(mentioned)
        decay = exp(-LAMBDA * days)

        alaya = (
            W_SEMANTIC * semantic +
            W_TIME * decay +
            W_IMPORTANCE * (importance / 10.0)
        )

        scored.append({
            'result': r,
            'alaya_score': alaya,
            'semantic': semantic,
            'decay': decay,
            'importance': importance,
            'days_ago': days,
        })

    scored.sort(key=lambda x: x['alaya_score'], reverse=True)

    return (
        [s['result'] for s in scored],
        [s for s in scored],
    )


def main():
    debug = '--debug' in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith('--')]

    # 读输入
    if args:
        with open(args[0], 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    results = data.get('results', [])
    if not results:
        json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
        return

    reranked, scored = rerank(results)

    # 注入 alaya_score 到每条结果
    for item, s in zip(reranked, scored):
        item['alaya_score'] = round(s['alaya_score'], 6)
        item['_alaya'] = {
            'semantic':    round(s['semantic'], 6),
            'time_decay':  round(s['decay'], 6),
            'importance':  s['importance'],
            'days_ago':    round(s['days_ago'], 1),
        }

    out = dict(data)
    out['results'] = reranked
    out['_alaya_meta'] = {
        'formula': '1.2×semantic + 0.3×time_decay + 0.1×(importance/10)',
        'lambda': LAMBDA,
        'reranked_count': len(reranked),
    }

    if debug:
        # 打印对比到 stderr
        print('\n  Alaya Rerank — 排名变化对比\n', file=sys.stderr)
        print(f'  {"#":>3}  {"Alaya":>8}  {"HindF":>8}  Δ  {"text[:60]"}', file=sys.stderr)
        print(f'  {"—"*3}  {"—"*8}  {"—"*8}  {"—"}  {"—"*60}', file=sys.stderr)
        for i, s in enumerate(scored):
            hind_final = s['result'].get('scores', {}).get('final', 0)
            old_rank = i + 1  # 简化: 对比 hindsight final 排序
            arrow = '→' if old_rank == i + 1 else f'↑{old_rank - (i+1)}' if old_rank > i + 1 else f'↓{(i+1) - old_rank}'
            text_preview = s['result'].get('text', '')[:60]
            print(
                f'  {i+1:>3}  {s["alaya_score"]:>8.4f}  {hind_final:>8.4f}  '
                f'{arrow:<3} {text_preview}',
                file=sys.stderr,
            )
        print(file=sys.stderr)

    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
