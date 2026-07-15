#!/usr/bin/env python3
"""
verify.py — 纠正验证
调廉价 LLM 检查 Agent 提取的纠正模板是否准确反映了 User 的纠正意图。

用法:
  python verify.py correction_context.txt extracted_lesson.txt
  → {match: bool, discrepancy: str|null}

配置: 在 config.py 中设置 VERIFY_LLM_API_KEY 和 VERIFY_LLM_ENDPOINT。
      不配置时优雅降级——输出 {match: null, reason: "not configured"}。
"""

import sys
import json
import subprocess
import tempfile
import os

# ── 配置（从 config.py 读取，不存在则降级） ──
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import config
    API_KEY = getattr(config, "VERIFY_LLM_API_KEY", None)
    ENDPOINT = getattr(config, "VERIFY_LLM_ENDPOINT", "https://api.openai.com/v1/chat/completions")
    MODEL = getattr(config, "VERIFY_LLM_MODEL", "gpt-3.5-turbo")
except ImportError:
    API_KEY = None
    ENDPOINT = None
    MODEL = None


def verify(correction_context: str, extracted_lesson: str) -> dict:
    """检查提取的教训是否准确反映纠正意图"""

    if not API_KEY:
        return {"match": None, "reason": "VERIFY_LLM_API_KEY not configured in config.py"}

    prompt = f"""You are a verification checker. Compare the user's correction with the agent's extracted lesson.
Output ONLY a JSON object, nothing else.

User's correction:
{correction_context}

Agent's extracted lesson:
{extracted_lesson}

If the extraction accurately captures the correction, output:
{{"match": true, "discrepancy": null}}

If NOT accurate, output:
{{"match": false, "discrepancy": "brief description of what's wrong"}}"""

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 200,
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False)
        tmp_in = f.name

    tmp_out = tmp_in + ".out"

    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", ENDPOINT,
             "-H", f"Authorization: Bearer {API_KEY}",
             "-H", "Content-Type: application/json",
             "--data-binary", f"@{tmp_in}",
             "--max-time", "15", "-o", tmp_out],
            capture_output=True, text=True, timeout=20
        )

        if os.path.exists(tmp_out):
            with open(tmp_out, 'r', encoding='utf-8') as f:
                response = json.load(f)
            choice = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            try:
                return json.loads(choice)
            except json.JSONDecodeError:
                return {"match": None, "reason": f"unparseable response: {choice[:100]}"}
        else:
            return {"match": None, "reason": f"LLM call failed: {result.stderr[:100]}"}

    finally:
        for p in [tmp_in, tmp_out]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass


def main():
    if len(sys.argv) < 3:
        print("用法: python verify.py <correction_context> <extracted_lesson>")
        print("  或: echo 'context' | python verify.py --stdin 'lesson'")
        sys.exit(1)

    context = sys.argv[1]
    lesson = sys.argv[2]
    result = verify(context, lesson)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
