import re
import requests
from config import (
    LLM_PROVIDER, LLM_URL, LLM_API_KEY, LLM_MODEL,
    SUMMARY_SYSTEM_PROMPT, SUMMARY_USER_PROMPT,
)


def _strip_thinking(text: str) -> str:
    """Gemma4 계열 모델의 thinking 채널 토큰 제거."""
    # <|channel>thought ... </channel> 형태 제거
    text = re.sub(r'<\|channel\>.*?</channel>', '', text, flags=re.DOTALL)
    # =====로 구분된 thinking 블록 제거 (mlx_lm generate 출력 형식)
    text = re.sub(r'^=+\n.*?\n=+\n', '', text, flags=re.DOTALL)
    return text.strip()


def _call_openai_compatible(messages):
    """OpenAI 호환 API 호출 (LM Studio, Ollama, OpenAI, OpenRouter, custom)."""
    headers = {"Content-Type": "application/json"}
    if LLM_API_KEY:
        headers["Authorization"] = f"Bearer {LLM_API_KEY}"

    resp = requests.post(
        f"{LLM_URL}/chat/completions",
        headers=headers,
        json={
            "model": LLM_MODEL,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 2048,  # thinking 모델은 reasoning에 많은 토큰 소비
        },
        timeout=180,
    )
    resp.raise_for_status()
    msg = resp.json()["choices"][0]["message"]
    # content → reasoning_content → reasoning 순서로 fallback
    content = _strip_thinking(msg.get("content", "").strip())
    if not content:
        content = _strip_thinking(msg.get("reasoning_content", "").strip())
    if not content:
        content = _strip_thinking(msg.get("reasoning", "").strip())
    return content


def _call_anthropic(messages):
    """Anthropic API 호출 (claude-* 모델)."""
    try:
        import anthropic as _anthropic
    except ImportError:
        raise RuntimeError(
            "anthropic 패키지가 필요합니다: pip install anthropic"
        )

    system = next((m["content"] for m in messages if m["role"] == "system"), "")
    user_messages = [m for m in messages if m["role"] != "system"]

    client = _anthropic.Anthropic(api_key=LLM_API_KEY)
    response = client.messages.create(
        model=LLM_MODEL,
        max_tokens=512,
        system=system,
        messages=user_messages,
    )
    return response.content[0].text.strip()


def _call_llm(messages):
    """설정된 프로바이더로 LLM을 호출한다."""
    if LLM_PROVIDER == "anthropic":
        return _call_anthropic(messages)
    return _call_openai_compatible(messages)


def summarize_item(item):
    """뉴스 항목을 요약한다."""
    desc_part = f"설명: {item['description']}" if item.get("description") else ""
    user_prompt = SUMMARY_USER_PROMPT.format(
        title=item["title"],
        url=item["url"],
        description=desc_part,
    )
    messages = [
        {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
        {"role": "user",   "content": user_prompt},
    ]

    try:
        content = _call_llm(messages)
        return parse_summary(content)
    except Exception as e:
        print(f"  [WARN] 요약 실패 ({item['title'][:30]}): {e}")
        return {"summary": item.get("description", item["title"]), "relevance": "💡"}


def parse_summary(text):
    """LLM 응답에서 요약과 관련도를 파싱한다."""
    summary = ""
    relevance = "💡"

    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("요약:"):
            summary = line[len("요약:"):].strip()
        elif line.startswith("관련도:"):
            rel = line[len("관련도:"):].strip()
            if "🔥" in rel:
                relevance = "🔥"
            elif "⭐" in rel:
                relevance = "⭐"
            else:
                relevance = "💡"

    if not summary:
        summary = text.split("\n")[0].strip()

    return {"summary": summary, "relevance": relevance}


def summarize_all(items):
    """모든 항목을 순차적으로 요약한다."""
    print(f"  제공자: {LLM_PROVIDER} / 모델: {LLM_MODEL}")
    results = []
    total = len(items)

    for i, item in enumerate(items, 1):
        print(f"  [{i}/{total}] {item['title'][:50]}...")
        result = summarize_item(item)
        item["summary"] = result["summary"]
        item["relevance"] = result["relevance"]
        results.append(item)

    return results
