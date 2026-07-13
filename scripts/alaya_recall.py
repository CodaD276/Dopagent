#!/usr/bin/env python3
"""
Alaya Recall — Hindsight recall + Alaya Rerank 一体化
用法:
  python alaya_recall.py "你的查询"                     # 直接用查询字符串
  python alaya_recall.py --file payload.json            # 用已有的 recall payload
  python alaya_recall.py "查询" --budget mid --debug    # 调参 + 排名对比

输出: Alaya 重排后的 recall JSON（到 stdout）
"""

import sys
import json
import subprocess
import tempfile
import os
import argparse
from datetime import datetime, timezone

HINDSIGHT_URL = "http://127.0.0.1:9177/v1/default/banks/hermes/memories/recall"
RERANK_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "alaya_rerank.py")
CURL = "curl.exe"


def recall(payload: dict, timeout: int = 120) -> dict:
    """调用 Hindsight recall API"""
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.json', delete=False, encoding='utf-8'
    ) as f:
        json.dump(payload, f, ensure_ascii=False)
        payload_path = f.name

    out_path = payload_path + '.out'

    try:
        result = subprocess.run(
            [CURL, '-s', '-X', 'POST', HINDSIGHT_URL,
             '-H', 'Content-Type: application/json',
             '--data-binary', f'@{payload_path}',
             '--max-time', str(timeout),
             '-o', out_path],
            capture_output=True, text=True, timeout=timeout + 5
        )

        if result.returncode != 0:
            stderr_msg = result.stderr.strip()
            # curl 28 = timeout
            if '28' in stderr_msg or 'timed out' in stderr_msg.lower():
                print(f"[Alaya] recall 超时（{timeout}s），Hindsight 本地模型响应慢", file=sys.stderr)
            else:
                print(f"[Alaya] recall 失败: {stderr_msg}", file=sys.stderr)
            return {'results': [], '_alaya_error': 'recall_failed'}

        with open(out_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    except subprocess.TimeoutExpired:
        print(f"[Alaya] recall 超时（{timeout}s）", file=sys.stderr)
        return {'results': [], '_alaya_error': 'timeout'}
    finally:
        for p in [payload_path, out_path]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass


def rerank(data: dict) -> dict:
    """调用 alaya_rerank.py 重排"""
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.json', delete=False, encoding='utf-8'
    ) as f:
        json.dump(data, f, ensure_ascii=False)
        in_path = f.name

    out_path = in_path + '.reranked'

    try:
        result = subprocess.run(
            [sys.executable, RERANK_SCRIPT, in_path],
            capture_output=True, text=True, timeout=10
        )
        # alaya_rerank 输出到 stdout
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"[Alaya] rerank 解析失败，返回原始结果", file=sys.stderr)
        return data
    finally:
        for p in [in_path, out_path]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass


def build_payload(query: str, budget: str = "mid", types: list = None,
                  max_tokens: int = 4096, tags: list = None) -> dict:
    """构建 recall payload"""
    if types is None:
        types = ["world", "experience", "observation"]
    payload = {
        "query": query,
        "types": types,
        "budget": budget,
        "max_tokens": max_tokens,
        "query_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
    }
    if tags:
        payload["tags"] = tags
        payload["tags_match"] = "any"
    return payload


def main():
    parser = argparse.ArgumentParser(description="Alaya Recall — Hindsight + Rerank")
    parser.add_argument('query', nargs='?', help='自然语言查询')
    parser.add_argument('--file', help='已有 recall payload JSON 文件')
    parser.add_argument('--budget', default='mid', choices=['low', 'mid', 'high'])
    parser.add_argument('--types', nargs='+', default=['world', 'experience', 'observation'])
    parser.add_argument('--max-tokens', type=int, default=4096)
    parser.add_argument('--tags', nargs='+')
    parser.add_argument('--timeout', type=int, default=120)
    parser.add_argument('--debug', action='store_true', help='打印排名对比到 stderr')
    parser.add_argument('--no-rerank', action='store_true', help='跳过 Alaya 重排')
    args = parser.parse_args()

    # 构建 payload
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            payload = json.load(f)
    elif args.query:
        payload = build_payload(
            args.query, budget=args.budget, types=args.types,
            max_tokens=args.max_tokens, tags=args.tags,
        )
    else:
        print("错误: 需要 query 或 --file", file=sys.stderr)
        sys.exit(1)

    # Step 1: Recall
    print(f"[Alaya] 召回中... query={payload.get('query', '(from file)')[:60]}", file=sys.stderr)
    data = recall(payload, timeout=args.timeout)

    if data.get('_alaya_error'):
        json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
        return

    result_count = len(data.get('results', []))
    print(f"[Alaya] 召回 {result_count} 条", file=sys.stderr)

    if result_count == 0 or args.no_rerank:
        json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
        return

    # Step 2: Rerank
    print(f"[Alaya] 重排中...", file=sys.stderr)
    reranked = rerank(data)

    result_count = len(reranked.get('results', []))
    print(f"[Alaya] 重排完成，{result_count} 条", file=sys.stderr)

    if args.debug:
        # 打印排名对比
        results = reranked.get('results', [])
        print(f'\n  {"#":>3}  {"Alaya":>8}  {"HindF":>8}  {"text[:70]"}', file=sys.stderr)
        print(f'  {"—"*3}  {"—"*8}  {"—"*8}  {"—"*70}', file=sys.stderr)
        for i, r in enumerate(results):
            alaya = r.get('alaya_score', 0)
            hind_f = r.get('scores', {}).get('final', 0)
            text = r.get('text', '')[:70]
            print(f'  {i+1:>3}  {alaya:>8.4f}  {hind_f:>8.4f}  {text}', file=sys.stderr)
        print(file=sys.stderr)

    json.dump(reranked, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
